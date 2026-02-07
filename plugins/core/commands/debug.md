---
description: >
  Systematic debugging with deep reasoning. Use for: investigating errors, tracing bugs,
  analyzing stack traces, or methodically diagnosing unexpected behavior.
  Example: "/debug TypeError: Cannot read property 'map' of undefined"
argument-hint: "[error message or issue description]"
---

# Debug

## Usage

- `/debug <ERROR_OR_ISSUE>` - Debug a specific error or issue
- `/debug` - Debug the current context (what user is working on)

## Context

**Explicit issue (if provided):** $ARGUMENTS

**If no arguments provided:** Analyze the current conversation context - what error, bug, or unexpected behavior is the user encountering? Use the conversation history to identify the debugging task.

## Instructions

Use the Task tool to spawn the `deep-think-partner` agent (subagent_type: "core:deep-think-partner") to systematically debug either:

1. The explicit error/issue provided in arguments, OR
2. The implicit problem inferred from the current conversation context

Provide the agent with a debugging-focused prompt that includes:

**Debugging Framework:**
1. **Problem Definition** - Clearly describe expected vs actual behavior
2. **Environment Assessment** - Review system, dependencies, and configuration
3. **Error Investigation** - Analyze error messages, logs, and stack traces
4. **Hypothesis Formation** - Propose likely causes ranked by probability
5. **Verification** - Read relevant code, trace execution paths, and test hypotheses
6. **Resolution** - Provide concrete fix recommendations with code

**Key instructions for the agent:**
- Start with the most likely causes and use systematic elimination
- Read the actual source code to verify hypotheses before recommending fixes
- Search for related error patterns in the codebase using Grep
- Provide specific, actionable fix recommendations with file paths and line numbers
- Suggest preventive measures to avoid similar issues in the future

Let the agent lead the debugging process. It will use sequential thinking for methodical analysis and codebase search tools to investigate the root cause.
