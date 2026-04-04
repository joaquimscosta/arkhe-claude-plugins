---
title: "Superpowers Agentic Patterns: Quick Reference"
version: "1.0.0"
status: Published
created: 2026-04-02
last_updated: 2026-04-02
---

# Superpowers Agentic Patterns: Quick Reference

> How the Superpowers plugin specializes generic multi-agent patterns into a battle-tested skill-driven development workflow.

## Executive Summary

This document catalogs 17 agentic patterns extracted from the 14 skills in the Superpowers Claude Code plugin project, organized into five categories: workflow orchestration (sequential chaining, hard gates, execution mode selection), subagent coordination (fresh subagents, two-stage review, status codes, model selection, parallel dispatch), quality and discipline enforcement (evidence-based verification, TDD iron law, systematic root cause investigation, rationalization prevention, code review reception), human-in-the-loop and context management (incremental design validation, worktree isolation), and meta-patterns (skill-as-TDD, Claude Search Optimization). Of the 17 patterns, 13 specialize generic multi-agent orchestration patterns documented in the companion overview, while 4 are novel patterns unique to LLM agent behavior shaping. This document serves as a quick-reference companion to the deep-dive analysis; for detailed implementations, pressure-test transcripts, and cross-pattern interaction diagrams, see the companion deep-dive document.

---

## Workflow Orchestration

### Sequential Skill Chaining

Skills define a terminal state that invokes the next skill, creating a strict linear pipeline. Brainstorming produces a design spec and invokes writing-plans. Writing-plans produces an implementation plan and offers execution mode selection. Execution completes and invokes finishing-branch. Each skill only knows its successor, not the full chain.

**Specializes**: [Pipeline](multi-agent-patterns-overview.md#pipeline). **Source skill**: brainstorming, writing-plans, subagent-driven-development, finishing-a-development-branch.
**When to use**: Multi-phase development workflows where each phase has distinct concerns and outputs that feed the next phase. **Analogy**: A relay race where each runner passes the baton to the next — no runner knows the full race strategy, only their leg and the handoff.

### Hard Gate Enforcement

Markup tags (`<HARD-GATE>`, `<EXTREMELY-IMPORTANT>`) embedded in skill text prevent the agent from advancing to the next phase without meeting explicit conditions. Unlike automated quality gates that run tests, hard gates are cognitive constraints that shape the agent's decision-making through explicit prohibitions and required approvals.

**Specializes**: [Backpressure (Quality Gates)](multi-agent-patterns-overview.md#backpressure-quality-gates). **Source skill**: brainstorming, using-superpowers.
**When to use**: Phase transitions where premature advancement would undermine quality — design approval before planning, plan approval before implementation. **Analogy**: A construction permit — you cannot begin building until the inspector signs off on the blueprints, regardless of how ready you feel.

### Execution Mode Selection

After planning is complete, the workflow pauses to let the user choose between two execution strategies: subagent-driven development (fresh subagent per task with two-stage review) or inline execution (tasks executed sequentially in the current session). This decision point prevents the system from assuming a one-size-fits-all execution approach.

**Specializes**: [Human-in-the-Loop](multi-agent-patterns-overview.md#human-in-the-loop). **Source skill**: writing-plans.
**When to use**: When execution strategy should be tailored to the task — parallel subagents for independent tasks, inline for tightly coupled work. **Analogy**: A general choosing between deploying multiple specialist squads simultaneously or advancing a single combined force — the terrain determines the tactic.

---

## Subagent Coordination

### Fresh Subagent Per Task

Each task is dispatched to a brand-new subagent with zero session history. The controller pastes the full task text directly into the subagent's prompt rather than referencing files, ensuring the subagent has exactly the context it needs and nothing more. No accumulated context, no previous task results, no drift.

**Specializes**: [Fresh Context per Iteration](multi-agent-patterns-overview.md#fresh-context-per-iteration). **Source skill**: subagent-driven-development.
**When to use**: Multi-task execution where context pollution between tasks would cause drift, hallucinated state, or compounding errors. **Analogy**: A hospital shift change — the incoming doctor reads the chart from scratch rather than relying on verbal handoff, preventing telephone-game degradation.

### Two-Stage Review Gate

After a subagent completes implementation, two specialized reviewers are dispatched in strict sequence. First, a spec-compliance reviewer verifies the code matches requirements — no missing features, no extras, no misinterpretations. Only after spec compliance passes does a code-quality reviewer assess architecture, patterns, and maintainability. The spec reviewer must independently inspect code, never trusting the implementer's self-report.

**Specializes**: [Critic-Actor](multi-agent-patterns-overview.md#critic-actor) + [Pipeline](multi-agent-patterns-overview.md#pipeline). **Source skill**: subagent-driven-development.
**When to use**: Quality-critical work where both "built the right thing" and "built the thing right" need independent verification. **Analogy**: A building inspection with two passes — first the inspector verifies the structure matches the blueprints (spec), then a separate inspector checks construction quality (code quality).

### Status Codes with Escalation

Subagents report completion using one of four structured status codes — DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED — each triggering a different controller response. This replaces free-form status reporting with a protocol that includes an explicit escalation path: "It is always OK to stop and say 'this is too hard for me.' Bad work is worse than no work."

**Specializes**: [Event-Driven Routing](multi-agent-patterns-overview.md#event-driven-routing). **Source skill**: subagent-driven-development.
**When to use**: Any controller-worker pattern where the controller needs to take different actions based on completion quality, not just completion itself. **Analogy**: A military radio protocol with standardized status codes — "mission complete", "complete with casualties", "requesting reinforcements", "pinned down" — each triggering a different command response.

### Model Selection by Complexity

Rather than using the most capable (and expensive) model for every task, the controller selects the least powerful model capable of handling each role. Mechanical single-file tasks get a cheap/fast model. Integration tasks across multiple files get a standard model. Architecture, design, and review tasks get the most capable model. This conserves cost and increases throughput.

*Novel pattern* — no generic counterpart. **Source skill**: subagent-driven-development.
**When to use**: Multi-model environments where tasks have varying complexity and the cost/speed tradeoff matters. **Analogy**: A hospital triage system — a nurse handles the bandage, a general practitioner handles the diagnosis, and the surgeon handles the operation. You don't send the surgeon for every patient.

### Parallel Agent Dispatch

When facing 3+ independent failures or tasks with no shared state, dispatch one agent per problem domain to work concurrently. Each agent gets isolated context, a focused problem scope, and specific output expectations. Results are reviewed when all agents complete, and changes are integrated with a full test suite run.

**Specializes**: [Parallel Execution](multi-agent-patterns-overview.md#parallel-execution). **Source skill**: dispatching-parallel-agents.
**When to use**: Independent failures across different subsystems, parallel feature work, or research branches where agents won't interfere with each other. **Analogy**: A kitchen during dinner service — multiple chefs prepare different dishes simultaneously while the expeditor coordinates plating and ensures nothing conflicts.

---

## Quality & Discipline Enforcement

### Evidence-Based Verification Gate

The iron law: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE." Before claiming any work is done, the agent must identify what command proves it, run the full command fresh, read the complete output, check the exit code, and only then make the claim. Red flags that trigger the gate: "should work now", "probably fixed", "seems to pass". A rationalization prevention table maps common excuses to reality checks.

**Specializes**: [Confidence-Gated Completion](multi-agent-patterns-overview.md#confidence-gated-completion). **Source skill**: verification-before-completion.
**When to use**: Any completion claim — tests pass, bug fixed, feature complete, PR ready. Every assertion must have evidence. **Analogy**: A courtroom standard of proof — "I believe the defendant is innocent" is not a verdict; only evidence-backed findings are accepted.

### TDD Iron Law

"NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST." The strict RED-GREEN-REFACTOR cycle: write a failing test, verify it fails for the right reason, write minimal code to pass, verify all tests pass, refactor while keeping green. Code written before a test? Delete it — no keeping as reference, no adapting while writing tests. "Violating the letter of the rules is violating the spirit of the rules."

**Specializes**: [Specification-First](multi-agent-patterns-overview.md#specification-first) + [Backpressure (Quality Gates)](multi-agent-patterns-overview.md#backpressure-quality-gates). **Source skill**: test-driven-development.
**When to use**: All feature implementation and bug fixes. Tests are behavior-level specifications that verify "what should this do?" rather than "what does this do?" **Analogy**: An architect who must draw each room's blueprint and get it approved before any wall goes up — discovering design flaws during construction is orders of magnitude more expensive.

### Systematic Root Cause Investigation

"NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST." A mandatory 4-phase process: (1) investigate — read errors, reproduce, check recent changes, trace data flow backward; (2) analyze patterns — find working examples, compare differences; (3) hypothesize — form a single hypothesis, test one variable at a time; (4) verify — confirm fix, test for regressions. If 3+ fixes fail, stop and question the architecture.

**Specializes**: [Scientific Method](multi-agent-patterns-overview.md#scientific-method). **Source skill**: systematic-debugging.
**When to use**: Any bug, test failure, or unexpected behavior. Prevents the "random walk" debugging approach of trying changes without reasoning. **Analogy**: A doctor's diagnostic process — symptoms, hypothesis, targeted test, diagnosis, treatment. No doctor prescribes medicine without first understanding the disease.

### Rationalization Prevention

Every discipline-enforcing skill includes explicit tables mapping agent excuses to reality checks. "Too simple to test" maps to "Simple code breaks. Test takes 30 seconds." "I already manually tested it" maps to "Ad-hoc testing is not systematic. No record, can't re-run." These tables are paired with red flags lists and the meta-rule: "Violating the letter of the rules is violating the spirit of the rules." This cross-cutting technique appears in verification, TDD, debugging, and skill-writing skills.

*Novel pattern* — no generic counterpart. Unique to LLM agent behavior shaping. **Source skill**: verification-before-completion, test-driven-development, systematic-debugging, writing-skills.
**When to use**: Any skill that enforces process discipline. LLM agents are skilled rationalizers — explicit excuse-to-reality mappings prevent the most common bypass attempts. **Analogy**: A checklist of known self-deceptions posted on the cockpit wall — pilots are trained to recognize their own cognitive biases before they lead to errors.

### Code Review Reception Protocol

When receiving code review feedback, never respond with performative agreement ("You're absolutely right!", "Great point!"). Instead, follow a 6-step protocol: READ the complete feedback without reacting, UNDERSTAND by restating in own words, VERIFY against the codebase reality, EVALUATE technical soundness for this specific codebase, RESPOND with technical acknowledgment or reasoned pushback, IMPLEMENT one item at a time with testing. For unclear feedback, stop before implementing anything and ask for clarification.

**Specializes**: [Critic-Actor](multi-agent-patterns-overview.md#critic-actor) (receiving side). **Source skill**: receiving-code-review.
**When to use**: Receiving any code review feedback — from humans, automated reviewers, or other agents. Technical rigor trumps social performance. **Analogy**: A scientist receiving peer review — they don't say "great point!" and blindly change everything. They evaluate each critique against their data and methodology, accepting valid criticism and defending sound decisions.

---

## Human-in-the-Loop & Context Management

### Incremental Design Validation

Rather than presenting a complete design for approval, the brainstorming skill presents design decisions in sections sized to complexity. After each section, the user approves or requests changes before the next section is presented. The written spec undergoes inline self-review, then the user reviews the full spec before any implementation begins. This prevents massive rework from late-stage design disagreements.

**Specializes**: [Human-in-the-Loop](multi-agent-patterns-overview.md#human-in-the-loop). **Source skill**: brainstorming.
**When to use**: Design phases where misalignment compounds — getting early approval on fundamentals prevents expensive pivots after detailed design is complete. **Analogy**: An architect presenting floor plans room by room — getting sign-off on the kitchen layout before designing the plumbing prevents tearing out pipes when the client wants the sink moved.

### Worktree Isolation

Git worktrees provide isolated workspaces sharing the same repository, allowing parallel development on multiple branches. The skill includes smart directory selection (check .worktrees/ then worktrees/ then CLAUDE.md preference then ask user), safety verification (ensure directory is git-ignored before creating), and automatic setup (detect dependencies, install, run baseline tests). This provides the infrastructure layer for parallel agent dispatch and subagent-driven development.

**Specializes**: [Parallel Execution](multi-agent-patterns-overview.md#parallel-execution) (infrastructure). **Source skill**: using-git-worktrees.
**When to use**: Feature work needing isolation from the current workspace, parallel development branches, or subagent-driven tasks that modify files. **Analogy**: A laboratory with multiple isolated clean rooms — each experiment runs in its own controlled environment, sharing the building's infrastructure but never contaminating each other.

---

## Meta-Patterns

### Skill-as-TDD

Writing skills IS Test-Driven Development applied to behavior shaping. RED: run a pressure scenario without the skill and observe the agent failing — document exact rationalizations used. GREEN: write a skill that addresses those specific failures with explicit rationalization counters. REFACTOR: run again, find new rationalizations the agent invents, close the loopholes, re-verify. The skill document is the "production code" and the pressure scenario is the "test case."

*Novel pattern* — no generic counterpart. Unique insight: treating documentation as code subject to TDD. **Source skill**: writing-skills.
**When to use**: Creating any new skill that enforces process discipline. Without testing against realistic pressure scenarios, skills will have gaps that agents exploit. **Analogy**: Penetration testing for policies — you don't just write a security policy, you hire someone to try to circumvent it, then strengthen the policy based on what they found.

### Claude Search Optimization (CSO)

The skill description field must ONLY describe triggering conditions ("Use when..."), never summarize the skill's workflow. Critical finding from testing: when a description summarizes the workflow, Claude may follow the description summary instead of reading the full skill content — leading to incomplete or incorrect execution. This is the LLM equivalent of SEO: optimize for discovery, not for content delivery.

*Novel pattern* — no generic counterpart. LLM-specific discovery optimization. **Source skill**: writing-skills.
**When to use**: Writing the `description` field for any skill. The description is a search query matcher, not a documentation summary. **Analogy**: A book's spine label vs. its contents — the spine says "Organic Chemistry" (triggering condition) not "covers bonding, reactions, and nomenclature in 12 chapters" (workflow summary). The spine helps you find the book; you read the book for the content.

---

## Pattern Composition

These patterns compose into common Superpowers workflows:

| Combination | Patterns | Example Workflow |
|-------------|----------|------------------|
| Full Feature Development | Sequential Chaining + Hard Gate + TDD Iron Law + Two-Stage Review + Evidence Verification | Design spec -> plan -> implement with TDD -> spec review -> quality review -> verify -> finish branch |
| Bug Investigation | Systematic Root Cause + TDD Iron Law + Evidence Verification | Investigate -> hypothesize -> write failing test -> fix -> verify |
| Parallel Problem Solving | Parallel Agent Dispatch + Fresh Subagent + Worktree Isolation | Identify independent domains -> dispatch isolated agents -> integrate |
| Skill Development | Skill-as-TDD + CSO + Rationalization Prevention | Observe failures -> write skill -> test -> close loopholes |

---

## Mapping to Generic Patterns

| # | Superpowers Pattern | Generic Counterpart | Key Specialization |
|---|---------------------|---------------------|--------------------|
| 1 | Sequential Skill Chaining | Pipeline | Skills as pipeline stages with implicit successor-only coupling |
| 2 | Hard Gate Enforcement | Backpressure (Quality Gates) | Cognitive constraints via markup tags, not automated tests |
| 3 | Execution Mode Selection | Human-in-the-Loop | User chooses execution strategy, not just approves output |
| 4 | Fresh Subagent Per Task | Fresh Context per Iteration | Full task text pasted into prompt, zero shared session state |
| 5 | Two-Stage Review Gate | Critic-Actor + Pipeline | Spec compliance before code quality, never trust self-report |
| 6 | Status Codes with Escalation | Event-Driven Routing | Four structured codes with explicit "too hard for me" path |
| 7 | Model Selection by Complexity | *Novel* | Cost/capability matching per task role |
| 8 | Parallel Agent Dispatch | Parallel Execution | Agent-per-domain with isolated context and focused scope |
| 9 | Evidence-Based Verification Gate | Confidence-Gated Completion | Fresh command output required, red flags list for claims |
| 10 | TDD Iron Law | Specification-First + Backpressure | Delete-if-written-first rule, no exceptions |
| 11 | Systematic Root Cause Investigation | Scientific Method | 4-phase mandatory process with 3-failure circuit breaker |
| 12 | Rationalization Prevention | *Novel* | Excuse-to-reality mapping tables for LLM self-deception |
| 13 | Code Review Reception Protocol | Critic-Actor (receiving side) | 6-step protocol replacing performative agreement |
| 14 | Incremental Design Validation | Human-in-the-Loop | Section-by-section approval sized to complexity |
| 15 | Worktree Isolation | Parallel Execution (infrastructure) | Smart directory selection, safety verification, auto-setup |
| 16 | Skill-as-TDD | *Novel* | Documentation as code subject to RED-GREEN-REFACTOR |
| 17 | Claude Search Optimization (CSO) | *Novel* | Description-as-trigger-matcher, not content summary |

---

## Choosing a Pattern

| If you need... | Start with... |
|----------------|---------------|
| Multi-phase development workflow | Sequential Skill Chaining |
| Prevent premature phase advancement | Hard Gate Enforcement |
| User-selected execution strategy | Execution Mode Selection |
| Context-clean task execution | Fresh Subagent Per Task |
| Independent spec and quality review | Two-Stage Review Gate |
| Structured completion reporting | Status Codes with Escalation |
| Cost-optimized multi-model dispatch | Model Selection by Complexity |
| Concurrent independent work | Parallel Agent Dispatch |
| Verified completion claims | Evidence-Based Verification Gate |
| Test-first implementation discipline | TDD Iron Law |
| Methodical debugging | Systematic Root Cause Investigation |
| Counter agent self-deception | Rationalization Prevention |
| Rigorous feedback processing | Code Review Reception Protocol |
| Early design alignment | Incremental Design Validation |
| Isolated parallel workspaces | Worktree Isolation |
| Battle-tested skill authoring | Skill-as-TDD |
| Effective skill discovery | Claude Search Optimization (CSO) |

## References

- **Superpowers Agentic Patterns: Deep Dive** -- Companion document with full analysis, pressure-test transcripts, and cross-pattern interaction diagrams. See `docs/research/superpowers-patterns-deep-dive.md`
- **Multi-Agent Orchestration Patterns: Quick Reference** -- Generic pattern catalog that this document specializes. See `docs/research/multi-agent-patterns-overview.md`
- **Multi-Agent Orchestration Patterns: Deep Dive** -- Detailed generic pattern implementations with Mermaid diagrams and YAML configurations. See `docs/research/multi-agent-patterns-deep-dive.md`
- **Superpowers Project** -- Source plugin from which these patterns were extracted. See `external-repos/superpowers/`
