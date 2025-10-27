# Git Plugin Architecture

## Overview

The Git plugin uses a **Hybrid Commands + Skills** pattern that aligns with Claude Code's official plugin system documentation.

## Naming Convention

### Hybrid Approach: Simple Directories + Descriptive Names

**Directory Names**: Simple, clean (`commit/`, `pr/`, `branch/`, `changelog/`)
- Brief and concise
- No redundancy with parent directory structure (`git/skills/`)
- Matches existing `changelog/` pattern

**Skill Names** (YAML frontmatter): Descriptive with context (`Git Commit Workflow`)
- Includes "Git" prefix for clarity when Claude verbalizes
- Natural reading: "I'm using the Git Commit Workflow"
- Provides plugin context without directory redundancy

**Example**:
```yaml
# Directory: git/skills/commit/
# Skill name in SKILL.md:
---
name: Git Commit Workflow
---
```

This gives us the best of both approaches:
- ✅ Clean, brief directory structure
- ✅ Descriptive skill names for user communication
- ✅ Plugin context clear in skill names
- ✅ No path redundancy (`git/skills/git-commit/` ❌)

## Architecture Pattern

### Why This Pattern?

According to Claude Code documentation:
- **Commands**: Simple prompts with optional inline bash commands
- **Skills**: Complex capabilities with scripts and multiple files

The git plugin requires complex bash scripts (10KB+), making Skills the appropriate choice.

### Structure

```
git/
├── commands/              # User-facing slash commands
│   ├── commit.md          # /commit command
│   ├── create-pr.md       # /create-pr command
│   ├── create-branch.md   # /create-branch command
│   └── changelog.md       # /changelog command
├── skills/                # Skills with scripts
│   ├── commit/            # Simple directory name
│   │   ├── SKILL.md       # Skill name: "Git Commit Workflow"
│   │   └── scripts/
│   │       ├── commit.sh  # Main workflow script
│   │       └── common.sh  # Shared utilities
│   ├── pr/                # Simple directory name
│   │   ├── SKILL.md       # Skill name: "Git PR Workflow"
│   │   └── scripts/
│   │       ├── pr.sh
│   │       └── common.sh
│   ├── branch/            # Simple directory name
│   │   ├── SKILL.md       # Skill name: "Git Branch Workflow"
│   │   └── scripts/
│   │       ├── branch.sh
│   │       └── common.sh
│   └── changelog/         # Simple directory name
│       └── SKILL.md       # Skill name: "Git Changelog Generation"
└── README.md
```

## How It Works

### 1. User Invocation
User runs a slash command (explicit control):
```bash
/commit
/create-pr
/create-branch
```

### 2. Command Delegation
The command file tells Claude to use the corresponding skill:

```markdown
# commands/commit.md
Use the **Git Commit Workflow** skill to execute the commit workflow with arguments: $ARGUMENTS
```

### 3. Skill Execution
The skill's SKILL.md file instructs Claude to execute the bash script:

```markdown
# skills/commit/SKILL.md
---
name: Git Commit Workflow
---
Execute the commit workflow by running the bash script:
git/skills/commit/scripts/commit.sh $ARGUMENTS
```

### 4. Script Processing
Claude uses the Bash tool to execute the script, which handles all complex logic.

## Key Principles

### 1. Commands = User Interface
- Lightweight .md files
- Provide user-facing documentation
- Delegate to skills for complex work
- Maintain explicit user control (not auto-invoked)

### 2. Skills = Implementation
- Contain complex logic and scripts
- Scripts travel with the plugin when installed
- Can include multiple supporting files
- Follow Claude Code Skills documentation pattern

### 3. Script Organization
- Each skill has its own scripts/ directory
- Common utilities can be copied or shared
- Scripts use absolute path resolution internally
- Executable permission required (`chmod +x`)

## Installation Behavior

When a user installs the git plugin via `/plugin install git@arkhe-claude-plugins`:

1. **Plugin files are stored** in Claude Code's plugin storage
2. **Commands become available** as slash commands (e.g., `/commit`)
3. **Skills are available** for Claude to invoke
4. **Scripts travel with the plugin** (no manual copying needed)
5. **Works immediately** after installation and restart

## Why This Pattern?

### The Old Approach (What We Avoided)

Some early attempts used inline script references in commands:

```markdown
# commands/commit.md
!.claude/scripts/commit.sh $ARGUMENTS
```

**Problems with this approach:**
- `.claude/scripts/` doesn't exist after plugin install
- No documented mechanism to distribute scripts
- Only works if users manually copy scripts
- Incompatible with Claude Code plugin system

### The Correct Approach (Current Implementation)

**Commands delegate to Skills:**
```markdown
# commands/commit.md
Use the **Git Commit Workflow** skill with arguments: $ARGUMENTS
```

**Skills contain scripts:**
```markdown
# skills/commit/SKILL.md
Execute: git/skills/commit/scripts/commit.sh $ARGUMENTS
```

**Why this works:**
- Skills are the official way to include scripts in plugins
- Scripts are bundled with the plugin during installation
- Follows documented Claude Code patterns
- Works identically in development and production

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
- Scripts organized by function
- Easy to test and debug
- Scalable for new commands

### ✅ User-Friendly
- Install and use immediately
- Explicit user control via slash commands
- Works as documented in README.md

## References

- [Git Plugin README.md](./README.md) - User-facing documentation
