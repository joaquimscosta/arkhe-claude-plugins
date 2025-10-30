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

Invoke the Skill tool with skill name "git:branch" and arguments: `$ARGUMENTS`

The skill will handle commit type detection, branch naming, auto-increment numbering, and can auto-generate from uncommitted changes when no arguments are provided.

For detailed documentation, see `git/skills/branch/SKILL.md`.
