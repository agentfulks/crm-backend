# TIER 2 ARCHITECT DELIVERABLE
## Context Management & Token Optimization Strategy
**Agent:** Kimi k2.5 | **Role:** System Architecture Design

---

## PROGRESS HANDOFF FROM TIER 1 (Scout - Gemini 3 Flash Preview)

### Tier 1 Research Summary

**OpenClaw-Native Context Management:**
- **Compaction Modes:** OpenClaw supports `safeguard` (default, conservative) and `aggressive` modes for context truncation
- **Auto-compaction triggers** when context approaches model limits (configurable via `reserveTokensFloor`, default 20,000)
- **Memory Flush:** Silent agentic turn before compaction to persist durable memories to disk
- **Pruning vs Compaction:** Pruning trims tool results in-memory per request; compaction summarizes and persists to JSONL

**Chonkie Analysis:**
- Lightweight Python chunking library with 33x faster token chunking than alternatives
- **SemanticChunker:** Uses embedding similarity (all-MiniLM-L6-v2) with configurable thresholds
- **RecursiveChunker:** Hierarchical semantic splitting ideal for code/documents
- **Pipeline Architecture:** CHOMP (Fetcher → Chef → Chunker → Refinery → Porter)
- Supports 32+ integrations including vector DBs (Chroma, Qdrant, Weaviate)
- Zero bloat philosophy aligns with OpenClaw's efficiency goals

**Cost-Performance Analysis:**
- Smaller chunks (128-256 tokens): Better granular semantic retrieval, higher recall
- Larger chunks (512-1024 tokens): Better context preservation, lower retrieval overhead
- **Target retention rate:** >85% for critical information
- Semantic chunking achieves 95.83% recall in RAG benchmarks

---

## TIER 2 ARCHITECTURE DESIGN

### 1. Chonkie Integration Implementation Plan

#### Phase 1: Infrastructure Layer (Foundation)

**Component:** `ContextChunkingService`
```
Location: agents/CASCADE-FLASH/skills/context-manager/
Purpose: Bridge between OpenClaw session state and chonkie processing
```

**Key Integration Points:**
1. **Pre-Compaction Hook:** Intercept auto-compaction triggers to apply semantic chunking
2. **Memory Index Pipeline:** Feed memory/*.md files through chonkie's CHOMP pipeline
3. **Session Context Streaming:** Real-time chunking of incoming tool outputs

**Architecture Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw Session Context                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Tool Results │  │ Chat History │  │ Memory References    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ContextChunkingService (Python Bridge)              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Chonkie Pipeline: SemanticChunker → OverlapRefinery      │ │
│  │  - Embedding Model: all-MiniLM-L6-v2 (local)              │ │
│  │  - Similarity Threshold: 0.75 (tunable)                   │ │
│  │  - Chunk Size: Dynamic based on tier (see below)          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Tiered Storage Architecture                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ TIER 1: HOT  │  │ TIER 2: WARM │  │ TIER 3: COLD         │  │
│  │  (in-RAM)    │  │  (Vector DB) │  │  (Disk Archive)      │  │
│  │  8K tokens   │  │  500K docs   │  │  Unlimited           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Phase 2: Chunking Strategy Configuration

**Installation Requirements:**
```bash
# Core chonkie with semantic chunking
pip install "chonkie[semantic]"

# Full pipeline with local embeddings
pip install "chonkie[semantic,code,catsu]"

# API server for multi-agent access
pip install "chonkie[api,semantic,code,catsu]"
```

**Python Service Wrapper:**
```python
# skills/context-manager/chunking_service.py
from chonkie import SemanticChunker, RecursiveChunker, Pipeline
from chonkie.types import Chunk
import sqlite3
from typing import List, Dict, Optional
import json

class OpenClawContextChunker:
    """
    Tier-aware context chunking for OpenClaw sessions.
    Optimized for 32GB RAM environments with local indexing.
    """
    
    CHUNK_PROFILES = {
        "hot": {
            "chunker": "recursive",
            "chunk_size": 512,
            "chunk_overlap": 64,
            "max_tokens": 8192,
            "priority": "latency"
        },
        "warm": {
            "chunker": "semantic", 
            "chunk_size": 1024,
            "similarity_threshold": 0.75,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "max_tokens": 32768,
            "priority": "balanced"
        },
        "cold": {
            "chunker": "semantic",
            "chunk_size": 2048,
            "similarity_threshold": 0.65,
            "compression": "gzip",
            "priority": "storage"
        }
    }
    
    def __init__(self, ram_gb: int = 32):
        self.ram_gb = ram_gb
        self.pipeline = self._init_pipeline()
        self.vec_db = self._init_vector_store()
        
    def _init_pipeline(self) -> Pipeline:
        """Initialize CHOMP pipeline with tier-aware chunking."""
        return (
            Pipeline()
            .process_with("text")
            .chunk_with("semantic", 
                       chunk_size=self.CHUNK_PROFILES["warm"]["chunk_size"],
                       similarity_threshold=0.75)
            .refine_with("overlap", context_size=128)
        )
    
    def chunk_for_tier(self, text: str, tier: str) -> List[Chunk]:
        """Apply tier-appropriate chunking strategy."""
        profile = self.CHUNK_PROFILES.get(tier, self.CHUNK_PROFILES["warm"])
        
        if tier == "hot":
            # Fast recursive chunking for hot tier
            chunker = RecursiveChunker(
                chunk_size=profile["chunk_size"],
                chunk_overlap=profile["chunk_overlap"]
            )
        else:
            # Semantic chunking for warm/cold tiers
            chunker = SemanticChunker(
                embedding_model=profile["embedding_model"],
                chunk_size=profile["chunk_size"],
                similarity_threshold=profile["similarity_threshold"]
            )
        
        return chunker(text)
```

---

### 2. Tiered Metadata Tagging System

#### Priority Classification Schema

```json
{
  "context_tiers": {
    "hot": {
      "description": "Immediate working memory - active conversation context",
      "retention_criteria": [
        "Last 3-5 conversation turns",
        "Active tool execution context",
        "Pending user questions",
        "Uncommitted code changes"
      ],
      "storage": "in-RAM (session state)",
      "max_tokens": 8192,
      "ttl_seconds": 3600,
      "chunk_size": 512,
      "metadata_tags": ["priority:critical", "tier:hot", "access:immediate"]
    },
    "warm": {
      "description": "Recent session history - indexed for fast retrieval",
      "retention_criteria": [
        "Summarized conversation history",
        "Frequently accessed memories",
        "Cached tool results",
        "Session compaction summaries"
      ],
      "storage": "vector_db (sqlite-vec)",
      "max_tokens": 32768,
      "ttl_hours": 168,
      "chunk_size": 1024,
      "metadata_tags": ["priority:high", "tier:warm", "access:fast"]
    },
    "cold": {
      "description": "Archived context - compressed long-term storage",
      "retention_criteria": [
        "Historical daily logs",
        "Inactive project context",
        "Old compaction summaries",
        "Compressed memory archives"
      ],
      "storage": "disk (compressed JSONL)",
      "max_tokens": "unlimited",
      "ttl_days": 365,
      "chunk_size": 2048,
      "metadata_tags": ["priority:archive", "tier:cold", "access:ondemand"]
    }
  }
}
```

#### Metadata Tag Specification

```python
# skills/context-manager/metadata_tags.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional
from datetime import datetime

class PriorityLevel(Enum):
    CRITICAL = auto()   # Never evict from hot tier
    HIGH = auto()       # Prefer warm tier retention
    NORMAL = auto()     # Standard lifecycle
    LOW = auto()        # Compress aggressively
    ARCHIVE = auto()    # Move to cold immediately

class ContextType(Enum):
    CONVERSATION = "conv"
    TOOL_RESULT = "tool"
    MEMORY_REF = "mem"
    CODE_SNIPPET = "code"
    FILE_CONTENT = "file"
    COMPACTION_SUMMARY = "compact"

@dataclass
class ContextMetadata:
    """Universal metadata tag for all context chunks."""
    
    # Identification
    chunk_id: str
    session_id: str
    parent_id: Optional[str] = None
    
    # Tier classification
    priority: PriorityLevel = PriorityLevel.NORMAL
    context_type: ContextType = ContextType.CONVERSATION
    current_tier: str = "hot"  # hot | warm | cold
    
    # Temporal tracking
    created_at: datetime = datetime.utcnow()
    last_accessed: datetime = datetime.utcnow()
    access_count: int = 0
    
    # Size metrics
    token_count: int = 0
    char_count: int = 0
    compressed_size: Optional[int] = None
    
    # Semantic fingerprint
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_vector: Optional[List[float]] = None
    
    # Relations
    related_chunks: List[str] = None
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
            "session": self.session_id[:8],
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
```

---

### 3. Goldilocks Chunk Size Determination

#### Mathematical Model for 32GB RAM Environment

```
RAM Budget Allocation (32GB):
├── OS + Gateway Services:     ~4GB  (12.5%)
├── Model Inference Cache:     ~8GB  (25%)   - For local embedding models
├── Vector Index (HNSW):       ~6GB  (18.75%) - In-memory similarity search
├── Hot Tier Context:          ~4GB  (12.5%)  - Active conversation buffer
├── Warm Tier Cache:           ~8GB  (25%)    - Frequently accessed chunks
└── Overhead/Buffer:           ~2GB  (6.25%)
```

#### Context Window vs Chunk Size Mapping

| Model Context | Hot Tier Chunk | Warm Tier Chunk | Cold Tier Chunk | Rationale |
|--------------|----------------|-----------------|-----------------|-----------|
| 8K tokens    | 256 tokens     | 512 tokens      | 1024 tokens     | Conservative for small contexts |
| 32K tokens   | 512 tokens     | 1024 tokens     | 2048 tokens     | Balanced (RECOMMENDED) |
| 128K tokens  | 1024 tokens    | 2048 tokens     | 4096 tokens     | Aggressive for large contexts |
| 200K+ tokens | 2048 tokens    | 4096 tokens     | 8192 tokens     | Maximum retention mode |

**RECOMMENDED Configuration for 32GB + Standard Context (32K):**

```json
{
  "chunking": {
    "hot": {
      "size": 512,
      "overlap": 64,
      "max_context_tokens": 8192,
      "strategy": "recursive"
    },
    "warm": {
      "size": 1024,
      "similarity_threshold": 0.75,
      "max_context_tokens": 32768,
      "strategy": "semantic",
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "cold": {
      "size": 2048,
      "similarity_threshold": 0.65,
      "compression": "gzip",
      "strategy": "semantic"
    }
  }
}
```

#### Embedding Model Selection

| Model | Dimensions | Size | Speed | Quality | Use Case |
|-------|------------|------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | 80MB | Very Fast | Good | **Default - balanced** |
| all-mpnet-base-v2 | 768 | 420MB | Fast | Better | Higher quality retrieval |
| BGE-small-en-v1.5 | 384 | 130MB | Very Fast | Excellent | Multi-lingual support |
| E5-base-v2 | 768 | 440MB | Medium | Best | Maximum accuracy |

**Recommendation:** `all-MiniLM-L6-v2` for 32GB environments - provides optimal speed/quality tradeoff with minimal RAM footprint.

---

## TIER 2 → TIER 3 HANDOFF

### What Tier 3 (GPT 5.3 Codex) Must Finalize:

1. **Precise openclaw.json Configuration Snippets**
   - Complete agents.defaults.compaction overrides
   - Memory search provider configuration
   - Custom model routing for compaction summaries

2. **Implementation Code**
   - Complete Python service implementation
   - OpenClaw plugin/hook integration points
   - Vector DB schema and indexing strategy

3. **High Performance / Zero Waste Strategy**
   - Token budget calculations
   - Cost-per-request optimizations
   - Performance benchmarks and monitoring

### Key Decisions Requiring Tier 3 Finalization:

| Decision Point | Tier 2 Recommendation | Tier 3 Authority |
|----------------|----------------------|------------------|
| Compaction model override | `openrouter/anthropic/claude-sonnet-4-5` | Final confirmation |
| Memory embedding provider | `local` (node-llama-cpp) vs `ollama` | Implementation detail |
| Vector DB backend | `sqlite-vec` vs `qdrant` (local) | Performance testing |
| Session pruning threshold | 40% of context window | Fine-tuning |