# design-intent — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

UI/UX Design Plugin - Visual fidelity from Figma/mockups, design system enforcement, React UI prototyping with live browser gallery, pattern memory, and brand icon asset generation.

## Skills

- **design-intent-specialist** — Creates accurate frontend implementations from visual references while maintaining design consistency. Use when user provides Figma URLs, screenshots, design images, requests visual implementation fr…
- **icon-forge** — Generate brand icons as SVG and produce all platform assets including favicon package (ICO, SVG with dark mode, apple-touch-icon), PWA manifest icons, and mobile app icons. Use when user runs /icon-f…
- **prototype** — Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt and serves them in a live browser gallery. Use when user runs /prototype, asks to "prototype a UI", "mock u…
- **stitch-to-react** — Converts Google Stitch exports into React components with design DNA integration. Use when user references design-intent/google-stitch exports, mentions "convert Stitch output", "Stitch to React", or…

## Commands as Trigger Phrases

### When the user says "/design-intent:design-intent" (args: Optional visual reference (screenshot, Figma URL) or description)

Guided UI/visual development with structured exploration, architecture design, and quality review

# Design Intent Development

You are helping a developer implement UI/visual work while maintaining design consistency. Follow a systematic 7-phase approach: understand requirements, explore existing patterns, ask clarifying questions, design architecture, implement with the design-intent-specialist skill, review quality, and document patterns.

## Core Principles

- **Visual fidelity matters**: Match visual references accurately, flag conflicts with existing patterns
- **Ask clarifying questions**: Identify all visual ambiguities, responsive needs, accessibility requirements
- **Explore before building**: Understand existing components, tokens, and patterns first
- **Read files identified by agents**: After agents complete, read identified files to build detailed context
- **Use TodoWrite**: Track all progress throughout the 7 phases
- **Invoke design-intent-specialist**: Use the skill during implementation phase for visual accuracy

## Quick Mode

If invoked with `--quick` in the arguments, skip Phases 2 (Exploration) and 4 (Architecture):
- Go directly from Discovery to Questions
- After Questions, proceed to Implementation
- Still perform Review and Patterns phases

Use `--quick` for small changes, single components, or when patterns are already well-known.

---

## Phase 1: Discovery

**Goal**: Understand what UI/visual work needs to be done

Initial request: $ARGUMENTS

**Actions**:
1. Create todo list with all 7 phases
2. Check if design-intent structure exists at `/design-intent/`
   - If not found, suggest running `/setup` first
3. Analyze the request type:
   - Screenshot/image reference provided
   - Figma URL provided
   - Text description of UI to build
   - Lightweight brief or notes (inline or file)
   - Existing spec from /develop or other workflow (read if present)
4. If visual reference provided, perform initial visual analysis:
   - Layout structure
   - Key components visible
   - Color palette impression
   - Typography observations
5. If requirements unclear, ask user:
   - What UI problem are they solving?
   - What should it look like/do?
   - What framework/design system are they using?
   - Any constraints (accessibility, mobile-first, performance)?
6. Summarize understanding and confirm with user before proceeding

**Skip to Phase 3 if**: `--quick` flag is present in arguments

---

## Phase 2: Exploration

**Goal**: Understand existing UI patterns, components, and design tokens

_…full command body at `plugins/design-intent/commands/design-intent.md`._

### When the user says "/design-intent:diary"

Create a session diary entry to document development progress, decisions, and handoff context

# /diary

This command creates a session diary entry to document development progress, decisions, and handoff context.

## Usage

```
/diary
```

Creates a new diary entry for the current date, or updates the existing entry if one already exists for today.

## Process

### 1. Determine File Path
- **File naming**: `/design-intent/diary/session-YYYY-MM-DD.md` (e.g., `/design-intent/diary/session-2024-01-15.md`)
- **Date format**: Use current date in YYYY-MM-DD format
- **Check existing**: If file already exists for today, update it instead of creating new

### 2. Gather Session Information
Before creating the entry, collect information about:
- **Session goals**: What was planned for this session
- **Accomplishments**: What was actually built or completed
- **Key decisions**: Important choices made during implementation
- **Current state**: Where the project stands now
- **Next priorities**: What should happen in the next session
- **Known issues**: Problems that aren't blocking but need attention

### 3. Create Diary Entry
Use the template from `/design-intent/diary/session-template.md`

### 4. Content Guidelines

#### What We Built Section
Focus on **concrete outcomes**:
- ✅ "Built gallery component with 3-card responsive layout"
- ✅ "Implemented user authentication flow with mock data"
- ❌ "Worked on some components"
- ❌ "Made progress on the frontend"

#### Key Implementation Details
Document **decisions and reasoning**:
- Why specific approaches were chosen
- What alternatives were considered
- How constitution principles were applied
- Trade-offs made for prototype goals

#### Current State
Be **specific about status**:
- What functionality works end-to-end
- What's partially implemented
- What's blocked or needs attention
- Any integration points established

#### Tomorrow's Priorities
Make priorities **actionable**:
- ✅ "Add loading states to gallery cards"
- ✅ "Implement search functionality for user dashboard"
- ❌ "Continue working on UI"
- ❌ "Fix various issues"

### 5. Update Existing Entry
If a diary entry already exists for today:
- **Append to accomplishments**: Add new items to "What We Built"
- **Update current state**: Reflect latest progress
- **Revise priorities**: Update based on what was completed
- **Add new decisions**: Document any additional key choices made

### 6. Output Confirmation
After creating/updating the diary entry:

```markdown
## Diary Entry Complete

_…full command body at `plugins/design-intent/commands/diary.md`._

### When the user says "/design-intent:prototype" (args: "<component description> [--vary <1|2|3>] [--dir <output-dir>] [--continue]")

Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt and serves them in a live browser gallery

# Prototype

Generate rapid UI prototypes following the **prototype** skill. Input: $ARGUMENTS

Generate all 3 artifacts in one pass — do not pause between them or ask for confirmation. The value is seeing 3 diverse approaches side-by-side in a live gallery.

If `$ARGUMENTS` contains `--continue`, read the user's pick from the most recent prototype session's `events.jsonl` and report it instead.

### When the user says "/design-intent:save-patterns" (args: "[category]")

Analyze recent work and suggest design patterns that should be preserved as design intent

# /save-patterns

**Purpose**: Analyze recent work and suggest design patterns that should be preserved as design intent

**Usage**: `/save-patterns [category]`

**Examples**:
- `/save-patterns` - Analyze all recent work for patterns
- `/save-patterns components` - Focus on component patterns only
- `/save-patterns foundations` - Focus on spacing, typography, color patterns
- `/save-patterns layouts` - Focus on layout and grid patterns

## What This Command Does

1. **Reviews Recent Work** - Analyzes code changes, components created, and design decisions made in the current session
2. **Identifies Reusable Patterns** - Finds design decisions that could benefit other features
3. **Suggests Documentation Locations** - Recommends where each pattern should be documented (components/, foundations/, patterns/)
4. **Presents Summary for Review** - Shows findings to user for manual decision-making
5. **Waits for User Direction** - Does NOT automatically document anything

## Analysis Focus

The agent will look for:

### **Custom Design Decisions**
- Layout patterns that deviate from standard design system
- Spacing decisions that aren't standard tokens
- Component compositions unique to your application
- Content hierarchies and information architecture patterns

### **Reusable Components**
- Custom components created during implementation
- Extensions to existing components
- Component variations that could be reused

### **Responsive Patterns**
- Breakpoint-specific behaviors
- Mobile optimization strategies
- Layout adaptations across screen sizes

### **Visual Treatments**
- Color usage beyond design system tokens
- Typography treatments for specific contexts
- Shadow, border, and elevation patterns

## Output Format

The agent will present findings as:

```markdown
## Design Intent Candidates

### Components Patterns
- **CustomDataCard** → `components/data-card.md`
  - Reason: Unique hover states and nested action buttons
  - Reusability: High - used in 3+ contexts

### Foundation Patterns
- **48px Section Spacing** → `foundations/custom-spacing.md`
  - Reason: Consistent spacing between major page sections
  - Reusability: Medium - applies to L1 layouts

### Layout Patterns
- **Three-Column Dashboard** → `patterns/dashboard-layout.md`
  - Reason: Specific grid system for dashboard pages
  - Reusability: High - dashboard variations

_…full command body at `plugins/design-intent/commands/save-patterns.md`._

### When the user says "/design-intent:setup"

Initialize design intent project structure with templates for memory, patterns, and session diary

# /setup

**Purpose**: Initialize the Design Intent project structure in your project with smart auto-detection

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

_…full command body at `plugins/design-intent/commands/setup.md`._
