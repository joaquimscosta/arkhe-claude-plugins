---
description: >
  Generate a terse, copy-paste-ready context block from the current conversation
  for cold-starting a new session. Produces freeform prose optimized for pasting
  into a new session's first message. Optionally focus on specific topics.
argument-hint: "[topic to focus on]"
---

# Context Prime

## Usage

- `/context-prime` - Summarize the entire conversation
- `/context-prime <TOPIC>` - Focus on specific topics (e.g., `/context-prime the auth refactor and DB migration`)

## Context

**Topic focus (if provided):** $ARGUMENTS

**If no arguments provided:** Summarize the entire conversation.

## Instructions

Analyze the current conversation and produce a terse context block that can be pasted into a new session for immediate situational awareness.

### What to extract

Review the conversation for:
- What is being worked on (project, feature, problem domain)
- Key decisions made and their rationale
- Current state — what's done, what's in progress, what's blocked
- Immediate next steps or open questions

**If a topic focus was provided**, narrow the analysis to only the conversation aspects relevant to that topic. Ignore unrelated threads.

### Output constraints

Produce **1-3 short paragraphs of freeform prose** directly in the console.

**Length:** 2-5 sentences per paragraph. The entire block should be readable in 15 seconds.

**Tone:** Direct and factual. Write as a terse briefing. Assume the reader is technical and familiar with the project.

**Content priorities (in order):**
1. What we're doing and why (one sentence of orientation)
2. Where things stand right now (current state, blockers)
3. What to do next (concrete actions, not vague direction)
4. Key decisions or constraints the next session must respect

**Do NOT include:**
- Preamble ("Here's your context...")
- Headers, bullet points, or markdown formatting
- Code blocks or file paths unless critical
- Anything obvious from the codebase itself
- A closing remark or offer to help

Output the prose block directly. Nothing before it, nothing after it.

### Save option

After outputting the context block, use the AskUserQuestion tool to ask the user if they want to save it to a file. Provide these options:

1. **No, I'll copy it** — Do nothing further.
2. **Save to .claude/context/** — Save to `.claude/context/context-YYYY-MM-DD.md` (create directory if needed). Use the current date.
3. **Save to custom path** — Let the user specify a path.

If the user chooses to save, write the context block to the chosen path using the Write tool.
