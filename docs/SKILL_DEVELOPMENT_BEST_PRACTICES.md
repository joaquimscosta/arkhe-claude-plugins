# Agent Skill Development: Best Practices

**Primary Source**: [SKILLS.md](./SKILLS.md) (Claude Code-specific)
**Architecture Reference**: [AGENT_SKILLS_OVERVIEW.md](./AGENT_SKILLS_OVERVIEW.md) (cross-platform concepts)
**Official Best Practices**: [Anthropic Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
**Date**: 2026-01-08
**Version**: 2.0

> **Scope**: This document focuses on **Claude Code plugin development**. For Skills across other Claude platforms (API, SDK, claude.ai), see AGENT_SKILLS_OVERVIEW.md.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [YAML Frontmatter Reference](#yaml-frontmatter-reference)
4. [Structure & Sizing](#structure--sizing)
5. [Content & Writing Standards](#content--writing-standards)
6. [File Organization](#file-organization)
7. [Advanced Patterns](#advanced-patterns)
8. [Scripts & Security](#scripts--security)
9. [Testing & Evaluation](#testing--evaluation)
10. [Quick Reference](#quick-reference)

---

## Overview

Agent Skills are modular capabilities that extend Claude's functionality in Claude Code. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant.

### What's New in This Version

This version adds documentation for:

- **5 new YAML frontmatter fields**: `model`, `context`, `agent`, `hooks`, `user-invocable`
- **Forked context execution**: Run Skills in isolated sub-agent contexts
- **Skill-scoped hooks**: Lifecycle event handlers for Skills
- **Skill-subagent integration**: Bidirectional patterns for Skills and agents

### How Skills Work

1. **Discovery**: At startup, Claude loads only `name` and `description` from each Skill (~100 tokens per Skill)
2. **Activation**: When your request matches a Skill's description, Claude asks to use it
3. **Execution**: Claude follows the Skill's instructions, loading referenced files or running scripts as needed

### When to Use Skills vs Other Options

| Use this | When you want to... | When it runs |
|----------|---------------------|--------------|
| **Skills** | Give Claude specialized knowledge | Claude chooses when relevant |
| **Slash commands** | Create reusable prompts | You type `/command` |
| **CLAUDE.md** | Set project-wide instructions | Loaded into every conversation |
| **Subagents** | Delegate tasks to separate context | Claude delegates or you invoke |
| **Hooks** | Run scripts on events | Fires on specific tool events |

---

## Core Principles

### 1. Conciseness: Context Windows Are Shared Resources

**Principle**: Only include information Claude doesn't already have.

The system loads skill metadata at startup, reads SKILL.md when relevant, and accesses additional files on-demand—meaning verbose documentation directly competes with conversation history.

- ✅ Assume Claude is already highly intelligent
- ✅ Add only novel information specific to your domain
- ❌ Avoid over-explaining general programming concepts
- ❌ Don't repeat what Claude already knows

**Challenge each piece of information**: "Does Claude need this, or does Claude already know this?"

### 2. Appropriate Freedom Levels

**Principle**: Match specificity to task fragility.

| Freedom Level | Format | When to Use |
|---------------|--------|-------------|
| **High** | Text instructions | Multiple valid approaches, context determines best path |
| **Medium** | Pseudocode with parameters | Preferred pattern exists but variation acceptable |
| **Low** | Specific scripts | Fragile operations, exact sequences required |

### 3. Progressive Disclosure

**Principle**: Load only what's needed, when it's needed.

```
Level 1: Metadata (~100 tokens) - Always loaded
Level 2: SKILL.md body (<5k tokens) - Loaded when triggered
Level 3: Resources (unlimited) - Loaded as needed or executed
```

### 4. One-Level Deep References

**Principle**: Keep file references shallow for easier navigation.

- ✅ `SKILL.md` → `EXAMPLES.md` (one level)
- ❌ `SKILL.md` → `advanced.md` → `details.md` (two levels)

### 5. Model-Specific Testing

**Principle**: Effectiveness varies across models.

Test with the lowest-tier model you intend to support:
- **Haiku** - Fast, efficient, less capable
- **Sonnet** - Balanced performance
- **Opus** - Most capable

Guidance sufficient for Opus may need enhancement for Haiku.

---

## YAML Frontmatter Reference

Every Skill requires a `SKILL.md` file with YAML frontmatter between `---` markers.

### Required Fields

| Field | Max Length | Description |
|-------|------------|-------------|
| `name` | 64 chars | Skill identifier. Lowercase letters, numbers, hyphens only. Cannot contain "anthropic" or "claude". |
| `description` | 1,024 chars | What the Skill does and when to use it. Claude uses this to decide when to apply the Skill. |

### Optional Fields

| Field | Description | Example |
|-------|-------------|---------|
| `allowed-tools` | Tools Claude can use without permission when Skill is active | `Read, Grep, Glob` |
| `model` | Model to use when Skill is active | `claude-sonnet-4-20250514` |
| `context` | Set to `fork` to run in isolated sub-agent context | `fork` |
| `agent` | Agent type when `context: fork` is set | `Explore`, `Plan`, `general-purpose`, or custom agent name |
| `hooks` | Skill-scoped lifecycle hooks | See [Advanced Patterns](#skill-scoped-hooks) |
| `user-invocable` | Set to `false` to hide from slash command menu | `false` |

### Complete Field Reference

#### name

```yaml
name: pdf-processing
```

**Constraints**:
- Only lowercase letters, numbers, and hyphens
- Cannot contain XML tags
- Cannot use reserved words ("anthropic", "claude")
- 1-64 characters
- Should match the directory name

**Naming convention**: Use gerund form (verb + -ing) for clarity:
- ✅ `processing-pdfs`, `analyzing-spreadsheets`, `generating-changelog`
- ❌ `helper`, `utils`, `documents`

#### description

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Writing convention**: Always use **third person** since descriptions inject into system prompts.

- ✅ "This skill should be used when..."
- ✅ "Extracts text from PDF files..."
- ❌ "I can help you process..." (first person)
- ❌ "You should use this when..." (second person)

**Template**:
```
[What it does]. Use when [trigger scenario 1], [trigger scenario 2], or [trigger scenario 3].
```

**Include varied trigger keywords**:
- "extract" → "extract/download/scrape/archive"
- "analyze" → "analyze/research/study/review"

#### allowed-tools

Restricts which tools Claude can use when the Skill is active.

```yaml
# Comma-separated string
allowed-tools: Read, Grep, Glob

# Or YAML list
allowed-tools:
  - Read
  - Grep
  - Glob
```

**Use cases**:
- Read-only Skills that shouldn't modify files
- Skills with limited scope (data analysis only, no file writing)
- Security-sensitive workflows

When omitted, Claude uses its standard permission model.

#### model

Override the model used when this Skill is active.

```yaml
model: claude-sonnet-4-20250514
```

Use when a Skill requires specific model capabilities or when you want consistent behavior regardless of the conversation's default model.

#### context

Run the Skill in an isolated sub-agent context with its own conversation history.

```yaml
context: fork
```

**When to use**:
- Complex multi-step operations that would clutter main conversation
- Skills that need isolated context for cleaner execution
- Analysis tasks that generate extensive intermediate output

See [Forked Context Skills](#forked-context-skills) for complete guidance.

#### agent

Specify which agent type to use when `context: fork` is set.

```yaml
context: fork
agent: Explore
```

**Available agent types**:
- `Explore` - Fast, read-only codebase exploration
- `Plan` - Research and planning tasks
- `general-purpose` - Full capabilities (default)
- Custom agent name from `.claude/agents/`

Only applicable when combined with `context: fork`.

#### hooks

Define hooks scoped to this Skill's lifecycle.

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh $TOOL_INPUT"
          once: true
```

Supports `PreToolUse`, `PostToolUse`, and `Stop` events. See [Skill-Scoped Hooks](#skill-scoped-hooks) for complete guidance.

#### user-invocable

Control whether the Skill appears in the slash command menu.

```yaml
user-invocable: false
```

Set to `false` for Skills that should only be triggered automatically by Claude, not manually invoked by users.

### Example: Complete Frontmatter

```yaml
---
name: code-analysis
description: Comprehensive code quality analysis with security checks. Use when reviewing code quality, checking for vulnerabilities, or analyzing code patterns.
allowed-tools: Read, Grep, Glob, Bash
model: claude-sonnet-4-20250514
context: fork
agent: general-purpose
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
user-invocable: true
---
```

---

## Structure & Sizing

### The Three-Level Architecture

```
Level 1: Metadata (Always Loaded)
├── YAML frontmatter: name + description
├── Size: ~100 tokens per Skill
└── Purpose: Skill discovery

Level 2: Instructions (Loaded When Triggered)
├── SKILL.md body
├── Size: < 500 lines (official maximum)
└── Purpose: Quick start and core guidance

Level 3+: Resources (Loaded As Needed)
├── Supporting docs, scripts, references
├── Size: Unlimited (loaded on-demand or executed)
└── Purpose: Deep dives and deterministic operations
```

### Size Guidelines

| Component | Size Limit | Notes |
|-----------|------------|-------|
| **SKILL.md total** | **< 500 lines** | Official maximum (~2,000-3,000 words) |
| YAML frontmatter | 5-15 lines | Keep concise |
| Supporting docs | Unlimited | Include TOC if >100 lines |
| Scripts | 0 tokens | Executed, not loaded to context |

### What Goes Where

**SKILL.md should contain**:
- ✅ Quick start (essential steps only)
- ✅ Output structure overview
- ✅ Common issues (1-2 per issue) with reference to TROUBLESHOOTING.md
- ✅ Brief examples with reference to EXAMPLES.md
- ✅ References to supporting files (don't embed them)

**SKILL.md should NOT contain**:
- ❌ Detailed step-by-step workflows → Use WORKFLOW.md
- ❌ Complete examples with full code → Use EXAMPLES.md
- ❌ Comprehensive error catalog → Use TROUBLESHOOTING.md
- ❌ Large reference docs → Use references/ directory

### Progressive Disclosure in Practice

**Good** (referencing pattern):
```markdown
## Common Issues

**"Authentication failed"**
- Verify credentials file exists
- Check token hasn't expired

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete error handling.
```

**Bad** (embedding everything):
```markdown
## Common Issues
### Error: Authentication failed
1. Check credentials file...
2. Verify token format...
(100+ lines of detailed troubleshooting)
```

### Optimization Strategy

**Extract detailed content**:
```markdown
<!-- Before: 200 lines embedded -->
## Workflow
### Step 1: Authenticate...
(90 more lines)

<!-- After: Reference -->
## Workflow
See [WORKFLOW.md](WORKFLOW.md) for detailed instructions.
**Quick overview**: Authenticate → Fetch data → Process → Generate output
```

---

## Content & Writing Standards

### Writing Style: Imperative Form

Use imperative/infinitive form (verb-first), not second-person directives.

| ✅ Good (Imperative) | ❌ Avoid (Second-person) |
|---------------------|-------------------------|
| "To accomplish X, do Y" | "You should do X" |
| "Create the skill directory" | "You'll want to create" |
| "Run the validation script" | "You might consider running" |

Apply throughout: SKILL.md, WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md, script comments.

### Terminology Consistency

Pick one term and use it throughout:
- "API endpoint" **or** "URL" - not both
- "field" **or** "element" **or** "control" - pick one
- "extract" **or** "pull" **or** "get" - stay consistent

### Provide One Default Option

**❌ Don't overwhelm**:
```
Use pypdf, pdfplumber, PyMuPDF, pdfrw, pikepdf, or any other PDF library
```

**✅ Provide default with escape hatch**:
```
Use pdfplumber for PDF extraction (or another library if you have a specific preference)
```

### MCP Tool References

Always use fully qualified names: `ServerName:tool_name`

- ✅ `BigQuery:bigquery_schema`
- ❌ `bigquery_schema`

### Templates and Examples

Show input/output pairs for clarity:
- Mark templates as **mandatory** for strict requirements
- Acknowledge **adaptation** for flexible guidance

### Avoid Time-Sensitive Information

**❌ Don't**:
```markdown
Before August 2025, use the old API. After August 2025, use the new API.
```

**✅ Do** (use collapsible sections):
```markdown
## Current Method
Use the v2 API endpoint: `api.example.com/v2/messages`

<details>
<summary>Legacy v1 API (deprecated)</summary>
The v1 API used: `api.example.com/v1/messages`
</details>
```

---

## File Organization

### Recommended Structure

```
.claude/skills/my-skill/
├── SKILL.md                    # Main instructions (<500 lines, REQUIRED)
├── WORKFLOW.md                 # Detailed step-by-step (optional)
├── EXAMPLES.md                 # Usage examples (recommended)
├── TROUBLESHOOTING.md          # Error handling (recommended)
├── scripts/                    # Tier 1: Executable code (0 tokens)
│   ├── main.py
│   └── helper.py
├── references/                 # Tier 2: Docs loaded to context as needed
│   ├── API_REFERENCE.md
│   └── SCHEMA.md
└── assets/                     # Tier 3: Output resources (not loaded)
    ├── templates/
    └── boilerplate/
```

### Three-Tier Resource Architecture

#### Tier 1: `scripts/` - Executable Code

**Purpose**: Deterministic operations executed without loading to context.

**Benefits**:
- Token efficient (0 tokens - executed, not loaded)
- Deterministic, reliable results
- Reusable across sessions

**When to include**:
- Tasks requiring deterministic reliability
- Code that Claude would otherwise rewrite repeatedly
- Complex operations better handled by scripts

#### Tier 2: `references/` - Documentation

**Purpose**: Reference material loaded into context as needed.

**Benefits**:
- Keeps SKILL.md lean
- Loaded only when Claude determines it's needed
- Progressive disclosure in action

**Best practices**:
- Include table of contents in files over 100 lines
- If very large (>10k words), include grep search patterns in SKILL.md
- No duplication: information should live in either SKILL.md or references, not both

#### Tier 3: `assets/` - Output Resources

**Purpose**: Files used in skill output, not loaded to context.

**Examples**: `assets/logo.png`, `assets/slides.pptx`, `assets/frontend-template/`

### File Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| Documentation | UPPERCASE.md | SKILL.md, WORKFLOW.md, EXAMPLES.md |
| Scripts | lowercase_with_underscores.py | main.py, extract_data.py |
| References | UPPERCASE.md in references/ | API_REFERENCE.md, SCHEMA.md |

---

## Advanced Patterns

This section covers advanced Skill features: forked context execution, skill-scoped hooks, and skill-subagent integration.

### Forked Context Skills

Use `context: fork` to run a Skill in an isolated sub-agent context with its own conversation history.

```yaml
---
name: code-analysis
description: Analyze code quality and generate detailed reports
context: fork
---
```

**When to use forked context**:
- Complex multi-step operations that generate extensive intermediate output
- Analysis tasks where you want clean separation from main conversation
- Skills that benefit from isolated context for focused execution

**Combining with agent field**:

```yaml
---
name: codebase-explorer
description: Explore and document codebase structure
context: fork
agent: Explore
---
```

**Available agent types**:

| Agent | Description | Use Case |
|-------|-------------|----------|
| `Explore` | Fast, read-only, uses Haiku | Quick file discovery, code search |
| `Plan` | Research and analysis, uses Sonnet | Planning, context gathering |
| `general-purpose` | Full capabilities, uses Sonnet | Complex tasks requiring modification |
| Custom agent | Your `.claude/agents/` agent | Specialized workflows |

### Skill-Scoped Hooks

Skills can define hooks that run during the Skill's lifecycle. These hooks are scoped to the Skill and only fire when the Skill is active.

```yaml
---
name: secure-operations
description: Perform operations with additional security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh $TOOL_INPUT"
          once: true
---
```

**Supported events**:

| Event | When it fires |
|-------|---------------|
| `PreToolUse` | Before a tool is executed |
| `PostToolUse` | After a tool completes |
| `Stop` | When the Skill execution ends |

**Hook options**:

| Option | Description |
|--------|-------------|
| `matcher` | Tool name to match (e.g., "Bash", "Edit") |
| `type` | Hook type: `command` for shell commands |
| `command` | Command to execute (can use `$TOOL_INPUT`) |
| `once` | If `true`, only run once per session |

**Example: Validation hook**

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "./scripts/lint-file.sh $TOOL_INPUT"
```

For complete hook configuration reference, see [HOOKS.md](./HOOKS.md).

### Skill-Subagent Integration

Skills and subagents can work together in two ways:

#### Pattern 1: Give a Subagent Access to Skills

Subagents don't automatically inherit Skills from the main conversation. To give a custom subagent access to specific Skills, list them in the subagent's `skills` field:

```yaml
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Review code for quality and best practices
skills: pr-review, security-check
---

You are a senior code reviewer...
```

The listed Skills are loaded into the subagent's context when it starts.

**Important**: Built-in agents (Explore, Plan, general-purpose) don't have access to your Skills. Only custom subagents you define in `.claude/agents/` with an explicit `skills` field can use Skills.

#### Pattern 2: Run a Skill in Subagent Context

Use `context: fork` and `agent` to run a Skill in a forked subagent:

```yaml
---
name: deep-analysis
description: Perform deep code analysis
context: fork
agent: code-reviewer
---
```

This runs the Skill using your custom `code-reviewer` agent in an isolated context.

**When to use each pattern**:

| Pattern | Use When |
|---------|----------|
| Skills in subagent | You want a subagent to always have certain Skills available |
| Skill in forked context | You want a specific Skill to run in isolation with a specific agent |

For complete subagent configuration, see [SUBAGENTS.md](./SUBAGENTS.md).

---

## Scripts & Security

### Script Best Practices

#### 1. Solve, Don't Punt

Handle error conditions explicitly rather than delegating to Claude.

**❌ Punting errors**:
```python
if not os.path.exists(path):
    raise FileNotFoundError(f"File {path} not found")
```

**✅ Solving the problem**:
```python
try:
    with open(path) as f:
        return f.read()
except FileNotFoundError:
    print(f"File {path} not found, creating default")
    with open(path, 'w') as f:
        f.write(DEFAULT_CONTENT)
    return DEFAULT_CONTENT
```

#### 2. Document Constants

Every "magic number" needs justification.

**❌ Undocumented**:
```python
REQUEST_TIMEOUT = 30
```

**✅ Documented**:
```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections and large responses
REQUEST_TIMEOUT = 30
```

#### 3. Make Scripts Executable

```bash
chmod +x scripts/*.py
```

Include shebang in all scripts:
```python
#!/usr/bin/env python3
```

### Package Dependencies

Document all required packages in the Skill description or SKILL.md.

**In description**:
```yaml
description: Extract text from PDFs. Requires pypdf and pdfplumber packages.
```

**In SKILL.md**:
````markdown
## Requirements

Install required packages:
```bash
pip install pdfplumber
```
````

**Note**: Claude will automatically install required dependencies or ask for permission when needed.

### Authentication Patterns

**Good pattern** (user-provided credentials):
```python
# User manually sets token in config file
# Script reads from known location
config_file = project_root / ".config" / "settings.json"
api_token = json.loads(config_file.read_text()).get("api_token")
```

**Why it's secure**:
- ✅ User provides credentials explicitly
- ✅ Credentials stored locally (not in code)
- ✅ No auto-scraping or credential theft
- ✅ Clear documentation of what's needed

**Bad pattern**:
```python
# ❌ Don't do this
username = input("Enter username: ")
password = input("Enter password: ")
```

### Security Checklist

Before publishing, verify:

- [ ] No `eval()` or `exec()` calls
- [ ] No obfuscated code (base64, hex strings)
- [ ] No unexpected network destinations
- [ ] No credential harvesting beyond documented authentication
- [ ] All operations match stated purpose
- [ ] Clear logging (no sensitive data in logs)
- [ ] Error messages don't leak secrets

---

## Testing & Evaluation

### Build Evaluations First

Create test scenarios BEFORE extensive documentation.

**Process**:
1. Establish baseline performance without the Skill
2. Create the Skill
3. Measure whether the Skill improves results
4. Iterate based on measurements

**Evaluation structure**:
```json
{
  "skills": ["skill-name"],
  "query": "User request",
  "files": ["relevant files"],
  "expected_behavior": [
    "Specific observable outcome 1",
    "Specific observable outcome 2"
  ]
}
```

### Iterative Development

1. **Complete a task with Claude normally** - Note what context you repeatedly provide
2. **Create a Skill** - Capture that repeated context
3. **Test with similar tasks** - What gaps exist?
4. **Observe Claude's behavior** - Unexpected exploration paths indicate structural improvements needed
5. **Iterate based on real usage** - Don't guess, iterate based on actual use

### Testing Across Models

Always test with the lowest-tier model you intend to support. If guidance works for Haiku, it will work for all models.

### Real-World Testing

Don't just test happy paths:
- ✅ Test with incomplete information
- ✅ Test with edge cases
- ✅ Test with ambiguous inputs
- ✅ Test with errors and failures
- ✅ Test with team members (fresh perspectives)

---

## Quick Reference

### Common Pitfalls

| Problem | Solution |
|---------|----------|
| SKILL.md too long (500+ lines) | Split into WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md |
| Skill not triggering | Add specific trigger keywords to description |
| Vague description | Include "what it does" + "when to use" + specific capabilities |
| Broken file references | Search `grep -r "old-filename.md" .` after any file move |
| Non-executable scripts | Add shebang + `chmod +x scripts/*.py` |
| Too many options given | Provide one default with escape hatch |
| Deeply nested references | Keep one level deep from SKILL.md |
| Inconsistent terminology | Pick one term, use throughout |
| Windows-style paths | Always use Unix-style `/` in paths |
| Undocumented constants | Add comment explaining every magic number |
| Plugin Skills not appearing | Clear cache: `rm -rf ~/.claude/plugins/cache`, reinstall |

### Anti-Patterns

| ❌ Avoid | ✅ Instead |
|---------|-----------|
| `scripts\helper.py` | `scripts/helper.py` |
| "Use pypdf, pdfplumber, PyMuPDF, or..." | "Use pdfplumber (or another library if preferred)" |
| `SKILL.md` → `A.md` → `B.md` → `C.md` | Keep one level deep |
| "Helps with data" | "Extract tables from CSV files. Use when analyzing spreadsheets." |
| First/second person in descriptions | Third person: "This skill should be used when..." |

### Pre-Publication Checklist

#### Structure
- [ ] SKILL.md under 500 lines
- [ ] Supporting docs split out (EXAMPLES.md, TROUBLESHOOTING.md)
- [ ] One-level deep references
- [ ] All file references valid

#### YAML Frontmatter
- [ ] Name: lowercase-with-hyphens, ≤64 chars
- [ ] Description: ≤1,024 chars, third person
- [ ] Description includes "what" and "when"
- [ ] No reserved words ("anthropic", "claude")

#### Code Quality
- [ ] Scripts executable (`chmod +x`)
- [ ] Shebang added (`#!/usr/bin/env python3`)
- [ ] Standard library preferred
- [ ] Constants documented
- [ ] Errors handled explicitly

#### Security
- [ ] No `eval()` or `exec()`
- [ ] No credential harvesting
- [ ] Clear auth documentation
- [ ] No obfuscated code

#### Testing
- [ ] Tested with target models (Haiku/Sonnet/Opus)
- [ ] Tested with edge cases
- [ ] Skill triggers correctly
- [ ] Scripts execute without errors

### Documentation Templates

#### SKILL.md Template

````markdown
---
name: your-skill-name
description: What it does. Use when [triggers].
---

# Skill Name

Brief description (1-2 sentences).

## Quick Start

```bash
# Most common usage
script.py "input" --flag
```

## Output Structure

```
output/
├── result1.txt
└── result2.json
```

## Common Issues

**"Error message"**
- Quick fix 1
- Quick fix 2

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete error handling.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for complete examples.
````

#### EXAMPLES.md Template

````markdown
# Usage Examples

## Table of Contents
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)

## Basic Usage

### Example 1: Simplest Case

```bash
script.py "input"
```

**Output:**
```
Expected output here
```
````

#### TROUBLESHOOTING.md Template

````markdown
# Troubleshooting Guide

## Table of Contents
- [Error Category 1](#error-category-1)

## Error Category 1

### Error: "Specific error message"

**Symptoms:**
```
Error output
```

**Causes:**
- Cause 1
- Cause 2

**Solutions:**
1. Solution 1
2. Solution 2
````

### Resources

**Official Documentation**:
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
- [Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Using Skills in Claude Code](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills)

**Official Skill Examples**:
- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Reference implementations
- [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) - Official reference implementation

**Local Documentation**:
- [SKILLS.md](./SKILLS.md) - Claude Code-specific guide
- [SUBAGENTS.md](./SUBAGENTS.md) - Subagent configuration
- [HOOKS.md](./HOOKS.md) - Hook configuration

---

**Document Version**: 2.0
**Last Updated**: 2026-01-08
