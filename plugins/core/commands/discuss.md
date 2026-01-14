---
description: Thorough technical discussion with context-aware clarifying questions
argument-hint: "[topic or problem to discuss]"
---

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
