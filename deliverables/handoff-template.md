# Handoff Package Template

## Tier Assessment
- **Source Tier**: [1|2]
- **Target Tier**: [2|3]
- **Confidence**: [0.0-1.0]
- **Escalation Reason**: [Why moving to next tier]

## Completed Work (Lower Tier)

### Research & Discovery
- [ ] Initial research completed
- [ ] Key sources identified
- [ ] Problem structured into components

### Analysis & Findings
- [ ] Preliminary analysis done
- [ ] Patterns identified
- [ ] Obvious issues caught

### Execution
- [ ] Simple tasks completed
- [ ] Foundation established
- [ ] Structure created

## Key Findings

### Finding 1: [Title]
**Description**: [What was discovered]
**Evidence**: [Supporting data]
**Implications**: [What this means for next tier]

### Finding 2: [Title]
**Description**: [What was discovered]
**Evidence**: [Supporting data]
**Implications**: [What this means for next tier]

### Finding 3: [Title]
**Description**: [What was discovered]
**Evidence**: [Supporting data]
**Implications**: [What this means for next tier]

## Remaining Work (For Next Tier)

### Must Do
- [ ] [Specific task requiring next tier's capabilities]
- [ ] [Specific task requiring next tier's capabilities]

### Should Do
- [ ] [Enhancement or optimization]
- [ ] [Additional validation]

### Could Do
- [ ] [Nice-to-have extension]
- [ ] [Future improvement]

## Context Required

### Background Knowledge
- [ ] [System architecture context]
- [ ] [Business requirements]
- [ ] [Technical constraints]

### Prior Decisions
- [ ] [Decision made at lower tier]
- [ ] [Rationale for approach]

### Resources
- **Documentation**: [Links/references]
- **Code**: [File paths]
- **Data**: [Datasets/samples]

## Success Criteria

### Definition of Done
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Quality Standards
- [ ] [Standard 1]
- [ ] [Standard 2]

### Validation Method
- [ ] [How to verify correctness]

---

## Usage Instructions

### For Tier 1 → Tier 2
1. Complete all Tier 1 tasks you can handle
2. Document findings clearly
3. Be specific about what Tier 2 should do
4. Include all research and context

### For Tier 2 → Tier 3
1. Synthesize Tier 1's research
2. Add your deep analysis
3. Clearly define the breakthrough needed
4. Provide architectural foundation

### For Receiving Tier
1. Read the entire handoff package
2. Understand what was already done
3. Focus ONLY on remaining work
4. Build on findings, don't redo them

---

## Example: Tier 1 → Tier 2

```yaml
Tier Assessment:
  Source: 1 (Flash)
  Target: 2 (Kimi)
  Confidence: 0.7
  Reason: "Need deep security analysis"

Completed Work:
  - Researched 15 auth libraries
  - Identified 3 obvious vulnerabilities
  - Structured code into 5 modules

Key Findings:
  1. JWT implementation uses weak algorithm (HS256)
  2. No rate limiting on login endpoint
  3. Session tokens don't expire

Remaining Work:
  - Deep security audit of crypto implementations
  - Design secure token refresh strategy
  - Evaluate OAuth2 integration approach

Context Required:
  - System uses microservices architecture
  - Must support 1M concurrent users
  - Compliance: SOC2 required

Success Criteria:
  - No critical vulnerabilities (CVSS > 7)
  - Token strategy handles all edge cases
  - Implementation guide provided
```

---

## Example: Tier 2 → Tier 3

```yaml
Tier Assessment:
  Source: 2 (Kimi)
  Target: 3 (Codex)
  Confidence: 0.8
  Reason: "Need novel algorithm design"

Completed Work:
  Tier 1:
    - Researched existing consensus algorithms
    - Identified gap in edge computing scenarios
  
  Tier 2:
    - Designed high-level architecture
    - Identified 3 potential approaches
    - Evaluated tradeoffs

Key Findings:
  1. Raft is too chatty for edge networks
  2. PBFT assumes synchronous communication
  3. Novel approach: latency-aware consensus

Remaining Work:
  - Design formal consensus algorithm
  - Provide mathematical proof of safety
  - Prove liveness under network partitions
  - Optimize for <100ms latency

Context Required:
  - Edge nodes: 10K-100K
  - Network: intermittent connectivity
  - Latency requirement: <100ms
  - Fault tolerance: 33% Byzantine

Success Criteria:
  - Algorithm is formally proven correct
  - Handles all edge cases
  - Performance meets <100ms target
  - Ready for production implementation
```
