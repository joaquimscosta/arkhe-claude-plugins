# Agent Skill Development: Best Practices

**Based on**: AGENT_SKILLS_OVERVIEW.md + Udemy-Extract Skill Implementation
**Date**: 2025-10-18
**Purpose**: Document lessons learned and best practices for creating Claude Code Skills

---

## Table of Contents

1. [Progressive Disclosure Strategy](#progressive-disclosure-strategy)
2. [YAML Frontmatter Guidelines](#yaml-frontmatter-guidelines)
3. [Token Optimization Techniques](#token-optimization-techniques)
4. [File Organization Patterns](#file-organization-patterns)
5. [Security Best Practices](#security-best-practices)
6. [Documentation Structure](#documentation-structure)
7. [Common Pitfalls](#common-pitfalls)
8. [Real-World Example: Udemy-Extract](#real-world-example-extract)

---

## Progressive Disclosure Strategy

### The Three-Level Architecture

**Principle**: Load only what's needed, when it's needed.

```
Level 1: Metadata (Always Loaded)
├── YAML frontmatter: name + description
├── Token cost: ~100 tokens
└── Purpose: Skill discovery

Level 2: Instructions (Loaded When Triggered)
├── SKILL.md body
├── Token cost: <5,000 tokens (target: <1,000)
└── Purpose: Quick start and core guidance

Level 3+: Resources (Loaded As Needed)
├── Supporting docs (TROUBLESHOOTING.md, EXAMPLES.md, etc.)
├── Executable scripts
├── Token cost: Effectively unlimited (loaded on-demand)
└── Purpose: Deep dives and deterministic operations
```

### Implementation Pattern

**SKILL.md should**:
- ✅ Provide quick start (essential steps only)
- ✅ Show output structure
- ✅ List common issues with references to detailed docs
- ✅ Reference supporting files (don't embed them)
- ❌ Avoid detailed step-by-step workflows (use separate WORKFLOW.md)
- ❌ Avoid embedding all examples (use EXAMPLES.md)
- ❌ Avoid complete error catalog (use TROUBLESHOOTING.md)

**Example from Udemy-Extract**:
```markdown
## Common Issues

**"Could not find course with slug"**
- Ensure you're enrolled in the course
- Course must appear in "My Courses"

For complete troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
```

**What NOT to do**:
```markdown
<!-- ❌ Don't embed the entire troubleshooting guide in SKILL.md -->
## Common Issues

### Error: Authentication failed
...100 lines of detailed troubleshooting...

### Error: Network timeout
...another 50 lines...
```

---

## YAML Frontmatter Guidelines

### Required Fields

```yaml
---
name: Your Skill Name
description: What this skill does and when to use it
---
```

### Limits

| Field | Maximum | Recommended | Purpose |
|-------|---------|-------------|---------|
| `name` | 64 chars | 20-40 chars | Concise identification |
| `description` | 1,024 chars | 200-400 chars | Discovery and triggering |

### Description Best Practices

**Template**:
```
[What it does]. Use when [trigger scenario 1], [trigger scenario 2], or [trigger scenario 3].
```

**Good Example** (Udemy-Extract):
> Extract complete Udemy course content including video transcripts, articles, quizzes, downloadable resources (PDFs, code files), and external links. Use when user provides a Udemy course URL, mentions extracting/downloading Udemy content, or wants to research/analyze a Udemy course offline.

**Why it works**:
- ✅ Lists specific capabilities (transcripts, articles, quizzes...)
- ✅ Defines clear triggers (URL, "extracting", "downloading")
- ✅ Includes use case (offline research/analysis)
- ✅ Under 300 characters (plenty of room to grow)

**Bad Example**:
> Processes Udemy courses. Use when needed.

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

---

## Token Optimization Techniques

### Target Token Budgets

| File | Target Tokens | Max Tokens | Typical Lines |
|------|--------------|------------|---------------|
| SKILL.md | <1,000 | <5,000 | <150 |
| Supporting doc | Any | Any | Unlimited |
| Scripts | 0 (executed) | 0 | Unlimited |

### Calculation Method

```python
# Approximate token count
tokens ≈ word_count / 0.75

# Example:
# 750 words ≈ 1,000 tokens
# 3,750 words ≈ 5,000 tokens
```

### Optimization Strategies

#### 1. Extract Detailed Content

**Before** (too detailed):
```markdown
## Workflow

### Step 1: Authenticate
1. Create cookies.json file
2. Add access_token from browser
3. Add client_id from browser
4. Verify format is correct
5. Test authentication...
(90 more lines)
```

**After** (optimized):
```markdown
## Workflow

See [WORKFLOW.md](WORKFLOW.md) for detailed step-by-step instructions.

**Quick overview**:
1. Authenticate (cookies.json)
2. Fetch course structure
3. Extract content
4. Generate output
```

**Savings**: ~80 lines, ~500 tokens

#### 2. Use References Over Embedding

**Before**:
```markdown
## Examples

Example 1: Full extraction
(50 lines of code and output)

Example 2: Selective extraction
(50 lines of code and output)

Example 3: Resource-only
(50 lines of code and output)
```

**After**:
```markdown
## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed examples including:
- Full course extraction
- Selective content type extraction
- Resource-only extraction
```

**Savings**: ~140 lines, ~900 tokens

#### 3. Condense Code Blocks

**Before**:
```markdown
### Full Example

```bash
python3 .claude/skills/my-skill/scripts/run.py \
  --option1 value1 \
  --option2 value2 \
  --option3 value3 \
  --option4 value4 \
  --option5 value5 \
  --option6 value6
```

**After**:
```markdown
### Example

```bash
python3 scripts/run.py "https://example.com" --custom-output
```

See EXAMPLES.md for all options.
```

**Savings**: Shorter code blocks + reference to full documentation

---

## File Organization Patterns

### Recommended Structure

```
.claude/skills/my-skill/
├── SKILL.md                    # Main instructions (<150 lines)
├── WORKFLOW.md                 # Detailed step-by-step (optional)
├── EXAMPLES.md                 # Usage examples
├── TROUBLESHOOTING.md          # Error handling
├── API_REFERENCE.md            # API docs (if applicable)
├── scripts/
│   ├── main.py                 # Entry point
│   ├── module1.py
│   ├── module2.py
│   └── tools/                  # Testing and analysis utilities
│       ├── analyze.py
│       └── test.py
├── templates/                  # Output templates
│   └── template.md
└── resources/                  # Reference materials
    └── schema.json
```

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

**Resources**:
- Use descriptive names
- Group by type in subdirectories

---

## Security Best Practices

### Runtime Environment Constraints

**Allowed**:
- ✅ Standard library imports only
- ✅ Pre-installed packages (check code execution docs)
- ✅ File operations within container
- ✅ Bash commands

**Forbidden**:
- ❌ Network access (except documented API usage)
- ❌ Runtime package installation (`pip install`)
- ❌ Accessing external URLs (unless skill's purpose)
- ❌ Credential harvesting beyond documented auth

### Authentication Patterns

**Good Pattern** (Udemy-Extract):
```python
# User manually creates cookies.json from browser
# Script reads from known location
auth_file = project_root / "cookies.json"
cookies = json.loads(auth_file.read_text())
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

### Code Audit Checklist

Before publishing a skill, verify:

- [ ] No `eval()` or `exec()` calls
- [ ] No obfuscated code (base64, hex strings)
- [ ] No unexpected network destinations
- [ ] Credentials handled securely
- [ ] All operations match stated purpose
- [ ] Clear logging (no sensitive data in logs)
- [ ] Error messages don't leak secrets

---

## Documentation Structure

### Essential Documentation

**Minimum required**:
1. `SKILL.md` - Main instructions

**Highly recommended**:
2. `EXAMPLES.md` - Usage examples
3. `TROUBLESHOOTING.md` - Error handling

**Optional but valuable**:
4. `WORKFLOW.md` - Detailed steps
5. `API_REFERENCE.md` - API documentation
6. `CONTRIBUTING.md` - For open-source skills

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

## Real-World Example: Udemy-Extract

### Implementation Analysis

**What it does well**:
1. ✅ **Excellent progressive disclosure**
   - SKILL.md: 258 lines (~1,264 tokens)
   - Supporting docs: 1,360 lines (loaded on-demand)
   - Scripts: 3,482 lines (executed, never loaded)

2. ✅ **Clear YAML frontmatter**
   - Name: 22 chars (34% of limit)
   - Description: 291 chars (28% of limit)
   - Includes "what" and "when"

3. ✅ **Secure implementation**
   - Standard library only
   - No runtime package installation
   - Cookie-based auth (user-provided)

4. ✅ **Well-organized files**
   - Clear separation of concerns
   - Scripts grouped by function
   - Supporting docs by user journey

**What could be improved**:
1. ⚠️ **SKILL.md could be more concise**
   - Current: 258 lines
   - Target: <150 lines
   - Action: Extract "Workflow" section to WORKFLOW.md

2. ⚠️ **Broken references** (post-consolidation)
   - 5 references to deleted files
   - Action: Update to new file names

### Lessons Learned

**Do**:
- ✅ Split instructions (SKILL.md) from examples (EXAMPLES.md) and troubleshooting (TROUBLESHOOTING.md)
- ✅ Use scripts for deterministic operations
- ✅ Reference supporting docs instead of embedding
- ✅ Make frontmatter descriptive and trigger-rich

**Don't**:
- ❌ Embed all content in SKILL.md
- ❌ Forget to update references after moving files
- ❌ Use third-party packages without checking availability
- ❌ Make scripts non-executable

---

## Quick Checklist for New Skills

### Before Publishing

**Structure**:
- [ ] SKILL.md with YAML frontmatter
- [ ] Name ≤ 64 characters
- [ ] Description ≤ 1,024 characters
- [ ] Description includes "what" and "when"
- [ ] SKILL.md <5,000 tokens (target: <1,000)
- [ ] Supporting docs created (EXAMPLES.md, TROUBLESHOOTING.md)

**Code Quality**:
- [ ] Scripts executable (`chmod +x`)
- [ ] Shebang added (`#!/usr/bin/env python3`)
- [ ] Standard library only (or pre-installed packages)
- [ ] No runtime package installation
- [ ] Secure authentication (if needed)

**Documentation**:
- [ ] Quick start examples
- [ ] Output structure documented
- [ ] Common issues listed
- [ ] All file references valid
- [ ] No broken links

**Testing**:
- [ ] Skill triggers correctly (test description keywords)
- [ ] Scripts execute without errors
- [ ] Supporting docs load on-demand
- [ ] Token usage within guidelines

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
- Real-world implementation analysis (Udemy-Extract skill)
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
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)

**Official Skill Examples**:
- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official reference implementations of Agent Skills with real-world examples, architecture patterns, and best practices from Anthropic's engineering team

**Internal References**:
- `AGENT_SKILLS_OVERVIEW.md` - Claude's official skills documentation
- `.claude/skills/extract/` - Reference implementation

---

## Official Anthropic Example: skill-creator

The [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) from Anthropic's official skills repository is an exemplary reference implementation demonstrating best practices for skill development.

### Key Characteristics

**Size**: 175 lines (~1,140 tokens)
- Slightly above 150-line target but demonstrates that comprehensive skills can be effective
- Well under 5,000 token hard limit
- Balances completeness with conciseness

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

4. **Size Tolerance**: skill-creator at 175 lines validates that comprehensive skills can exceed 150 lines if the content is valuable and well-organized

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
