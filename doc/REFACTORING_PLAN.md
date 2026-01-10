# Doc Plugin Refactoring Plan

**Date**: 2026-01-10
**Status**: Draft - Pending Approval

---

## Overview

This plan consolidates the doc plugin components by:
1. Fixing naming inconsistencies
2. Converting verbose commands to skills with progressive disclosure
3. Merging overlapping documentation capabilities

## Rationale

- **Best Practice Alignment**: Skills use progressive disclosure (SKILL.md + supporting files)
- **Token Efficiency**: Commands at 650+ lines consume significant context
- **Clarity**: Clear separation between agents (complex tasks) and skills (auto-invoke patterns)

---

## Phase 1: Rename `mermaid/` → `diagramming/`

**Effort**: Low | **Risk**: Low

### Changes

1. **Rename directory**
   ```bash
   mv doc/skills/mermaid/ doc/skills/diagramming/
   ```

2. **Verify SKILL.md** (no change needed - already has `name: diagramming`)

3. **Update README.md references**
   - Change "mermaid" to "diagramming" in component descriptions

4. **Update any cross-references**
   - Check `/diagram` command references
   - Check `docs-architect` agent references

### Validation
- [ ] Skill triggers on diagram-related keywords
- [ ] `/diagram` command works correctly
- [ ] No broken references in docs

---

## Phase 2: Convert `/code-explain` to Skill

**Effort**: Medium | **Risk**: Low

### Current State
- `commands/code-explain.md`: ~810 lines with embedded examples and code analysis patterns

### Target State

**Create `skills/code-explanation/`:**

| File | Content | Target Size |
|------|---------|-------------|
| `SKILL.md` | Quick start, core approach, output format | ~100-150 lines |
| `WORKFLOW.md` | Step-by-step methodology | Extracted from command |
| `EXAMPLES.md` | Interactive examples, visualizations | Extracted from command |
| `TROUBLESHOOTING.md` | Common pitfalls, learning paths | Extracted from command |

**SKILL.md Structure:**
```yaml
---
name: code-explanation
description: Explains complex code through clear narratives, visual diagrams,
and step-by-step breakdowns. Use when user asks to explain code, understand
algorithms, or wants code walkthroughs with visualizations.
---

# Code Explanation

Expert skill for explaining complex code to developers at all levels.

## Quick Start
1. Analyze code complexity
2. Choose explanation depth based on audience
3. Generate visual aids (flowcharts, class diagrams)
4. Provide step-by-step breakdown

## Core Approach
- Progressive complexity: simple → complex
- Visual aids for complex flows
- Real examples from the actual codebase

## Output Format
1. Complexity analysis
2. Visual diagrams (Mermaid)
3. Step-by-step breakdown
4. Interactive examples
5. Learning resources

## Resources
- [WORKFLOW.md](WORKFLOW.md) - Detailed methodology
- [EXAMPLES.md](EXAMPLES.md) - Comprehensive examples
```

**Refactor `commands/code-explain.md`:**
```markdown
---
description: Explain complex code through clear narratives and visual diagrams
---

# Code Explanation

Explain complex code sections, algorithms, or design patterns with visual aids.

## Usage

```
/code-explain <file or code description>
```

## Examples

```
/code-explain src/utils/data-transformer.ts
/code-explain the caching strategy in api/cache-manager.js
/code-explain the authentication algorithm
```

This command invokes the code-explanation skill with: $ARGUMENTS
```

### Validation
- [ ] Skill auto-invokes on "explain this code" type requests
- [ ] `/code-explain` command works and invokes skill
- [ ] Progressive disclosure works (supporting docs load on demand)

---

## Phase 3: Merge Documentation Capabilities

**Effort**: Medium | **Risk**: Medium

### Current State
- `agents/docs-architect.md`: Comprehensive long-form documentation agent
- `commands/doc-generate.md`: ~650 lines with API docs, README generation, etc.

### Target State

**Keep `agents/docs-architect.md`** (enhanced)
- Add explicit guidance on when to use
- Reference the new lightweight skill

**Create `skills/documentation-generation/`:**

| File | Content | Target Size |
|------|---------|-------------|
| `SKILL.md` | Pattern guidance, quick templates, routing | ~100-150 lines |
| `WORKFLOW.md` | Detailed documentation workflows | Extracted from command |
| `EXAMPLES.md` | Template examples (README, API docs) | Extracted from command |

**SKILL.md Structure:**
```yaml
---
name: documentation-generation
description: Provides patterns and templates for generating API docs, architecture
guides, READMEs, and technical documentation. Use when writing documentation,
creating docs from code, or generating documentation artifacts. Routes to
docs-architect agent for comprehensive analysis.
---

# Documentation Generation

Quick patterns for common documentation tasks.

## Quick Reference

| Documentation Type | Approach |
|--------------------|----------|
| Quick README | Use templates in EXAMPLES.md |
| API Documentation | OpenAPI generation patterns |
| Architecture Guide | Use docs-architect agent |
| Comprehensive Docs | Use docs-architect agent |

## When to Use docs-architect Agent

For complex documentation needs (10-100+ pages):
- Deep codebase analysis
- Architecture documentation
- Technical manuals
- System documentation

Invoke: "Use the docs-architect agent to document [scope]"

## Quick Patterns

### README Generation
[Brief template reference]

### API Documentation
[Brief OpenAPI pattern reference]

## Resources
- [WORKFLOW.md](WORKFLOW.md) - Detailed documentation workflows
- [EXAMPLES.md](EXAMPLES.md) - Complete templates and examples
```

**Refactor `commands/doc-generate.md`:**
```markdown
---
description: Generate comprehensive documentation from code with AI-powered analysis
---

# Documentation Generation

Generate documentation for your codebase.

## Usage

```
/doc-generate <scope or type>
```

## Quick Documentation

For quick docs (READMEs, API refs), specify the scope:
```
/doc-generate README for the authentication module
/doc-generate API documentation for src/api/users
```

## Comprehensive Documentation

For deep analysis and long-form documentation, use the docs-architect agent:
```
"Use the docs-architect agent to create comprehensive documentation for [system]"
```

This command invokes the documentation-generation skill with: $ARGUMENTS
```

### Validation
- [ ] Skill auto-invokes on documentation-related requests
- [ ] Clear routing between quick patterns and agent
- [ ] `/doc-generate` works for simple cases
- [ ] Complex cases route to docs-architect agent

---

## Phase 4: Update README and Cross-References

**Effort**: Low | **Risk**: Low

### Changes

1. **Update `doc/README.md`**
   - Update skills section (diagramming, documentation-generation, code-explanation, adr)
   - Update commands section (thin routers)
   - Update examples

2. **Update `CLAUDE.md`** (root)
   - Update doc plugin description if needed

3. **Verify all cross-references**
   - Check skill-to-skill references
   - Check command-to-skill references
   - Check agent references in skills

---

## Implementation Order

1. **Phase 1** (Low risk): Rename mermaid → diagramming
2. **Phase 2** (Low risk): Convert code-explain to skill
3. **Phase 3** (Medium risk): Merge documentation capabilities
4. **Phase 4** (Low risk): Update README and references

Each phase is independently deployable and can be tested before proceeding.

---

## Rollback Plan

Each phase can be rolled back via git:
```bash
git checkout -- doc/
```

Or selectively:
```bash
git checkout -- doc/skills/mermaid/  # Undo rename
git checkout -- doc/commands/code-explain.md  # Undo conversion
```

---

## Success Criteria

- [ ] All components follow naming conventions
- [ ] Skills use progressive disclosure (SKILL.md < 150 lines)
- [ ] Commands are thin routers (~50-100 lines)
- [ ] Clear separation between agent (complex) and skills (patterns)
- [ ] All existing functionality preserved
- [ ] README accurately reflects new structure

---

## Approval

- [ ] Plan reviewed
- [ ] Ready to implement

**Next Step**: Once approved, begin with Phase 1 (rename mermaid → diagramming)
