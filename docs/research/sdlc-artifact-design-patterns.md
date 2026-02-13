# AI-Ready SDLC Design Patterns

**Version:** 2.0.0
**Status:** Living Document
**Purpose:** Design patterns for structuring SDLC artifacts that AI coding assistants can navigate efficiently

---

## Quick Reference

### Artifact Types at a Glance

| Artifact | Created | Contains | Primary Consumer |
|----------|---------|----------|-----------------|
| **Spec** | Phase 1 (Requirements) | Functional requirements (FR-XXX), acceptance criteria, constraints | Architecture, implementation, verification |
| **Plan** | Phase 2 (Architecture) | Technical design, key files, implementation phases, decision rationale | Task breakdown, implementation, verification |
| **Tasks** | Phase 3 (Workstreams) | Task breakdown (T-XX), wave grouping, dependencies, effort estimates | Implementation, resume, verification |
| **Reuse Matrix** | Phase 0 (Discovery) | REUSE/ENHANCE/CREATE classification of existing components | Architecture design |
| **ADR** | Phase 2 (Architecture) | Architecture decisions, alternatives considered, consequences | Implementation, verification |
| **API Contract** | Phase 2 (Architecture) | Endpoint definitions, request/response shapes, versioning | Implementation, verification |
| **Data Models** | Phase 2 (Architecture) | Entity definitions, schemas, migrations, relationships | Implementation, verification |
| **Wave Context** | Phase 4 (Implementation) | Per-wave completion state, files changed, next-wave lookahead | Session resume |
| **Verification Report** | Post-implementation | Architecture alignment scores, requirement coverage, evidence log | Quality assurance |

### Information Lookup Matrix

| I need to... | Search in | Look for |
|--------------|-----------|----------|
| Understand business requirement | Spec | `FR-XXX` identifiers |
| Understand constraints | Spec | Constraints section (performance, security, compatibility) |
| Find the chosen architecture | Plan | Architecture section, decision rationale |
| See what files to create/modify | Plan | Key Files table |
| Find an architecture decision | ADRs | Decision title, technology keywords |
| Find reusable components | Reuse Matrix | REUSE/ENHANCE/CREATE categories |
| Understand a data entity | Data Models | Entity name, table name |
| See API endpoints | API Contract | HTTP method + path |
| Find my next task | Tasks | Status: SELECTED, current wave |
| Check task dependencies | Tasks | Dependencies field per task |
| Resume interrupted work | Wave Context | Latest `wave-{N}-context` file |
| Validate implementation | Verification Report | Scores, evidence log, flagged items |

### Core Retrieval Pattern

```
1. content_search(pattern, scope)   # Find relevant sections
2. read_file(path, section)         # Load only what you need
3. validate_understanding()         # Can you proceed?
4. repeat if gaps remain            # Iterate as needed
```

---

## 1. Introduction

### Why SDLC Artifacts Need to Be AI-Consumable

AI coding assistants operate under a fundamental constraint: **context windows are finite and expensive**. A well-structured SDLC pipeline might produce 50,000+ tokens of documentation per feature. Loading all of it before writing a single line of code wastes 80% of the available context window.

The solution is designing artifacts that support **progressive disclosure** — structured so that AI agents (or human developers) can find exactly what they need without reading everything.

### The Progressive Disclosure Principle

Organize information in tiers of increasing detail:

| Tier | Purpose | Token Budget | Example |
|------|---------|-------------|---------|
| **Metadata** | Routing and discovery | ~100 tokens | Artifact type, ID, status, cross-references |
| **Summary** | Decision-making | ~500 tokens | Overview section, key decisions, dependencies |
| **Detail** | Implementation | ~2,000 tokens | Full specification, acceptance criteria, technical notes |
| **Context** | Edge cases and history | Unlimited | ADRs, edge cases, migration strategies |

A well-designed SDLC pipeline allows an agent to route to the right artifact with ~100 tokens, understand the scope with ~500, and implement with ~2,000 — rather than consuming 50,000 tokens upfront.

### Token Economics

Search-first retrieval patterns reduce token consumption by 60-98% compared to bulk-loading:

| Approach | Tokens Consumed | Effective Information |
|----------|----------------|---------------------|
| Load all artifacts | ~50,000 | ~2,000 (4% relevant) |
| Search-first, load on demand | ~2,000-5,000 | ~2,000 (40-100% relevant) |

The difference compounds across tasks. A 10-task feature saves 450,000+ tokens by using targeted retrieval.

---

## 2. Artifact Architecture

### Phase-to-Artifact Mapping

A structured SDLC pipeline produces artifacts across distinct phases. Each phase answers a different question:

```
Phase 0: Discovery       → "What exists already?"      → Reuse Matrix
Phase 1: Requirements    → "What should we build?"     → Spec
Phase 2: Architecture    → "How should we build it?"   → Plan, ADRs, API Contract, Data Models
Phase 3: Workstreams     → "In what order?"            → Tasks (with waves and dependencies)
Phase 4: Implementation  → "Build and verify"          → Wave Context (per session)
Phase 5: Summary         → "Is it complete?"           → Updated Spec + Tasks (status sync)
```

Optional post-implementation:
```
Verification             → "Does it match the plan?"   → Verification Report
```

### Directory Structure Pattern

Artifacts for a single feature live in a self-contained directory:

```
{specs_dir}/{feature-id}/
├── spec.md                    # Requirements (Phase 1)
├── plan.md                    # Architecture (Phase 2)
├── tasks.md                   # Task breakdown (Phase 3)
├── reuse-matrix.md            # Component reuse analysis (Phase 0)
├── adr-001.md                 # Architecture Decision Record (Phase 2, conditional)
├── adr-002.md                 # Additional ADRs as needed
├── api-contract.md            # API endpoint definitions (Phase 2, conditional)
├── data-models.md             # Database schemas (Phase 2, conditional)
├── wave-1-context.md          # Wave 1 completion state (Phase 4)
├── wave-2-context.md          # Wave 2 completion state (Phase 4)
└── verification-report.md     # Post-implementation validation (optional)
```

Key design decisions in this structure:
- **Flat directory** — no nested subdirectories. Every artifact is one `read_file` call away.
- **Predictable names** — agents can construct file paths without searching.
- **Self-contained** — all context for a feature lives in one directory.
- **Conditional artifacts** — ADRs, API contracts, and data models only exist when relevant.

### Artifact Lifecycle

Each artifact has a clear creation point and update pattern:

| Artifact | Created | Updated | Final State |
|----------|---------|---------|-------------|
| Reuse Matrix | Phase 0 | Never (snapshot) | Complete after discovery |
| Spec | Phase 1 | Phase 5 (status sync) | Status: Complete |
| Plan | Phase 2 | Never (immutable after approval) | Approved |
| ADRs | Phase 2 | Never (append-only — new ADR supersedes old) | Accepted/Deprecated |
| API Contract | Phase 2 | Never (versioned externally) | Version 1.0.0 |
| Data Models | Phase 2 | Never | Complete after Phase 2 |
| Tasks | Phase 3 | Phase 4 (status updates per wave) | All tasks COMPLETED |
| Wave Context | Phase 4 (per wave) | Never (each wave creates a new file) | Append-only |
| Verification Report | Post-implementation | Never | PASS/REVIEW/FAIL |

---

## 3. Artifact Design Patterns

### Pattern 1: Frontmatter for Machine-Readability

Every artifact should start with structured metadata that enables routing without reading the full content:

```markdown
# Feature Name Specification

**ID:** 001-user-auth
**Created:** 2025-10-15
**Status:** Draft | Approved | In Progress | Complete
```

This metadata enables:
- **Status-based filtering** — skip completed specs, find in-progress work
- **ID-based cross-referencing** — link between artifacts without fragile file paths
- **Date-based ordering** — resolve conflicts between documents

### Pattern 2: Unique Identifiers for Cross-Referencing

Use hierarchical, unique identifiers that can be searched across artifacts:

| Scope | Pattern | Example | Appears In |
|-------|---------|---------|-----------|
| Requirement | `FR-{NNN}` | FR-001 | Spec, Plan, Tasks, Verification Report |
| Task | `T-{NN}` | T-01 | Tasks, Wave Context, Verification Report |
| ADR | `ADR-{NNN}` | ADR-001 | Plan (decision rationale), standalone file |
| API Endpoint | `{METHOD} {path}` | POST /api/v1/users | API Contract, Verification Report |

A well-implemented cross-reference system means an agent can find every mention of `FR-001` across all artifacts with a single content search.

### Pattern 3: Section Markers for Targeted Retrieval

Structure artifacts so that sections are independently addressable:

```markdown
## Wave 1 (Parallel - No Dependencies)

### T-01: Create user model
**Type**: feature
**Priority**: P0
**Effort**: M (2-4h)
**Status**: SELECTED
**Dependencies**: none
**Wave**: 1

#### Acceptance Criteria
- [ ] User model has required fields
- [ ] Migration runs successfully
```

This structure allows:
- **Heading-based navigation** — search for `## Wave 2` to jump directly to that section
- **Field-based filtering** — search for `**Status**: SELECTED` to find ready tasks
- **Checkbox tracking** — search for `- [ ]` to find incomplete criteria

### Pattern 4: Predictable Naming Conventions

Use naming conventions that allow agents to construct paths without searching:

| Convention | Pattern | Why It Works |
|-----------|---------|-------------|
| Feature directories | `{NNN}-{slug}` | Sortable, searchable by number or name |
| Wave context files | `wave-{N}-context.md` | Predictable sequence, latest = highest N |
| ADR files | `adr-{NNN}.md` | Sequential, searchable by number |
| Core artifacts | `spec.md`, `plan.md`, `tasks.md` | Fixed names, no discovery needed |

### Pattern 5: Wave-Based Grouping for Parallel Execution

Group tasks into dependency waves rather than flat lists:

```
Wave 1 (no dependencies)    → Tasks that can start immediately
Wave 2 (depends on Wave 1)  → Tasks that need Wave 1 results
Wave 3 (depends on Wave 2)  → Tasks that need Wave 2 results
```

Each wave forms a natural checkpoint for session handoff. When an agent resumes work, it reads the latest wave context file instead of re-analyzing the entire task list.

---

## 4. Navigation Patterns

### Search-First Retrieval

The foundational pattern for AI-assisted development. Instead of loading files in sequence, search for the specific information needed:

```
# Instead of this (bulk load):
read_file("spec.md")           # 3,000 tokens
read_file("plan.md")           # 4,000 tokens
read_file("tasks.md")          # 5,000 tokens
# Total: 12,000 tokens, mostly irrelevant

# Do this (search-first):
content_search("FR-001", "spec.md")           # 200 tokens
content_search("AuthService", "plan.md")       # 300 tokens
read_file("tasks.md", section="## Wave 1")     # 800 tokens
# Total: 1,300 tokens, all relevant
```

### Progressive Loading Tiers

Load information in expanding circles:

**Tier 1 — Route** (~100 tokens): Read task assignment. Identify which artifacts matter.

**Tier 2 — Scope** (~500 tokens): Search spec for the relevant requirement. Search plan for the architecture section. Confirm you understand the scope.

**Tier 3 — Implement** (~2,000 tokens): Read the full task specification. Read the relevant data model. Read the relevant ADR if architecture is non-obvious.

**Tier 4 — Verify** (as needed): Search edge cases document. Read API contract for endpoint validation. Check reuse matrix for existing components.

### Cross-Reference Tracing

Artifacts form a directed graph of references. Trace forward (requirements to code) or backward (code to requirements):

```
Forward Trace (Why does this code exist?):
  Spec (FR-001) → Plan (architecture decision) → Tasks (T-01) → Code (file:line)

Backward Trace (Does the code satisfy requirements?):
  Code (file:line) → Tasks (T-01 acceptance criteria) → Spec (FR-001) → Plan (architecture)
```

The cross-reference identifiers (FR-XXX, T-XX, ADR-XXX) make this tracing possible with content search operations.

### Wave-Based Resume

When resuming interrupted work, the wave context file provides a complete handoff:

```
1. file_search("wave-*-context.md")     # Find all wave context files
2. read_file("wave-{latest}-context.md") # Load latest wave state
3. Extract:
   - What was completed (tasks, files changed, commits)
   - What comes next (next wave tasks, files to modify)
   - Current git state (branch, last commit)
4. Continue from next wave
```

A wave context file captures everything needed to resume without re-reading spec, plan, or tasks:
- **Feature summary** — what this feature does (from spec)
- **Architecture overview** — key design decisions (from plan)
- **Completed tasks** — what was done, files changed, test status
- **Next wave** — tasks ready for implementation, their dependencies
- **Git state** — branch, last commit hash, diff stats

---

## 5. Common Scenarios

### Scenario 1: Implement a Task

```
1. read_file("tasks.md")
   → Find task T-03 in Wave 2
   → Note: depends on T-01, T-02 (both COMPLETED)

2. content_search("FR-002", "spec.md")
   → Read the functional requirement this task addresses

3. content_search("AuthService", "plan.md")
   → Understand where this fits in the architecture

4. read_file("reuse-matrix.md")
   → Check: REUSE existing auth middleware, ENHANCE token validation

5. content_search("auth.*error|token.*expired", "spec.md")
   → Find edge cases to handle

6. Implement with full context (~2,500 tokens consumed)
```

### Scenario 2: Understand an Architecture Decision

```
1. file_search("adr-*.md")
   → Discover: adr-001.md, adr-002.md, adr-003.md

2. content_search("caching|redis|valkey", "adr-*.md")
   → Match: adr-003.md

3. read_file("adr-003.md")
   → Context, decision, alternatives considered, consequences

4. content_search("cache", "plan.md")
   → See how the decision integrates into the overall architecture
```

### Scenario 3: Resume Interrupted Work

```
1. file_search("wave-*-context.md")
   → Found: wave-1-context.md, wave-2-context.md

2. read_file("wave-2-context.md")
   → Wave 2 complete: T-03, T-04 done
   → Next: Wave 3 — T-05 (integration tests), T-06 (documentation)
   → Git state: branch feature/user-auth, last commit abc123

3. content_search("T-05", "tasks.md")
   → Read T-05 details, acceptance criteria

4. Continue implementation from Wave 3
```

### Scenario 4: Verify Implementation Completeness

```
1. read_file("spec.md", section="Requirements")
   → Extract all FR-XXX identifiers

2. For each FR-XXX:
   content_search("FR-XXX", "tasks.md")
   → Verify requirement has implementing tasks

3. For each task:
   content_search("T-XX", "wave-*-context.md")
   → Verify task was completed

4. content_search("TODO|FIXME|STUB", implementation_files)
   → Verify no placeholder code remains

5. Generate verification report with:
   - Architecture alignment score
   - Requirements coverage percentage
   - Evidence log (file:line references)
```

---

## 6. Anti-Patterns

### Context Window Exhaustion

**Symptom:** Loading all SDLC artifacts before starting work.

**Cost:** 50,000+ tokens consumed for ~2,000 tokens of useful information. Leaves insufficient room for code generation and reasoning.

**Fix:** Use the search-first pattern. Start with the task assignment, expand context only as needed.

### Missing Cross-References

**Symptom:** Artifacts use prose references ("see the architecture document") instead of identifiers.

**Cost:** AI agents cannot trace requirements to implementation. Verification becomes manual.

**Fix:** Use unique identifiers (FR-XXX, T-XX, ADR-XXX) consistently across all artifacts. Every requirement should appear in both the spec and the implementing task.

### Stale Documentation

**Symptom:** Artifacts lack timestamps or status fields. No way to tell if a document reflects current state.

**Cost:** AI agents follow deprecated patterns. Implementation diverges from actual requirements.

**Fix:** Include `Status` and `Created/Updated` metadata in every artifact. Use wave context files as the source of truth for current state.

### Happy-Path-Only Specifications

**Symptom:** Requirements describe success scenarios but omit error handling, edge cases, and failure modes.

**Cost:** AI agents implement the happy path only. Error handling is invented (hallucinated) rather than specified.

**Fix:** Include explicit edge case documentation. List error conditions, validation rules, and failure recovery alongside functional requirements.

### Monolithic Artifacts

**Symptom:** A single `spec.md` contains requirements, architecture, tasks, and implementation notes in one 10,000-token file.

**Cost:** Agents must load the entire file even when they need a single section. No way to use progressive disclosure.

**Fix:** Split artifacts by concern. Each artifact type serves a distinct phase and audience. Keep individual files under 5,000 tokens where possible.

### No Resume Capability

**Symptom:** Multi-session work relies on agents re-reading all artifacts to reconstruct state.

**Cost:** Every session starts with 10,000+ tokens of context reconstruction. No guarantee of consistent state recovery.

**Fix:** Generate wave context files at each checkpoint. Each file captures the complete state needed to resume, including completed tasks, files changed, and next steps.

---

## 7. Evaluation Checklist

Use this checklist to assess whether your SDLC artifact structure is optimized for AI-assisted development.

### Structure

- [ ] Each feature's artifacts live in a single, self-contained directory
- [ ] Core artifacts have fixed, predictable names (no discovery needed)
- [ ] Conditional artifacts (ADRs, API contracts) only exist when relevant
- [ ] Directory structure is flat (no nested subdirectories for artifacts)

### Machine-Readability

- [ ] Every artifact includes structured metadata (ID, status, dates)
- [ ] Cross-references use unique identifiers (FR-XXX, T-XX, ADR-XXX)
- [ ] Identifiers are consistent across all artifacts
- [ ] Sections are independently addressable via headings

### Progressive Disclosure

- [ ] An agent can route to the right artifact with ~100 tokens
- [ ] An agent can understand scope with ~500 tokens
- [ ] An agent can implement a task with ~2,000 tokens
- [ ] Full context (edge cases, history) is available but not required upfront

### Resume Capability

- [ ] Session state is captured in wave context files
- [ ] Wave context includes: completed tasks, files changed, next steps, git state
- [ ] Resuming requires reading one file (latest wave context), not all artifacts
- [ ] Task status is tracked inline (SELECTED/COMPLETED/DEFERRED)

### Traceability

- [ ] Every requirement (FR-XXX) maps to at least one task (T-XX)
- [ ] Every task references the requirement(s) it implements
- [ ] Architecture decisions (ADR-XXX) are referenced from the plan
- [ ] Verification can trace from code back to requirements

### Token Efficiency

- [ ] Individual artifacts stay under 5,000 tokens
- [ ] Search-first retrieval can satisfy most queries in under 1,000 tokens
- [ ] No information is duplicated across artifacts (reference instead)
- [ ] Edge cases and history are in separate sections/files from core content

---

## Summary

Designing AI-ready SDLC artifacts comes down to three principles:

1. **Progressive disclosure** — Structure information in tiers so agents load only what they need. Metadata for routing (~100 tokens), summaries for understanding (~500 tokens), details for implementation (~2,000 tokens).

2. **Search-first retrieval** — Use unique identifiers, predictable naming, and structured sections so agents can find information with content search rather than sequential reading. This reduces token consumption by 60-98%.

3. **Stateful checkpoints** — Capture session state in wave context files so multi-session work resumes cleanly. Each checkpoint file is a complete handoff document, eliminating the need to re-read all artifacts.

When in doubt: **Search, Read, Validate, Implement.**
