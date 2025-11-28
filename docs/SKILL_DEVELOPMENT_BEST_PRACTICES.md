# Agent Skill Development: Best Practices

**Based On**: AGENT_SKILLS_OVERVIEW.md + skill-creator Reference + [Official Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md)
**Date**: 2025-10-27
**Purpose**: Document lessons learned and best practices for creating Claude Code Skills

> **📚 Official Reference**: This document integrates guidance from [Anthropic's Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md) with real-world implementation lessons from this repository's skills.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Structure & Sizing Best Practices](#structure--sizing-best-practices)
3. [YAML Frontmatter Guidelines](#yaml-frontmatter-guidelines)
4. [Content & Writing Standards](#content--writing-standards)
5. [Degrees of Freedom](#degrees-of-freedom)
6. [File Organization Patterns](#file-organization-patterns)
7. [Workflows and Feedback Loops](#workflows-and-feedback-loops)
8. [Scripts & Security](#scripts--security)
9. [Documentation Templates](#documentation-templates)
10. [Evaluation and Iteration](#evaluation-and-iteration)
11. [Common Pitfalls](#common-pitfalls)
12. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
13. [Anatomy of a Well-Designed Skill](#anatomy-of-a-well-designed-skill)
14. [Quick Checklist for New Skills](#quick-checklist-for-new-skills)
15. [Skills Documentation Reference](#skills-documentation-reference)
16. [Resources](#resources)

---

## Core Principles

> **Source**: [Official Best Practices - Core Principles](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#core-principles)

### 1. Conciseness: Context Windows Are Shared Resources

**Principle**: Only include information Claude doesn't already have.

The system loads skill metadata at startup, reads SKILL.md when relevant, and accesses additional files on-demand—meaning verbose documentation directly competes with conversation history and other context.

**Implementation**:
- ✅ Assume Claude is already highly intelligent
- ✅ Add only novel information specific to your domain
- ❌ Avoid over-explaining general programming concepts
- ❌ Don't repeat what Claude already knows

**Challenge each piece of information**: "Does Claude need this, or does Claude already know this?"

### 2. Appropriate Freedom Levels

**Principle**: Match specificity to task fragility.

- **High Freedom** (text instructions): Simple decisions, multiple valid approaches
- **Medium Freedom** (pseudocode): Preferred patterns with acceptable variation
- **Low Freedom** (specific scripts): Fragile operations requiring exact sequences

See [Degrees of Freedom](#degrees-of-freedom) section for detailed guidance.

### 3. Model-Specific Testing

**Principle**: Effectiveness varies across models.

Skills should be tested with:
- **Haiku** - Fast, efficient, less capable
- **Sonnet** - Balanced performance
- **Opus** - Most capable

Guidance sufficient for Opus may need enhancement for Haiku.

**Best practice**: Test with the lowest-tier model you intend to support.

### 4. Progressive Disclosure

**Principle**: Load only what's needed, when it's needed.

See [Structure & Sizing Best Practices](#structure--sizing-best-practices) section for detailed implementation.

### 5. One-Level Deep References

**Principle**: Keep file references shallow for easier navigation.

- ✅ `SKILL.md` → `advanced.md` (one level)
- ❌ `SKILL.md` → `advanced.md` → `details.md` (two levels)

**Why**: Reduces cognitive load and makes skills easier to maintain.

---

## Structure & Sizing Best Practices

> **Source**: [Official Best Practices - File Structure and Progressive Disclosure](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#file-structure-and-progressive-disclosure)

### The Three-Level Architecture

**Principle**: Load only what's needed, when it's needed. This is the foundation of effective skill design.

```
Level 1: Metadata (Always Loaded)
├── YAML frontmatter: name + description
├── Size: 5-10 lines
└── Purpose: Skill discovery

Level 2: Instructions (Loaded When Triggered)
├── SKILL.md body
├── Size: < 500 lines (official maximum)
└── Purpose: Quick start and core guidance

Level 3+: Resources (Loaded As Needed)
├── Supporting docs (WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md)
├── Executable scripts
├── Size: Unlimited (loaded on-demand or executed)
└── Purpose: Deep dives and deterministic operations
```

### Size Guidelines

| Component | Size Limit | Notes |
|-----------|------------|-------|
| **SKILL.md total** | **< 500 lines** | Official maximum (typically 2,000-3,000 words) |
| YAML frontmatter | 5-10 lines | See [YAML Frontmatter Guidelines](#yaml-frontmatter-guidelines) |
| Supporting docs | Unlimited | Include TOC if >100 lines |
| Scripts | 0 tokens | Executed, not loaded to context |

**Measurement**: Official guidance uses **line count**, not word count.

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

**Good example** (referencing pattern):
```markdown
## Common Issues

**"Authentication failed"**
- Verify credentials file exists
- Check token hasn't expired

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete error handling.
```

**Bad example** (embedding everything):
```markdown
<!-- ❌ Don't do this -->
## Common Issues

### Error: Authentication failed
1. Check credentials file...
2. Verify token format...
(100+ lines of detailed troubleshooting)

### Error: Network timeout
1. Check connectivity...
(50+ more lines)
```

### Optimization Strategies

#### Strategy 1: Extract Detailed Content

Extract workflows to separate files, keep only overview in SKILL.md.

**Before** (bloated SKILL.md):
```markdown
## Workflow

### Step 1: Authenticate
1. Create cookies.json file
2. Add access_token from browser
3. Add client_id from browser
(90 more lines)
```

**After** (optimized):
```markdown
## Workflow

See [WORKFLOW.md](WORKFLOW.md) for detailed instructions.

**Quick overview**: Authenticate → Fetch data → Process → Generate output
```

**Savings**: ~80 lines

#### Strategy 2: Reference vs. Embed Examples

**Before**:
```markdown
## Examples
Example 1: Basic usage (50 lines)
Example 2: Advanced usage (50 lines)
Example 3: Error handling (50 lines)
```

**After**:
```markdown
## Examples

See [EXAMPLES.md](EXAMPLES.md) for:
- Basic usage
- Advanced usage with custom options
- Error handling patterns
```

**Savings**: ~140 lines

---

## YAML Frontmatter Guidelines

> **Source**: [Official Best Practices - YAML Frontmatter](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#yaml-frontmatter-requirements)

### Required Fields

```yaml
---
name: lowercase-with-hyphens  # 64 characters max
description: What this skill does and when to use it  # 1,024 characters max
---
```

### Naming Conventions

**Format**: Use gerund form (verb + -ing) for clarity

✅ **Good Examples**:
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`

❌ **Avoid**:
- Vague terms: `helper`, `utils`, `tools`
- Generic names: `documents`, `data`, `processor`
- Reserved terms: `anthropic`, `claude`

**Constraints**:
- Only lowercase letters, numbers, and hyphens
- Cannot contain XML tags
- Cannot use reserved words ("anthropic", "claude")
- Must be between 1-64 characters

### Limits

| Field | Maximum | Recommended | Purpose |
|-------|---------|-------------|---------|
| `name` | 64 chars | 20-40 chars | Concise identification |
| `description` | 1,024 chars | 200-400 chars | Discovery and triggering |

### Description Best Practices

> **Source**: [Official Best Practices - Writing Effective Descriptions](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#writing-effective-descriptions)

**Writing Convention**: Always write in **third person** since descriptions inject into system prompts.

**Template**:
```
[What it does]. Use when [trigger scenario 1], [trigger scenario 2], or [trigger scenario 3].
```

**Third-person examples**:
- ✅ "Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
- ✅ "This skill should be used when..."
- ✅ "Guide for creating effective skills"

**First/Second-person (avoid)**:
- ❌ "I can help you process Excel files" (first person)
- ❌ "You should use this when..." (second person)
- ❌ "Helps with documents" (vague)

**Why this matters**: Descriptions are injected into Claude's system prompt, so third-person maintains consistent voice.

**Good Example** (Mermaid Diagramming):
> Creates and edits Mermaid diagrams for flowcharts, sequence diagrams, ERDs, state machines, architecture diagrams, process flows, timelines, and more. Use when user mentions diagram, flowchart, mermaid, visualize, refactor diagram, sequence diagram, ERD, architecture diagram, process flow, state machine, or needs visual documentation.

**Why it works**:
- ✅ Lists specific capabilities (flowcharts, sequence diagrams, ERDs...)
- ✅ Defines clear triggers ("diagram", "flowchart", "visualize")
- ✅ Includes use case (visual documentation)
- ✅ Under 300 characters (plenty of room to grow)

**Bad Example**:
> Creates diagrams. Use when needed.

**Why it fails**:
- ❌ Vague about capabilities
- ❌ No specific triggers
- ❌ No use case context

### Trigger Keywords

Include varied keywords for better skill discovery:

**Example expansions**:
- "extract" → "extract/download/scrape/archive"
- "analyze" → "analyze/research/study/review"
- "transcript" → "transcript/captions/subtitles"

### Optional: allowed-tools Field

**Purpose**: Restrict which tools Claude can use when a skill is active.

**Source**: [SKILLS.md - Restrict tool access](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills#restrict-tool-access-with-allowed-tools)

**Syntax**:
```yaml
---
name: safe-file-reader
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---
```

**When specified**: Claude can only use the listed tools without asking for permission.

**When omitted**: Claude asks for permission to use tools as normal (standard permission model).

**Use cases**:
- ✅ Read-only skills that shouldn't modify files
- ✅ Skills with limited scope (e.g., only data analysis, no file writing)
- ✅ Security-sensitive workflows where you want to restrict capabilities

**Example - Code review skill (read-only)**:
```yaml
---
name: code-reviewer
description: Review code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
allowed-tools: Read, Grep, Glob
---
```

**Important**: `allowed-tools` is only supported for skills in Claude Code.

---

## Content & Writing Standards

> **Sources**: [Official Best Practices - Content Guidelines](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#content-guidelines) + [skill-creator reference](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md)

### Writing Style: Imperative Form

**Principle**: Use imperative/infinitive form (verb-first), not second-person directives.

**✅ Good** (Imperative):
- "To accomplish X, do Y"
- "Create the skill directory"
- "Run the validation script"

**❌ Avoid** (Second-person):
- "You should do X"
- "You'll want to create"
- "You might consider running"

**Why**: Maintains consistency and clarity for AI consumption. Treats skills as procedural documentation.

**Apply throughout**: SKILL.md, WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md, script comments

**Example transformation:**
```markdown
❌ Before: "If you want to extract content, you should first authenticate..."
✅ After: "To extract content, first authenticate by creating cookies.json"
```

### Terminology Consistency

**Principle**: Choose one term and use it throughout.

**Examples**:
- Pick "API endpoint" **or** "URL" - not both
- Use "field," "box," "element," **or** "control" - stay consistent
- Select "extract," "pull," "get," **or** "retrieve" - pick one

**Why**: Reduces confusion and makes skills easier to follow.

### Avoid Time-Sensitive Information

**❌ Don't**:
```markdown
Before August 2025, use the old API. After August 2025, use the new API.
```

**✅ Do** (use collapsible sections):
```markdown
## Current Method
Use the v2 API endpoint: `api.example.com/v2/messages`

## Old Patterns
<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
</details>
```

### Templates and Examples

**Principle**: Show input/output pairs for clarity.

- Mark templates as **mandatory** for strict requirements
- Acknowledge **adaptation** for flexible guidance

**Example**:

## Output Format

Use this template structure:
```json
{"title": "...", "sections": [...]}
```

Adapt field names based on the data source schema.

### Provide One Default Option

**❌ Don't overwhelm**:
"Use pypdf, pdfplumber, PyMuPDF, pdfrw, pikepdf, or any other PDF library"

**✅ Provide default with escape hatch**:
"Use pdfplumber for PDF extraction (or another library if you have a specific preference)"

### MCP Tool References

Always use **fully qualified names**: `ServerName:tool_name`

**Examples**:
- `BigQuery:bigquery_schema` (not `bigquery_schema`)
- `GitHub:create_issue` (not `create_issue`)

### Documentation File Structure

**Required**:
- `SKILL.md` - Main instructions (<500 lines)

**Highly recommended**:
- `EXAMPLES.md` - Usage examples
- `TROUBLESHOOTING.md` - Error handling

**Optional**:
- `WORKFLOW.md` - Detailed steps
- `references/` - API docs, schemas, policies (include TOC if >100 lines)
- `assets/` - Templates, images, boilerplate

See [File Organization Patterns](#file-organization-patterns) for detailed structure.

---

## Degrees of Freedom

> **Source**: [Official Best Practices - Degrees of Freedom Guidance](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#degrees-of-freedom-guidance)

**Principle**: Match the level of specificity to the fragility of the task.

### High Freedom (Text-Based Instructions)

**When to use**: Multiple valid approaches exist and context determines the best path.

**Format**: Natural language instructions with flexibility.

**Example use cases**:
- Code review processes (multiple valid review approaches)
- Content generation with stylistic variation
- Research and analysis tasks

**Example**:
```markdown
Review the codebase for:
- Code quality and best practices
- Performance implications
- Security vulnerabilities
- Documentation completeness

Provide actionable recommendations prioritized by impact.
```

### Medium Freedom (Pseudocode with Parameters)

**When to use**: A preferred pattern exists but variation is acceptable.

**Format**: Structured guidance with parameters Claude can adapt.

**Example use cases**:
- Report generation with templates
- API integration with configurable endpoints
- Data transformation with schema variations

**Example**:
```markdown
Generate report following this structure:
1. Executive summary (2-3 paragraphs)
2. Key findings (bulleted list)
3. Detailed analysis (sections per finding)
4. Recommendations (prioritized)

Adapt tone and depth based on audience identified in context.
```

### Low Freedom (Specific Scripts, Minimal Parameters)

**When to use**: Operations are fragile, consistency is critical, or exact sequences must be followed.

**Format**: Executable scripts with specific parameters.

**Example use cases**:
- Database migrations (must execute in exact order)
- API authentication flows (specific token refresh sequences)
- Data extraction with complex parsing logic

**Example**:
```python
#!/usr/bin/env python3
# Generate changelog from git history with specific formatting and grouping
python3 scripts/generate_changelog.py --since "v1.0.0" --format "keepachangelog"
```

**Why use scripts**: Deterministic reliability, token efficiency (executed not loaded), reusable across sessions.

### Decision Framework

Ask these questions when designing a skill:

1. **Is there one correct approach?** → Low freedom (script)
2. **Are there multiple valid approaches?** → High freedom (text)
3. **Is there a preferred approach with acceptable variations?** → Medium freedom (pseudocode)
4. **Does the task require exact sequencing?** → Low freedom (script)
5. **Can Claude adapt the approach based on context?** → High/Medium freedom

---

## File Organization Patterns

### Recommended Structure

**Source**: [skill-creator three-tier resource organization](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md)

```
.claude/skills/my-skill/
├── SKILL.md                    # Main instructions (<500 lines)
├── WORKFLOW.md                 # Detailed step-by-step (optional)
├── EXAMPLES.md                 # Usage examples (recommended)
├── TROUBLESHOOTING.md          # Error handling (recommended)
├── scripts/                    # Tier 1: Executable code
│   ├── main.py                 # Entry point
│   ├── module1.py              # Supporting modules
│   └── module2.py
├── references/                 # Tier 2: Documentation loaded to context
│   ├── API_REFERENCE.md        # API documentation (include TOC if >100 lines)
│   ├── SCHEMA.md               # Data schemas
│   └── POLICY.md               # Domain knowledge, policies
└── assets/                     # Tier 3: Output resources (not loaded)
    ├── templates/
    │   └── template.md         # Output templates
    └── boilerplate/
        └── starter.html        # Boilerplate code
```

### Three-Tier Resource Architecture

**Source**: [skill-creator resource organization rationale](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md)

#### Tier 1: `scripts/` - Executable Code
**Purpose**: Deterministic operations executed without loading to context.

**When to include**:
- Tasks requiring deterministic reliability
- Code that Claude would otherwise rewrite repeatedly
- Complex operations better handled by scripts

**Benefits**:
- Token efficient (0 tokens - executed, not loaded)
- Deterministic, reliable results
- Reusable across sessions

**Examples**: Data processing, API calls, file transformations

---

#### Tier 2: `references/` - Documentation
**Purpose**: Reference material loaded into context as needed.

**When to include**:
- Database schemas, API specifications
- Company policies, domain knowledge
- Detailed workflow guides
- Large documentation (>10k words)

**Benefits**:
- Keeps SKILL.md lean
- Loaded only when Claude determines it's needed
- Progressive disclosure in action

**Best practices**:
- **Table of contents**: Include a table of contents in reference files over 100 lines (official requirement)
- **Search patterns**: If files are very large (>10k words), include grep search patterns in SKILL.md
- **No duplication**: Information should live in either SKILL.md or references files, not both

**Examples**: API_REFERENCE.md, DATABASE_SCHEMA.md, COMPANY_POLICY.md

---

#### Tier 3: `assets/` - Output Resources
**Purpose**: Files used in skill output, not loaded to context.

**When to include**:
- Templates (HTML, React, PowerPoint)
- Images, icons, logos
- Fonts, sample documents
- Boilerplate code

**Benefits**:
- Separates output resources from documentation
- Enables Claude to use files without loading them to context
- Keeps context window clean

**Examples**: `assets/logo.png`, `assets/slides.pptx`, `assets/frontend-template/`

### File Naming Conventions

**Instructions** (Markdown files):
- `SKILL.md` - Main instructions (REQUIRED)
- `WORKFLOW.md` - Detailed steps (optional but recommended)
- `EXAMPLES.md` - Usage examples (recommended)
- `TROUBLESHOOTING.md` - Error handling (recommended)
- Use UPPERCASE for documentation files
- Use descriptive names (not `DOC1.md`, `DOC2.md`)

**Scripts** (Python files):
- `main.py` or `extract.py` - Entry point
- `module_name.py` - Lowercase with underscores
- Make scripts executable: `chmod +x *.py`
- Include shebang: `#!/usr/bin/env python3`

**References** (Documentation):
- Use UPPERCASE.md for reference documentation
- Use descriptive names (API_REFERENCE.md, SCHEMA.md)
- Store in `references/` directory

**Assets** (Output resources):
- Use descriptive names
- Group by type in subdirectories within `assets/`
- Examples: `assets/templates/`, `assets/images/`, `assets/boilerplate/`

---

## Workflows and Feedback Loops

> **Source**: [Official Best Practices - Workflows and Feedback Loops](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#workflows-and-feedback-loops)

### Workflow Structure

**For complex operations**: Break into sequential, numbered steps.

**Best practice**: Provide a checklist Claude can copy and check off:

Copy this checklist and track your progress:

```
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Why this works**: Explicit checklists help Claude track progress and reduce missed steps.

### Validation Patterns

**Principle**: Implement feedback loops to improve output quality.

**Pattern**: Run validator → Fix errors → Repeat

**Example workflow**:
```markdown
1. Generate output
2. Run validation script: `python3 scripts/validate.py output.json`
3. If errors found, fix and repeat step 2
4. Once validation passes, proceed
```

**For code-heavy skills**:
1. Analyze requirements
2. Create implementation plan
3. Validate plan (run through checklist)
4. Execute implementation
5. Verify output (run tests, validation scripts)

**Why this works**: Validation loops catch errors early and significantly improve output quality.

### Intermediate Verification

**For complex operations**: Use plan-validate-execute pattern.

**Steps**:
1. Claude creates a structured plan file
2. A script validates the plan (checks for completeness, conflicts)
3. Execution follows only after validation passes

**Example**:
```markdown
1. Create migration plan: `plan.json`
2. Validate plan: `python3 scripts/validate_plan.py plan.json`
3. If validation passes, execute: `python3 scripts/execute_plan.py plan.json`
```

---

## Scripts & Security

> **Sources**: [Official Best Practices - Executable Scripts and Code](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#executable-scripts-and-code) + [SKILLS.md - Multi-file Skill example](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills#multi-file-skill)

### Script Best Practices

#### 1. Solve, Don't Punt

**Principle**: Handle error conditions explicitly rather than delegating to Claude.

❌ **Don't punt errors**:
```python
if not os.path.exists(path):
    raise FileNotFoundError(f"File {path} not found")
```

✅ **Solve the problem**:
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

**Every "magic number" needs justification**.

❌ **Undocumented constant**:
```python
REQUEST_TIMEOUT = 30
```

✅ **Documented constant**:
```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections and large responses
REQUEST_TIMEOUT = 30
```

#### 3. Provide Utility Scripts

**Benefits**:
- More reliable than generated code
- Save tokens (executed, not loaded to context)
- Ensure consistency across uses

**Make clear**: Should Claude execute the script or read it as reference? (Most common: execute)

#### 4. Visual Analysis

**When inputs can be rendered as images**: Have Claude analyze them visually rather than text representations.

**Example use cases**: Screenshots of UI elements, diagrams, flowcharts, data visualizations

### Package Dependencies

**Document all required packages** in the skill description or SKILL.md.

**Note**: Claude.ai can install packages, but the Anthropic API has no network access during code execution.

❌ **Don't assume packages are available**:
```markdown
Use the pdf library to process files.
```

✅ **Be explicit about dependencies**:

Install required package:
```bash
pip install pdfplumber
```

Then use:
```python
from pdfplumber import open
```

**Example** (from official docs):
```yaml
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber packages.
```

### Runtime Environment

**Allowed**:
- ✅ Standard library imports
- ✅ Third-party packages (Claude auto-installs or asks permission)
- ✅ File operations within project scope
- ✅ Bash commands
- ✅ Network access for skill functionality (e.g., API calls)

**Best practices**:
- ✅ Use standard library when possible (no installation needed)
- ✅ Document required packages in description field
- ✅ Clear documentation of external dependencies

**Package installation**: Per [SKILLS.md line 437-584](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills), "Claude will automatically install required dependencies (or ask for permission to install them) when it needs them."

### Authentication Patterns

**Good Pattern** (API Token Authentication):
```python
# User manually sets token in environment or config file
# Script reads from known location
config_file = project_root / ".config" / "settings.json"
api_token = json.loads(config_file.read_text()).get("api_token")
```

**Why it's secure**:
- ✅ User provides credentials explicitly
- ✅ Credentials stored locally (not in code)
- ✅ No auto-scraping or credential theft
- ✅ Clear documentation of what's needed

**Bad Pattern**:
```python
# ❌ Don't do this
username = input("Enter username: ")
password = input("Enter password: ")
# Auto-login to external service
```

**Why it's bad**:
- ❌ Credentials handled by skill (risky)
- ❌ Could send credentials anywhere
- ❌ User has no control

### Security Requirements

**Code audit checklist** (before publishing):

- [ ] No `eval()` or `exec()` calls
- [ ] No obfuscated code (base64, hex strings)
- [ ] No unexpected network destinations
- [ ] No credential harvesting beyond documented authentication
- [ ] Credentials handled securely
- [ ] All operations match stated purpose
- [ ] Clear logging (no sensitive data in logs)
- [ ] Error messages don't leak secrets

---

## Documentation Templates

See [Content & Writing Standards](#content--writing-standards) for file structure guidelines.

### SKILL.md Template

```markdown
---
name: Your Skill Name
description: What it does. Use when [triggers].
---

# Skill Name

Brief description (1-2 sentences).

## When to Use This Skill

- Trigger scenario 1
- Trigger scenario 2
- Trigger scenario 3

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

For complete troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for:
- Example scenario 1
- Example scenario 2
- Example scenario 3

## Related Files

- `scripts/main.py` - Entry point
- `WORKFLOW.md` - Detailed steps
- `TROUBLESHOOTING.md` - Error handling
```

### EXAMPLES.md Template

```markdown
# Usage Examples

Comprehensive examples demonstrating all features.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Real-World Examples](#real-world-examples)

## Basic Usage

### Example 1: Simplest Case

Description of what this example does.

```bash
script.py "input"
```

**Output:**
```
Expected output here
```

**When to use**: Description of use case

---

(More examples...)
```

### TROUBLESHOOTING.md Template

```markdown
# Troubleshooting Guide

Complete error handling reference.

## Table of Contents

- [Error Category 1](#error-category-1)
- [Error Category 2](#error-category-2)

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

---

(More errors...)
```

---

## Evaluation and Iteration

> **Source**: [Official Best Practices - Evaluation and Iteration](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#evaluation-and-iteration)

### Build Evaluations First

**Principle**: Create test scenarios BEFORE extensive documentation.

**Process**:
1. Establish baseline performance without the skill
2. Create the skill
3. Measure whether the skill improves results
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

**Why this works**: Evaluations provide objective measurements of skill effectiveness.

### Iterative Development with Claude

**Recommended workflow**:

1. **Complete a task with Claude normally** - Note what context you repeatedly provide
2. **Ask Claude A to create a skill** - Capture that repeated context as a skill
3. **Test the skill with Claude B** - Use on similar tasks
4. **Observe Claude B's behavior** - What gaps exist? What's missed?
5. **Return to Claude A with observations** - Provide specific feedback for refinement
6. **Repeat based on real usage patterns** - Don't guess, iterate based on actual use

**Key insight**: Monitor how Claude navigates your skill. Unexpected exploration paths, missed connections, or ignored content indicate structural improvements needed.

### Testing Across Models

**Always test with multiple models**:
- **Haiku** - Fast, efficient, less capable (good baseline test)
- **Sonnet** - Balanced performance (most common use case)
- **Opus** - Most capable (if skill works on Haiku, it will work on Opus)

**Best practice**: If guidance works for Haiku, it will work for all models.

### Real-World Testing

**Don't just test happy paths**:
- ✅ Test with incomplete information
- ✅ Test with edge cases
- ✅ Test with ambiguous inputs
- ✅ Test with errors and failures
- ✅ Test with team members (fresh perspectives)

**Incorporate feedback**: Real usage reveals issues that theoretical testing misses.

---

## Common Pitfalls

### Pitfall #1: Embedding Everything in SKILL.md

**Problem**:
```markdown
<!-- SKILL.md becomes 500+ lines -->
# My Skill

## Instructions
(200 lines)

## Examples
(100 lines)

## Troubleshooting
(150 lines)

## API Reference
(50 lines)
```

**Solution**:
Split into multiple files with references:
```markdown
# My Skill (50 lines)

## Quick Start
(Essential steps)

## Examples
See [EXAMPLES.md](EXAMPLES.md)

## Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
```

---

### Pitfall #2: Broken Documentation References

**Problem**:
- Moving/renaming files without updating references
- Consolidating docs but forgetting to update links
- Result: Users encounter "file not found" errors

**Solution**:
```bash
# After any file move/delete, search for references:
grep -r "old-filename.md" .

# Update all references to point to new location
```

---

### Pitfall #3: Vague Descriptions

**Problem**:
```yaml
description: Processes data. Use when needed.
```

**Solution**:
```yaml
description: Extract structured data from PDFs including tables, images, and form fields. Use when user provides PDF files, mentions extracting tables/forms from PDFs, or needs to convert PDF data to JSON/CSV.
```

**Key improvements**:
- Specific capabilities (tables, images, forms)
- Clear triggers (PDF files, "extracting tables")
- Output formats (JSON, CSV)

---

### Pitfall #4: Non-Executable Scripts

**Problem**:
```bash
$ python3 scripts/extract.py
# Works

$ ./scripts/extract.py
# bash: permission denied
```

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.py

# Add shebang to scripts
#!/usr/bin/env python3
```

---

### Pitfall #5: Too Many Options

**Problem**:
```markdown
Use pypdf, pdfplumber, PyMuPDF, pdfrw, pikepdf, or any other PDF library.
```

**Why it fails**:
- Overwhelms Claude with choices
- No clear default
- Increases decision fatigue

**Solution**:
```markdown
Use pdfplumber for PDF extraction (or another library if you have a specific preference).
```

**Key improvement**: Provide one default with an escape hatch for special cases.

---

### Pitfall #6: Deeply Nested References

**Problem**:
```
SKILL.md → WORKFLOW.md → DETAILS.md → ADVANCED.md
```

**Why it fails**:
- Difficult to navigate
- Increases cognitive load
- Hard to maintain

**Solution**: Keep references one level deep
```
SKILL.md → WORKFLOW.md ✓
SKILL.md → EXAMPLES.md ✓
SKILL.md → TROUBLESHOOTING.md ✓
```

---

### Pitfall #7: Windows-Style Paths

**Problem**:
```markdown
See `scripts\helper.py` for details.
```

**Why it fails**: Windows-style backslashes cause issues on Unix systems.

**Solution**:
```markdown
See `scripts/helper.py` for details.
```

**Always use Unix-style forward slashes** in documentation and code.

---

### Pitfall #8: Inconsistent Terminology

**Problem**:
```markdown
Use the API endpoint to fetch data from the URL using the web service address...
```

**Why it fails**: Multiple terms for the same concept create confusion.

**Solution**: Pick one term and stick with it
```markdown
Use the API endpoint to fetch data...
```

---

## Anti-Patterns to Avoid

> **Source**: [Official Best Practices - Anti-Patterns](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#anti-patterns-to-avoid)

Quick reference of patterns to avoid:

- ❌ Windows-style paths (`scripts\helper.py`) → Use Unix-style (`scripts/helper.py`)
- ❌ Too many options ("Use pypdf, pdfplumber, PyMuPDF, or...") → Provide one default with escape hatch
- ❌ Deeply nested references (3+ levels) → Keep one level deep from SKILL.md
- ❌ Vague descriptions ("Helps with data") → Include both what the skill does and when to use it
- ❌ Over-explaining known concepts → Challenge each piece of information for necessity
- ❌ Time-sensitive information ("Before Aug 2025...") → Use collapsible sections
- ❌ Inconsistent terminology → Pick one term and use throughout
- ❌ First/second-person descriptions → Always use third person
- ❌ Non-executable scripts → Always include shebang and `chmod +x`
- ❌ Undocumented constants → Every magic number needs justification
- ❌ Punting errors to Claude → Handle errors explicitly in scripts

---

## Anatomy of a Well-Designed Skill

This section breaks down the characteristics of effective skills using real implementation examples.

### 1. Progressive Disclosure Architecture

**Principle**: Load only what's needed, when it's needed. Distribute content across the three-level loading system.

**Ideal distribution**:
- **Level 1 (YAML)**: 5-10 lines (always loaded)
- **Level 2 (SKILL.md body)**: <500 lines, target <200 (loaded when triggered)
- **Level 3 (Resources)**: Unlimited size (loaded on-demand or executed)

**Example** (Mermaid Diagramming skill):
- SKILL.md: 112 lines (~550 words) - well under limit ✅
- Supporting docs: WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md - loaded on-demand ✅
- No scripts needed - Claude generates diagrams directly ✅

**Key insight**: Heavy documentation is offloaded to supporting files, keeping SKILL.md lean for quick loading.

### 2. Effective YAML Frontmatter

**Characteristics of good frontmatter**:
- ✅ Concise name (20-40 chars recommended, 64 max)
- ✅ Descriptive but not verbose (200-400 chars recommended, 1,024 max)
- ✅ Third-person voice ("This skill should be used when...")
- ✅ Includes "what" (capabilities) and "when" (triggers)
- ✅ Lists varied trigger keywords for discovery

**Example** (Mermaid Diagramming):
```yaml
name: diagramming  # 11 chars (17% of 64-char limit)
description: Creates and edits Mermaid diagrams for flowcharts, sequence diagrams, ERDs, state machines, architecture diagrams, process flows, timelines, and more. Use when user mentions diagram, flowchart, mermaid, visualize, refactor diagram, sequence diagram, ERD, architecture diagram, process flow, state machine, or needs visual documentation.  # 318 chars (31% of 1,024-char limit)
```

**Why it works**: Lists specific capabilities, defines clear triggers, includes varied keywords (diagram/flowchart/visualize/ERD).

### 3. Secure Authentication Patterns

**Good pattern characteristics**:
- ✅ User provides credentials explicitly
- ✅ Credentials stored locally (not in code)
- ✅ No auto-scraping or credential harvesting
- ✅ Clear documentation of requirements
- ✅ Standard library when possible (no external dependencies)

**Example** (API token-based auth):
```python
# User manually sets token in config file
# Script reads from known location
config_file = project_root / ".config" / "settings.json"
api_token = json.loads(config_file.read_text()).get("api_token")
```

**Why it's secure**: User controls credentials, script only reads from documented location, no network harvesting.

### 4. Clear File Organization

**Effective organization patterns**:
- ✅ Separate instructions (SKILL.md) from examples (EXAMPLES.md) and troubleshooting (TROUBLESHOOTING.md)
- ✅ Group scripts by function in `scripts/` directory
- ✅ Organize supporting docs by user journey
- ✅ One-level deep references (no nested chains)

**Example structure**:
```
.claude/skills/my-skill/
├── SKILL.md                    # Core instructions (<500 lines)
├── EXAMPLES.md                 # Usage examples
├── TROUBLESHOOTING.md          # Error handling
├── scripts/                    # Executable code (0 tokens)
│   ├── main.py
│   ├── module1.py
│   └── module2.py
└── references/                 # Loaded on-demand
    ├── API_REFERENCE.md
    └── SCHEMA.md
```

### 5. Implementation Checklist

Use this checklist to evaluate skill quality:

**Progressive disclosure**:
- [ ] SKILL.md under 500 lines (target: under 200)
- [ ] Supporting docs split out (EXAMPLES.md, TROUBLESHOOTING.md)
- [ ] Scripts are executable (0 tokens consumed)
- [ ] References loaded on-demand

**YAML frontmatter**:
- [ ] Name: 20-40 chars (64 max)
- [ ] Description: 200-400 chars (1,024 max)
- [ ] Third-person voice
- [ ] Includes capabilities ("what") and triggers ("when")
- [ ] Varied keywords for discovery

**Security**:
- [ ] User-provided credentials only
- [ ] No credential harvesting
- [ ] Clear auth documentation
- [ ] Standard library preferred
- [ ] No `eval()` or `exec()` calls

**Organization**:
- [ ] Clear separation of concerns
- [ ] Scripts grouped logically
- [ ] One-level deep references
- [ ] No broken references
- [ ] Required packages documented

### Common Mistakes to Avoid

Based on real-world implementations:

- ❌ **Embedding everything in SKILL.md** → Split into supporting docs
- ❌ **Vague frontmatter** → Include specific capabilities and triggers
- ❌ **Non-executable scripts** → Add shebang and `chmod +x`
- ❌ **Undocumented dependencies** → List required packages in description
- ❌ **Broken references** → Verify all links after file changes
- ❌ **Credential handling** → Let user provide, never harvest

---

## Quick Checklist for New Skills

> **Source**: Combined from [Official Best Practices - Pre-Launch Checklist](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md#pre-launch-checklist) and local experience

### Before Publishing

**Quality Assurance**:
- [ ] Description includes key terms and activation triggers
- [ ] SKILL.md is under 500 lines (official maximum)
- [ ] Additional details in separate files with appropriate organization
- [ ] No time-sensitive information (use collapsible sections for legacy)
- [ ] Terminology is consistent throughout
- [ ] Examples are concrete with real scenarios
- [ ] File references are one-level deep (not nested)
- [ ] Reference files over 100 lines include table of contents
- [ ] Progressive disclosure is used appropriately
- [ ] Workflows have numbered, clear steps

**YAML Frontmatter**:
- [ ] Name uses lowercase-with-hyphens format
- [ ] Name ≤ 64 characters (20-40 recommended)
- [ ] Name uses gerund form (verb + -ing)
- [ ] Description ≤ 1,024 characters (200-400 recommended)
- [ ] Description written in third person
- [ ] Description includes "what" and "when to use"
- [ ] No reserved words ("anthropic", "claude")
- [ ] No XML tags

**Code Quality**:
- [ ] Scripts handle errors explicitly (don't punt to Claude)
- [ ] All constants are documented (no magic numbers)
- [ ] Required packages are listed and verified
- [ ] No Windows-style paths (use Unix-style `/`)
- [ ] Validation steps protect critical operations
- [ ] Feedback loops included where quality matters
- [ ] Scripts executable (`chmod +x`)
- [ ] Shebang added (`#!/usr/bin/env python3`)

**Content Guidelines**:
- [ ] One default option provided (not overwhelming choices)
- [ ] Consistent terminology throughout
- [ ] Templates and examples with input/output pairs
- [ ] MCP tools use fully qualified names (ServerName:tool_name)
- [ ] Visual analysis used where appropriate
- [ ] Checklists provided for complex workflows

**Testing**:
- [ ] Created at least three evaluation scenarios
- [ ] Tested with Haiku, Sonnet, and Opus (or target models)
- [ ] Tested in real usage scenarios (not just happy paths)
- [ ] Tested with incomplete information and edge cases
- [ ] Incorporated team feedback
- [ ] Skill triggers correctly (test description keywords)
- [ ] Scripts execute without errors
- [ ] Supporting docs load on-demand
- [ ] All file references valid (no broken links)

---

## Skills Documentation Reference

This section provides a comprehensive cross-reference to all skills documentation, helping you find the right resource for your needs.

### Quick Navigation

| Document | Type | Purpose | Best For |
|----------|------|---------|----------|
| [SKILLS.md](./SKILLS.md) | Local (Synced) | Practical how-to guide for creating and managing skills in Claude Code | Learning the basics, quick reference |
| [AGENT_SKILLS_OVERVIEW.md](./AGENT_SKILLS_OVERVIEW.md) | Local (Synced) | Architecture and concepts behind Agent Skills | Understanding how skills work across Claude products |
| [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) | External (Anthropic) | Official reference implementation demonstrating best practices | Following official patterns, structure examples |
| **This Document** | Local (Custom) | Lessons learned from real-world skill implementations | Practical tips, optimization techniques, troubleshooting |
| [Anthropic Skills Repository](https://github.com/anthropics/skills) | External (Anthropic) | Collection of official skill examples | Exploring different skill types, real implementations |

### Learning Paths

Choose your path based on your current goal:

#### 🚀 **Getting Started** (First-time skill developer)
1. Start: [SKILLS.md](./SKILLS.md) - Learn skill structure and creation process
2. Follow: [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md) - See official example
3. Reference: This document - Apply best practices and avoid common pitfalls
4. Explore: [Anthropic Skills Repository](https://github.com/anthropics/skills) - Study different skill types

#### 🏗️ **Architecture & Concepts** (Understanding the system)
1. Start: [AGENT_SKILLS_OVERVIEW.md](./AGENT_SKILLS_OVERVIEW.md) - Three-level loading, progressive disclosure
2. Deep dive: [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) - Resource organization patterns
3. Apply: This document - Progressive Disclosure Strategy section

#### 🔨 **Implementation** (Building your skill)
1. Quick reference: [SKILLS.md](./SKILLS.md) - File structure, YAML frontmatter
2. Follow patterns: [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md) - Writing style, organization
3. Optimize: This document - Token optimization, file organization
4. Validate: This document - Pre-publication checklist

#### 🔍 **Troubleshooting** (Fixing issues)
1. Check: [SKILLS.md](./SKILLS.md) - Troubleshooting section
2. Review: This document - Common Pitfalls section
3. Compare: [Anthropic Skills Repository](https://github.com/anthropics/skills) - Working examples

### Document Comparison

| Aspect | SKILLS.md | AGENT_SKILLS_OVERVIEW.md | skill-creator | This Document |
|--------|-----------|-------------------------|---------------|---------------|
| **Focus** | Practical how-to | Conceptual architecture | Official example | Lessons learned |
| **Depth** | Comprehensive | Deep technical | Implementation | Practical tips |
| **Format** | Step-by-step guide | Architecture docs | Working skill | Best practices |
| **Audience** | All developers | Architecture-focused | All developers | Experienced devs |
| **Updates** | Auto-synced | Auto-synced | Anthropic-maintained | Custom (manual) |
| **Examples** | Generic | Conceptual | Real implementation | Real analysis |

### Key Topics by Document

#### SKILLS.md - Practical Guide
- Creating personal, project, and plugin skills
- Writing SKILL.md with YAML frontmatter
- Adding supporting files (scripts, references, assets)
- Restricting tool access with `allowed-tools`
- Viewing, testing, and debugging skills
- Sharing skills via plugins or git
- Troubleshooting common issues

#### AGENT_SKILLS_OVERVIEW.md - Architecture
- Progressive disclosure architecture (3-level loading)
- Skills across Claude products (Claude Code, Agent SDK, Claude.ai)
- Token budget management
- Skill structure and components
- Auto-invocation mechanisms
- Best practices at architectural level

#### skill-creator - Official Reference
- 6-step skill creation process
- Writing style (imperative/infinitive form)
- Resource organization (scripts/references/assets)
- YAML frontmatter best practices (third-person descriptions)
- Validation and packaging
- Real working example to study

#### This Document - Practical Lessons
- Token optimization techniques (progressive disclosure)
- Real-world implementation analysis (Mermaid, Changelog skills)
- Security patterns (cookie-based auth, standard library)
- File organization patterns
- Common pitfalls and solutions
- Pre-publication checklist

### When to Use Which Document

**"How do I create my first skill?"**
→ Start with [SKILLS.md](./SKILLS.md)

**"Why do skills use progressive disclosure?"**
→ Read [AGENT_SKILLS_OVERVIEW.md](./AGENT_SKILLS_OVERVIEW.md)

**"What does a good skill look like?"**
→ Study [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md)

**"How can I optimize my skill's token usage?"**
→ Reference this document's Progressive Disclosure Strategy section

**"My skill isn't triggering, what should I check?"**
→ Check [SKILLS.md](./SKILLS.md) Troubleshooting section, then this document's Common Pitfalls

**"Where can I see more skill examples?"**
→ Browse [Anthropic Skills Repository](https://github.com/anthropics/skills)

---

## Resources

**Official Documentation**:
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
- **[Agent Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md)** - **PRIMARY REFERENCE** for this document
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Using Skills in Claude Code](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/using-skills)

**Official Skill Examples**:
- **[Anthropic Skills Repository](https://github.com/anthropics/skills)** - Official reference implementations with real-world examples and best practices
- [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) - Exemplary reference implementation

**Local Documentation**:
- [SKILLS.md](./SKILLS.md) - Practical guide for creating and managing skills
- [AGENT_SKILLS_OVERVIEW.md](./AGENT_SKILLS_OVERVIEW.md) - Architecture and concepts
- This document - Lessons learned and integrated best practices

**Internal References**:
- `doc/skills/mermaid/` - Reference implementation (diagram generation)
- `git/skills/generating-changelog/` - Reference implementation (changelog automation)

---

## Official Anthropic Example: skill-creator

The [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) from Anthropic's official skills repository is an exemplary reference implementation demonstrating best practices for skill development.

### Key Characteristics

**Size**: 175 lines
- Well under the official 500-line maximum
- Demonstrates that comprehensive skills can be effective while staying concise
- Good example of balancing completeness with brevity

**Structure**:
```
skill-creator/
├── SKILL.md (175 lines)
└── scripts/
    ├── init_skill.py
    └── package_skill.py
```

### Writing Style Guidelines

The skill-creator demonstrates **imperative/infinitive form** throughout:

✅ **Good** (Imperative/Infinitive):
- "To accomplish X, do Y"
- "Create the skill directory"
- "Answer the following questions"
- "Use objective, instructional language"

❌ **Avoid** (Second-person):
- ~~"You should do X"~~
- ~~"If you need to do X"~~
- ~~"You can accomplish this by"~~

**Why this matters**: Imperative form maintains consistency and clarity for AI consumption, treating the skill as procedural documentation rather than conversational guidance.

### Resource Organization Pattern

The skill-creator exemplifies the three-tier resource architecture:

#### 1. `scripts/` - Executable Code
**Purpose**: Deterministic operations that would otherwise be rewritten repeatedly

**When to include**:
- Tasks requiring deterministic reliability
- Code that's rewritten frequently
- Complex operations better handled by scripts

**Benefits**:
- Token efficient (executed without loading to context)
- Deterministic results
- Reusable across sessions

**Example from skill-creator**: `init_skill.py`, `package_skill.py`

#### 2. `references/` - Documentation
**Purpose**: Reference material loaded into context as needed

**When to include**:
- Database schemas, API specifications
- Company policies, domain knowledge
- Detailed workflow guides

**Benefits**:
- Keeps SKILL.md lean
- Loaded only when Claude determines it's needed
- Progressive disclosure in action

**Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md

**Avoid duplication**: Information should live in either SKILL.md or references files, not both

#### 3. `assets/` - Output Resources
**Purpose**: Files used in output, not loaded to context

**When to include**:
- Templates (HTML, React, PowerPoint)
- Images, icons, logos
- Fonts, sample documents
- Boilerplate code

**Benefits**:
- Separates output resources from documentation
- Enables Claude to use files without loading them to context
- Keeps context window clean

**Examples**: `assets/logo.png`, `assets/slides.pptx`, `assets/frontend-template/`

### Progressive Disclosure in Practice

The skill-creator demonstrates the three-level loading system:

1. **Level 1: Metadata** (~100 words, always loaded)
   - YAML frontmatter: `name` and `description`
   - Determines when Claude uses the skill

2. **Level 2: SKILL.md body** (<5k words, loaded when triggered)
   - Essential procedures and guidance
   - References to bundled resources

3. **Level 3: Bundled resources** (Unlimited, loaded as needed)
   - Scripts can be executed without reading to context
   - References loaded when Claude needs them
   - Assets used in output without loading

### YAML Frontmatter Best Practices

From skill-creator's metadata:

```yaml
---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
---
```

**Key observations**:
- ✅ **Third-person description**: "This skill should be used when..." (not "Use this skill when...")
- ✅ **Specific about purpose**: "Guide for creating effective skills"
- ✅ **Clear triggers**: "when users want to create a new skill"
- ✅ **Describes capabilities**: "specialized knowledge, workflows, or tool integrations"
- ✅ Length: 225 chars (within 200-400 recommended range)

### Comparison to Our Skills

How our audited skills compare to skill-creator:

| Aspect | skill-creator | Our Skills | Assessment |
|--------|--------------|------------|------------|
| **Size** | 175 lines | 98-219 lines | ✅ Most comparable or better |
| **Writing style** | Imperative | Mixed | ⚠️ Could improve consistency |
| **Resource org** | 3-tier (scripts/references/assets) | Scripts only | ✅ Matches our needs |
| **YAML quality** | Third-person, specific | Good, varied | ✅ Comparable quality |
| **Progressive disclosure** | Explicit 3-level | Good but implicit | ✅ Well implemented |

### Actionable Takeaways

1. **Writing Style**: Review our skills for second-person language ("you should") and convert to imperative form ("to accomplish X, do Y")

2. **Resource Organization**: Our git skills effectively use `scripts/`. Consider adding `references/` or `assets/` if:
   - Documentation gets embedded in SKILL.md (move to `references/`)
   - Templates or boilerplate are needed (move to `assets/`)

3. **YAML Descriptions**: Review for third-person consistency:
   - ✅ "This skill should be used when..."
   - ❌ "Use this skill when..."

4. **Size Guidance**: skill-creator at 175 lines demonstrates effective use of the 500-line budget - comprehensive yet concise

5. **Avoid Duplication**: Ensure information doesn't appear in both SKILL.md and supporting docs

### Full skill-creator SKILL.md

For complete reference, see: https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md

The full content demonstrates:
- 6-step skill creation process
- Resource organization rationale
- Writing style consistency
- Progressive disclosure architecture
- Validation and packaging guidance

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Based On**: AGENT_SKILLS_OVERVIEW.md + skill-creator Reference
