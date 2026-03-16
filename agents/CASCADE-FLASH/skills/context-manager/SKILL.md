# Context Manager Skill

Tier-aware semantic chunking for OpenClaw using chonkie.

## Purpose

This skill provides intelligent context management and token optimization through:
- Three-tier storage architecture (hot/warm/cold)
- Semantic chunking using chonkie
- Vector-based memory indexing
- Automated compaction workflows

## Installation

```bash
pip install "chonkie[semantic,code,catsu]"
```

## Usage

```python
from skills.context_manager.chunking_service import get_chunker, ContextMetadata, PriorityLevel

# Initialize chunker
chunker = get_chunker(workspace_path="~/.openclaw/workspace", ram_gb=32)

# Chunk text for warm tier
chunks = chunker.chunk_text(
    text="Your long text here...",
    tier="warm",
    metadata=ContextMetadata(
        session_id="session-123",
        priority=PriorityLevel.HIGH,
        current_tier="warm"
    )
)

# Store chunks
chunker.store_chunks(chunks)

# Retrieve from storage
results = chunker.retrieve_chunks(
    session_id="session-123",
    tier="warm",
    limit=50
)
```

## Architecture

### Three-Tier System

| Tier | Storage | Chunk Size | Strategy | Use Case |
|------|---------|------------|----------|----------|
| Hot | RAM | 512 tokens | Recursive | Active conversation |
| Warm | Vector DB | 1024 tokens | Semantic | Recent history |
| Cold | Disk (compressed) | 2048 tokens | Semantic | Archive |

### Configuration

See `context_config.json` for tier profiles optimized for 32GB RAM.

## Integration with OpenClaw

Add to your `openclaw.json`:

```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000
        }
      },
      memorySearch: {
        provider: "local",
        local: {
          modelPath: "~/.openclaw/models/all-MiniLM-L6-v2.gguf"
        }
      }
    }
  }
}
```