---
description: Invoke the deep-think-partner agent for collaborative reasoning on complex problems
argument-hint: [optional: problem or question to think through]
---

# Think

## Usage

- `/think <PROBLEM_OR_QUESTION>` - Think through a specific problem
- `/think` - Think through the current context (what user is working on)

## Context

**Explicit problem (if provided):** $ARGUMENTS

**If no arguments provided:** Analyze the current conversation context - what is the user working on? What problem, decision, or challenge are they facing? Use the conversation history to identify the thinking task.

## Instructions

Use the Task tool to spawn the `deep-think-partner` agent (subagent_type: "core:deep-think-partner") to collaboratively reason through either:

1. The explicit problem provided in arguments, OR
2. The implicit problem inferred from the current conversation context

The agent will:

1. Restate the problem to confirm understanding
2. Break it down into logical components
3. Explore multiple angles and trade-offs
4. Highlight uncertainties and assumptions
5. Provide concrete recommendations

Let the agent lead the thinking process. Engage as a collaborative partner - build on insights, ask clarifying questions, and work toward a well-reasoned conclusion together.
