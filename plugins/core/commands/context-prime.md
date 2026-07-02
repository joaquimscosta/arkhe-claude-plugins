---
description: >
  Generate a highly structured, copy-paste-ready context block from the current
  conversation for cold-starting a new session. Produces a YAML-fronted Markdown
  block optimized for an LLM/AI to quickly gain situational awareness, including
  skills/agents used and a resume hint for checkpoint continuation. Optionally
  focus on specific topics.
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

1. **## Objective:** What we are trying to achieve and why.
2. **## Current State:** Where things stand right now, including what's working and any current blockers.
3. **## Key Decisions & Constraints:** Technical decisions made, architectural rules, or constraints the next session must respect.
4. **## Relevant Files:** Key files, variables, or functions that are critical to the current work. Use `file_path:line_number` format where applicable.
5. **## Skills & Agents Used:** Skills invoked (e.g., `superpowers:brainstorming`, `core:debug`) and subagents spawned (e.g., `code-explorer`, `deep-researcher`) during the session. Helps the next session resume mid-workflow. Omit the section only if none were used.
6. **## Next Steps:** Concrete actions or open questions to tackle next.
7. **## Resume Hint:** A single suggested command for the next session to continue the work — typically a slash command like `/develop <topic>`, `/core:debug <symptom>`, or `/context-prime <slug>`. If no clear next command, suggest a one-line prompt the user can paste.

**Do NOT include:**
- Preamble ("Here is the context...")
- A closing remark or offer to help
- Anything outside the YAML+Markdown structure itself

Output the YAML frontmatter and Markdown block directly. Nothing before it, nothing after it.

### Save option

After outputting the context block, use the AskUserQuestion tool to ask the user if they want to save it to a file. Provide these options:

1. **Save to `.scratch/context/`** (Recommended) — Save to `.scratch/context/context-YYYY-MM-DD-{slug}.md` (create directory if needed). Local scratch, not checked into shared docs.
2. **Save to `.claude/context/`** — Save to `.claude/context/context-YYYY-MM-DD-{slug}.md` (create directory if needed). Use when the context should live alongside other `.claude/` artifacts.
3. **Save to custom path** — Let the user specify a path.
4. **No, I'll copy it** — Do nothing further.

If the user chooses to save, write the context block to the chosen path using the Write tool, using the `{slug}` and date already determined for the frontmatter.
