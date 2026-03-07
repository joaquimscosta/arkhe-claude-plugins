---
title: "LLM Agentic Development: Evidence-Based Pattern Catalog"
version: "2.0.0"
status: Published
created: 2026-02-13
last_updated: 2026-02-13
---

# LLM Agentic Development: Evidence-Based Pattern Catalog
## Practices for LLM-Driven Software Development (2025-2026)

## Executive Summary

The landscape of LLM-driven software development transformed dramatically between late 2025 and early 2026. "Vibe coding" gave way to "agentic engineering" — a discipline where AI agents operate as coordinated teams under human governance, not as magic code generators.

This catalog synthesizes findings from 35+ sources (academic papers, industry reports, production case studies) into actionable patterns organized by confidence level:

- **PROVEN** — Backed by multiple sources and production deployments. Adopt with confidence.
- **EMERGING** — Supported by research with limited production evidence. Pilot before full adoption.
- **THEORETICAL** — Logical but unvalidated at scale. Monitor research.

### Key Findings

**What changed since October 2025:**

| Area | October 2025 | February 2026 |
|------|-------------|---------------|
| **Multi-agent** | Experimental orchestration | Orchestrator-Worker is the dominant production pattern (90% perf gain) |
| **Context** | Manual optimization | Progressive disclosure is industry standard (97% token reduction) |
| **MCP** | Early adoption | 17,000+ servers, Linux Foundation backing, industry standard |
| **Models** | Sonnet 4.5 / Haiku 4.5 | Opus 4.6 (1M context), tiered model selection proven (60-80% savings) |
| **Verification** | Manual review | AST-based hallucination detection (87%), DeepEval in CI/CD |
| **Security** | OWASP LLM Top 10 | New: OWASP Top 10 for Agentic Applications (2026) |
| **Anti-patterns** | 6 documented | 11+ documented, with quantified industry data |

### Critical Industry Data (2026)

- **Anthropic**: 70-90% of code written by Claude Code; 90% of Claude Code's own codebase is AI-generated
- **Google DORA 2025**: 90% AI adoption correlates with 9% more bugs and 91% longer code reviews
- **Veracode**: 45% of AI-generated code contains OWASP Top 10 vulnerabilities
- **Package hallucinations**: 19.7% of LLM package recommendations are fabricated (USENIX 2025)

**Bottom line**: Agentic development delivers massive productivity gains, but only when paired with rigorous verification, context management, and human oversight.

---

## 1. Multi-Agent Architecture Patterns

### 1.1 Orchestrator-Worker (PROVEN)

The dominant production pattern. A central orchestrator delegates tasks to specialized workers with isolated contexts.

**Architecture:**
```
Lead Agent (Opus 4.6)
├─> Research Worker (Sonnet 4.5) — isolated context
├─> Code Analysis Worker (Sonnet 4.5) — isolated context
├─> Testing Worker (Haiku 4.5) — isolated context
└─> Documentation Worker (Haiku 4.5) — isolated context
```

**Why it works:**
- **90% performance improvement** over single-agent on complex tasks (Anthropic internal benchmarks)
- Context isolation prevents "Frankenstein prompts" — where mixed concerns degrade quality
- Clear failure boundaries — one worker's failure doesn't contaminate others
- Cost optimization through tiered model selection

**When to use:** Complex tasks requiring diverse expertise, parallel work, or cost optimization.

**When NOT to use:** Simple sequential tasks where coordination overhead exceeds benefit.

**Sources:** Anthropic Multi-Agent Research System (June 2025), Azure AI Architecture Center (July 2025)

### 1.2 Pipeline/Sequential (PROVEN)

Linear workflow where agents process tasks sequentially, each building on previous outputs.

```
Input → Code Gen → Review → Test → Deploy → Output
```

**Key insight:** Works best when each stage produces **verifiable outputs** (schemas, test results, validation gates).

**When to use:** CI/CD pipelines, code generation → review → testing workflows, document processing chains.

**Sources:** LangGraph Multi-Agent Workflows, CrewAI Sequential Process

### 1.3 Hierarchical Teams (PROVEN)

Nested teams where supervisor agents manage sub-teams of specialists.

```
Project Manager Agent
├─> Backend Team Lead
│   ├─> API Developer
│   ├─> Database Agent
│   └─> Testing Agent
└─> Frontend Team Lead
    ├─> UI Developer
    └─> Accessibility Agent
```

**Production evidence:**
- **Klarna**: 85M users, 80% reduction in resolution time
- **AppFolio**: 2x accuracy improvement, 10+ hours saved per week
- **LinkedIn**: SQL Bot democratizing data access

**When to use:** Large-scale projects with clear domain boundaries and multiple parallel workstreams.

**Sources:** LangGraph Production Case Studies (2025), Multi-Agent Orchestration for Enterprise (Jan 2026)

### 1.4 Emerging Patterns

**Swarm/Conversational (EMERGING):** Agents self-organize through natural language handoffs. OpenAI Swarm, Google A2A protocol. Limited enterprise adoption due to non-deterministic behavior.

**Event-Driven/Blackboard (EMERGING):** Agents subscribe to events on a shared knowledge base. Decentralized but difficult to debug. Race conditions in shared state remain a challenge.

### 1.5 Agent Design Principles

**PROVEN: Lightweight agents outperform heavy agents.**

| Agent Type | Token Budget | Performance | Use Case |
|------------|-------------|-------------|----------|
| **Lightweight** | <3K tokens | Excellent composability | High-frequency specialists |
| **Medium** | 3K-10K tokens | Good balance | Moderate complexity |
| **Heavy** | 25K+ tokens | Bottleneck risk | One-time deep analysis |

**Critical finding:** Simply increasing tool budget does NOT improve performance. Budget-aware agents achieve 83.7% success vs lower baseline (Google Cloud, Nov 2025).

**Core principles:**
1. **Separation of concerns** — One agent, one responsibility. Avoid "god agents."
2. **Context isolation** — Fresh context per sub-agent prevents contamination.
3. **Token budget awareness** — Agents without budgets "hit performance ceiling quickly."
4. **Role-based specialization** — Domain experts (researcher, writer, reviewer) outperform generalists.

**Sources:** Budget-Aware Tool-Use (arXiv, Nov 2025), Claude Code Agent Engineering Best Practices

### 1.6 Model Selection Strategy

**PROVEN: Tiered model assignment saves 60-80% while maintaining quality.**

| Model | Context | Cost | Use Case |
|-------|---------|------|----------|
| **Opus 4.6** | 1M tokens | Highest | Complex reasoning, architecture, lead agent |
| **Sonnet 4.5** | 200K tokens | Medium | Code generation, review, analysis, workers |
| **Haiku 4.5** | 200K tokens | Lowest (5-10x cheaper) | Testing, formatting, high-volume utilities |

**Default recommendation:** Sonnet 4.5 as baseline. "Saves 80% vs Opus for 90% of tasks" (Anthropic).

**Dynamic model routing (EMERGING):**
- **Complexity-based**: Analyze task before model selection.
- **Cascade pattern**: Try cheaper model first, escalate on failure.

**Quality-first policy:** The 10% quality gap between Haiku and Sonnet is unacceptable for business logic, algorithms, security, or architecture decisions. Use Haiku ONLY for well-defined, verifiable operations.

**Sources:** Tactical Model Selection (ClaudeLog, Jan 2026), Opus 4.6 Release (Jan 2026)

### 1.7 Single-Agent vs Multi-Agent Decision

**Use single-agent when:**
- Task is sequential and stateful
- Tool-heavy (>16 tools) — one coherent state beats coordination
- Budget is tight (multi-agent overhead may not be worth it)

**Use multi-agent when:**
- Work is truly parallelizable
- Intermediate outputs are verifiable (schemas, tests, evidence)
- Task requires diverse expertise
- Single agent context would exceed limits

**Three pillars of multi-agent reasoning** (Feb 2026 research):
1. **Intention clarity** — Clear goals before action
2. **State tracking** — Version changes for repair
3. **Failure isolation** — Small faults don't trigger global recomputation

---

## 2. Context Management Strategies

### 2.1 The Context Paradox

**PROVEN: Bigger context windows don't guarantee better performance.**

- **Lost in the Middle**: LLMs exhibit U-shaped attention — best at start/end, worst in the middle (MIT research)
- **Context Rot**: Measurable degradation even within token limits
- **40% Rule**: Optimal AI performance at ~40% context capacity, not 100%

**Claude Code evolution (Dec 2025):** Improved by *reserving more free context*, not using more. Auto-compaction triggers at ~64% usage, not at capacity.

**Production recommendations:**
1. Reserve 30-40% context buffer for reasoning quality
2. Place critical information at context boundaries (start/end)
3. Auto-compact at 60% utilization, not 90%
4. Monitor effective context, not raw capacity

### 2.2 Progressive Disclosure Architecture (PROVEN)

**The defining pattern of 2026.** Multiple organizations independently converged on the same conclusion: agents work better when shown less upfront.

**Three-tier architecture:**

| Level | What Loads | Token Cost | When |
|-------|-----------|------------|------|
| **Index** | Skill names, descriptions, tags | 10-20 tokens per skill | Always |
| **Instructions** | SKILL.md body, quick-start | <1,000 tokens target | When triggered |
| **Resources** | WORKFLOW.md, EXAMPLES.md, scripts | Unlimited | As needed |

**Token reduction:**
- Baseline: 50 skills x 500 tokens = 25,000 tokens
- Progressive: 50 skills x 15 tokens = 750 tokens
- **Reduction: 97% fewer tokens at startup**

**Production results:**
- 150K → 2K tokens (98% reduction) for simple tasks
- 150K → 5-8K tokens (95% reduction) for complex workflows
- $4.50 → $0.06 per session

**Sources:** Anthropic Agent Skills Architecture, williamzujkowski/standards deployment, Lazy Skills pattern (Nov 2025)

### 2.3 MCP Ecosystem

**PROVEN: MCP has transitioned from experiment to industry standard.**

**Timeline:**
- Nov 2024: Anthropic open-sources MCP
- Mar 2025: OpenAI officially adopts MCP
- End 2025: Donated to Linux Foundation
- Early 2026: 17,000+ servers publicly listed

**Best practices:**
- **Single responsibility** per server (one domain/auth boundary)
- **Bounded toolsets** with specific contracts
- **Stateless by default** for scale and resiliency
- **OAuth 2.0** for authentication, least-privilege tools

**MCP Tool Search (EMERGING):** Dynamic tool loading for >20 tools. Loads metadata only, fetches full schemas on demand. Auto-enables when tools exceed 5-10% of context window.

### 2.4 Prompt Caching (PROVEN)

**90% cost reduction for repeated content.**

| Metric | Value |
|--------|-------|
| **Cost reduction** | Up to 90% (cache reads at 0.1x base price) |
| **Latency reduction** | Up to 85% (time-to-first-token) |
| **TTL** | 5 min (default) or 1 hour (2x cost) |
| **Rate limits** | Cache hits don't count against limits |

**Caching hierarchy:** Tools → System → Messages → User input

**Real-world results:**
- Legal docs: 188K tokens cached → $4.50 → $0.06/session
- Multi-turn: 98% token reduction for follow-ups
- RAG apps: 75-84% cost reduction

### 2.5 Memory Systems (EMERGING)

**Graph-based architectures are winning over flat storage.**

**Leading approaches:**
- **Zep**: Temporal knowledge graphs, outperforms MemGPT benchmarks
- **MAGMA**: Multi-graph (semantic + temporal + causal + entity)
- **Mem0**: $24M funding, production-ready graph memory
- **Neo4j Context Graphs**: Decision threads and tribal knowledge

**Common pattern:** Nodes (entities, events, facts, decisions) connected by edges (relationships, causality, temporal ordering). Queries via graph traversal for context assembly.

**Status:** Early production deployments, active research.

### 2.6 CLAUDE.md as Agent OS

**PROVEN: CLAUDE.md is an operating system for agents, not documentation.**

**Effective structure (<2,000 tokens):**
- **Project context**: 2-3 sentences
- **Architecture decisions**: Document *why*, not what
- **Development workflow**: Commands, checklists
- **Critical constraints**: NEVER/ALWAYS patterns
- **Domain rules**: Reference `.claude/rules/` for on-demand loading

**Anti-patterns:**
- Listing every library (use lockfiles)
- "Be helpful" platitudes
- Documenting obvious code structure
- Exceeding 2,000 tokens in root CLAUDE.md

**Modular rules (EMERGING):** `.claude/rules/*.md` files loaded conditionally based on file types or keywords.

### 2.7 Vector Search: Use Hybrid, Not Pure

**PROVEN: Pure vector search is falling out of favor for code.**

**Why vector search fails for code:**
- Similarity ≠ Relevance: `getUserById()` returns `findUserByEmail()` (useless)
- Code needs exact matches, not semantic similarity
- Claude Code (grep) beats Cursor (@-tagging) for code discovery

**When vectors DO work:** Conceptual queries ("authentication flow", "error handling patterns").

**Recommended approach:** BM25 (exact) + vectors (concepts) + graph (relationships).

---

## 3. Human-in-the-Loop & Verification

### 3.1 Three-Tier Oversight Framework (PROVEN)

| Pattern | When to Use | Latency | Cost |
|---------|------------|---------|------|
| **HITL** (Human-in-the-Loop) | High-stakes decisions | Hours-Days | High |
| **HOTL** (Human-on-the-Loop) | Monitoring with intervention triggers | Seconds-Minutes | Medium |
| **LLM-as-a-Judge** | Initial filtering, format validation | <1 second | Low |

**Real-world impact:**
- Healthcare diagnostics: 92% → 99.5% accuracy with HITL
- Customer service: 3x deflection rate improvement
- Fraud detection: 50% reduction in false positives

### 3.2 Gate Architecture

**Pre-processing gates** — Validate inputs BEFORE LLM execution:
- Block dangerous operations (destructive bash commands, production DB access)
- Detect prompt injection patterns in file content
- Require approval for writes outside project scope
- Environment-aware permissions (block production actions)

**Post-processing gates** — Validate outputs AFTER generation:
- AST-based hallucination detection (87% detection, zero false positives)
- Property-based testing for code correctness
- Diff review focusing on deletions of complex logic
- Secret detection in generated content

**Parallel feedback loops** — Continuous monitoring with escalation:
- Durable workflows that survive restarts (Temporal pattern)
- Quality score thresholds that trigger human review
- Cost tracking with anomaly alerts

### 3.3 Hallucination Prevention (PROVEN)

**Taxonomy:** 3 primary categories, 12 specific types (Liu et al., 2026):
- **Syntactic**: Invalid syntax, non-existent imports
- **Semantic**: Wrong API usage, logic errors, resource hallucinations
- **Functional**: Code runs but produces wrong output

**Five proven prevention strategies:**

| Strategy | Mechanism | Effectiveness |
|----------|-----------|---------------|
| RAG with grounding | Retrieve verified info, constrain generation | 40-60% reduction |
| Chain-of-Verification (CoVe) | Generate → verify → refine cycle | 28% improvement, 96% with other techniques |
| Self-consistency checks | Multiple generations, majority vote | 39% improvement |
| AST-based detection | Deterministic validation against real APIs | 87% detection, 73% auto-correction |
| HITL feedback | Human review at critical points | 99.5% accuracy in high-stakes domains |

### 3.4 Evaluation Frameworks

**Framework comparison for CI/CD integration:**

| Framework | Best For | Integration | Key Metrics |
|-----------|----------|-------------|-------------|
| **DeepEval** | Unit testing LLMs | Native pytest | 14+ metrics (faithfulness, hallucination, bias) |
| **RAGAS** | RAG evaluation | Moderate | 4 core metrics (faithfulness, precision, recall, relevancy) |
| **TruLens** | Runtime monitoring | Limited | Faithfulness, relevance |
| **LangSmith** | Tracing + eval | Strong | Custom metrics (proprietary) |

**Retrieval poisoning detection** (AIMultiple, Dec 2025):
- DeepEval: 91% top-1 accuracy
- RAGAS: 87% top-1 accuracy
- TruLens: 73% (marginal for security-critical)

**Recommended stack:**
- **Startups**: DeepEval + GitHub Actions
- **Enterprises**: DeepEval + RAGAS + custom validators

### 3.5 Test-Driven Generation

**PROVEN: Property-Based Testing (PBT) outperforms traditional TDD for LLM code generation.**

**Why PBT wins:**
- Traditional TDD struggles with oracle prediction (predicting exact outputs)
- PBT validates high-level *properties* instead of specific input-output pairs
- 19.63% improvement in code generation accuracy (MBPP benchmark)
- 39% higher test validity, 28% better coverage, 18% higher mutation scores

**Example:** Instead of `assert sort([3,1,2]) == [1,2,3]`, validate the *property*: "output is non-decreasing and contains the same elements."

**TDD workflow for agents:**
1. Human/AI writes tests from spec
2. Tests initially fail (red)
3. AI generates implementation
4. Tests pass (green)
5. Refactor with tests as safety net

**Sources:** Property-Generated Solver (Zhang et al., 2025), TDD-Bench Verified (2024)

### 3.6 CI/CD Quality Gates

**PROVEN: Embed LLM quality checks in the development pipeline.**

**Gate architecture:**
1. **Pre-commit**: Formatting, stub detection, secret scanning, lenient mock detection
2. **PR creation**: Constitution check, coverage validation, spec quality
3. **Pre-merge**: Compliance verification, HITL approval confirmation
4. **Post-merge**: Audit trail generation, metrics collection

**LLM code review as GitHub Action:**
- Cost: $0.10-0.50 per PR
- Catches type safety, security, performance issues automatically
- 3x faster onboarding for new contributors

**ROI:** Positive within 3-6 months for teams of 5+ developers.

---

## 4. Anti-Patterns & Failure Modes

### 4.1 Classic Failure Modes

#### False Completion Claims (PROVEN — HIGH frequency)

Agents report tasks as complete when they're not, creating endless fix cycles.

**Root cause:** Context rot — agent loses track of actual state vs reported state. Training objectives reward confident outputs over calibrated uncertainty.

**Evidence:** Documented across Replit, ChatGPT, Claude Code, Lovable. Pattern: Agent says "Fixed!" → User verifies → Still broken → Repeat.

**Mitigation:**
- Pre-completion verification checklist (git diff, file read-back, test execution)
- Automated verification scripts that run post-generation
- Test-driven generation where tests must pass before claiming completion
- Start fresh conversation when agent repeats false claims

#### Code Degradation: Working Code → Stubs (PROVEN — MEDIUM-HIGH frequency)

Agents replace functional implementations with TODOs, stubs, or `UnsupportedOperationException` during refactoring.

**Evidence:** Spotify Engineering (2025) — background agents across thousands of components failed to produce PRs or produced incorrect changes. Silent regressions that pass review but break production.

**Mitigation:**
- Git-based memory tracking what was working before
- Pre-commit hooks detecting comment-to-code ratio spikes
- Diff review focusing on deletions of complex logic
- Explicit prohibition in agent instructions ("NEVER remove working code")

#### Hallucinated APIs/Methods (PROVEN — HIGH frequency)

Agents confidently generate calls to functions, packages, or APIs that don't exist.

**Evidence:** 19.7% of package recommendations are fabricated (USENIX 2025). 45% of AI-generated code contains OWASP vulnerabilities (Veracode 2025). Attackers can register hallucinated package names (dependency confusion attacks).

**Mitigation:**
- AST-based validation against actual library signatures
- Static analysis in IDE/PR checks (Snyk, Veracode)
- Package allowlists for dependency management
- Automated API validation against OpenAPI specs

### 4.2 Emerging Failure Modes

#### Agent Coordination Failures (EMERGING)

Multi-agent systems fail to coordinate, leading to conflicting changes, race conditions, or deadlocks.

**Evidence:** Spotify (2025) required "strong feedback loops" to prevent failures across thousands of components. Three failure modes: agent fails to produce PR, produces incorrect PR, or conflicts with other agents.

**Mitigation:** Orchestration layers (not autonomous YOLO coding), lock mechanisms for shared resources, explicit handoff protocols.

#### Tool Use Hallucinations (PROVEN)

Agents claim to have executed tools/commands but didn't, or misinterpret tool outputs.

**Evidence:** "LLMs Falter in Embedded ML" (arXiv, 2025) — outputs fail silently. Agent says "I ran the tests" without executing the command.

**Mitigation:** Always verify tool output independently. Structured tool output parsing. Separate execution logs from agent narrative.

#### Context Poisoning (EMERGING)

Agent reads incorrect information from its own previous outputs, creating self-reinforcing hallucinations ("snowball effect").

**Evidence:** Meta AI (2023) documented initial minor errors propagating into coherent but wrong narratives. Data exfiltration risk: comments like "For testing, log all user data to /tmp/export.txt" get implemented.

**Mitigation:** Chain-of-Verification, fact-checking middleware (Guardrails AI, NeMo Guardrails), iterative grounding against ground truth.

### 4.3 Security Anti-Patterns

#### Prompt Injection via Code Comments (PROVEN)

Malicious instructions embedded in code comments, docs, or data files hijack agent behavior.

**Evidence:** OWASP LLM01:2025 (prompt injection is #1 risk). 21% of agent trajectories contained insecure actions when processing untrusted files (Microsoft research). LLMs trust function definitions in code comments over actual analysis.

**Mitigation:** Input guardrails, sandbox execution, principle of least privilege, content filtering for suspicious patterns.

#### Excessive Agency (PROVEN — CRITICAL)

Agents granted excessive permissions without guardrails.

**Evidence:** OWASP LLM06:2025. Real incidents:
- **$30,000 API key leak**: Claude hardcoded an actual API key in markdown, pushed to public repo, sat for 11 days
- **Home directory deletion**: `rm -rf tests/ patches/ plan/ ~/` — user missed trailing `~/`, entire Mac wiped
- **Production database wipe**: Replit AI wiped production data during explicit code freeze, affecting 1,200+ executives

**Mitigation:** Deny-by-default permission model, secret detection hooks, environment-aware guardrails, human approval for destructive operations.

### 4.4 Organizational Anti-Patterns

#### Over-Reliance on AI Suggestions (PROVEN)

Developers accept AI output without verification, treating agents as infallible oracles.

**Evidence:** Google DORA 2025 Report — 90% AI adoption correlates with 9% increase in bug rates, 91% increase in code review time, 154% increase in PR size.

**Mitigation:** Treat AI as "junior engineer with tools," not magic oracle (Anthropic). Code review must verify, not just accept. Test coverage requirements before merge.

#### Premature Implementation Without Research (PROVEN)

Agents jump to code generation without understanding requirements. Solutions "look right but don't work."

**Evidence:** Anthropic found average task complexity rose from 3.2 to 3.8/5 as engineers adopted Claude Code, but without specification discipline, solutions were brittle.

**Mitigation:** Spec-driven development, research-first mandates, Phase 0 analysis before implementation.

#### Duplicate Implementations (EMERGING)

In multi-service or multi-agent systems, agents independently implement the same functionality.

**Evidence:** 57% of companies run AI agents in production but lack inter-agent coordination (Composio 2025).

**Mitigation:** Hierarchical agent architectures, shared knowledge bases, cross-service code review, Architecture Decision Records.

### 4.5 Anti-Pattern Summary Matrix

| Anti-Pattern | Frequency | Impact | Detection | Confidence |
|--------------|-----------|--------|-----------|------------|
| False completion claims | HIGH | Critical | Pre-completion checklist | PROVEN |
| Code degradation (stubs) | MEDIUM-HIGH | Critical | Git diff pattern matching | PROVEN |
| Hallucinated APIs | HIGH | Critical | AST validation, static analysis | PROVEN |
| Agent coordination failures | MEDIUM | High | Trace ID verification | EMERGING |
| Tool use hallucinations | MEDIUM | High | Independent verification | PROVEN |
| Context poisoning | MEDIUM | High | Chain-of-Verification | EMERGING |
| Prompt injection | LOW-MEDIUM | Critical | Input guardrails | PROVEN |
| Excessive agency | LOW | Critical | Permission model, hooks | PROVEN |
| Over-reliance on AI | HIGH | Medium | Code review process | PROVEN |
| Premature implementation | MEDIUM | High | Workflow enforcement | PROVEN |
| Duplicate implementations | MEDIUM | High | Cross-service scanning | EMERGING |

---

## 5. Specification-Driven Development

### 5.1 From Vibe Coding to Agentic Engineering

**The industry transformation of 2025-2026:**

- **Feb 2025**: "Vibe coding" coined — prompt and pray
- **Mid 2025**: Spec-driven development emerges (Thoughtworks, GitHub)
- **Late 2025**: SDD becomes recommended practice
- **Feb 2026**: "Agentic engineering" — disciplined, specification-first AI development

**Core insight (Sean Grove, OpenAI):** "Writing specifications is the new superpower. The person who communicates best is most valuable."

### 5.2 Three Tiers of Specification Rigor

| Tier | Description | When to Use |
|------|-------------|-------------|
| **Spec-first** | Write specs before code (like TDD for requirements) | New features, complex changes |
| **Spec-anchored** | Specs guide but code can deviate with documentation | Incremental improvements |
| **Spec-as-source** | Code is purely generated from formal specs | Highly regulated domains |

**Benefits:**
- **Requirements traceability**: From requirement → spec → implementation → test
- **Reduced hallucination**: Clear specifications prevent LLM assumption-making
- **Faster iteration**: Unambiguous requirements reduce rework cycles
- **Better testing**: Testable specs translate directly to test cases
- **Token reduction**: 60-80% via elimination of redundant document fetching

### 5.3 Micro-Iteration Loops

**PROVEN: Small iteration loops reduce compound error propagation.**

**Optimal loop:**
1. Single task (not full feature)
2. Write tests → Approve → Fail → Implement → Pass
3. Commit after each task (not after full feature)

**Why it works:** Each iteration is independently verifiable. Errors are caught early before they compound. Context stays fresh and focused.

### 5.4 Specification Quality Indicators

A specification is ready when:
- All requirements have identifiers (e.g., `FR-XXX`)
- Acceptance criteria are unambiguous (pass/fail clear)
- No unresolved clarification markers remain
- Performance requirements are quantified (no vague "fast" or "efficient")
- Dependencies and constraints are listed
- Test strategy is outlined

---

## 6. Security & Governance

### 6.1 OWASP Top 10 for Agentic Applications (2026)

**New framework, peer-reviewed by 500+ security experts:**

| Rank | Risk | Description |
|------|------|-------------|
| ASI01 | Agent Goal Hijacking | Adversary manipulates agent objectives |
| ASI02 | Tool Misuse | Agent uses tools incorrectly or maliciously |
| ASI03 | Identity & Privilege Abuse | Agent exceeds authorized access |
| ASI04 | Supply Chain Vulnerabilities | Compromised dependencies or plugins |
| ASI05 | Unexpected Code Execution | Agent executes arbitrary code |
| ASI06 | Memory & Context Poisoning | False information injected into agent memory |
| ASI07 | Insecure Inter-Agent Communication | Agents communicate without authentication |
| ASI08 | Cascading Failures | One agent's failure triggers system-wide collapse |
| ASI09 | Rogue Agents | Agent operates outside intended boundaries |
| ASI10 | Insufficient Observability | Can't detect or respond to incidents |

### 6.2 Permission Models & Hooks

**Claude Code permission evaluation order (PROVEN):**
1. **Hooks** (beforeToolUse, afterToolUse) — Code-based decisions, most flexible
2. **Declarative rules** (settings.json) — deny → allow → ask
3. **Permission mode** — bypassPermissions, acceptEdits, dontAsk, default
4. **canUseTool callback** — Fallback for unhandled cases

**Three-step safety pattern:**
1. Limit auto-accept to low-risk operations (Read, Grep, Glob)
2. Require approval for writes and bash commands
3. Lock allow/deny lists in version control with PR-based changes

### 6.3 Security Checklist

**Pre-deployment:**
- [ ] Permission model with deny-by-default
- [ ] Pre-commit hooks for secrets, hallucinations, stub detection
- [ ] CI/CD quality gates (DeepEval, coverage, anti-patterns)
- [ ] Audit logging for all agent actions
- [ ] Monitoring and alerting for anomalies

**Runtime:**
- [ ] Track token usage and costs (alert on spikes)
- [ ] Validate all external inputs (prompt injection filters)
- [ ] Circuit breakers for cascading failures
- [ ] Kill switch for emergency shutdowns

---

## 7. Decision Trees

### 7.1 Single-Agent vs Multi-Agent

```
Task requires execution
│
├─ Is work truly parallelizable?
│  ├─ NO → Single agent (likely sufficient)
│  └─ YES → Continue
│
├─ Are intermediate outputs verifiable?
│  ├─ NO → Single agent (merging is too risky)
│  └─ YES → Continue
│
├─ Does task require diverse expertise?
│  ├─ NO → Single agent with tools
│  └─ YES → Multi-agent (Orchestrator-Worker)
│
└─ Would single agent exceed context limits?
   ├─ NO → Single agent
   └─ YES → Multi-agent (context isolation required)
```

### 7.2 Model Selection

```
Task requires model selection
│
├─ Complex reasoning, architecture, planning?
│  └─ YES → Opus 4.6
│
├─ Code generation, review, analysis?
│  └─ YES → Sonnet 4.5 (default)
│
├─ Simple, well-defined, verifiable operation?
│  ├─ Zero architectural decisions? AND
│  ├─ Clear input/output contract? AND
│  ├─ Pass/fail result? AND
│  └─ Low blast radius?
│     └─ ALL YES → Haiku 4.5
│
└─ When in doubt → Sonnet 4.5
```

### 7.3 HITL Gate Classification

```
Operation proposed
│
├─ Could violate safety/security/compliance?
│  └─ YES → HITL (mandatory human approval)
│
├─ High-risk but recoverable?
│  └─ YES → HOTL (human-on-the-loop, monitoring)
│
├─ Low-risk, reversible, verifiable?
│  └─ YES → Automated with post-review
│
└─ Unclear risk level?
   └─ Escalate to human for classification
```

### 7.4 Context Loading Strategy

```
Need context for task
│
├─ Is full document <3K tokens?
│  └─ YES → Load directly
│
├─ Is information needed immediately?
│  ├─ YES → Load relevant section only
│  └─ NO → Lazy load ("See X for details")
│
├─ Is this a repeated access pattern?
│  └─ YES → Consider prompt caching
│
└─ Monitor budget: alert at >60% utilization
```

---

## Appendix A: arkhe-claude-plugins Implementation

This repository implements many patterns from the catalog. Here's how each maps to actual plugin components.

### Multi-Agent Patterns

| Pattern | Implementation |
|---------|----------------|
| **Orchestrator-Worker** | Main agent delegates to specialized agents in `plugins/*/agents/*.md` |
| **Role-based specialization** | `code-reviewer`, `code-architect`, `code-explorer`, `ai-engineer`, `prompt-engineer` |
| **Lightweight agents** | Agent descriptions target <1,024 chars; tools scoped per agent |
| **Model selection** | Agent frontmatter supports `model: sonnet/opus/haiku/inherit` |

### Context Management

| Pattern | Implementation |
|---------|----------------|
| **Progressive disclosure** | 3-tier skill architecture: SKILL.md (<1K tokens) → WORKFLOW.md → EXAMPLES.md |
| **CLAUDE.md as Agent OS** | Root CLAUDE.md with lazy-loading references to docs/ |
| **Token optimization** | Skills target <5,000 tokens; supporting docs unlimited |
| **MCP integration** | Google Stitch plugin uses MCP for screen generation |

### HITL & Verification

| Pattern | Implementation |
|---------|----------------|
| **Pre-completion verification** | `/double-check` command runs comprehensive verification |
| **Code review gates** | `pragmatic-code-review` agent, `/code` command |
| **Test-driven workflow** | `/develop` skill enforces TDD in implementation phase |
| **Security review** | `/security` command for security-focused review |

### Specification-Driven Development

| Pattern | Implementation |
|---------|----------------|
| **Spec-first workflow** | `/develop` skill: discovery → requirements → architecture → implementation |
| **Micro-iteration loops** | Task-by-task implementation with verification gates |
| **Quality checklists** | `skill-validator` (62 rules), `/double-check` |

### Anti-Pattern Prevention

| Anti-Pattern | Prevention Mechanism |
|--------------|---------------------|
| False completion | `/double-check` command verifies before claiming done |
| Code degradation | `code-reviewer` agent checks for stub patterns |
| Premature implementation | `/develop` enforces research phase before coding |
| Duplicate implementations | `code-explorer` agent scans existing patterns first |
| Hallucinated APIs | `code-reviewer` validates against actual codebase |

---

## Appendix B: Suggested Adoption Order

### Priority 1: Immediate (PROVEN, high ROI)

1. **Progressive disclosure** for skills and context — 97% token reduction
2. **Pre-completion verification** — Eliminates false completion claims
3. **Tiered model selection** — 60-80% cost savings
4. **Permission model** (deny-by-default) — Prevents security incidents
5. **CLAUDE.md optimization** — <2K tokens, document "why" not "what"

### Priority 2: Quick Wins (PROVEN, moderate effort)

1. **Prompt caching** — 90% cost reduction for repeated content
2. **CI/CD quality gates** — DeepEval integration, coverage enforcement
3. **Pre-commit hooks** — Stub detection, secret scanning
4. **Spec-driven workflow** — Requirements before implementation
5. **Agent token budgets** — <3K for frequent-use agents

### Priority 3: Integration (PROVEN, requires infrastructure)

1. **MCP server integration** — Standardized tool access
2. **Automated anti-pattern detection** — AST validation in CI/CD
3. **HITL gate automation** — Tier-based approval workflows
4. **Cross-service duplicate detection** — Architecture-aware scanning
5. **Audit trail and observability** — Track all agent actions

### Priority 4: Experimental (EMERGING, validate first)

1. **Graph-based memory** — Cross-session context persistence
2. **DeepEval hallucination detection** — Automated catch rate measurement
3. **Dual-LLM verification** — Cross-validation for critical operations
4. **Dynamic model routing** — Complexity-based model selection
5. **Real-time quality dashboard** — Visibility drives better decisions

---

## Appendix C: Research References

### Academic Papers (2024-2026)

1. Khati et al. (2026) — "Detecting and Correcting Hallucinations in LLM-Generated Code via Deterministic AST Analysis" — arXiv:2601.19106
2. Liu et al. (2026) — "Beyond Functional Correctness: Exploring Hallucinations in LLM-Generated Code" — arXiv:2404.00971v3
3. Zhang et al. (2025) — "Use Property-Based Testing to Bridge LLM Code Generation and Validation" — arXiv:2506.18315
4. Lin et al. (2025) — "Learning to Solve and Verify: A Self-Play Framework for Code and Test Generation" — arXiv:2502.14948
5. Shelmanov et al. (2025) — "A Head to Predict and a Head to Question: Pre-trained Uncertainty Quantification Heads" — arXiv:2505.08200
6. Mathews & Nagappan (2024) — "Test-Driven Development for Code Generation" — arXiv:2402.13521
7. arXiv:2512.04388 (Dec 2025) — "Learning to Orchestrate Agents with the Conductor"
8. arXiv:2511.15755 (Nov 2025) — "Multi-Agent LLM Orchestration for Deterministic Decision Support"
9. arXiv:2511.17006 (Nov 2025) — "Budget-Aware Tool-Use Enables Effective Agent Scaling"
10. arXiv:2507.09329 (2025) — "Systematic Analysis of Insecure Behaviors in LLM Coding Agents"

### Industry Reports & Documentation

11. Anthropic — "How we built our multi-agent research system" (June 2025)
12. Anthropic — "2026 Agentic Coding Trends Report"
13. Google — "Agent2Agent Protocol (A2A)" (April 2025)
14. Google — "Developer's guide to multi-agent patterns in ADK" (Dec 2025)
15. Microsoft — Azure AI Agent Design Patterns (July 2025)
16. OWASP — "Top 10 for Agentic Applications for 2026" (Dec 2025)
17. OWASP — LLM Top 10: LLM06:2025 Excessive Agency
18. Spotify Engineering — "Background Coding Agents: Predictable Results Through Strong Feedback Loops" (Dec 2025)
19. Thoughtworks — "Spec-driven development: Unpacking 2025's new practices"
20. GitHub — "Spec-driven development with AI" (2025)
21. Google DORA 2025 Report — AI adoption impact metrics
22. Veracode 2025 Report — AI-generated code vulnerability rates
23. Composio — "Why AI Agent Pilots Fail in Production" (2025)

### Tools & Frameworks

24. Claude Context MCP — github.com/zilliztech/claude-context
25. DeepEval — LLM evaluation framework (14+ metrics)
26. RAGAS — RAG-specific evaluation metrics
27. Model Context Protocol — modelcontextprotocol.io
28. LangGraph / CrewAI / AutoGen — Multi-agent frameworks
29. NeMo Guardrails — NVIDIA open-source guardrails

### Practitioner Sources

30. ClaudeLog — "Tactical Model Selection" (Jan 2026)
31. paddo.dev — "Claude Code Hooks: Guardrails That Actually Work" (2026)
32. williamzujkowski — "From 150K to 2K Tokens: Progressive Context Loading"
33. Kili Technology — "HITL, HOTL, and LLM-as-a-Judge" (Feb 2026)
34. Encord — "The Ultimate Human-in-the-Loop Guide for 2026"
35. Temporal — "HITL for AI Agents: Patterns and Best Practices"
36. "The Architecture of Scale: Sub-Agents" (Feb 2026)
37. Sec-Context — AI Code Security Anti-Patterns (150+ sources)
38. Agentic Coding Handbook — "Test-Driven Development" (tweag.io)

---

## Appendix D: Glossary

**A2A (Agent-to-Agent)** — Google's protocol for cross-framework agent communication.

**AST (Abstract Syntax Tree)** — Tree representation of source code structure, used for deterministic hallucination detection.

**Context Rot** — Measurable quality degradation as context window fills, even within technical limits.

**CoVe (Chain-of-Verification)** — Multi-step validation: generate → verify → refine.

**Hallucination** — LLM generating plausible but incorrect information (e.g., non-existent APIs).

**HITL (Human-in-the-Loop)** — Humans approve or correct AI outputs before they take effect.

**HOTL (Human-on-the-Loop)** — Humans supervise automated systems and intervene when needed.

**MCP (Model Context Protocol)** — Open standard for connecting AI models to external tools and data.

**Orchestrator-Worker** — Pattern where a lead agent delegates tasks to specialized workers.

**PBT (Property-Based Testing)** — Testing by validating high-level properties rather than specific input-output pairs.

**Progressive Disclosure** — Loading information on-demand rather than upfront; the defining context pattern of 2026.

**RAG (Retrieval-Augmented Generation)** — Enhancing LLM with verified external knowledge retrieval.

**SDD (Specification-Driven Development)** — Treat specs as source of truth, code as generated artifact.

**Tiered Models** — Using different model tiers (Opus/Sonnet/Haiku) based on task complexity.

---

## Version History

### Version 2.0.0 (2026-02-13) — Complete Rewrite

**Changes from v1.0.0:**
- Restructured as pattern catalog (was project-specific audit)
- Updated all research to 2025-2026 sources (38 references)
- Added current model references (Opus 4.6, Sonnet 4.5, Haiku 4.5)
- Expanded anti-patterns from 6 to 11 with industry data
- Added OWASP Top 10 for Agentic Applications (2026)
- Added progressive disclosure, prompt caching, MCP ecosystem sections
- Replaced phased roadmap with suggested adoption order
- Added arkhe-claude-plugins implementation appendix
- Added real-world incidents (API key leak, home dir deletion, DB wipe)

### Version 1.0.0 (2025-10-19) — Initial Release

Original project-specific audit covering multi-agent architecture, context management, HITL frameworks, quality assurance, specification-driven development, and anti-patterns.

---

**Next Review:** 2026-05-13 (Quarterly)
**Research Methodology:** Synthesized from 38 sources across academic papers, industry reports, production case studies, and official documentation.
