"""
Context Chunking Service for OpenClaw
Tier-aware semantic chunking using chonkie
Optimized for 32GB RAM environments
"""

from chonkie import (
    SemanticChunker, RecursiveChunker, SentenceChunker,
    Pipeline, OverlapRefinery
)
from chonkie.types import Chunk
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Dict, Optional, Any
import sqlite3
import json
import hashlib
import gzip
import os


class PriorityLevel(Enum):
    """Priority levels for context retention."""
    CRITICAL = auto()   # Never evict from hot tier
    HIGH = auto()       # Prefer warm tier retention  
    NORMAL = auto()     # Standard lifecycle
    LOW = auto()        # Compress aggressively
    ARCHIVE = auto()    # Move to cold immediately


class ContextType(Enum):
    """Types of context content."""
    CONVERSATION = "conv"
    TOOL_RESULT = "tool"
    MEMORY_REF = "mem"
    CODE_SNIPPET = "code"
    FILE_CONTENT = "file"
    COMPACTION_SUMMARY = "compact"
    SYSTEM_PROMPT = "system"


@dataclass
class ContextMetadata:
    """Universal metadata for all context chunks."""
    
    # Identification
    chunk_id: str
    session_id: str
    parent_id: Optional[str] = None
    
    # Tier classification
    priority: PriorityLevel = PriorityLevel.NORMAL
    context_type: ContextType = ContextType.CONVERSATION
    current_tier: str = "hot"  # hot | warm | cold
    
    # Temporal tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    
    # Size metrics
    token_count: int = 0
    char_count: int = 0
    compressed_size: Optional[int] = None
    
    # Semantic fingerprint
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_vector: Optional[List[float]] = None
    
    # Relations
    related_chunks: List[str] = field(default_factory=list)
    source_file: Optional[str] = None
    source_line_start: Optional[int] = None
    source_line_end: Optional[int] = None
    
    # Lifecycle
    compaction_version: int = 0
    is_compressed: bool = False
    is_summarized: bool = False
    
    def to_tags(self) -> Dict[str, str]:
        """Convert to flat tag dictionary for vector DB indexing."""
        return {
            "id": self.chunk_id,
            "tier": self.current_tier,
            "priority": self.priority.name.lower(),
            "type": self.context_type.value,
            "session": self.session_id[:8] if self.session_id else "",
            "created": self.created_at.isoformat(),
            "tokens": str(self.token_count),
            "accessed": str(self.access_count),
            "compaction_ver": str(self.compaction_version)
        }
    
    def should_promote(self) -> bool:
        """Check if chunk should be promoted to hotter tier."""
        if self.current_tier == "hot":
            return False
        return self.access_count > 5 and self.priority == PriorityLevel.HIGH
    
    def should_demote(self) -> bool:
        """Check if chunk should be demoted to colder tier."""
        if self.current_tier == "cold":
            return False
        hours_since_access = (datetime.utcnow() - self.last_accessed).total_seconds() / 3600
        
        demotion_rules = {
            "hot": hours_since_access > 1 and self.access_count < 3,
            "warm": hours_since_access > 24 and self.access_count < 2
        }
        return demotion_rules.get(self.current_tier, False)


@dataclass 
class TierConfig:
    """Configuration for a context tier."""
    chunk_size: int
    chunk_overlap: int = 0
    similarity_threshold: float = 0.75
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_tokens: int = 8192
    strategy: str = "recursive"  # recursive | semantic | sentence
    compression: Optional[str] = None


class OpenClawContextChunker:
    """
    Tier-aware context chunking service for OpenClaw.
    
    Implements the three-tier architecture:
    - HOT: In-RAM, fast recursive chunking, 512 token chunks
    - WARM: Vector DB, semantic chunking, 1024 token chunks  
    - COLD: Disk archive, compressed, 2048 token chunks
    """
    
    # Predefined chunk profiles optimized for 32GB RAM
    TIER_PROFILES = {
        "hot": TierConfig(
            chunk_size=512,
            chunk_overlap=64,
            max_tokens=8192,
            strategy="recursive"
        ),
        "warm": TierConfig(
            chunk_size=1024,
            chunk_overlap=128,
            similarity_threshold=0.75,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            max_tokens=32768,
            strategy="semantic"
        ),
        "cold": TierConfig(
            chunk_size=2048,
            similarity_threshold=0.65,
            max_tokens=131072,
            strategy="semantic",
            compression="gzip"
        )
    }
    
    def __init__(self, 
                 workspace_path: str = "~/.openclaw/workspace",
                 ram_gb: int = 32,
                 embedding_device: str = "cpu"):
        """
        Initialize the context chunker.
        
        Args:
            workspace_path: Path to OpenClaw workspace
            ram_gb: Available RAM for tier sizing
            embedding_device: Device for embeddings (cpu/cuda)
        """
        self.workspace_path = os.path.expanduser(workspace_path)
        self.ram_gb = ram_gb
        self.embedding_device = embedding_device
        
        # Initialize chunkers for each tier
        self._chunkers: Dict[str, Any] = {}
        self._init_chunkers()
        
        # Initialize vector database
        self.vec_db_path = os.path.join(self.workspace_path, "context_index.db")
        self._init_vector_store()
        
    def _init_chunkers(self):
        """Initialize chunker instances for each tier."""
        for tier, config in self.TIER_PROFILES.items():
            if config.strategy == "recursive":
                self._chunkers[tier] = RecursiveChunker(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap
                )
            elif config.strategy == "semantic":
                self._chunkers[tier] = SemanticChunker(
                    embedding_model=config.embedding_model,
                    chunk_size=config.chunk_size,
                    similarity_threshold=config.similarity_threshold
                )
            elif config.strategy == "sentence":
                self._chunkers[tier] = SentenceChunker(
                    chunk_size=config.chunk_size
                )
    
    def _init_vector_store(self):
        """Initialize SQLite vector store with sqlite-vec extension."""
        os.makedirs(os.path.dirname(self.vec_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.vec_db_path)
        cursor = conn.cursor()
        
        # Enable sqlite-vec if available
        try:
            cursor.execute("SELECT load_extension('vec0')")
        except sqlite3.OperationalError:
            pass  # sqlite-vec not available, use regular SQLite
        
        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_chunks (
                chunk_id TEXT PRIMARY KEY,
                session_id TEXT,
                parent_id TEXT,
                tier TEXT,
                priority TEXT,
                context_type TEXT,
                content TEXT,
                content_compressed BLOB,
                token_count INTEGER,
                char_count INTEGER,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                compaction_version INTEGER DEFAULT 0,
                is_compressed BOOLEAN DEFAULT 0,
                is_summarized BOOLEAN DEFAULT 0,
                embedding_json TEXT,
                metadata_json TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON context_chunks(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tier ON context_chunks(tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON context_chunks(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accessed ON context_chunks(last_accessed)")
        
        conn.commit()
        conn.close()
    
    def chunk_text(self, 
                   text: str, 
                   tier: str = "warm",
                   metadata: Optional[ContextMetadata] = None) -> List[Dict[str, Any]]:
        """
        Chunk text according to tier configuration.
        
        Args:
            text: Text to chunk
            tier: Target tier (hot/warm/cold)
            metadata: Optional metadata for chunks
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunker = self._chunkers.get(tier, self._chunkers["warm"])
        raw_chunks = chunker(text)
        
        results = []
        for i, chunk in enumerate(raw_chunks):
            chunk_id = self._generate_chunk_id(text, i)
            
            chunk_meta = metadata or ContextMetadata(
                chunk_id=chunk_id,
                session_id="default",
                current_tier=tier
            )
            chunk_meta.chunk_id = chunk_id
            chunk_meta.token_count = chunk.token_count
            chunk_meta.char_count = len(chunk.text)
            
            result = {
                "chunk_id": chunk_id,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "metadata": chunk_meta,
                "tier": tier
            }
            results.append(result)
        
        return results
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store chunks in the appropriate tier storage.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.vec_db_path)
        cursor = conn.cursor()
        
        for chunk in chunks:
            meta = chunk["metadata"]
            tier = chunk["tier"]
            content = chunk["text"]
            
            # Compress if cold tier
            if tier == "cold":
                content_compressed = gzip.compress(content.encode('utf-8'))
                is_compressed = True
            else:
                content_compressed = None
                is_compressed = False
            
            cursor.execute("""
                INSERT OR REPLACE INTO context_chunks (
                    chunk_id, session_id, parent_id, tier, priority, context_type,
                    content, content_compressed, token_count, char_count,
                    created_at, last_accessed, access_count, compaction_version,
                    is_compressed, is_summarized, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meta.chunk_id,
                meta.session_id,
                meta.parent_id,
                tier,
                meta.priority.name,
                meta.context_type.value,
                content if not is_compressed else None,
                content_compressed,
                meta.token_count,
                meta.char_count,
                meta.created_at.isoformat(),
                meta.last_accessed.isoformat(),
                meta.access_count,
                meta.compaction_version,
                is_compressed,
                meta.is_summarized,
                json.dumps(meta.to_tags())
            ))
        
        conn.commit()
        conn.close()
        return True
    
    def retrieve_chunks(self, 
                       session_id: Optional[str] = None,
                       tier: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from storage.
        
        Args:
            session_id: Filter by session
            tier: Filter by tier
            limit: Maximum results
            
        Returns:
            List of chunk dictionaries
        """
        conn = sqlite3.connect(self.vec_db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM context_chunks WHERE 1=1"
        params = []
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if tier:
            query += " AND tier = ?"
            params.append(tier)
        
        query += " ORDER BY last_accessed DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in cursor.description:
            print(row[0])
        
        conn.close()
        return results
    
    def compact_session(self, 
                       session_id: str,
                       target_tier: str = "warm") -> Dict[str, Any]:
        """
        Compact session context by moving to colder tier.
        
        Args:
            session_id: Session to compact
            target_tier: Target tier for compaction
            
        Returns:
            Compaction statistics
        """
        # TODO: Implement compaction logic
        return {
            "session_id": session_id,
            "target_tier": target_tier,
            "chunks_moved": 0,
            "tokens_saved": 0
        }
    
    def _generate_chunk_id(self, text: str, index: int) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{text[:100]}:{index}:{datetime.utcnow().timestamp()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


# Singleton instance
_chunker_instance: Optional[OpenClawContextChunker] = None


def get_chunker(workspace_path: str = "~/.openclaw/workspace", 
                ram_gb: int = 32) -> OpenClawContextChunker:
    """Get or create singleton chunker instance."""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = OpenClawContextChunker(workspace_path, ram_gb)
    return _chunker_instance