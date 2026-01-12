---
description: Initialize design intent project structure with templates for memory, specs, and design patterns
---

# /setup

**Purpose**: Initialize the Design Intent for SDD (Spec-Driven Development) structure in your project with smart auto-detection

**Usage**: `/setup`

## What This Command Does

1. **Detects Project Configuration** - Analyzes package.json, README, .mcp.json, and existing code
2. **Confirms Settings with User** - Individual confirmations for each detected setting
3. **Creates Directory Structure** - Sets up the complete design intent folder hierarchy
4. **Auto-fills Templates** - Intelligently populates templates based on confirmed settings
5. **Supports Incremental Updates** - Re-running updates specific sections without overwriting customizations

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

### 1. Check for Existing Setup

If `design-intent/` directory already exists, offer incremental update:

```
Design Intent structure already exists.

What would you like to update?
1. Project vision (preserve customizations)
2. Constitution (merge new framework guidance)
3. Team roles (update MCP capabilities)
4. All templates (reset to defaults)
5. Cancel
```

### 2. Detection Phase

Analyze the project to auto-detect configuration:

**From package.json:**
- Framework (React, Vue, Angular, Next.js)
- Design system (@fluentui/react-components, @mui/material, @chakra-ui/react)
- TypeScript usage
- Key dependencies

**From README.md:**
- Project description and goals
- Target users mentioned
- Key features

**From .mcp.json:**
- Figma MCP server configured
- Fluent Pilot MCP configured
- Other relevant MCPs

**From existing code:**
- Design system component usage patterns
- Styling approach (CSS-in-JS, Tailwind, CSS Modules)

### 3. Confirmation Flow

Present each detection individually for confirmation:

```
## Project Configuration

Detected: Fluent UI v9 - use this as design system? (Y/n)
Detected: React 18 + TypeScript - configure for this? (Y/n)
Detected: Enterprise dashboard - confirm project type? (Y/n)
Detected: Figma MCP available - enable integration? (Y/n)
```

**When detection fails, prompt with options:**

```
Could not detect design system. Which are you using?
1. Fluent UI
2. Material UI
3. Chakra UI
4. Tailwind CSS
5. Other (specify)
```

```
Could not determine project type. What best describes your project?
1. Enterprise dashboard
2. Consumer application
3. Internal tool
4. Marketing site
5. Other (specify)
```

### 4. Create Directories

```bash
mkdir -p design-intent/memory
mkdir -p design-intent/specs/000-template
mkdir -p design-intent/patterns
mkdir -p design-intent/diary
```

### 5. Auto-fill Templates

Based on confirmed settings, customize each template:

**project-vision.md:**
- Author: from `git config user.name`
- Date: current date
- Overview: extracted from README.md
- Target Users: based on project type

**constitution.md:**
- Adjust Article I (Simplicity) priorities based on project type
- Add framework-specific guidance to Article II
- Customize Article VI (UI Quality) for design system
- Add detected MCP capabilities to workflow guidance

**team-roles.md:**
- Configure AI capabilities based on available MCPs
- Set expectations for design system expertise
- Adjust collaboration patterns for project complexity

### 6. Post-Setup Summary

```markdown
## Design Intent Setup Complete

### Detected Configuration
- Design System: Fluent UI v9
- Framework: React 18 + TypeScript
- Project Type: Enterprise dashboard
- MCP Servers: Figma, Fluent Pilot

### Files Created
✓ design-intent/memory/constitution.md (customized for React + Fluent UI)
✓ design-intent/memory/team-roles.md (MCP-aware)
✓ design-intent/memory/project-vision.md (pre-filled from README)
✓ design-intent/specs/000-template/ (spec templates)
✓ design-intent/patterns/design-intent-template.md
✓ design-intent/diary/session-template.md

### Next Steps
1. Review: design-intent/memory/constitution.md
2. Refine: design-intent/memory/project-vision.md (add specifics)
3. Start: /feature [your first feature]
```

## Template Locations in Plugin

The templates are sourced from the plugin's `templates/` directory. Do not modify these - they serve as the canonical source. Customize the copies in your project.

## When to Use

- **New projects** - Starting a new React prototype project
- **Existing projects** - Adding design intent workflow to an existing codebase
- **Configuration changes** - Re-run to update templates when adding new MCPs or changing design systems
- **Team onboarding** - Update team-roles.md when collaboration patterns change

## Incremental Update Behavior

When run on an existing project, `/setup` intelligently handles updates:

- **Preserves customizations** - Won't overwrite user content in project-vision.md
- **Merges new guidance** - Adds framework-specific sections to constitution.md
- **Updates capabilities** - Refreshes team-roles.md with newly detected MCPs
- **Offers granular control** - Choose which templates to update

## Detection Fallbacks

When auto-detection cannot determine a setting:

| Setting | Fallback Behavior |
|---------|-------------------|
| Design System | Prompt with common options (Fluent, Material, Chakra, Tailwind) |
| Framework | Prompt with common options (React, Vue, Angular, Next.js) |
| Project Type | Prompt with common options (Enterprise, Consumer, Internal, Marketing) |
| MCP Servers | Skip MCP-specific customizations |

## Template Customization Reference

### Constitution Adjustments by Project Type

**Enterprise Dashboard:**
- Emphasize data density and information hierarchy
- Prioritize keyboard navigation and accessibility
- Focus on consistent patterns over visual novelty

**Consumer Application:**
- Emphasize visual appeal and breathing room
- Prioritize microinteractions and delight
- Focus on progressive disclosure and simplicity

### Framework-Specific Guidance

**React + TypeScript:**
- Component composition patterns
- Hook usage guidelines
- Type safety expectations

**Next.js:**
- Server/client component decisions
- Route organization patterns
- Data fetching strategies
