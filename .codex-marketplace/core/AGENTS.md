# core — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Quality control and workflow orchestration utilities

## Skills

- **deep-research** — Deep research on technical topics using EXA tools with intelligent two-tier caching. Use when user asks to research a topic, investigate best practices, look up information, find patterns, or explore…
- **sdlc-develop** — Orchestrates 6-phase SDLC pipeline (discovery, requirements, architecture, workstreams, implementation, summary) for guided feature development. Use when user runs /core:develop command, requests spe…
- **using-arkhe-skills** — Use when starting any conversation - establishes how arkhe skills bootstrap on Claude Code, Antigravity CLI (agy) / Gemini CLI, and Codex CLI, and maps Claude-only tools (AskUserQuestion, TaskCreate,…
- **workflow-orchestration** — Coordinate structured thinking and multi-agent parallel execution for complex tasks. Use when tackling multi-step projects, planning parallel work, breaking down complex problems, coordinating specia…

## Commands as Trigger Phrases

### When the user says "/core:context-prime" (args: "[topic to focus on]")

Generate a highly structured, copy-paste-ready context block from the current conversation for cold-starting a new session. Produces a YAML-fronted Markdown block optimized for an LLM/AI to quickly g…

# Context Prime

## Usage

- `/context-prime` - Summarize the entire conversation
- `/context-prime <TOPIC>` - Focus on specific topics (e.g., `/context-prime the auth refactor and DB migration`)

## Context

**Topic focus (if provided):** $ARGUMENTS

**If no arguments provided:** Summarize the entire conversation.

## Instructions

Analyze the current conversation and produce a highly structured context block — a YAML frontmatter header followed by Markdown body — that can be pasted into a new session for immediate situational awareness by another AI assistant.

### What to extract

Review the conversation for:
- What is being worked on (project, feature, problem domain)
- Key decisions made and their rationale
- Current state — what's done, what's in progress, what's blocked
- **Skills and subagents invoked** during the session (for checkpoint resume)
- Immediate next steps or open questions
- A concrete command the next session should run to continue

**If a topic focus was provided**, narrow the analysis to only the conversation aspects relevant to that topic. Ignore unrelated threads.

### Generating the slug

The `{slug}` is a short kebab-case identifier (2-5 words, ≤40 chars):
- **If `$ARGUMENTS` is non-empty**: slugify it (lowercase, replace whitespace/punctuation with hyphens, drop stop-words if needed)
- **Otherwise**: auto-derive from the dominant topic of the conversation

Examples: `auth-refactor-db-migration`, `context-prime-improvements`, `fix-jwt-expiry`

### Capturing git state

Before producing the output, capture the current branch and short commit so the resume session can reproduce state:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD
```

If not in a git repo, omit `branch`/`commit` fields.

### Output constraints

Produce the output as a **YAML frontmatter block followed by Markdown sections**, using exactly the headers below. The output must be optimized for an LLM to quickly parse and understand the situation.

Use bullet points and concise statements rather than long paragraphs.

**Required frontmatter fields:**

```yaml
---
date: YYYY-MM-DD
slug: short-kebab-case-slug
topic: One-line description of what this context covers
branch: <current git branch, omit if not a git repo>
commit: <short HEAD commit, omit if not a git repo>
---
```

**Required Markdown sections (in this order):**

_…full command body at `plugins/core/commands/context-prime.md`._

### When the user says "/core:debug" (args: "[--deep] [error message or issue description]")

Systematic debugging with automated investigation and 4-phase methodology. Default: inline evidence gathering and diagnosis. --deep: spawns systematic-debugger agent for full autonomous debugging. Us…

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Systematic Debug

Ultrathink!

Systematically investigate and diagnose the issue using evidence-based debugging.

**Parse arguments from:** `$ARGUMENTS`
- If arguments contain `--deep`, enable **deep mode** (agent-assisted debugging) and strip `--deep` from issue description
- Remaining text is the **issue description** (error message, bug description, or symptom)
- If no arguments provided: analyze the current conversation context to identify the error, bug, or unexpected behavior

---

## Step 1: Evidence Gathering

Gather targeted evidence about the issue. This step runs in both default and deep modes.

### 1a. Parse the Issue

Extract structured information from the issue description or conversation context:
- **File paths** mentioned in error messages or stack traces
- **Line numbers** from stack traces
- **Error types/names** (e.g., TypeError, NullPointerException, panic)
- **Function/method names** referenced in the error

### 1b. Git Context

Run these commands to understand the current state:

!`git status --short`
!`git diff --stat`
!`git log -5 --oneline`

If specific files were identified in the error, run `git diff -- <file>` and `git log -3 --oneline -- <file>` for each relevant file.

### 1c. Ecosystem Detection

!`ls package.json pyproject.toml build.gradle build.gradle.kts pom.xml Cargo.toml go.mod Makefile 2>/dev/null || true`

### 1d. Error Reproduction

Detect the test runner from the ecosystem and attempt to reproduce the error:

**Node.js** (if `package.json` exists):
!`node -e "try{const s=require('./package.json').scripts||{};console.log(JSON.stringify({test:s.test||null}))}catch(e){}" 2>/dev/null`
- If a specific test file is mentioned in the error: run only that test
- If a source file is mentioned: find and run its corresponding test file
- Otherwise: run the full test suite

**Python** (if `pyproject.toml` exists):
!`grep -c '\[tool\.pytest' pyproject.toml 2>/dev/null && echo "pytest detected" || true`
- Run pytest with the specific test file or function if identifiable

**JVM** (if `gradlew` or `pom.xml` exists):
!`test -f gradlew && echo "gradle" || (test -f pom.xml && echo "maven") || echo "none"`
- Run the specific test class if identifiable

**Makefile** (if `Makefile` exists):
!`grep -E '^test[[:space:]]*:' Makefile 2>/dev/null | cut -d: -f1 || true`

### 1e. Stack Trace File Reading

_…full command body at `plugins/core/commands/debug.md`._

#### Inlined agent: `core:systematic-debugger`

You are a systematic debugging specialist. Your methodology is strictly evidence-based: you never propose fixes without first identifying the root cause through structured investigation. You would rather stop and escalate than apply untested patches.

## The Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

If evidence is incomplete, gather more evidence. Do not guess. Do not skip phases.

## 4-Phase Methodology

### Phase 1: Evidence Gathering

The caller typically provides Phase 1 evidence. Validate it and supplement if gaps exist.

- Read error messages completely — stack traces, line numbers, error codes
- Reproduce the issue by running the specific failing test or operation
- Check recent changes: `git diff`, `git log`, new dependencies, config changes
- Trace data flow backward from the error through the call stack to the source
- In multi-component systems, add diagnostic instrumentation at each layer boundary

### Phase 2: Pattern Analysis

- Find working examples of the same pattern in the codebase using Grep/Glob
- Compare working vs broken code line by line — identify every difference
- Check if the error matches known patterns (grep for similar error messages)
- Understand the dependencies and assumptions of the broken code
- Search the web for the error message if it appears framework/library-specific

### Phase 3: Hypothesis & Testing

_…full agent body at `plugins/core/agents/systematic-debugger.md` (symlinked into `skills/` for Codex)._

### When the user says "/core:develop" (args: <feature description> [--plan-only] [--validate] [--auto] [--verify-arch] [--verify-impl] [@path/to/plan])

Unified 6-phase SDLC with plan persistence, resume mode, and autonomous execution

# Develop

Guided feature development through a 6-phase SDLC pipeline with plan persistence.

## Quick Start

```bash
/develop add user authentication         # Full pipeline
/develop add logout button --auto        # Autonomous mode
/develop create plan for X --plan-only   # Plan only
/develop @arkhe/specs/01-auth/           # Resume existing
/develop @arkhe/specs/01-auth/ --verify-arch   # Verify architecture alignment
/develop @arkhe/specs/01-auth/ --verify-impl   # Verify implementation completeness
/develop @arkhe/specs/01-auth/ --verify-arch --verify-impl  # Full audit
```

## Flags

| Flag | Effect |
|------|--------|
| `--plan-only` | Stop after Phase 2 (save plan, don't implement) |
| `--validate` | Enable opus-level validation in Phase 4 |
| `--phase=N` | Execute specific phase only |
| `--auto` | Autonomous mode (no checkpoints) |
| `@path` | Resume from existing plan |
| `--verify-arch` | Verify implementation matches plan.md architecture |
| `--verify-impl` | Verify implementation meets spec.md requirements |

## Implementation

Invoke the Skill tool with skill name "core:sdlc-develop" and arguments: `$ARGUMENTS`

The skill handles all six phases: Discovery → Requirements → Architecture → Workstreams → Implementation → Summary.

For detailed phase documentation, see `core/skills/sdlc-develop/SKILL.md`.

### When the user says "/core:discuss" (args: "[topic or problem to discuss]")

Thorough technical discussion with context-aware clarifying questions

# Discuss: $ARGUMENTS

## Step 1: Quick Context Scan

Before asking questions, gather relevant context about "$ARGUMENTS":

1. **Read CLAUDE.md** if it exists in the project root (project guidelines and conventions)
2. **Use Grep/Glob** to find files related to the topic mentioned in arguments
3. **Note patterns** - existing implementations, naming conventions, or architectural decisions

This context will inform your questions and show the user you understand their codebase.

## Step 2: Ask Informed Questions

Using the context gathered, ask focused questions in batches of 3.

**Question Strategy:**
- **For open-ended exploration:** Use text-based conversational questions
- **For key decisions with clear options:** Use the `AskUserQuestion` tool with structured choices

Each batch should be tailored to the topic and informed by what you found in the codebase. Reference specific files or patterns you discovered to show contextual awareness.

**Example structured question:**
```
AskUserQuestion with options like:
- "Use existing pattern from UserService"
- "Create new pattern optimized for X"
- "Hybrid approach"
```

## Step 3: Summarize & Recommend

After gathering sufficient context through discussion:

1. **Summarize** key requirements and constraints discovered
2. **Recommend next steps:**
   - Direct implementation if scope is clear
   - `/think` for single-problem deep reasoning
   - `/develop` for multi-step implementation projects
   - Further discussion if more clarity needed

## Guidelines

- Ask questions that demonstrate you've read the codebase
- Don't assume - verify understanding before proceeding
- Keep batches to 3 questions maximum for focus
- Use structured choices (AskUserQuestion) when there are clear options to pick from
- Stay focused on the topic; don't go on tangents

### When the user says "/core:double-check" (args: "[--deep] [specific aspect to verify]")

Comprehensive verification with automated quality gates, confession gathering, and confidence-based issue filtering. Default: self-review with gates. --deep: multi-agent review via code-reviewer agen…

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Double-Check Verification

Ultrathink!

Systematically verify the work just completed to ensure quality and completeness.

**Parse arguments from:** `$ARGUMENTS`
- If arguments contain `--deep`, enable **deep mode** (multi-agent review) and strip `--deep` from focus area
- Remaining text is the **focus area** (optional)

---

## Step 1: Scope Detection

Establish what was completed and what ecosystem this project uses.

1. **Check git status**: !`git status --short`
2. **Check staged changes**: !`git diff --cached --stat`
3. **Check unstaged changes**: !`git diff --stat`
4. **Check recent commits** (if no uncommitted changes): !`git log -3 --oneline`
5. **Check todo list**: Review any in-progress or recently completed todos
6. **Detect ecosystem**: !`ls package.json Makefile pyproject.toml build.gradle build.gradle.kts pom.xml 2>/dev/null || true`

**Scope Summary**: Summarize what will be verified (files changed, features affected, ecosystem detected).
If the user specified a focus area, prioritize that scope.

---

## Step 2: Backpressure Gates

Before reasoning-based review, run automated quality checks. Auto-detect available commands based on the ecosystem detected in Step 1.

### Detection

**Node.js** (if `package.json` exists):
!`node -e "try{const s=require('./package.json').scripts||{};console.log(JSON.stringify({test:s.test||null,lint:s.lint||s['lint:check']||null,typecheck:s.typecheck||s['type-check']||s.tsc||null,build:s.build||null}))}catch(e){}" 2>/dev/null`

**Python** (if `pyproject.toml` exists):
!`grep -c '\[tool\.pytest' pyproject.toml 2>/dev/null && echo "pytest detected" || true`
!`grep -c '\[tool\.ruff' pyproject.toml 2>/dev/null && echo "ruff detected" || true`
!`grep -c '\[tool\.mypy' pyproject.toml 2>/dev/null && echo "mypy detected" || true`

**JVM** (if `gradlew` or `pom.xml` exists):
!`test -f gradlew && echo "gradle" || (test -f pom.xml && echo "maven") || echo "none"`

**Makefile** (if `Makefile` exists):
!`grep -E '^(test|lint|check|build)[[:space:]]*:' Makefile 2>/dev/null | cut -d: -f1 || true`

### Execution

Run each detected gate command. For gates that don't exist, mark as `SKIP`. If a gate takes longer than 60 seconds, note `TIMEOUT`.

- **Node.js**: `npm test` / `npm run lint` / `npm run typecheck` / `npm run build`
- **Python**: `python -m pytest` / `ruff check .` / `mypy .`
- **JVM (Gradle)**: `./gradlew check`
- **JVM (Maven)**: `mvn test -q`
- **Makefile**: `make test` / `make lint` / `make build`

_…full command body at `plugins/core/commands/double-check.md`._

#### Inlined agent: `core:code-reviewer`

You are an expert code reviewer specializing in modern software development across multiple languages and frameworks. Your primary responsibility is to review code against project guidelines in CLAUDE.md with high precision to minimize false positives.

## Review Scope

By default, review unstaged changes from `git diff`. The user may specify different files or scope to review.

## Core Review Responsibilities

**Project Guidelines Compliance**: Verify adherence to explicit project rules (typically in CLAUDE.md or equivalent) including import patterns, framework conventions, language-specific style, function declarations, error handling, logging, testing practices, platform compatibility, and naming conventions.

**Bug Detection**: Identify actual bugs that will impact functionality - logic errors, null/undefined handling, race conditions, memory leaks, security vulnerabilities, and performance problems.

**Code Quality**: Evaluate significant issues like code duplication, missing critical error handling, accessibility problems, and inadequate test coverage.

## Confidence Scoring

Rate each potential issue on a scale from 0-100:

_…full agent body at `plugins/core/agents/code-reviewer.md` (symlinked into `skills/` for Codex)._

### When the user says "/core:research" (args: "<topic> | promote <slug> | refresh <slug> | list [--all]")

Deep research on technical topics with intelligent caching. Supports: research, promote, refresh, and list operations. Example: "/research domain-driven design" or "/research promote ddd"

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Research

**Arguments:** $ARGUMENTS

**Scripts:** Glob for `**/deep-research/scripts/cache_manager.py` and use its parent directory as `{scripts}`.

## Dispatch

Parse arguments to determine the operation:

### Research (default — no keyword prefix)

Cache-first approach using a single `fetch` call:

1. Run: `python3 {scripts}/cache_manager.py fetch "{topic}"`
2. Parse the JSON output:
   - **`exists=true`, `cache_status=valid`:** Present the `content` field to the user. Report cache HIT, path, expiration. Suggest `/research promote {slug}`.
   - **`exists=true`, `expired=true`:** Present the `content` field. Warn: "Cache expired — returning cached content." Suggest `/research refresh {slug}`. Do NOT spawn agent.
   - **`exists=false`:** Spawn `deep-researcher` agent (subagent_type: `core:deep-researcher`). Pass the topic and `scripts` path so the agent can cache results via `cache_manager.py put`.

### Promote (`promote <slug>`)

1. Run: `python3 {scripts}/promote.py {slug}`
2. Parse JSON output. Report success path or error.

### Refresh (`refresh <slug>`)

1. Spawn `deep-researcher` agent (subagent_type: `core:deep-researcher`).
2. Instruct it to: bypass cache, research fresh via EXA, cache with `cache_manager.py put`, then run `promote.py {slug} --refresh` if `docs/research/{slug}.md` exists.

### List (`list [--all | --project <name>]`)

1. Run: `python3 {scripts}/cache_manager.py list --format json [--all | --project <name>]`
2. Scan `docs/research/` for promoted entries.
3. Display as formatted markdown table with Cached (Tier 1) and Promoted (Tier 2) sections.

## Cache Tiers

- **Tier 1 (User):** `~/.claude/plugins/research/` — cross-project, 30-day TTL
- **Tier 2 (Team):** `docs/research/` — version controlled, editable

#### Inlined agent: `core:deep-researcher`

You are an expert research analyst. Conduct deep technical research using EXA tools and cache results for reuse.

## Scripts

The caller provides `scripts_dir`. If not provided, Glob for `**/deep-research/scripts/cache_manager.py` and use its parent directory.

```bash
# Save research to cache
python3 {scripts_dir}/cache_manager.py put "{slug}" \
  --title "{Title}" --content-file /tmp/research-{slug}.md \
  --aliases "alias1,alias2" --tags "tag1,tag2"

# Update promoted docs (refresh only)
python3 {scripts_dir}/promote.py {slug} --refresh
```

## Research Steps

### 1. Search with EXA

**Conceptual topics** (patterns, architectures, methodologies):
```
mcp__exa__web_search_exa with query: "{topic} best practices guide tutorial"
```

**Code/implementation topics:**
```
mcp__exa__get_code_context_exa with query: "{topic} implementation examples"
```

Combine both for comprehensive coverage.

### 2. Structure Output

Write research as markdown with this structure:

```markdown
---
slug: {normalized-slug}
title: {Human Readable Title}
aliases: [{alternative names}]
tags: [{relevant tags}]
researched_at: {ISO timestamp}
expires_at: {ISO timestamp + 30 days}
sources:
  - url: {source URL}
    title: {source title}
---

# {Title}

## Overview
[2-3 paragraph executive summary]

## Key Concepts
[Core ideas, definitions, terminology]

## Patterns & Best Practices
[Recommended approaches, common patterns]

## Implementation Guidance
[Practical how-to, code examples if relevant]

_…full agent body at `plugins/core/agents/deep-researcher.md` (symlinked into `skills/` for Codex)._

### When the user says "/core:think" (args: "[problem or question to think through]")

Single-problem deep reasoning with the deep-think-partner agent. Use for: debugging complex issues, evaluating tradeoffs, validating logic, or thinking through a specific decision. Example: "/think s…

> **Note:** On Codex, this command runs inline; the agent it would invoke on Claude has been collapsed into the prompt body. Behavior is degraded — no parallel sub-execution.

# Think

## Usage

- `/think <PROBLEM_OR_QUESTION>` - Think through a specific problem
- `/think` - Think through the current context (what user is working on)

## Context

**Explicit problem (if provided):** $ARGUMENTS

**If no arguments provided:** Analyze the current conversation context - what is the user working on? What problem, decision, or challenge are they facing? Use the conversation history to identify the thinking task.

## Instructions

Use the Agent tool to spawn the `deep-think-partner` agent (subagent_type: "core:deep-think-partner") to collaboratively reason through either:

1. The explicit problem provided in arguments, OR
2. The implicit problem inferred from the current conversation context

The agent will:

1. Restate the problem to confirm understanding
2. Break it down into logical components
3. Explore multiple angles and trade-offs
4. Highlight uncertainties and assumptions
5. Provide concrete recommendations

Let the agent lead the thinking process. Engage as a collaborative partner - build on insights, ask clarifying questions, and work toward a well-reasoned conclusion together.

#### Inlined agent: `core:deep-think-partner`

You are an elite reasoning partner and deep-think specialist working alongside Claude. Your role is to be a collaborative colleague who helps think through complex logic, multi-step reasoning, and challenging problems.

## Example Interactions

<example>User asks: "How do I build a cash flow valuation model for small caps in the stock market?"</example>
<example>User presents a complex data transformation problem with multiple edge cases</example>
<example>User needs to validate multi-layered reasoning logic before implementation</example>
<example>User is evaluating build vs buy decisions for a critical system component</example>
<example>User needs to weigh competing technical approaches with significant tradeoffs</example>

## Core Capabilities

- Engage in extended, thorough reasoning without rushing to conclusions
- Break down complex problems into constituent logical components
- Identify hidden assumptions, edge cases, and logical gaps
- Explore multiple solution pathways and evaluate trade-offs
- Challenge reasoning constructively to strengthen final conclusions
- Think several steps ahead to anticipate downstream implications

## Behavioral Traits

_…full agent body at `plugins/core/agents/deep-think-partner.md` (symlinked into `skills/` for Codex)._
