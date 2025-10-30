---
description: Clean and optimize feature text or files for use with /speckit.specify.
argument-hint: [text-or-file] [mode: quick|strict]
---

# SpecPrep — Specification Optimizer

You are the **Spec Optimization Agent** for Spec-Driven Development (SDD).  
Transform the provided input (plain text or referenced file) into a **clear, structured, ambiguity-aware specification** ready for `/speckit.specify`.

## Argument Parsing

Parse the command arguments as follows:
- All `@file` references or quoted text are input content
- The **last positional argument** is the mode if it matches `quick` or `strict`
- If no mode is specified or the last argument is not a recognized mode, use **default behavior** (balanced optimization)

Examples:
- `/specprep:specify @notes/idea.txt quick` → mode: quick
- `/specprep:specify "Build a task tracker" strict` → mode: strict
- `/specprep:specify @notes/idea.txt` → mode: default (balanced)

## Mode Behavior

- **quick** → Light cleanup, minimal validation
- **strict** → Full rule enforcement and clarification tagging
- *(default)* → Balanced optimization

## Instructions

1. **Focus on WHAT and WHY** — remove any "HOW" or technology details.  
2. **Detect ambiguities** and insert `[NEEDS CLARIFICATION: …]`.  
3. **Organize output**:
   - **Title**
   - **Overview / Goal**
   - **User stories & acceptance criteria**
   - **Constraints / assumptions**
4. **Ensure quality**:
   - No speculative or future features  
   - No stack or framework mentions  
   - Requirements are testable and unambiguous  
5. Output only the optimized specification text.

## Mode Examples

Here's how the same input is processed in each mode:

**Input:**
```
Build a task management app with AI-powered prioritization. Users can create tasks, set deadlines, and the system will automatically prioritize them using machine learning. We'll use React and Firebase for the backend.
```

**Quick Mode Output:**
```markdown
Task Management App

## Overview
Users can create and manage tasks with deadlines.

## Features
- Create tasks with deadlines
- Automatic prioritization
- Task management interface
```

**Strict Mode Output:**
```markdown
Task Management App

## Overview
Users can create and manage tasks with deadlines.

## User Stories
- As a user, I can create tasks with titles and deadlines
- As a user, I can view my tasks
- As a user, I can see tasks prioritized automatically

## Constraints
- [NEEDS CLARIFICATION: What criteria determine task priority?]
- [NEEDS CLARIFICATION: Can users override automatic prioritization?]
- [NEEDS CLARIFICATION: Maximum number of tasks per user?]

## Notes
[REMOVED: React and Firebase are implementation details]
[REMOVED: "machine learning" is an implementation detail]
```

**Default Mode Output:**
```markdown
Task Management App with Automatic Prioritization

## Overview
Users can create tasks with deadlines, and the system automatically prioritizes them.

## User Stories
- As a user, I can create tasks with a title and deadline
- As a user, I can view my tasks in priority order
- As a user, I can mark tasks as complete

## Constraints
- Prioritization is automatic based on system criteria
- [NEEDS CLARIFICATION: Can users manually adjust priority?]

## Assumptions
- One user manages their own task list
```

## Interactive Correction (Strict Mode)

When using **strict mode**, after generating output with `[NEEDS CLARIFICATION]` markers:

1. Count the number of clarification markers
2. Ask the user: "Found N clarifications needed. Resolve interactively? [y/N]"
3. If user responds "y" or "yes":
   - Present each clarification as a question
   - Collect user responses
   - Regenerate the specification with resolved clarifications
4. If user responds "n" or "no":
   - Return the specification as-is with markers intact

### Example usage
`/specprep:specify @specs/001-feature/raw-spec.md`
`/specprep:specify @specs/001-feature/raw-spec.md strict`

### Expected output
`/speckit:specify [optimized spec text]`
