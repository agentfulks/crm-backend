# OpenClaw Multi-Model Routing: Flash Triage + Advanced Execution Strategy

## Executive Summary

This research covers cutting-edge strategies for cost optimization in OpenClaw through intelligent model routing. The core principle: **Use fast, cheap "flash" models for triage and simple tasks, while reserving powerful models (like kimi k2.5) for complex work that actually requires advanced reasoning.**

**Expected Cost Reduction: 50-80%**

---

## 1. THE PROBLEM: DEFAULT SINGLE-MODEL ARCHITECTURE

### Current Default Behavior
By default, OpenClaw sends **everything** to your primary model:
- Heartbeat checks every 30 minutes → Primary model
- Quick file lookups → Primary model
- Sub-agents doing parallel work → Primary model
- Complex reasoning tasks → Primary model

**The Cost Problem:**
Using Opus/kimi k2.5 for a heartbeat check is like "hiring a lawyer to check your mailbox." It works, but makes no financial sense.

### Cost Comparison (per 1M tokens)
| Model Tier | Example | Input Cost | Output Cost | Use Case |
|------------|---------|------------|-------------|----------|
| **Flash** | gpt-4o-mini, moonshot/kimi-lite | $0.15 | $0.60 | Triage, simple queries |
| **Standard** | gpt-4o, claude-sonnet-4 | $2.50 | $10.00 | General tasks |
| **Advanced** | kimi k2.5, claude-opus-4 | $3.00-$15.00 | $15.00-$75.00 | Complex reasoning |

**Potential Savings:** 78% cost reduction using flash models for 80% of tasks.

---

## 2. CONFIGURATION STRATEGIES

### 2.1 Basic Multi-Model Configuration

**File:** `~/.openclaw/openclaw.json`

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5",
        "fallbacks": ["moonshot/kimi-lite", "openai/gpt-4o-mini"]
      },
      "models": {
        "moonshot/kimi-k2.5": {
          "alias": "kimi",
          "temperature": 0.7,
          "maxTokens": 8192
        },
        "moonshot/kimi-lite": {
          "alias": "flash",
          "temperature": 0.3,
          "maxTokens": 4096
        },
        "openai/gpt-4o-mini": {
          "alias": "mini",
          "temperature": 0.3,
          "maxTokens": 4096
        }
      },
      "subagents": {
        "maxConcurrent": 8,
        "model": {
          "primary": "moonshot/kimi-lite"
        }
      }
    }
  }
}
```

### 2.2 Per-Agent Model Overrides

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-lite"
      }
    },
    "list": [
      {
        "id": "main",
        "model": {
          "primary": "moonshot/kimi-k2.5"
        }
      },
      {
        "id": "code-architect",
        "model": {
          "primary": "moonshot/kimi-k2.5",
          "fallbacks": ["openai/gpt-5.1-codex"]
        }
      },
      {
        "id": "quick-research",
        "model": {
          "primary": "moonshot/kimi-lite"
        }
      }
    ]
  }
}
```

### 2.3 CLI Model Switching (Ad-hoc)

Switch models on the fly without editing config:

```bash
# Quick question - use flash model
/model flash
"What's the weather today?"

# Complex task - switch to advanced
/model kimi
"Design a distributed system architecture for a trading platform"

# Check current model
/model
```

---

## 3. INTELLIGENT ROUTING ARCHITECTURES

### 3.1 Strategy 1: Sub-Agent Tiering (Recommended)

**Concept:** Spawn different sub-agents with different models based on task complexity.

```javascript
// Main agent (kimi k2.5) decides complexity
const task = "Analyze this codebase for security vulnerabilities";

// For simple analysis → Flash model sub-agent
sessions_spawn({
  task: "Scan for common vulnerabilities (OWASP top 10)",
  agentId: "security-scanner",
  model: "moonshot/kimi-lite"  // Flash model
});

// For complex architecture review → Advanced model sub-agent
sessions_spawn({
  task: "Deep analysis of authentication flow and crypto implementations",
  agentId: "security-architect",
  model: "moonshot/kimi-k2.5"  // Advanced model
});
```

**Configuration:**
```json
{
  "agents": {
    "list": [
      {
        "id": "security-scanner",
        "model": { "primary": "moonshot/kimi-lite" }
      },
      {
        "id": "security-architect",
        "model": { "primary": "moonshot/kimi-k2.5" }
      }
    ]
  }
}
```

### 3.2 Strategy 2: Task-Based Routing in SOUL.md

**Concept:** Define routing logic in your agent's SOUL.md

```markdown
# SOUL

## Model Routing Rules

### Automatic Model Selection
For each incoming request, classify complexity:

**Use FLASH model (moonshot/kimi-lite) for:**
- Heartbeat checks
- File listings and directory navigation
- Simple text searches
- Status queries ("what's the git status?")
- Quick lookups ("find my TODO list")

**Use STANDARD model (moonshot/kimi-k2.5-standard) for:**
- Code reviews
- Documentation writing
- Research queries
- Data analysis

**Use ADVANCED model (moonshot/kimi-k2.5) for:**
- System architecture design
- Complex debugging
- Security audits
- Algorithm optimization
- Multi-step reasoning tasks

### Routing Logic
Before processing any request:
1. Classify the task complexity
2. If flash-suitable → Switch to /model flash
3. If standard-suitable → Use current model
4. If advanced-required → Switch to /model kimi
5. Process the request
6. Return to default model if changed
```

### 3.3 Strategy 3: Pre-Processing Router Agent

**Concept:** Create a dedicated "router" sub-agent that classifies tasks.

```json
{
  "agents": {
    "list": [
      {
        "id": "router",
        "model": { "primary": "openai/gpt-4o-mini" },
        "description": "Classifies task complexity and routes to appropriate agent"
      },
      {
        "id": "executor-flash",
        "model": { "primary": "moonshot/kimi-lite" }
      },
      {
        "id": "executor-standard",
        "model": { "primary": "moonshot/kimi-k2.5" }
      }
    ]
  }
}
```

**Workflow:**
```
User Request → Router Agent (flash) → Classification → 
  ├─ Simple → Executor-Flash
  ├─ Medium → Executor-Standard
  └─ Complex → Executor-Advanced
```

---

## 4. SPECIFIC IMPLEMENTATION PATTERNS

### 4.1 Pattern: Heartbeat Optimization

**Current:** Heartbeat uses primary model every 30 minutes
**Optimized:** Heartbeat uses flash model

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "enabled": true,
        "model": "moonshot/kimi-lite",
        "prompt": "Read HEARTBEAT.md and check for scheduled tasks only."
      }
    }
  }
}
```

### 4.2 Pattern: Skill-Based Model Assignment

**Assign cheap models to specific skills:**

```json
{
  "skills": {
    "entries": {
      "file_search": {
        "enabled": true,
        "model": "moonshot/kimi-lite"
      },
      "web_search": {
        "enabled": true,
        "model": "moonshot/kimi-lite"
      },
      "code_review": {
        "enabled": true,
        "model": "moonshot/kimi-k2.5"
      }
    }
  }
}
```

### 4.3 Pattern: Context-Aware Switching

**In your AGENTS.md:**

```markdown
## Cost-Optimized Execution Protocol

### Step 1: Task Classification
Before any execution, classify the task:

```
COMPLEXITY_INDICATORS = {
  "flash": [
    "list", "show", "find", "search", "status",
    "heartbeat", "check", "simple", "quick"
  ],
  "advanced": [
    "design", "architect", "debug", "optimize",
    "security", "refactor", "complex", "analyze deep"
  ]
}
```

### Step 2: Model Selection
```python
if any(keyword in request for keyword in COMPLEXITY_INDICATORS["flash"]):
    use_model("flash")
elif any(keyword in request for keyword in COMPLEXITY_INDICATORS["advanced"]):
    use_model("advanced")
else:
    use_model("standard")
```

### Step 3: Execution
Process the request with selected model.

### Step 4: Verification
If flash model result seems incomplete, escalate to standard model.
```

---

## 5. KNOWN LIMITATIONS & WORKAROUNDS

### 5.1 Issue: Sub-Agent Model Override Not Working

**Problem:** `sessions_spawn` model parameter may be ignored (GitHub Issue #7330, #13159)

**Workaround 1: Per-Agent Configuration**
Instead of passing model in spawn, create dedicated agents:
```json
{
  "agents": {
    "list": [
      { "id": "flash-worker", "model": { "primary": "moonshot/kimi-lite" } },
      { "id": "advanced-worker", "model": { "primary": "moonshot/kimi-k2.5" } }
    ]
  }
}
```

Then spawn by agent ID:
```javascript
sessions_spawn({
  agentId: "flash-worker",  // Pre-configured with flash model
  task: "Simple research task"
});
```

**Workaround 2: CLI Subagent Command**
Use CLI with model flag:
```bash
/subagents spawn main "Task description" --model moonshot/kimi-lite
```

**Workaround 3: Direct API Calls**
For isolated tasks, bypass OpenClaw's agent loop:
```javascript
// Call model API directly for simple classification
const response = await fetch('https://api.moonshot.cn/v1/chat/completions', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${process.env.MOONSHOT_API_KEY}` },
  body: JSON.stringify({
    model: 'kimi-lite',
    messages: [{ role: 'user', content: 'Classify this task: ' + task }]
  })
});
```

### 5.2 Issue: Model Override in Isolated Sessions

**Problem:** Isolated sessions may ignore model parameter (Issue #13159)

**Workaround:** Use `session_status` to verify and patch:
```javascript
const session = await sessions_spawn({
  task: "Complex task",
  model: "moonshot/kimi-k2.5",
  mode: "session"
});

// Verify model
const status = await session_status({ sessionKey: session.key });
if (status.model !== "moonshot/kimi-k2.5") {
  // Patch the session
  await sessions_send({
    sessionKey: session.key,
    message: "/model kimi"
  });
}
```

### 5.3 Issue: Defaults Override Per-Agent Config

**Problem:** `agents.defaults.model.primary` overrides per-agent config (Issue #29571)

**Workaround:** Remove defaults, use explicit per-agent configs only:
```json
{
  "agents": {
    "defaults": {
      "model": {}  // Empty - no default
    },
    "list": [
      { "id": "main", "model": { "primary": "moonshot/kimi-k2.5" } },
      { "id": "worker", "model": { "primary": "moonshot/kimi-lite" } }
    ]
  }
}
```

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1: Immediate Setup (Day 1)

1. **Configure Model Aliases**
```json
{
  "agents": {
    "defaults": {
      "models": {
        "moonshot/kimi-k2.5": { "alias": "kimi" },
        "moonshot/kimi-lite": { "alias": "flash" },
        "openai/gpt-4o-mini": { "alias": "mini" }
      }
    }
  }
}
```

2. **Create Specialized Agents**
```json
{
  "agents": {
    "list": [
      {
        "id": "TRIAGE",
        "model": { "primary": "moonshot/kimi-lite" },
        "description": "Fast task classifier and router"
      },
      {
        "id": "DEEP_WORK",
        "model": { "primary": "moonshot/kimi-k2.5" },
        "description": "Complex reasoning and architecture tasks"
      }
    ]
  }
}
```

3. **Update SOUL.md with Routing Logic**
Add the model selection rules to your agent's personality.

### Phase 2: Automation (Week 1)

1. **Heartbeat Optimization**
Configure heartbeat to use flash model.

2. **Sub-Agent Tiering**
Spawn different agents for different complexity levels.

3. **Monitoring**
Use ClawMetry to track cost per model.

### Phase 3: Advanced Routing (Week 2)

1. **Implement Router Pattern**
Create a dedicated router agent for automatic classification.

2. **Feedback Loop**
Track which tasks required escalation from flash to advanced models.

3. **Optimize Thresholds**
Adjust complexity indicators based on actual usage.

---

## 7. COST TRACKING & OPTIMIZATION

### 7.1 Monitor Per-Model Usage

**In ClawMetry:**
- View cost breakdown by model
- Track token usage per tier
- Identify optimization opportunities

**Manual Tracking:**
```bash
# Daily cost by model
openclaw usage --date $(date +%Y-%m-%d) --json | jq '.by_model'
```

### 7.2 Optimization Metrics

| Metric | Target | Action if Exceeding |
|--------|--------|---------------------|
| Flash model % | >70% | Good - most tasks are simple |
| Advanced model % | <20% | Review - too many complex tasks? |
| Cost per session | <$5 | Adjust routing thresholds |
| Escalation rate | <10% | Flash model missing complex tasks |

### 7.3 Cost Alerts

Set up alerts in HEARTBEAT.md:
```markdown
## Daily Cost Check
- [ ] Check ClawMetry dashboard
- [ ] If daily cost > $20, review model usage
- [ ] Identify tasks that could use cheaper models
```

---

## 8. REAL-WORLD EXAMPLES

### Example 1: VC Outreach Workflow

**Task:** Research 10 VC firms and generate outreach messages

**Without Routing:**
- All 10 research tasks → kimi k2.5
- Cost: ~$15-20

**With Routing:**
- Task classification → kimi-lite (flash) [$0.10]
- Firm research (8 simple) → kimi-lite [$2.00]
- Complex thesis analysis (2 firms) → kimi k2.5 [$5.00]
- Message generation → kimi-lite [$1.00]
- **Total Cost: ~$8.10 (60% savings)**

### Example 2: Code Review Workflow

**Task:** Review PR for security issues

**Without Routing:**
- Entire PR → kimi k2.5
- Cost: ~$5-8

**With Routing:**
- File listing and basic scan → kimi-lite [$0.50]
- Pattern matching for common issues → kimi-lite [$1.00]
- Complex auth flow analysis → kimi k2.5 [$3.00]
- **Total Cost: ~$4.50 (40% savings)**

---

## 9. ANTI-PATTERNS TO AVOID

1. **Over-optimization:** Don't route critical security/medical tasks to flash models
2. **Excessive Switching:** Model changes add latency; batch similar tasks
3. **Ignoring Escalations:** If flash model fails often, your thresholds are wrong
4. **No Monitoring:** Track costs to verify savings
5. **Complex Router:** Keep routing logic simple and fast

---

## 10. CONFIGURATION TEMPLATES

### Template A: Conservative (20% savings)
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "moonshot/kimi-k2.5" },
      "subagents": { "model": { "primary": "moonshot/kimi-lite" } }
    }
  }
}
```

### Template B: Balanced (50% savings)
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "moonshot/kimi-lite" },
      "models": {
        "moonshot/kimi-k2.5": { "alias": "kimi" },
        "moonshot/kimi-lite": { "alias": "flash" }
      }
    },
    "list": [
      { "id": "main", "model": { "primary": "moonshot/kimi-k2.5" } },
      { "id": "architect", "model": { "primary": "moonshot/kimi-k2.5" } },
      { "id": "researcher", "model": { "primary": "moonshot/kimi-lite" } }
    ]
  }
}
```

### Template C: Aggressive (80% savings)
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "openai/gpt-4o-mini" },
      "subagents": { "model": { "primary": "openai/gpt-4o-mini" } },
      "heartbeat": { "model": "openai/gpt-4o-mini" }
    },
    "list": [
      { 
        "id": "main",
        "model": { 
          "primary": "moonshot/kimi-k2.5",
          "fallbacks": ["moonshot/kimi-lite"]
        }
      }
    ]
  }
}
```

---

## Resources

- **OpenClaw Sub-Agents:** https://docs.openclaw.ai/tools/subagents
- **Multi-Model Routing Guide:** https://velvetshark.com/openclaw-multi-model-routing
- **GitHub Issue #7330:** Model override discussion
- **GitHub Issue #13159:** Isolated session model issues
- **ClawMetry:** Monitor per-model costs

---

*Strategy based on OpenClaw documentation, community best practices, and real-world cost optimization case studies. Adjust thresholds based on your specific use case and quality requirements.*
