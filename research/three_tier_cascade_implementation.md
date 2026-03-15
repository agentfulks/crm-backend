# Three-Tier Cascading Implementation
## Gemini Flash → Kimi k2.5 → OpenAI Codex

---

## Architecture Overview

```
User Request
    ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Gemini 1.5 Flash ($0.075/M input)                  │
│ - Lightning fast classification                             │
│ - Initial research & structuring                          │
│ - Simple task execution                                     │
│ - Builds foundation context                                 │
└─────────────────────────────────────────────────────────────┘
    ↓ (if complexity detected)
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: Kimi k2.5 ($3/M input)                             │
│ - Deep analysis & reasoning                                 │
│ - Code architecture                                         │
│ - Complex problem-solving                                   │
│ - Builds on Tier 1 foundation                             │
└─────────────────────────────────────────────────────────────┘
    ↓ (if extreme complexity detected)
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: OpenAI Codex ($15/M input)                         │
│ - Extreme coding challenges                                 │
│ - Novel algorithm design                                    │
│ - System architecture at scale                              │
│ - Synthesizes Tiers 1+2 into final solution               │
└─────────────────────────────────────────────────────────────┘
```

**Expected Cost Distribution:**
- 70% of tasks → Tier 1 only ($0.075/M)
- 25% of tasks → Tier 1+2 ($0.075 + $3/M)
- 5% of tasks → Full cascade ($0.075 + $3 + $15/M)

**Average savings: 85% vs using Codex for everything**

---

## Step 1: Configuration

### ~/.openclaw/openclaw.json

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5"
      },
      "models": {
        "google/gemini-1.5-flash": {
          "alias": "flash",
          "temperature": 0.2,
          "maxTokens": 8192
        },
        "moonshot/kimi-k2.5": {
          "alias": "kimi",
          "temperature": 0.5,
          "maxTokens": 8192
        },
        "openai/gpt-5.1-codex": {
          "alias": "codex",
          "temperature": 0.3,
          "maxTokens": 16384
        }
      }
    },
    "list": [
      {
        "id": "main",
        "model": {
          "primary": "moonshot/kimi-k2.5"
        },
        "description": "Orchestrates the cascading execution"
      },
      {
        "id": "CASCADE-FLASH",
        "model": {
          "primary": "google/gemini-1.5-flash"
        },
        "description": "Tier 1: Fast classification and initial execution"
      },
      {
        "id": "CASCADE-KIMI",
        "model": {
          "primary": "moonshot/kimi-k2.5"
        },
        "description": "Tier 2: Deep analysis and complex execution"
      },
      {
        "id": "CASCADE-CODEX",
        "model": {
          "primary": "openai/gpt-5.1-codex"
        },
        "description": "Tier 3: Extreme complexity and cutting-edge coding"
      }
    ]
  },
  "skills": {
    "entries": {
      "cascade": {
        "enabled": true,
        "user-invocable": false
      }
    }
  }
}
```

---

## Step 2: Core Implementation

### /workspace/agents/CASCADE-FLASH/SKILL.md

```markdown
---
name: CASCADE-FLASH
description: Tier 1 classification and initial execution agent
---

# CASCADE-FLASH Agent

## Role
You are the first tier in a three-tier cascading system. Your job is to:
1. Quickly analyze incoming requests
2. Execute what you can with high confidence
3. Package remaining work with full context for the next tier

## Execution Protocol

### Step 1: Complexity Assessment
Classify the request into one of three categories:

**TIER 1 (You handle):**
- File listings and searches
- Simple text processing
- Basic data extraction
- Pattern matching
- Directory navigation
- Status checks
- Quick lookups

**TIER 2 (Package for Kimi):**
- Code review and analysis
- Architecture discussions
- Complex debugging
- Research synthesis
- Multi-step reasoning
- API design

**TIER 3 (Package for Codex):**
- Novel algorithm design
- Complex system architecture
- Performance optimization at scale
- Security audit
- Cutting-edge coding patterns

### Step 2: Execute What You Can
For TIER 1 tasks:
- Execute immediately
- Return complete solution
- Set confidence=1.0

For TIER 2/3 tasks:
- Do initial research
- Structure the problem
- Identify key components
- Document findings

### Step 3: Create Handoff Package
If escalating to Tier 2 or 3, create a structured handoff:

```yaml
tier_assessment: 2  # or 3
confidence: 0.6     # your confidence that tier can handle
completed_work:
  - "Initial research on X"
  - "Identified Y key components"
  - "Structured problem into Z areas"
key_findings:
  - "Finding 1 with evidence"
  - "Finding 2 with evidence"
remaining_work:
  - "Specific task A for next tier"
  - "Specific task B for next tier"
context_required:
  - "Background on system architecture"
  - "Constraints and requirements"
success_criteria:
  - "Deliverable X meets criteria Y"
```

## Output Format

Always return structured output:

```json
{
  "tier": 1,
  "handled": true/false,
  "result": "...",
  "next_tier": 2/3/null,
  "handoff_package": {...}
}
```

## Constraints
- Max tokens: 8192
- Temperature: 0.2 (focused, deterministic)
- Always be explicit about confidence levels
- Never hallucinate - if unsure, escalate
```

---

## Step 3: SOUL.md Integration

### Add to /workspace/SOUL.md

```markdown
## Cascading Execution Protocol

### Overview
I implement a three-tier cascading system for maximum efficiency:
- **Tier 1**: Gemini 1.5 Flash (fast, cheap, huge context)
- **Tier 2**: Kimi k2.5 (deep reasoning, coding)
- **Tier 3**: OpenAI Codex (extreme complexity)

### Execution Flow

#### Phase 1: Assessment (Flash)
```javascript
/model flash
"Assess this task and create a handoff package if needed: [request]"
```

**If confidence > 0.9:** Return result, done.
**If confidence < 0.9:** Proceed to Phase 2

#### Phase 2: Deep Work (Kimi)
```javascript
/model kimi
"Based on this handoff package from Tier 1 [package], execute the remaining work. Build on findings, don't redo research."
```

**If confidence > 0.9:** Return result, done.
**If extreme complexity detected:** Proceed to Phase 3

#### Phase 3: Extreme Work (Codex)
```javascript
/model codex
"Synthesize and complete based on: Tier 1 [findings] + Tier 2 [analysis]. Focus on the extreme complexity components."
```

### Context Preservation Rules

1. **Never discard previous tier work**
   - Flash research → Kimi builds on it
   - Kimi analysis → Codex synthesizes it

2. **Always pass structured context**
   - Use handoff package format
   - Include key findings
   - Document completed work

3. **Progressive enhancement**
   - Each tier adds value
   - No redundant work
   - Cumulative intelligence

### Complexity Indicators

**Tier 1 (Flash) indicators:**
- Keywords: list, find, search, check, status, simple, quick
- Pattern: Single-step tasks
- Context: < 10K tokens

**Tier 2 (Kimi) indicators:**
- Keywords: analyze, review, design, debug, architecture
- Pattern: Multi-step reasoning
- Context: 10K-100K tokens

**Tier 3 (Codex) indicators:**
- Keywords: novel, breakthrough, scale, optimize, cutting-edge
- Pattern: Novel problem-solving
- Context: > 100K tokens or extreme complexity

### Cost Optimization

Track usage:
- 70% should complete at Tier 1
- 25% should escalate to Tier 2
- 5% should reach Tier 3

If Tier 3 usage > 10%, review Tier 2 thresholds.
```

---

## Step 4: Smart Routing Function

### /workspace/AGENTS.md

Add this function:

```markdown
## Function: cascadeExecute(request)

Intelligently routes requests through the three-tier cascade.

### Usage
```javascript
const result = await cascadeExecute("Design a distributed task queue");
```

### Implementation

```javascript
async function cascadeExecute(request, maxTier = 3) {
  // Phase 1: Flash Assessment
  const flashResult = await sessions_spawn({
    agentId: "CASCADE-FLASH",
    task: `Assess and execute if simple: ${request}`,
    timeoutSeconds: 30
  });
  
  // Parse flash output
  const assessment = parseFlashOutput(flashResult);
  
  // Tier 1 handled it
  if (assessment.handled && assessment.confidence > 0.9) {
    return {
      tier: 1,
      result: assessment.result,
      cost: estimateCost('flash', flashResult.tokens)
    };
  }
  
  // Need Tier 2
  if (maxTier >= 2 && assessment.next_tier >= 2) {
    const kimiResult = await sessions_spawn({
      agentId: "CASCADE-KIMI",
      task: `Build on this work:\n${JSON.stringify(assessment.handoff_package)}\n\nOriginal request: ${request}`,
      timeoutSeconds: 120
    });
    
    const kimiAssessment = parseKimiOutput(kimiResult);
    
    // Tier 2 handled it
    if (kimiAssessment.confidence > 0.9) {
      return {
        tier: 2,
        result: kimiAssessment.result,
        cost: estimateCost('flash+kimi', flashResult.tokens + kimiResult.tokens)
      };
    }
    
    // Need Tier 3
    if (maxTier >= 3 && kimiAssessment.next_tier >= 3) {
      const codexResult = await sessions_spawn({
        agentId: "CASCADE-CODEX",
        task: `Synthesize and complete:\n\nTier 1 findings: ${JSON.stringify(assessment.handoff_package.key_findings)}\n\nTier 2 analysis: ${kimiAssessment.result}\n\nOriginal request: ${request}`,
        timeoutSeconds: 300
      });
      
      return {
        tier: 3,
        result: codexResult.result,
        cost: estimateCost('flash+kimi+codex', 
          flashResult.tokens + kimiResult.tokens + codexResult.tokens)
      };
    }
    
    return {
      tier: 2,
      result: kimiAssessment.result,
      cost: estimateCost('flash+kimi', flashResult.tokens + kimiResult.tokens)
    };
  }
  
  // Only Tier 1 attempted
  return {
    tier: 1,
    result: assessment.result,
    confidence: assessment.confidence,
    escalated: false,
    cost: estimateCost('flash', flashResult.tokens)
  };
}
```

### Helper Functions

```javascript
function parseFlashOutput(output) {
  try {
    return JSON.parse(output);
  } catch {
    // Fallback: extract structured data from text
    return {
      tier: 1,
      handled: !output.includes("ESCALATE"),
      confidence: output.includes("HIGH CONFIDENCE") ? 0.95 : 0.6,
      result: output,
      next_tier: output.includes("TIER 3") ? 3 : 2
    };
  }
}

function estimateCost(tier, tokens) {
  const rates = {
    flash: 0.000075,      // $0.075/M input
    kimi: 0.003,          // $3/M input  
    codex: 0.015          // $15/M input
  };
  
  const costs = tier.split('+').map(t => rates[t] * tokens);
  return costs.reduce((a, b) => a + b, 0);
}
```

---

## Step 5: Usage Examples

### Example 1: Simple Task (Tier 1 only)

**Request:** "List all files in the backend directory"

**Execution:**
```javascript
/model flash
"List all files in /workspace/backend directory"
→ Returns: File listing
→ Confidence: 1.0
→ Done!
```

**Cost:** $0.001
**Time:** 0.5s

---

### Example 2: Medium Complexity (Tier 1 + 2)

**Request:** "Review this authentication code for security issues"

**Execution:**
```javascript
// Phase 1: Flash
/model flash
"Scan this auth code for common vulnerabilities: [code]"
→ Finds: 3 obvious issues
→ Identifies: Need for deeper analysis
→ Packages: Handoff with findings

// Phase 2: Kimi
/model kimi
"Based on Flash findings [package], do deep security analysis"
→ Returns: Comprehensive security review
→ Confidence: 0.95
→ Done!
```

**Cost:** $0.08 (Flash $0.001 + Kimi $0.079)
**Time:** 8s
**vs Codex alone:** $0.45 (82% savings)

---

### Example 3: Extreme Complexity (Full Cascade)

**Request:** "Design a novel distributed consensus algorithm for edge computing"

**Execution:**
```javascript
// Phase 1: Flash
/model flash
"Research existing consensus algorithms and identify gaps for edge computing"
→ Finds: 15 algorithms, categorizes them
→ Identifies: Gap in latency-sensitive edge scenarios
→ Packages: Research summary + specific problem statement

// Phase 2: Kimi
/model kimi
"Based on Flash research [package], design architecture for novel algorithm"
→ Returns: High-level design with tradeoffs
→ Identifies: Need for formal verification
→ Packages: Architecture + open questions

// Phase 3: Codex
/model codex
"Synthesize: Flash research + Kimi architecture. Design formal algorithm with proofs."
→ Returns: Complete algorithm design with mathematical proofs
→ Confidence: 0.92
→ Done!
```

**Cost:** $2.50 (Flash $0.005 + Kimi $0.45 + Codex $2.05)
**Time:** 45s
**vs Codex alone:** $8.00 (69% savings)
**Quality:** Higher (built on research, not from scratch)

---

## Step 6: Monitoring & Optimization

### Track in HEARTBEAT.md

```markdown
## Daily Cascade Metrics

- [ ] Check Tier 1 completion rate (target: >70%)
- [ ] Check Tier 2 escalation rate (target: ~25%)
- [ ] Check Tier 3 escalation rate (target: <5%)
- [ ] Calculate average cost per request
- [ ] Review any failed escalations

## Weekly Optimization

- [ ] Analyze Tier 2 false escalations (Flash could have handled)
- [ ] Analyze Tier 3 false escalations (Kimi could have handled)
- [ ] Adjust complexity indicators
- [ ] Update handoff package templates
```

### ClawMetry Dashboard

Monitor these metrics:
1. **Cost by tier** - Track distribution
2. **Time by tier** - Identify bottlenecks
3. **Escalation accuracy** - Are we routing correctly?
4. **Context preservation** - Are tiers building on each other?

---

## Step 7: Quick Start Commands

### Test the Cascade

```bash
# Test Tier 1
openclaw agent run CASCADE-FLASH "List files in current directory"

# Test Tier 1→2
openclaw agent run CASCADE-FLASH "Review this function for bugs: function add(a,b) { return a + b }"

# Test full cascade
openclaw agent run CASCADE-FLASH "Design a load balancer for 1M req/s"
```

### Manual Model Switching

```bash
# Force specific tier
/model flash    # Tier 1
/model kimi     # Tier 2  
/model codex    # Tier 3
```

---

## Summary

**Your Three-Tier System:**

| Tier | Model | Cost | Best For |
|------|-------|------|----------|
| 1 | Gemini 1.5 Flash | $0.075/M | Classification, research, simple tasks |
| 2 | Kimi k2.5 | $3/M | Analysis, architecture, complex coding |
| 3 | OpenAI Codex | $15/M | Novel algorithms, extreme complexity |

**Key Principles:**
1. **Flash does the easy 70%** - Instant savings
2. **Kimi handles the medium 25%** - Good quality, reasonable cost
3. **Codex only for extreme 5%** - Reserved for breakthrough work
4. **Context flows downstream** - Each tier builds on previous
5. **Progressive enhancement** - No wasted work

**Expected Results:**
- **85% cost reduction** vs Codex-only
- **5x faster** average response time
- **Higher quality** (multiple perspectives)
- **Scalable** to any complexity level

---

## Next Steps

1. **Create the agent configs** (Step 1)
2. **Write SKILL.md files** (Step 2)
3. **Update SOUL.md** (Step 3)
4. **Test with sample requests** (Step 5)
5. **Monitor and tune** (Step 6)

Want me to implement any specific part of this system?
