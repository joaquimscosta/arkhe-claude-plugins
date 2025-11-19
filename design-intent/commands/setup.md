---
description: Initialize design intent project structure with templates for memory, specs, and design patterns
---

# /setup

**Purpose**: Initialize the Design Intent for SDD (Spec-Driven Development) structure in your project

**Usage**: `/setup`

## What This Command Does

1. **Creates Directory Structure** - Sets up the complete design intent folder hierarchy
2. **Copies Templates** - Installs all necessary templates for specs, design patterns, and session documentation
3. **Establishes Memory** - Creates constitution, team roles, and project vision files
4. **Prepares Workflow** - Everything needed to start the SDD workflow immediately

## Directory Structure Created

```
your-project/
├── design-intent/
│   ├── memory/
│   │   ├── constitution.md      # Core development principles
│   │   ├── team-roles.md        # AI/User collaboration expectations
│   │   └── project-vision.md    # Your project overview (template)
│   ├── specs/
│   │   └── 000-template/
│   │       ├── feature-spec.md       # Feature specification template
│   │       └── implementation-plan.md # Implementation plan template
│   ├── patterns/
│   │   └── design-intent-template.md  # Pattern documentation template
│   └── diary/
│       └── session-template.md   # Session diary template
```

## Process

### 1. Check Prerequisites
- Verify git repository exists
- Check if structure already exists (warn if overwriting)

### 2. Create Directories
```bash
mkdir -p design-intent/memory
mkdir -p design-intent/specs/000-template
mkdir -p design-intent/patterns
mkdir -p design-intent/diary
```

### 3. Copy Template Files

Copy all templates from the plugin to your project:
- Memory files (constitution, team-roles, project-vision)
- Spec templates (feature-spec, implementation-plan)
- Design intent template
- Session diary template

### 4. Post-Setup Guidance

After setup completes:

1. **Review Constitution** - Read `design-intent/memory/constitution.md` to understand the principles
2. **Customize Project Vision** - Fill in `design-intent/memory/project-vision.md` with your project details
3. **Optional MCP Setup** - Configure Figma and Fluent UI MCPs for enhanced capabilities

## Template Locations in Plugin

The templates are sourced from the plugin's `templates/` directory. Do not modify these - they serve as the canonical source. Customize the copies in your project.

## Next Steps After Setup

1. **Read the constitution** - Understand the development principles
2. **Customize your project vision** - Make it specific to your goals
3. **Start with `/feature`** - Create your first feature specification
4. **Use `/design`** - Implement from visual references
5. **Document with `/document-design-intent`** - Capture successful patterns

## When to Use

- Starting a new React prototype project
- Adding design intent workflow to an existing project
- Resetting to fresh templates (will prompt before overwriting)

## Output

```markdown
## Design Intent Setup Complete

✓ Created directory structure
✓ Installed memory files (constitution, team-roles, project-vision)
✓ Installed spec templates
✓ Installed design intent template
✓ Installed diary template

### Next Steps
1. Read: design-intent/memory/constitution.md
2. Customize: design-intent/memory/project-vision.md
3. Start: /feature [your first feature]

### Optional: MCP Server Setup
For enhanced capabilities, configure these MCP servers:
- figma-dev-mode-mcp-server (Figma integration)
- fluent-pilot (Fluent UI guidance)

See plugin README for setup instructions.
```
