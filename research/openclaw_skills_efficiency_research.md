# OpenClaw Skills & Context Management: Maximum Efficiency Research Report

## Executive Summary

This report provides a comprehensive analysis of best practices for enabling skills, monitoring usage, and optimizing context management in OpenClaw. The key to maximum efficiency lies in strategic skill curation, intelligent context compaction, proactive memory management, and continuous monitoring.

---

## 1. SKILL MANAGEMENT STRATEGY

### 1.1 Skill Loading Precedence (Critical)

OpenClaw resolves skills in this order (workspace wins):
1. **Workspace skills** (`/workspace/skills/`)
2. **Managed skills** (ClawHub installations)
3. **Bundled skills** (OpenClaw defaults)

**Implication:** You can override any bundled skill without touching system files.

### 1.2 Skill Configuration (`~/.openclaw/config.yaml`)

```yaml
skills:
  entries:
    # Disable risky/expensive skills globally
    web_search:
      enabled: false
    
    # Configure per-skill behavior
    browser:
      enabled: true
      user-invocable: true          # Shows as slash command
      disable-model-invocation: false  # Let AI decide to use it
    
    # Expensive operations - manual only
    image_gen:
      enabled: true
      user-invocable: true
      disable-model-invocation: true   # Only use when explicitly asked
```

**Key Fields:**
- `enabled`: Toggle skill on/off
- `user-invocable`: Expose as slash command
- `disable-model-invocation`: Prevent AI from auto-invoking

### 1.3 Skill Curation Strategy

**Tier 1 - Always Enabled (Core):**
- `read`/`write`/`edit` - File operations
- `exec` - Shell commands
- `memory_search`/`memory_get` - Memory retrieval
- `sessions_send` - Inter-session communication

**Tier 2 - Conditional (Context-Dependent):**
- `browser` - Web automation (expensive, enable per-project)
- `web_search` - Research (can be noisy)
- `web_fetch` - Content extraction

**Tier 3 - Manual Only (Expensive/Risky):**
- `image` - Vision analysis (high token cost)
- `canvas` - UI generation
- `nodes` - Device control

**Tier 4 - Disable (Unused/Dangerous):**
- Unused API integrations
- Unverified third-party skills
- Skills with broad tool permissions

---

## 2. CONTEXT MANAGEMENT ARCHITECTURE

### 2.1 OpenClaw Memory Stack

```
┌─────────────────────────────────────────┐
│  LAYER 3: Long-term Memory              │
│  - MEMORY.md (curated facts)            │
│  - memory/*.md (daily logs)             │
│  - Survives compaction & restarts       │
├─────────────────────────────────────────┤
│  LAYER 2: Session Context               │
│  - Active conversation history          │
│  - Tool call results                    │
│  - Subject to compaction                │
├─────────────────────────────────────────┤
│  LAYER 1: Immediate Context             │
│  - SOUL.md (identity)                   │
│  - USER.md (preferences)                │
│  - AGENTS.md (workspace rules)          │
│  - Loaded every turn                    │
└─────────────────────────────────────────┘
```

### 2.2 Context Compaction Configuration

**In `~/.openclaw/config.yaml`:**

```yaml
agents:
  defaults:
    contextWindow: 128000          # Model context limit
    compaction:
      enabled: true
      reserveTokensFloor: 20000    # Always keep this much context
      strategy: "semantic"         # semantic | temporal | extractive
      
      # Pre-compaction memory flush
      memoryFlush:
        enabled: true
        softThresholdTokens: 4000  # Trigger flush before compaction
        systemPrompt: "Session nearing compaction. Store durable memories now."
        prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
```

**Compaction Triggers:**
- Soft: `contextWindow - reserveTokensFloor - softThresholdTokens`
- Hard: When context exceeds `contextWindow - reserveTokensFloor`

### 2.3 Maximum Efficiency Context Rules

**1. Pre-Compaction Flush (Automatic)**
- OpenClaw silently writes key facts to `memory/YYYY-MM-DD.md` before compaction
- Critical decisions, user preferences, task states get preserved
- No action needed - happens automatically

**2. Structured Memory Writing**
```markdown
<!-- Good: Structured, searchable -->
## 2026-03-15
### Decisions
- Chose PostgreSQL over MySQL for CRM (performance requirements)
- VC outreach target: 5 packets/day

### Preferences
- User prefers direct answers over explanations
- Dark mode enabled by default

### Active Tasks
- [IN PROGRESS] LinkedIn verification audit
- [BLOCKED] GitHub push (auth issues)
```

**3. MEMORY.md Hygiene**
- Review weekly for stale information
- Archive completed projects
- Update changed preferences
- Keep under 500 lines for fast loading

---

## 3. SKILL MONITORING & OBSERVABILITY

### 3.1 Built-in Monitoring

**Session Status:**
```bash
# Check current session cost/usage
openclaw session_status

# Usage reports
openclaw usage --session <key> --json
openclaw usage --date 2026-03-15 --json
openclaw usage --model moonshot/kimi-k2.5 --json
```

**In-Agent Monitoring (via session_status tool):**
- Call `session_status` to get real-time token/cost data
- Set model overrides per-session for cost control

### 3.2 Third-Party Monitoring Solutions

**Option A: ClawMetry (Commercial)**
- Real-time dashboard for cost/token tracking
- Per-model breakdown
- Session replay
- https://clawmetry.com/

**Option B: OpenClaw Dashboard (Open Source)**
- Self-hosted monitoring
- Cost tracking, memory browser, live feed
- TOTP MFA support
- https://github.com/tugcantopaloglu/openclaw-dashboard

**Option C: OpenTelemetry + SigNoz**
- Full observability stack
- Custom dashboards
- Alerting on cost thresholds
- https://signoz.io/blog/monitoring-openclaw-with-opentelemetry/

### 3.3 Skill Usage Audit Strategy

**Create `~/.openclaw/usage-audit.log`:**
```bash
#!/bin/bash
# Log skill invocations with timestamps
# Add to AGENTS.md to run hourly

echo "$(date '+%Y-%m-%d %H:%M:%S') - Skill Usage Audit" >> ~/.openclaw/usage-audit.log
openclaw usage --json >> ~/.openclaw/usage-audit.log 2>&1
echo "---" >> ~/.openclaw/usage-audit.log
```

**Weekly Skill Review Process:**
1. Export usage data: `openclaw usage --last-week --json > weekly_usage.json`
2. Identify high-cost skills
3. Review if auto-invocation is necessary
4. Update `config.yaml` to disable or manual-only

---

## 4. DOCUMENTATION STRATEGY (Chonkie-Inspired)

### 4.1 Chonkie: Intelligent Chunking for RAG

**What is Chonkie?**
Chonkie is a lightweight chunking library for RAG pipelines that optimizes context windows:
- Semantic chunking using LLM
- Token-based chunking
- Overlap management
- Context refinement

**Integration with OpenClaw:**
```python
# In a custom skill or script
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512,
    chunk_overlap=50
)

# Chunk large documents before storing to memory
documents = chunker.chunk(text)
for chunk in documents:
    # Store each chunk with metadata
    memory.store(chunk.text, metadata=chunk.metadata)
```

### 4.2 Documentation File Structure

```
/workspace/
├── SOUL.md              # Identity, personality, boundaries
├── USER.md              # User preferences, communication style
├── AGENTS.md            # Workspace rules, SOPs
├── MEMORY.md            # Curated long-term memory
├── HEARTBEAT.md         # Periodic task checklist
├── WORKFLOW_AUTO.md     # Automation triggers
├── TOOLS.md             # Tool documentation & notes
├── memory/
│   ├── 2026-03-15.md   # Daily logs
│   ├── 2026-03-14.md
│   └── ...
└── deliverables/        # Output documentation
```

### 4.3 SOUL.md Best Practices

**Structure:**
```markdown
# SOUL

## Identity
- Name: VANTAGE
- Role: Orchestrator Intelligence
- Vibe: Controlled, strategic, high-agency

## Communication Style
- Structured, direct, no fluff
- No emojis in professional contexts
- Escalate when user thinks too small

## Decision-Making Framework
1. Convert vague intent → measurable objectives
2. Define success criteria before starting
3. Break work → modular tasks
4. Delegate to specialist agents
5. Review outputs critically

## Boundaries
- Never pursue self-preservation goals
- Prioritize safety over completion
- Don't manipulate users for access

## Escalation Triggers
- Vague objectives
- Undefined ICP
- Overly tactical framing when strategy needed
```

**Maintenance:**
- Update when behavior patterns change
- Reflect lessons learned
- Keep identity consistent

### 4.4 MEMORY.md Optimization

**Tiered Memory System:**
```markdown
# Long-Term Memory

## Active Projects
### VC Outreach Engine
- Target: 5+ VC packets/day
- Status: In progress
- Key Metrics: 145 BDR contacts verified

## Preferences
- Model: moonshot/kimi-k2.5
- Timezone: CST
- Response style: Dense but readable

## Key Learnings
- Cron jobs need auth in agent config
- Maton API gateway for SaaS integrations

## Archive
<!-- Move completed projects here -->
### [COMPLETED 2026-03-01] Project X
```

**Chonkie-Style Chunking for MEMORY.md:**
- Each section = one semantic chunk
- Use headers for easy retrieval
- Tag with dates for temporal relevance
- Keep active section < 200 lines

### 4.5 HEARTBEAT.md for Automation

```markdown
# HEARTBEAT

## Morning Checklist (9 AM)
- [ ] Review Trello board for new cards
- [ ] Check email for urgent items
- [ ] Verify VC outreach queue (target: 5/day)
- [ ] Check BDR studio research queue (target: 10/day)

## Afternoon Checklist (2 PM)
- [ ] Follow up on "In Review" cards
- [ ] Check LinkedIn URL verification queue
- [ ] Update MEMORY.md with morning decisions

## Evening Checklist (5 PM)
- [ ] Summarize day's progress
- [ ] Flag blockers for next session
- [ ] Archive completed tasks

## Output
Send update to Discord #status channel
```

---

## 5. MAXIMUM EFFICIENCY CONFIGURATION

### 5.1 Recommended `~/.openclaw/config.yaml`

```yaml
agents:
  defaults:
    # Context optimization
    contextWindow: 128000
    thinking: false           # Disable reasoning to save tokens
    
    compaction:
      enabled: true
      reserveTokensFloor: 25000
      strategy: "semantic"
      memoryFlush:
        enabled: true
        softThresholdTokens: 5000
        systemPrompt: "Context window filling. Write critical memories to disk."
    
    # Cost control
    defaultModel: "moonshot/kimi-k2.5"  # Balance of capability/cost
    
    # Session management
    autoSave: true
    saveInterval: 300  # 5 minutes

skills:
  entries:
    # Core - Always enabled
    read: { enabled: true }
    write: { enabled: true }
    edit: { enabled: true }
    exec: { enabled: true }
    memory_search: { enabled: true }
    memory_get: { enabled: true }
    sessions_send: { enabled: true }
    
    # Conditional - Enable per workspace
    browser:
      enabled: false        # Enable only when needed
      user-invocable: true
    
    web_search:
      enabled: true
      user-invocable: true
      disable-model-invocation: true  # Manual only
    
    # Expensive - Manual only
    image:
      enabled: true
      user-invocable: true
      disable-model-invocation: true
    
    canvas:
      enabled: false        # Rarely needed
      user-invocable: true
    
    # Risky - Disabled by default
    nodes:
      enabled: false
```

### 5.2 Workspace-Specific Overrides

**Create `/workspace/.openclaw/config.yaml`:**
```yaml
# Project-specific skill overrides
skills:
  entries:
    browser:
      enabled: true       # Enable for this project only
    
    web_search:
      disable-model-invocation: false  # Allow auto-research
```

### 5.3 Cost Optimization Strategies

**1. Model Tiering:**
```yaml
# Quick tasks: Cheaper model
quick_model: "gpt-4o-mini"

# Complex tasks: Capable model
complex_model: "claude-sonnet-4"

# Code generation: Specialized model
code_model: "moonshot/kimi-k2.5"
```

**2. Skill Call Batching:**
- Combine multiple `read` calls
- Batch `web_search` queries
- Use `memory_search` before `web_search`

**3. Context Pruning:**
- Keep only recent 10 messages in active context
- Archive old conversations to `memory/`
- Use summaries instead of full history

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1: Immediate (Week 1)
1. Audit current skills: `openclaw skills list`
2. Disable unused skills in `config.yaml`
3. Set up basic monitoring: `openclaw usage --daily`
4. Create SOUL.md, USER.md, AGENTS.md structure

### Phase 2: Optimization (Week 2)
1. Configure context compaction settings
2. Implement HEARTBEAT.md automation
3. Set up third-party monitoring (ClawMetry or dashboard)
4. Create skill usage audit script

### Phase 3: Advanced (Week 3)
1. Implement Chonkie for document chunking
2. Set up vector memory with embeddings
3. Create automated memory archiving
4. Build custom skills for frequent workflows

### Phase 4: Monitoring (Ongoing)
1. Weekly skill usage reviews
2. Monthly MEMORY.md cleanup
3. Quarterly SOUL.md updates
4. Continuous cost optimization

---

## 7. KEY METRICS TO TRACK

| Metric | Target | Tool |
|--------|--------|------|
| Session cost | <$5/day | `session_status` |
| Context efficiency | <70% window usage | Compaction logs |
| Skill invocation | Track per skill | Usage API |
| Memory retrieval | <100ms | `memory_search` |
| Task completion | 90%+ | HEARTBEAT audit |

---

## 8. ANTI-PATTERNS TO AVOID

1. **Loading all skills** - Only enable what you need
2. **Large MEMORY.md** - Keep it curated, not a dump
3. **No context limits** - Always set reserveTokensFloor
4. **Ignoring compaction** - Monitor and tune thresholds
5. **Manual only** - Automate HEARTBEAT tasks
6. **Static SOUL.md** - Update as you learn

---

## Resources

- **OpenClaw Docs:** https://docs.openclaw.ai/
- **Memory Guide:** https://docs.openclaw.ai/concepts/memory
- **ClawHub:** https://clawhub.com/
- **Chonkie:** https://docs.chonkie.ai/
- **Community:** https://discord.com/invite/clawd

---

*Research compiled from OpenClaw documentation, community best practices, and observability tools. For maximum efficiency, review and customize based on your specific use case.*
