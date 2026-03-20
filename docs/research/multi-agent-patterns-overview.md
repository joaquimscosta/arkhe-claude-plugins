---
title: "Multi-Agent Orchestration Patterns: Quick Reference"
version: "1.0.0"
status: Published
created: 2026-03-19
last_updated: 2026-03-19
---

# Multi-Agent Orchestration Patterns: Quick Reference

> Reusable patterns for any multi-agent system — skills, agents, workflows, or autonomous loops.

---

## Core Architectural Concepts

### Specialized Roles (Hats)

Assign each agent a focused role with clear boundaries: what it does, what triggers it, and what it produces. A hat is not an agent — it is a *persona* an agent wears for one phase of work. By constraining each role to a single concern, you get predictable behavior and composable workflows.

**When to use**: Any workflow involving more than one concern (e.g., building vs. reviewing, proposing vs. critiquing). **Analogy**: A surgical team where the surgeon, anesthesiologist, and nurse each have distinct responsibilities — no one tries to do everything.

### Event-Driven Routing

Agents communicate through events, not direct calls. Each role declares which events *trigger* it and which events it *publishes*. The orchestrator routes events to the appropriate role. This decouples agents from each other — they only know about events, not about who handles them.

**When to use**: Multi-step workflows where agents need to hand off work without knowing the next step. **Analogy**: A relay race — each runner passes the baton without knowing the full race strategy.

### Completion Promise

A predefined output signal (e.g., `LOOP_COMPLETE`) that tells the orchestration system the work is done. Without an explicit completion signal, autonomous loops have no reliable way to know when to stop. The promise is the contract between the agent and the system.

**When to use**: Any autonomous loop or multi-iteration workflow that needs a termination condition. **Analogy**: A pilot announcing "final approach" — the control tower knows the landing sequence is complete.

### Backpressure (Quality Gates)

Instead of prescribing *how* agents should work, define gates that *reject bad output*. Tests, linters, type checks, and build steps act as automated quality gates. If the gate fails, the work bounces back. This lets agents be creative while maintaining quality standards.

**When to use**: When you want quality enforcement without micromanaging the agent's approach. **Analogy**: A bouncer at a club — doesn't tell you how to dress, just won't let you in if standards aren't met.

---

## Multi-Agent Coordination Patterns

### Pipeline

Linear flow where Agent A's output feeds Agent B, which feeds Agent C. Each stage has a single concern. The simplest multi-agent pattern and the one to reach for first.

**When to use**: Sequential workflows with clear stages (spec -> implement -> verify, draft -> review -> publish). **Analogy**: An assembly line — each station adds value before passing the product forward.

### Critic-Actor

One agent proposes work, another agent critiques it. The critic is rewarded for finding problems, not for approving. This separation prevents the "builder bias" where the creator of work is too invested to find its flaws.

**When to use**: Quality-critical work where self-review is insufficient (code review, RFC evaluation, design decisions). **Analogy**: A writer and an editor — the editor's job is to improve the manuscript, not to praise it.

### Adversarial Review

A stronger form of Critic-Actor where the reviewing agent actively *tries to break* the work. Red team vs. blue team. The attacker explores edge cases, security vulnerabilities, and failure modes that the builder might not consider.

**When to use**: Security-critical code, robustness testing, stress-testing designs before committing. **Analogy**: A penetration tester hired to break into your own building to find security gaps.

### Supervisor-Worker

A coordinator agent decomposes complex tasks and delegates subtasks to specialist agents. The supervisor manages scope, priority, and integration while workers focus on execution.

**When to use**: Complex tasks that require decomposition into independent subtasks. **Analogy**: A general contractor who hires electricians, plumbers, and painters for a renovation.

### Rotating Roles

Multiple agents take turns examining the same work from different perspectives. Each brings a unique lens — architecture, testing, usability, performance — preventing tunnel vision.

**When to use**: When you need breadth of perspective on a single artifact (design reviews, mob programming, architecture decisions). **Analogy**: A panel of judges scoring a performance — each evaluates different criteria.

### Scientific Method

A hypothesis-driven investigation pattern: observe symptoms, form a hypothesis, design an experiment, test it, and either confirm or reject. Prevents the "random walk" debugging approach where changes are tried without reasoning.

**When to use**: Debugging mysterious bugs, investigating performance issues, root cause analysis. **Analogy**: A doctor diagnosing a patient — symptoms, hypothesis, test, diagnosis, treatment.

---

## Quality & Confidence Patterns

### Confidence-Gated Completion

Work is not considered "done" until a self-audit reports a confidence score above a threshold (e.g., 80/100). This prevents premature completion where the agent declares success without adequate verification.

**When to use**: Any workflow where "done" needs verification — feature implementation, migration, refactoring. **Analogy**: A pilot's pre-flight checklist — you don't take off until every item checks out.

### Confession Pattern

After completing work, the builder records an honest internal monologue — shortcuts taken, assumptions made, uncertainties remaining. A separate auditor agent reads these confessions and decides whether the work is trustworthy. The builder is rewarded for honesty, not for looking good.

**When to use**: Post-implementation review, self-critique before handoff, building trust in autonomous systems. **Analogy**: A Catholic confession — the act of admitting weaknesses leads to resolution and trust.

### Specification-First

Write a precise, testable specification *before* any implementation. A separate agent reviews the spec for completeness. Implementation follows the spec literally. Verification checks the implementation against the spec.

**When to use**: Features with complex requirements, API design, any work where ambiguity is expensive. **Analogy**: An architect drawing blueprints before construction begins — build to spec, not to imagination.

### Documentation-First

Write the user-facing documentation *before* writing any code. If you can't explain what something does clearly, you don't understand it well enough to build it. The docs become the spec.

**When to use**: Libraries, APIs, developer tools — anything where the user experience matters as much as the implementation. **Analogy**: Writing the README before the code — if the usage examples don't make sense, the design needs work.

---

## State & Persistence Patterns

### Persistent Memory

Agents record learnings, decisions, and context as persistent memories that survive across iterations and sessions. Memories are typed (decisions, context, blockers) and searchable, allowing future agents to benefit from past work.

**When to use**: Long-running workflows, multi-session projects, any system where agents need to learn from previous iterations. **Analogy**: A team wiki — knowledge captured by one person is available to everyone later.

### Task Tracking

Work is broken into discrete, structured tasks with explicit status (pending, in-progress, completed, blocked). Tasks serve as the handoff mechanism between iterations — the next agent picks up where the last one left off.

**When to use**: Multi-step implementations, project management within autonomous loops, any work that spans multiple iterations. **Analogy**: A kanban board — each card moves through stages, and anyone can see what's done and what's next.

### Fresh Context per Iteration

Each iteration starts with a clean slate — the agent re-reads specs, plans, and code from disk rather than relying on accumulated context. This prevents context drift, hallucinated state, and compounding errors across iterations.

**When to use**: Autonomous loops, long-running agents, any system where context reliability matters more than speed. **Analogy**: A shift change at a hospital — the incoming doctor reads the chart from scratch rather than relying on verbal handoff alone.

---

## Scaling & Integration Patterns

### Human-in-the-Loop

Agents can pause execution to ask humans for feedback, decisions, or approvals. The human response is injected back into the event stream. Proactive human guidance can also be sent without the agent asking.

**When to use**: Approval gates, subjective decisions, design reviews, any point where human judgment adds value. **Analogy**: A self-driving car that pulls over and asks the passenger which route to take at an ambiguous junction.

### Parallel Execution

Multiple agents or loops work simultaneously on independent subtasks. Each runs in isolation (e.g., separate git worktrees), and results are merged when complete. A coordination layer manages merge ordering and conflict resolution.

**When to use**: Independent subtasks that don't conflict, research branches, parallel feature development. **Analogy**: A kitchen during dinner service — multiple chefs prepare different dishes simultaneously, and the expeditor coordinates plating.

---

## Pattern Composition

These patterns compose naturally. Common combinations:

| Combination | Example |
|-------------|---------|
| Pipeline + Critic-Actor | Spec -> Implement -> Review -> Fix -> Verify |
| Confession + Confidence Gate | Builder records shortcuts, auditor scores confidence, gate blocks premature completion |
| Fresh Context + Persistent Memory | Each iteration starts clean but reads memories from disk |
| Pipeline + Human-in-the-Loop | Automated stages with human approval gates between phases |
| Adversarial Review + Scientific Method | Red team finds vulnerabilities, then systematically verifies each one |

---

## Choosing a Pattern

| If you need... | Start with... |
|----------------|---------------|
| Sequential workflow | Pipeline |
| Quality assurance | Critic-Actor |
| Security validation | Adversarial Review |
| Task decomposition | Supervisor-Worker |
| Multiple perspectives | Rotating Roles |
| Systematic debugging | Scientific Method |
| Verified completion | Confidence-Gated Completion |
| Honest self-assessment | Confession Pattern |
| Requirements clarity | Specification-First |
| User experience clarity | Documentation-First |
| Cross-session learning | Persistent Memory |
| Multi-step execution | Task Tracking |
| Context reliability | Fresh Context per Iteration |
| Human judgment | Human-in-the-Loop |
| Independent work streams | Parallel Execution |
