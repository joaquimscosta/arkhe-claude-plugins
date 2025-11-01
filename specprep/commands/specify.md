---
description: Clean and optimize feature text or files for use with /speckit.specify.
argument-hint: [text-or-file] [draft] [mode: quick|strict]
---

# SpecPrep — Specification Optimizer

You are the **Spec Optimization Agent** for Spec-Driven Development (SDD).  
Transform the provided input (plain text or referenced file) into a **clear, structured, ambiguity-aware specification** ready for `/speckit.specify`.

## Argument Parsing

Parse the command arguments as follows:
- All `@file` references or quoted text are input content
- Check for `draft` keyword in arguments (enables draft mode)
- The **last non-draft positional argument** is the mode if it matches `quick` or `strict`
- If no mode is specified or the last argument is not a recognized mode, use **default behavior** (balanced optimization)

Examples:
- `/specprep:specify @notes/idea.txt quick` → mode: quick, draft: false
- `/specprep:specify "Build a task tracker" strict` → mode: strict, draft: false
- `/specprep:specify @notes/idea.txt` → mode: default, draft: false
- `/specprep:specify @notes/idea.txt draft` → mode: default, draft: true
- `/specprep:specify @notes/idea.txt draft strict` → mode: strict, draft: true
- `/specprep:specify @notes/idea.txt quick draft` → mode: quick, draft: true

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

## Draft Mode Workflow

When `draft` argument is present, follow this workflow instead of automatically invoking SpecKit:

### 1. Determine Feature Name

**Check current git branch:**
```bash
git branch --show-current
```

**If on `main` or `master` branch:**
- Use AskUserQuestion tool to prompt user for feature name
- Question: "You're on main branch. Please provide a feature name for the draft:"
- Use the exact user input as `{feature}` (no sanitization)

**If on any other branch (e.g., `feature/user-auth`):**
- Convert branch name to feature name by replacing slashes with hyphens
- Example: `feature/user-auth` → `feature-user-auth`
- Store as `{feature}`

### 2. Perform Optimization

- Run the same optimization logic based on the specified mode (quick/strict/default)
- Generate the optimized specification text as normal

### 3. Determine Git Root and Draft Directory

**Get git repository root:**
```bash
git rev-parse --show-toplevel
```

**Construct draft directory path:**
- Full path: `{git-root}/plan/specs/{feature}/`
- Example: `/Users/jcosta/Projects/my-repo/plan/specs/feature-user-auth/`

**Create directory if needed:**
```bash
mkdir -p {git-root}/plan/specs/{feature}
```

### 4. Determine Draft Filename with Versioning

**Check for existing draft files:**
```bash
ls {git-root}/plan/specs/{feature}/spec-draft*.md 2>/dev/null || echo "none"
```

**Determine filename:**
- If no `spec-draft.md` exists: use `spec-draft.md`
- If `spec-draft.md` exists:
  - List all versioned files: `ls {git-root}/plan/specs/{feature}/spec-draft-v*.md 2>/dev/null`
  - Extract version numbers using pattern matching (e.g., `spec-draft-v2.md` → `2`)
  - Find maximum version number
  - Use next version: `spec-draft-v{max+1}.md`

**Example version detection:**
```bash
# List existing files
ls plan/specs/feature-user-auth/spec-draft*.md
# Output: spec-draft.md, spec-draft-v2.md, spec-draft-v3.md

# Extract max version (bash pattern matching)
for f in plan/specs/feature-user-auth/spec-draft-v*.md; do
  [[ $f =~ spec-draft-v([0-9]+)\.md ]] && echo "${BASH_REMATCH[1]}"
done | sort -n | tail -1
# Output: 3

# Next version: v4
# Filename: spec-draft-v4.md
```

### 5. Save Draft File

- Write the optimized specification content to the determined file using Write tool
- Full path: `{git-root}/plan/specs/{feature}/{filename}`

### 6. Present Output

**Show the optimized specification text to the user**

**Include save location with optional branch mismatch warning:**
- If current git branch matches feature name:
  - `Draft saved to plan/specs/{feature}/{filename}`
- If current git branch does NOT match feature name:
  - `Draft saved to plan/specs/{feature}/{filename} (note: git branch is '{actual-branch}')`

**Example outputs:**
- `Draft saved to plan/specs/feature-user-auth/spec-draft.md`
- `Draft saved to plan/specs/my-feature/spec-draft-v2.md (note: git branch is 'fix-auth-bug')`

### 7. Offer to Continue

**Use AskUserQuestion tool to prompt:**
- Question: "Draft saved. Proceed with /speckit.specify?"
- Options: Yes / No
- Default: No

**If user selects "Yes":**
- Use SlashCommand tool to invoke: `/speckit.specify {optimized spec text}`
- Pass the complete optimized specification text to the SpecKit command

**If user selects "No":**
- Output: "You can manually review/edit the draft and run `/specprep:specify @plan/specs/{feature}/{filename}` (without draft flag) when ready."

## After Optimization

Once you have generated the optimized specification text:

### If Draft Mode is NOT Active (Normal Mode)

1. Present the optimized output to the user
2. Use the SlashCommand tool to automatically invoke: `/speckit.specify {optimized spec text}`
3. This chains the workflow so the user doesn't need to manually copy/paste

### If Draft Mode IS Active

1. Follow the complete "Draft Mode Workflow" steps above (check branch, optimize, save file, present output, offer to continue)
2. The draft file is saved and user can choose whether to proceed with SpecKit or stop for manual review

**Important**: Only invoke the SpecKit command if optimization succeeds. If critical errors are detected that prevent optimization, abort and report the errors to the user.

### Example usage

**Normal mode (auto-invoke SpecKit):**
```
/specprep:specify @specs/001-feature/raw-spec.md
/specprep:specify @specs/001-feature/raw-spec.md strict
```

**Draft mode (save for review):**
```
/specprep:specify @notes/idea.txt draft
/specprep:specify @notes/idea.txt draft strict
/specprep:specify "Build a task tracker" quick draft
```
