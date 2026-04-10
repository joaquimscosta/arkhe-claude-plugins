# Git Plugin Architecture

## Overview

The Git plugin uses a **Commands + Skills** pattern with inline Bash workflows that aligns with Claude Code's official plugin system documentation.

## Naming Convention

### Hybrid Approach: Simple Directories + Descriptive Names

**Directory Names**: Match skill names using gerund form (`creating-commit/`, `creating-pr/`, `creating-branch/`, `generating-changelog/`)
- Matches YAML `name` field exactly
- Follows official Anthropic `skill-creator` pattern
- Uses gerund form (verb + -ing) for clarity
- Improves discoverability and consistency

**Skill Names** (YAML frontmatter): Gerund form describing the action
- Uses verb + -ing format (creating, generating, etc.)
- Aligns with best practices documentation
- Descriptive and action-oriented

**Example**:
```yaml
# Directory: git/skills/creating-commit/
# Skill name in SKILL.md:
---
name: creating-commit
---
```

This follows best practices:
- ✅ Directory name matches YAML name exactly
- ✅ Gerund form (verb + -ing) for clarity
- ✅ Follows official Anthropic pattern
- ✅ Consistent with other plugins in arkhe-claude-plugins

## Architecture Pattern

### Why This Pattern?

According to Claude Code documentation:
- **Commands**: Simple prompts that delegate to skills
- **Skills**: Complex capabilities with inline Bash workflows and supporting documentation

The git plugin requires complex git workflows with multi-repo support, making Skills with inline Bash the appropriate choice.

### Structure

```
git/
├── commands/              # User-facing slash commands
│   ├── commit.md          # /commit command
│   ├── create-pr.md       # /create-pr command
│   ├── create-branch.md   # /create-branch command
│   ├── changelog.md       # /changelog command
│   ├── stale-branches.md      # /stale-branches command
│   ├── cleanup-branches.md   # /cleanup-branches command
│   ├── release.md            # /release command
│   └── worktree.md           # /worktree command
├── skills/                # Skills with inline Bash workflows
│   ├── creating-commit/
│   │   ├── SKILL.md           # Inline Bash workflow (414 lines)
│   │   ├── WORKFLOW.md        # Detailed step-by-step process
│   │   ├── EXAMPLES.md        # Real-world usage examples
│   │   └── TROUBLESHOOTING.md # Common issues and solutions
│   ├── creating-pr/
│   │   ├── SKILL.md           # Inline Bash workflow (458 lines)
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   └── TROUBLESHOOTING.md
│   ├── creating-branch/
│   │   ├── SKILL.md           # Inline Bash workflow (370 lines)
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   └── TROUBLESHOOTING.md
│   ├── generating-changelog/
│   │   ├── SKILL.md           # Inline Bash workflow (217 lines)
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   └── TROUBLESHOOTING.md
│   ├── listing-stale-branches/
│   │   ├── SKILL.md           # Inline Bash workflow for stale branch detection
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   └── TROUBLESHOOTING.md
│   ├── cleaning-up-branches/
│   │   ├── SKILL.md           # Inline Bash workflow for branch cleanup
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   └── TROUBLESHOOTING.md
│   ├── releasing/
│   │   ├── SKILL.md           # Inline Bash workflow + scaffolding instructions
│   │   ├── WORKFLOW.md
│   │   ├── EXAMPLES.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── scripts/           # Scaffold templates (copied to target projects)
│   │   │   ├── release.sh
│   │   │   ├── validate-changelog.sh
│   │   │   ├── extract-release-notes.sh
│   │   │   └── create-github-release.sh
│   │   └── templates/
│   │       └── release.yml    # GitHub Actions workflow template
│   └── creating-worktree/
│       ├── SKILL.md           # Inline Bash workflow for worktree creation
│       ├── WORKFLOW.md
│       ├── EXAMPLES.md
│       └── TROUBLESHOOTING.md
└── README.md
```

## How It Works

### 1. User Invocation
User runs a slash command (explicit control):
```bash
/commit
/create-pr
/create-branch
/worktree
```

### 2. Command Delegation
The command file tells Claude to use the corresponding skill:

```markdown
# commands/commit.md
Use the **Git Commit Workflow** skill to execute the commit workflow with arguments: $ARGUMENTS
```

### 3. Skill Execution
The skill's SKILL.md file contains inline Bash workflow that Claude executes:

```markdown
# skills/creating-commit/SKILL.md
---
name: creating-commit
---
## Commit Workflow Steps

### Step 1: Detect Repositories with Changes
```bash
# Find monorepo root (works from submodules too)
if SUPERPROJECT=$(git rev-parse --show-superproject-working-tree 2>/dev/null)...
```

### Step 2: Select Target Repository
...

(Complete inline workflow in SKILL.md)
```

### 4. Workflow Execution
Claude executes the inline Bash commands using the Bash tool, following the step-by-step workflow in SKILL.md.

## Key Principles

### 1. Commands = User Interface
- Lightweight .md files
- Provide user-facing documentation
- Delegate to skills for complex work
- Maintain explicit user control (not auto-invoked)

### 2. Skills = Implementation
- Contain inline Bash workflows in SKILL.md
- Progressive disclosure via WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md
- All logic visible and maintainable in markdown files
- Follow Claude Code Skills documentation pattern

### 3. Workflow Organization
- Each skill contains complete workflow in SKILL.md
- SKILL.md stays under 500-line official limit
- Supporting docs loaded on-demand
- Bash commands executed via Claude's Bash tool

## Installation Behavior

When a user installs the git plugin via `/plugin install git@arkhe-claude-plugins`:

1. **Plugin files are stored** in Claude Code's plugin storage
2. **Commands become available** as slash commands (e.g., `/commit`)
3. **Skills are loaded** with inline Bash workflows
4. **Documentation available** on-demand (WORKFLOW.md, EXAMPLES.md)
5. **Works immediately** after installation and restart

## Why This Pattern?

### The Evolution

**Early Approach: External Scripts**
```markdown
# skills/creating-commit/scripts/commit.sh
#!/usr/bin/env bash
# 848 lines of bash code
```

**Problems:**
- 2,557 lines of bash scripts to maintain
- 1,164 lines of duplicated common.sh utilities
- Hidden logic not visible in SKILL.md
- Harder to modify and understand

**Current Approach: Inline Bash Workflows**
```markdown
# skills/creating-commit/SKILL.md (414 lines)
## Commit Workflow Steps

### Step 1: Detect Repositories
```bash
if SUPERPROJECT=$(git rev-parse --show-superproject-working-tree...
```
...
```

**Why this works better:**
- All logic visible in SKILL.md files
- No code duplication (eliminated 1,164 lines)
- Easier to maintain and modify
- Progressive disclosure keeps SKILL.md under 500-line limit
- Follows changelog skill pattern (already script-free)

## Benefits of This Architecture

### ✅ Follows Claude Code Best Practices
- Documented in COMMANDS.md and PLUGINS.md
- Skills are the official way to include scripts
- Commands delegate to skills (separation of concerns)

### ✅ Works Everywhere
- ✅ Plugin development environment
- ✅ Consumer projects after `/plugin install`
- ✅ No manual setup required
- ✅ No symlinks or copying needed

### ✅ Maintainable
- Clear separation: Commands (UX) vs Skills (logic)
- All logic visible in SKILL.md files
- No hidden scripts or duplicated code
- Easy to test and debug
- Scalable for new commands

### ✅ User-Friendly
- Install and use immediately
- Explicit user control via slash commands
- Works as documented in README.md

## References

- [Git Plugin README.md](./README.md) - User-facing documentation
