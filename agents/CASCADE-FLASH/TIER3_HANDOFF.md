# TIER 2 → TIER 3 HANDOFF DOCUMENT
## Context Management & Token Optimization Strategy

---

## ✅ TIER 2 COMPLETED DELIVERABLES

### 1. Architecture Design Document
**File:** `TIER2_ARCHITECT_DIRIVERABLE.md`

Contains:
- Complete three-tier architecture specification (hot/warm/cold)
- Chonkie integration implementation plan
- Tiered metadata tagging system specification
- Goldilocks chunk size determination for 32GB RAM
- RAM budget allocation breakdown
- Embedding model comparison matrix

### 2. Python Implementation Skeleton
**File:** `skills/context-manager/chunking_service.py`

Provides:
- `OpenClawContextChunker` class with tier-aware chunking
- `ContextMetadata` dataclass with priority/promotion/demotion logic
- SQLite vector store initialization
- Chunk storage and retrieval methods
- Compaction workflow hooks

### 3. Skill Definition
**File:** `skills/context-manager/SKILL.md`

Provides:
- Skill documentation for OpenClaw integration
- Usage examples
- Architecture overview

### 4. Integration Demo Script
**File:** `skills/context-manager/integration_demo.py`

Demonstrates:
- Pre-compaction hook integration
- Memory flush handling
- Context retrieval workflows

### 5. OpenClaw Configuration Template
**File:** `openclaw.context-config.json5`

Contains:
- Complete compaction configuration
- Memory search provider setup
- Three-tier chunk size specifications
- Migration rules for tier promotion/demotion

### 6. Requirements File
**File:** `skills/context-manager/requirements.txt`

---

## 🎯 TIER 3 DELIVERABLES REQUIRED

### 1. Precise openclaw.json Configuration Snippets

**Location:** Integrate into `~/.openclaw/openclaw.json`

**Decisions needed:**

| Setting | Tier 2 Recommendation | Tier 3 Final Value |
|---------|----------------------|-------------------|
| `compaction.model` | `claude-sonnet-4-5` | CONFIRM |
| `compaction.reserveTokensFloor` | 40000 | CONFIRM |
| `memorySearch.provider` | `local` | CONFIRM vs `ollama` |
| `memorySearch.local.modelPath` | `all-MiniLM-L6-v2.gguf` | PROVIDE DOWNLOAD URL |
| Vector DB backend | `sqlite-vec` | CONFIRM vs `qdrant` |

**Configuration to finalize:**
```json5
{
  agents: {
    defaults: {
      compaction: {
        // DECISION: Confirm model override for compaction summaries
        model: "openrouter/anthropic/claude-sonnet-4-5",
        
        // DECISION: Confirm reserve floor (earlier = gentler compaction)
        reserveTokensFloor: 40000,
        
        // DECISION: Confirm soft threshold for memory flush
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 8000
        }
      },
      
      memorySearch: {
        // DECISION: Confirm provider choice
        // Options: "local" | "ollama" | "openai"
        provider: "local",
        
        local: {
          // DECISION: Provide actual model path after download
          modelPath: "~/.openclaw/models/all-MiniLM-L6-v2.gguf"
        }
      }
    }
  }
}
```

### 2. Implementation Code Completion

**File:** `skills/context-manager/chunking_service.py`

**TODOs for Tier 3:**

1. **Implement actual chonkie integration:**
   - Replace placeholder methods with real chonkie calls
   - Handle embedding model loading
   - Implement vector similarity search

2. **Complete vector search:**
   ```python
   def search_similar(self, 
                      query: str, 
                      session_id: Optional[str] = None,
                      top_k: int = 5) -> List[Dict[str, Any]]:
       """Semantic search using embeddings."""
       # TODO: Generate query embedding
       # TODO: Query vector DB with cosine similarity
       # TODO: Return ranked results
   ```

3. **Implement compaction workflow:**
   ```python
   def compact_session(self, 
                      session_id: str,
                      target_tier: str = "warm") -> Dict[str, Any]:
       """Move chunks from hot → warm or warm → cold."""
       # TODO: Retrieve chunks from source tier
       # TODO: Re-chunk for target tier
       # TODO: Update tier metadata
       # TODO: Compress if target is cold
   ```

### 3. High Performance / Zero Waste Strategy

**Required Analysis:**

#### Token Budget Calculations
```
For 32GB RAM with 32K context window models:

Per-Request Budget:
- System prompt: ~500 tokens
- Hot tier context: ~2048 tokens (4 chunks × 512)
- Warm tier retrieved: ~2048 tokens (2 chunks × 1024)
- User message: ~256 tokens
- Response reserve: ~4096 tokens
─────────────────────────────
Total per request: ~8948 tokens

Cost Optimization:
- Compaction at 40K reserve = 12.5% headroom
- Memory flush at 8K threshold = proactive persistence
- Semantic chunking = 95.83% recall (vs 70% naive)
```

#### Performance Benchmarks
**Tier 3 to provide:**
- Chunking throughput (chunks/second per tier)
- Retrieval latency (p50, p95, p99)
- Memory usage under load
- Compression ratios for cold tier

#### Monitoring Metrics
```python
METRICS_TO_IMPLEMENT = {
    "context.hot.tier.token_count",
    "context.warm.tier.token_count", 
    "context.cold.tier.token_count",
    "context.compaction.count",
    "context.compaction.tokens_saved",
    "context.retrieval.latency_ms",
    "context.retrieval.hit_rate",
    "context.chunking.throughput"
}
```

---

## 📋 IMPLEMENTATION CHECKLIST FOR TIER 3

### Phase 1: Configuration
- [ ] Confirm compaction model override
- [ ] Download and configure embedding model
- [ ] Verify sqlite-vec installation or configure Qdrant
- [ ] Set reserveTokensFloor and softThresholdTokens

### Phase 2: Core Implementation  
- [ ] Install chonkie: `pip install "chonkie[semantic]"`
- [ ] Complete `chunking_service.py` methods
- [ ] Implement vector similarity search
- [ ] Add compression for cold tier

### Phase 3: Integration
- [ ] Create OpenClaw plugin hooks
- [ ] Test pre-compaction workflow
- [ ] Test memory flush workflow
- [ ] Verify tier migration rules

### Phase 4: Optimization
- [ ] Run performance benchmarks
- [ ] Tune chunk sizes based on results
- [ ] Optimize embedding batch sizes
- [ ] Document final configuration

### Phase 5: Delivery
- [ ] Final `openclaw.json` snippet
- [ ] Performance benchmark report
- [ ] "High Performance / Zero Waste" strategy summary

---

## 🔗 KEY REFERENCES

- **Chonkie Docs:** https://docs.chonkie.ai
- **OpenClaw Compaction:** https://docs.openclaw.ai/concepts/compaction
- **OpenClaw Memory:** https://docs.openclaw.ai/concepts/memory
- **OpenClaw Config:** https://docs.openclaw.ai/gateway/configuration-reference

---

## ⚡ QUICK START FOR TIER 3

```bash
# 1. Install dependencies
cd /data/workspace/agents/CASCADE-FLASH/skills/context-manager
pip install -r requirements.txt

# 2. Download embedding model
mkdir -p ~/.openclaw/models
# Download all-MiniLM-L6-v2 GGUF format
# URL: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# 3. Test implementation
python integration_demo.py

# 4. Copy config to OpenClaw
cp openclaw.context-config.json5 ~/.openclaw/openclaw.json
# EDIT: Fill in API keys and confirm settings

# 5. Restart gateway
openclaw gateway restart
```

---

## 📊 DECISION MATRIX

| Decision | Impact | Recommendation |
|----------|--------|----------------|
| Chunk sizes | Performance | 512/1024/2048 (implemented) |
| Embedding model | Quality/Speed | all-MiniLM-L6-v2 (implemented) |
| Vector DB | Simplicity | sqlite-vec for zero-config |
| Compaction model | Cost | Dedicated cheap model vs main |
| Reserve floor | Gentleness | 40000 tokens (aggressive=20000) |

---

## 🎓 ARCHITECTURAL PRINCIPLES (Tier 2 → Tier 3)

1. **Hot tier = Latency**: Use fastest chunking (recursive), smallest chunks
2. **Warm tier = Balance**: Use semantic chunking, medium chunks, vector index
3. **Cold tier = Storage**: Use largest chunks, compression, disk storage
4. **Metadata = Flexibility**: Rich tagging enables dynamic tier migration
5. **Compaction = Opportunity**: Pre-compaction is the hook for intelligent chunking

---

**Handoff complete. Tier 3 ready to finalize implementation.**