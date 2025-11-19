# Design Intent Plugin

Design Intent for Spec-Driven Development (SDD) - Build React prototypes with AI while maintaining design consistency through documented patterns.

## Overview

This plugin provides a complete workflow for building frontend prototypes with AI assistance while maintaining design consistency. It combines:

- **Spec-Driven Development (SDD)** - Structured workflow from specification to implementation
- **Design Intent Documentation** - Capture your team's design dialect for consistency
- **Specialized Agents** - Visual accuracy specialist for UI implementation

## Installation

```bash
# Add marketplace (if not already added)
/plugin marketplace add ./arkhe-claude-plugins

# Install plugin
/plugin install design-intent@arkhe-claude-plugins
```

## Quick Start

### 1. Initialize Your Project

```bash
/setup
```

This creates the complete design intent structure in your project with all templates.

### 2. Start Building

**Create a feature:**
```bash
/feature user authentication flow
```

**Plan implementation:**
```bash
/plan
```

**Implement from visual reference:**
```bash
/design [screenshot or Figma URL]
```

**Execute full implementation:**
```bash
/implement
```

### 3. Document Patterns

After completing work, capture successful design patterns:
```bash
/document-design-intent
```

### 4. Create Session Diary

Before ending your session:
```bash
/diary
```

## Commands

| Command | Description |
|---------|-------------|
| `/setup` | Initialize design intent structure with templates |
| `/feature [description]` | Create feature specification |
| `/plan` | Generate implementation plan from spec |
| `/design [reference]` | Implement from visual references (screenshots, Figma) |
| `/implement` | Execute implementation plan |
| `/document-design-intent` | Analyze work and suggest patterns to preserve |
| `/diary` | Create session diary for handoff |

## Skill

### Design Intent Specialist

Auto-invoked skill for creating accurate frontend implementations from visual references while maintaining design consistency.

**Capabilities:**
- Mandatory design intent pattern check before implementation
- Visual reference analysis (screenshots, Figma, descriptions)
- Section-by-section implementation for complex designs
- Conflict resolution between references and existing patterns
- Support for iterative "vibe coding" refinement

**Auto-triggers on:**
- Figma URLs
- Screenshots/design images
- UI implementation requests
- `/design` and `/implement` commands

**Documentation:**
- `skills/design-intent-specialist/SKILL.md` - Quick start
- `skills/design-intent-specialist/WORKFLOW.md` - Detailed process
- `skills/design-intent-specialist/EXAMPLES.md` - Usage examples
- `skills/design-intent-specialist/TROUBLESHOOTING.md` - Common issues

## Project Structure After Setup

```
your-project/
├── design-intent/
│   ├── memory/
│   │   ├── constitution.md      # Core development principles (7 Articles)
│   │   ├── team-roles.md        # AI/User collaboration expectations
│   │   └── project-vision.md    # Your project overview
│   ├── specs/
│   │   └── 000-template/        # Feature spec and plan templates
│   ├── patterns/
│   │   └── design-intent-template.md  # Pattern documentation template
│   └── diary/
│       └── session-template.md  # Session diary template
```

## The Constitution

The constitution (7 Articles) governs prototype development:

- **Article I**: Simplicity Imperative - Start simple, evolve gradually
- **Article II**: Anti-Abstraction Principle - Framework-first development
- **Article III**: Responsive Design Mandate - Mobile-first approach
- **Article IV**: Prototype Principles - Mock data, happy paths
- **Article V**: Feature-First Development - Features over visual fidelity
- **Article VI**: UI Quality Standards - Microinteractions, visual hierarchy
- **Article VII**: Design Intent Documentation - Document proven patterns

## Optional: MCP Server Setup

For enhanced capabilities, configure these optional MCP servers:

### Figma Dev Mode MCP Server

Enables reading Figma designs, extracting code, and retrieving design tokens.

**Installation:**
```bash
npm install -g @anthropic/mcp-server-figma-dev-mode
```

**Configuration (`.mcp.json`):**
```json
{
  "mcpServers": {
    "figma-dev-mode-mcp-server": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-figma-dev-mode"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your-figma-token"
      }
    }
  }
}
```

**Get Figma Token:**
1. Go to Figma → Account Settings → Personal Access Tokens
2. Generate a new token with read access

### Fluent UI Pilot MCP Server

Provides Fluent UI v9 component information and guidance.

**Installation:**
```bash
npm install -g @anthropic/mcp-server-fluent-pilot
```

**Configuration (`.mcp.json`):**
```json
{
  "mcpServers": {
    "fluent-pilot": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-fluent-pilot"]
    }
  }
}
```

### Combined Configuration

```json
{
  "mcpServers": {
    "figma-dev-mode-mcp-server": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-figma-dev-mode"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your-figma-token"
      }
    },
    "fluent-pilot": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-fluent-pilot"]
    }
  }
}
```

## Workflow

### Complete Development Cycle

```
1. /setup              → Initialize project structure
2. /feature            → Create feature specification
3. /plan               → Generate implementation plan
4. /implement or /design → Build the feature
5. /document-design-intent → Capture successful patterns
6. /diary              → Document session for handoff
```

### Design Intent Pattern

The workflow captures your team's "design dialect" - custom decisions that won't come from the design system:

- **Custom Layout Patterns** - App-specific compositions
- **Contextual Spacing** - Spacing decisions that deviate from tokens
- **Content Hierarchies** - Information architecture patterns
- **Custom Compositions** - Unique component combinations

**NOT documented:** Standard design system artifacts (colors, typography, default behaviors)

## When to Use This Plugin

- Starting a new React prototype project
- Building AI-assisted frontend implementations
- Maintaining design consistency across features
- Documenting design decisions for team alignment
- Creating session handoff documentation

## Requirements

- Git repository
- React project (for implementations)
- Claude Code CLI

## License

MIT
