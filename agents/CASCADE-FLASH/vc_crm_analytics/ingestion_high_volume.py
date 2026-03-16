# ============================================================
# VC Outreach CRM Analytics Engine - PHASE 3 SCALING
# Optimizations for 10k events/sec ingestion
# ============================================================

"""
This module provides high-scale ingestion capabilities:
- Connection pooling (asyncpg)
- Redis caching for real-time queries
- Kafka buffering for event streaming
- Batch processing with backpressure handling
"""

import asyncio
import json
import aioredis
import asyncpg
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import kafka
from kafka import KafkaProducer, KafkaConsumer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# CONNECTION POOLING (Database)
# ============================================================

class DatabasePool:
    """Managed database connection pool for high concurrency"""
    
    def __init__(self, dsn: str, min_size: int = 10, max_size: int = 100):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize the connection pool"""
        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60,
            server_settings={
                'jit': 'off',  # Disable JIT for short queries
                'application_name': 'vc_crm_analytics'
            }
        )
        logger.info(f"Database pool initialized: {self.min_size}-{self.max_size} connections")
    
    async def close(self):
        if self._pool:
            await self._pool.close()
    
    @property
    def pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("Pool not initialized")
        return self._pool

# ============================================================
# REDIS CACHE LAYER
# ============================================================

class MetricsCache:
    """Redis-backed cache for real-time metrics"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
    
    async def initialize(self):
        self._redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get_realtime_metrics(self) -> Optional[dict]:
        """Get cached real-time metrics"""
        if not self._redis:
            return None
        data = await self._redis.get("metrics:realtime")
        return json.loads(data) if data else None
    
    async def set_realtime_metrics(self, metrics: dict, ttl: int = 30):
        """Cache real-time metrics with short TTL"""
        if self._redis:
            await self._redis.setex(
                "metrics:realtime",
                ttl,
                json.dumps(metrics, default=str)
            )
    
    async def increment_counter(self, key: str, amount: int = 1):
        """Increment a counter (for real-time stats)"""
        if self._redis:
            await self._redis.incrby(f"counter:{key}", amount)
            await self._redis.expire(f"counter:{key}", 3600)  # 1 hour TTL
    
    async def get_campaign_stats_cached(self, campaign_id: str) -> Optional[dict]:
        """Get cached campaign statistics"""
        if not self._redis:
            return None
        data = await self._redis.get(f"campaign:{campaign_id}:stats")
        return json.loads(data) if data else None
    
    async def set_campaign_stats(self, campaign_id: str, stats: dict, ttl: int = 300):
        """Cache campaign stats with 5 minute TTL"""
        if self._redis:
            await self._redis.setex(
                f"campaign:{campaign_id}:stats",
                ttl,
                json.dumps(stats, default=str)
            )

# ============================================================
# KAFKA EVENT STREAMING
# ============================================================

@dataclass
class EmailEvent:
    email_id: str
    event_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    link_url: Optional[str]
    occurred_at: datetime
    metadata: dict


class KafkaEventProducer:
    """Kafka producer for event buffering"""
    
    def __init__(self, bootstrap_servers: List[str] = ["localhost:9092"]):
        self.bootstrap_servers = bootstrap_servers
        self._producer: Optional[KafkaProducer] = None
    
    def initialize(self):
        """Initialize Kafka producer (blocking, run in thread)"""
        self._producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            batch_size=65536,  # 64KB batches
            linger_ms=10,      # 10ms batching
            compression_type='gzip',
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=5
        )
        logger.info(f"Kafka producer connected to {self.bootstrap_servers}")
    
    def send_event(self, topic: str, event: EmailEvent, key: Optional[str] = None):
        """Send event to Kafka topic"""
        if self._producer:
            self._producer.send(
                topic,
                key=key,
                value={
                    'email_id': event.email_id,
                    'event_type': event.event_type,
                    'ip_address': event.ip_address,
                    'user_agent': event.user_agent,
                    'link_url': event.link_url,
                    'occurred_at': event.occurred_at.isoformat(),
                    'metadata': event.metadata
                }
            )
    
    def flush(self):
        """Flush pending messages"""
        if self._producer:
            self._producer.flush()
    
    def close(self):
        if self._producer:
            self._producer.close()


class KafkaEventConsumer:
    """Kafka consumer for batch database writes"""
    
    def __init__(
        self,
        bootstrap_servers: List[str],
        topic: str,
        db_pool: DatabasePool,
        batch_size: int = 1000,
        flush_interval_ms: int = 5000
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.db_pool = db_pool
        self.batch_size = batch_size
        self.flush_interval_ms = flush_interval_ms
        self._consumer: Optional[KafkaConsumer] = None
        self._batch: List[EmailEvent] = []
        self._running = False
    
    def initialize(self):
        self._consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='analytics-ingestion',
            auto_offset_reset='latest',
            enable_auto_commit=False,
            max_poll_records=self.batch_size
        )
    
    async def run(self):
        """Main consumer loop"""
        self._running = True
        last_flush = datetime.utcnow()
        
        while self._running:
            # Poll Kafka (blocking, run in executor)
            messages = await asyncio.get_event_loop().run_in_executor(
                None, self._poll_batch
            )
            
            for msg in messages:
                event = EmailEvent(
                    email_id=msg.value['email_id'],
                    event_type=msg.value['event_type'],
                    ip_address=msg.value.get('ip_address'),
                    user_agent=msg.value.get('user_agent'),
                    link_url=msg.value.get('link_url'),
                    occurred_at=datetime.fromisoformat(msg.value['occurred_at']),
                    metadata=msg.value.get('metadata', {})
                )
                self._batch.append(event)
            
            # Check if we should flush
            time_since_flush = (datetime.utcnow() - last_flush).total_seconds() * 1000
            should_flush = (
                len(self._batch) >= self.batch_size or
                time_since_flush >= self.flush_interval_ms
            )
            
            if should_flush and self._batch:
                await self._flush_batch()
                last_flush = datetime.utcnow()
                
                # Commit offsets after successful write
                if self._consumer:
                    self._consumer.commit()
    
    def _poll_batch(self, timeout_ms: int = 1000):
        """Poll messages from Kafka (blocking)"""
        if self._consumer:
            return self._consumer.poll(timeout_ms=timeout_ms).get(self.topic, [])
        return []
    
    async def _flush_batch(self):
        """Write batch to database using COPY for speed"""
        if not self._batch:
            return
        
        records = [
            (
                e.email_id, e.event_type, e.ip_address,
                e.user_agent, e.link_url, json.dumps(e.metadata), e.occurred_at
            )
            for e in self._batch
        ]
        
        try:
            async with self.db_pool.pool.acquire() as conn:
                await conn.copy_records_to_table(
                    'email_events',
                    records=records,
                    columns=['email_id', 'event_type', 'ip_address', 
                            'user_agent', 'link_url', 'metadata', 'occurred_at']
                )
            
            logger.info(f"Flushed {len(records)} events to database")
            self._batch.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush batch: {e}")
            # Keep batch for retry, implement backoff
    
    def stop(self):
        self._running = False
        if self._consumer:
            self._consumer.close()

# ============================================================
# HIGH-VOLUME INGESTION SERVICE
# ============================================================

class HighVolumeIngestionService:
    """
    Unified service for high-volume event ingestion.
    
    Flow: API -> Kafka -> Batch Consumer -> PostgreSQL
    This provides backpressure handling and buffering during DB slowdowns.
    """
    
    def __init__(
        self,
        db_dsn: str,
        redis_url: str = "redis://localhost:6379",
        kafka_servers: List[str] = ["localhost:9092"]
    ):
        self.db_pool = DatabasePool(db_dsn)
        self.cache = MetricsCache(redis_url)
        self.kafka_producer = KafkaEventProducer(kafka_servers)
        self.kafka_consumer = KafkaEventConsumer(
            bootstrap_servers=kafka_servers,
            topic="email-events",
            db_pool=self.db_pool
        )
        self._initialized = False
    
    async def initialize(self):
        """Initialize all components"""
        await self.db_pool.initialize()
        await self.cache.initialize()
        
        # Start Kafka producer in background thread
        await asyncio.get_event_loop().run_in_executor(
            None, self.kafka_producer.initialize
        )
        
        # Start consumer
        await asyncio.get_event_loop().run_in_executor(
            None, self.kafka_consumer.initialize
        )
        asyncio.create_task(self.kafka_consumer.run())
        
        self._initialized = True
        logger.info("HighVolumeIngestionService initialized")
    
    async def ingest_event(self, event: EmailEvent) -> bool:
        """
        Ingest a single event.
        For high volume, events are buffered in Kafka before DB write.
        """
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        # Send to Kafka (fast, non-blocking)
        self.kafka_producer.send_event(
            "email-events",
            event,
            key=event.email_id  # Partition by email for ordering
        )
        
        # Update Redis counters for real-time display
        await self.cache.increment_counter(f"events:{event.event_type}")
        
        return True
    
    async def ingest_batch(self, events: List[EmailEvent]) -> int:
        """Batch ingest events"""
        for event in events:
            self.kafka_producer.send_event("email-events", event)
        
        self.kafka_producer.flush()
        return len(events)
    
    async def get_realtime_metrics(self) -> dict:
        """Get real-time metrics (cached + counters)"""
        # Try cache first
        cached = await self.cache.get_realtime_metrics()
        if cached:
            return cached
        
        # Fall back to database query
        async with self.db_pool.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) FILTER (WHERE occurred_at >= NOW() - INTERVAL '1 hour') as events_last_hour,
                    COUNT(DISTINCT email_id) FILTER (WHERE occurred_at >= NOW() - INTERVAL '1 day') as unique_emails_today
                FROM email_events
                WHERE occurred_at >= NOW() - INTERVAL '1 day'
            """)
        
        metrics = dict(row)
        await self.cache.set_realtime_metrics(metrics)
        return metrics
    
    async def close(self):
        """Graceful shutdown"""
        self.kafka_consumer.stop()
        self.kafka_producer.close()
        await self.db_pool.close()

# ============================================================
# USAGE EXAMPLE
# ============================================================

async def main():
    """Example usage of high-volume ingestion"""
    service = HighVolumeIngestionService(
        db_dsn="postgresql://user:pass@localhost/vc_crm",
        redis_url="redis://localhost:6379",
        kafka_servers=["localhost:9092"]
    )
    
    await service.initialize()
    
    # Ingest a single event
    event = EmailEvent(
        email_id="550e8400-e29b-41d4-a716-446655440000",
        event_type="open",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        link_url=None,
        occurred_at=datetime.utcnow(),
        metadata={"campaign_id": "123"}
    )
    
    await service.ingest_event(event)
    
    # Get metrics
    metrics = await service.get_realtime_metrics()
    print(f"Metrics: {metrics}")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(main())
