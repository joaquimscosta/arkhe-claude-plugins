---
description: Create a new feature branch with optimized short naming, or auto-generate from uncommitted changes
argument-hint: [feature_description]
---

# Branch Creation Command

Creates feature branches with intelligent naming and auto-incrementing.

## Usage

```bash
# Create from description
/create-branch <feature_description>

# Auto-generate from uncommitted changes
/create-branch
```

## Examples

```bash
/create-branch add newsletter signup
# Creates: feat/003-newsletter-signup

/create-branch fix authentication bug
# Creates: fix/004-authentication-bug

/create-branch
# Auto-detected from changes: feat/005-authentication-system
```

## Implementation

Delegates to the **git:branch** skill for all branch creation logic:

```
If arguments provided:
  Invoke Skill tool with skill name "git:branch" and arguments: $ARGUMENTS

If no arguments provided:
  Invoke Skill tool with skill name "git:branch" with no arguments
```

For detailed documentation including commit type detection, branch naming format, auto-generation workflow, and configuration options, see `git/skills/branch/SKILL.md`.
