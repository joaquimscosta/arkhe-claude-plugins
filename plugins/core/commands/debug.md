---
description: >
  Systematic debugging with automated investigation and 4-phase methodology.
  Default: inline evidence gathering and diagnosis. --deep: spawns systematic-debugger
  agent for full autonomous debugging. Use for errors, stack traces, test failures,
  or unexpected behavior.
argument-hint: "[--deep] [error message or issue description]"
---

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

If specific files were identified in the error:
!`git diff -- <file>` and !`git log -3 --oneline -- <file>` for each

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

For each file:line extracted from the error or stack trace, use Read to examine ~20 lines of context around the error location. This gives the diagnosis phase concrete code to work with.

### 1f. Evidence Summary

Present findings:

```
### Evidence Summary

**Issue:** [restated issue from args or context]
**Ecosystem:** [detected ecosystem]
**Recent Changes:** [summary of git status/diff relevant to the issue]
**Error Reproduction:** [test result, reproduced/not reproduced]
**Files Examined:** [list with file:line references]
**Key Observations:** [notable findings from file reading and git history]
```

---

## Step 2: Pattern Analysis

Search the codebase for patterns related to the issue. This step runs in both modes.

1. **Find working examples**: Use Grep/Glob to find similar patterns in the codebase that work correctly (e.g., other functions using the same API, other components following the same pattern)

2. **Compare working vs broken**: Read working examples and note structural differences from the broken code

3. **Search for similar errors**: Grep the codebase for the same error message or similar error patterns
   !`git log --all --oneline --grep="<relevant keyword>" -5 2>/dev/null || true`

4. **Check related commits**: Look for recent commits that touched related files or functionality

Present findings:

```
### Pattern Analysis

**Working examples found:** [file:line references]
**Key differences:** [what differs between working and broken code]
**Similar errors in codebase:** [any matches found]
**Related commits:** [relevant history]
```

---

## Step 3: Diagnosis

This step differs by mode.

### Default Mode (inline diagnosis)

Using the evidence from Steps 1-2, reason through the issue:

**Phase 3 — Hypothesis Formation:**
- Form ranked hypotheses based on the evidence gathered
- For each hypothesis, reference specific evidence that supports or contradicts it
- Consider: recent changes, pattern differences, error reproduction results

**Phase 4 — Root Cause Identification:**
- Identify the most likely root cause with a full reasoning chain
- If the evidence is insufficient, run additional targeted investigation before concluding

**Red Flag Check:**
- If the conversation context reveals 3+ previous fix attempts that failed: **STOP**. State explicitly: "Multiple fix attempts detected. The underlying architecture may need rethinking before attempting another fix." Recommend investigation of the broader design.

### Deep Mode (`--deep`)

Delegate Phases 3-4 to the systematic-debugger agent for autonomous investigation.

Use the **Agent tool** to spawn the `systematic-debugger` agent:
- `subagent_type`: `core:systematic-debugger`
- `description`: "Systematic debugging of [brief issue description]"

Provide the agent with:
1. The **issue description** (original error/issue)
2. The **evidence summary** from Step 1
3. The **pattern analysis** from Step 2
4. The **conversation context** (what was the user doing when this broke?)
5. The **fix attempt count** (if previous attempts are visible in conversation)

Instruct the agent: "Complete Phases 2-4 of systematic debugging. Phase 1 evidence is provided below. Run additional investigation as needed. Follow the 4-phase methodology strictly. If 3+ fixes have already been attempted, question the architecture before proposing another fix."

**Graceful degradation**: If the Agent tool is unavailable or the agent cannot be spawned, fall back to default inline diagnosis mode and note: "Agent dispatch unavailable — running inline diagnosis."

---

## Step 4: Resolution

Based on the diagnosis (whether inline or from the agent):

**Recommended Fix:**
- Specific changes with file paths and line numbers
- Rationale explaining why this addresses the root cause

**Suggested Test Case:**
- A minimal test that reproduces the bug (fails before fix, passes after)

**Preventive Measures:**
- How to avoid similar issues in the future

---

## Step 5: Synthesis

Present the final output:

### Debug Results

**Issue:** [restated issue]

**Mode:** Default | Deep (systematic-debugger agent)

**Status:** ROOT CAUSE IDENTIFIED | NEEDS INVESTIGATION | ARCHITECTURAL ISSUE

**Evidence Summary:**

| Category | Findings |
|----------|----------|
| Ecosystem | ... |
| Recent Changes | ... |
| Error Reproduction | Reproduced / Not reproduced |
| Files Examined | ... |

**Hypotheses:**

| # | Hypothesis | Supporting Evidence | Confidence |
|---|-----------|-------------------|------------|
| 1 | ... | ... | High/Medium/Low |
| 2 | ... | ... | ... |

**Root Cause:** [identified cause with reasoning]

**Recommended Fix:**
- File: `path/to/file`, line N
- Change: [specific change]
- Rationale: [why this fixes the root cause]

**Test Case:** [suggested test]

**Prevention:** [measures to avoid recurrence]

**Red Flags:** [if applicable — architecture concerns, repeated failures, or escalation needed]
