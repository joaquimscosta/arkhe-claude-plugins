# design-intent — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

UI/UX Design Plugin - Visual fidelity from Figma/mockups, design system enforcement, React UI prototyping with pattern memory, and brand icon asset generation.

## Skills

- **design-intent-specialist** — Creates accurate frontend implementations from visual references while maintaining design consistency. Use when user provides Figma URLs, screenshots, design images, requests visual implementation fr…
- **icon-forge** — Generate brand icons as SVG and produce all platform assets including favicon package (ICO, SVG with dark mode, apple-touch-icon), PWA manifest icons, and mobile app icons. Use when user runs /icon-f…
- **prototype** — Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt, each driven by a unique physical/material metaphor. Use when user runs /prototype, asks to "prototype a UI…
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

**Actions**:
1. Launch 2-3 ui-explorer agents in parallel. Each agent should:
   - Focus on a different aspect of the UI codebase
   - Return list of 5-10 key files to read
   - Identify reuse opportunities and conflicts

   **Example agent prompts**:
   - "Find existing components similar to [requirement], analyze their props, styling, and usage patterns"
   - "Map design token usage in this codebase: colors, spacing, typography, shadows"
   - "Analyze /design-intent/patterns/ for established design decisions that apply to [task]"
   - "Identify responsive patterns, breakpoints, and mobile-first approaches in [area]"

2. Once agents return, read all files they identified
3. Present comprehensive summary:
   - Reusable components found (with file:line)
   - Design tokens and conventions
   - Established design intent patterns
   - Similar implementations for reference
   - Potential conflicts to resolve

---

## Phase 3: Clarifying Questions

**Goal**: Fill in visual/UI gaps and resolve all ambiguities

**CRITICAL**: Do not skip this phase. Ambiguity leads to rework.

**Actions**:
1. Review exploration findings (if Phase 2 was run) and original request
2. Identify underspecified aspects:

   **Visual Preferences**
   - Color palette choices (which semantic colors?)
   - Spacing preferences (compact, comfortable, spacious?)
   - Typography details (sizes, weights, line heights?)

   **Responsive Behavior**
   - Target breakpoints (mobile, tablet, desktop?)
   - Mobile layout approach (stack, hide, drawer?)
   - Tablet-specific needs?

   **Interactive States**
   - Hover effects needed?
   - Focus styling approach?
   - Loading states?
   - Error states?
   - Disabled appearance?

   **Accessibility**
   - ARIA label requirements?
   - Keyboard navigation needs?
   - Screen reader considerations?
   - Color contrast requirements?

   **Edge Cases**
   - Empty state design?
   - Error/failure states?
   - Overflow handling (truncate, wrap, scroll)?
   - Maximum content scenarios?

   **Animation/Transitions**
   - Motion preferences (subtle, expressive, none)?
   - Duration and easing?
   - Entrance/exit animations?

   **Component Variations**
   - Different sizes needed?
   - Theme variants (light/dark)?
   - Density options?

3. Present all questions in organized list by category
4. **Wait for user answers before proceeding to architecture**

If user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple UI implementation approaches with trade-offs

**Actions**:
1. Launch 2-3 ui-architect agents with different design philosophies:
   - **Minimal/Conservative**: "Design UI architecture with maximum reuse of existing components, smallest changes to codebase"
   - **Clean/Ideal**: "Design optimal UI component architecture with proper abstractions and long-term maintainability"
   - **Pragmatic/Balanced**: "Design UI architecture balancing reuse with new components where clarity requires it"

2. Each agent provides:
   - Component structure diagram
   - Props/interface definitions
   - Styling approach
   - State management needs
   - Responsive strategy
   - File organization

3. Review all approaches and form your recommendation based on:
   - Task complexity (simple fix vs. new feature)
   - Existing patterns in codebase
   - User's stated preferences
   - Long-term maintainability needs

4. Present to user:
   - Brief summary of each approach (2-3 sentences)
   - Trade-offs comparison table
   - **Your recommendation with clear reasoning**
   - Concrete implementation differences

5. **Ask user which approach they prefer before proceeding**

---

## Phase 5: Implementation

**Goal**: Build the UI using the design-intent-specialist skill

**DO NOT START without explicit user approval**

**Actions**:
1. Wait for explicit user approval ("proceed", "go ahead", "implement", etc.)
2. Read all relevant files identified in previous phases
3. Read the chosen architecture plan from Phase 4 (or your default approach if `--quick`)
4. **Invoke the design-intent-specialist skill** by working through its workflow:
   - Mandatory design intent pattern check
   - Visual reference analysis
   - Section decomposition for complex designs
   - Implementation following established patterns
   - Conflict resolution when reference diverges from patterns
5. Follow the architecture chosen in Phase 4
6. Use established patterns from Phase 2 exploration
7. Update todos as you progress through implementation
8. Support iterative refinement ("more spacing", "darker", "align left")

**Skill Integration**: The design-intent-specialist skill handles actual visual implementation with its specialized capabilities for accuracy and pattern awareness.

---

## Phase 6: Quality Review

**Goal**: Ensure UI is visually consistent, accessible, and follows patterns

**Actions**:
1. Launch 3 design-reviewer agents in parallel with different focuses:
   - **Visual consistency**: "Review for design token compliance, spacing adherence, typography correctness, visual hierarchy"
   - **Accessibility/Responsiveness**: "Review for ARIA implementation, keyboard navigation, responsive breakpoints, touch targets"
   - **Pattern adherence**: "Review for design intent pattern compliance, component consistency, naming conventions"

2. Each reviewer uses confidence scoring (only >=80 reported)

3. Consolidate findings by severity:
   - **Critical**: Must fix - accessibility violations, broken responsive, major pattern conflicts
   - **Important**: Should fix - visual inconsistencies, minor UX issues

4. Present findings to user and ask decision:
   - **Fix now**: Address issues before completing
   - **Fix later**: Document as known issues, proceed
   - **Proceed as-is**: Accept current state

5. Address issues based on user decision

---

## Phase 7: Patterns

**Goal**: Extract and document reusable design patterns

**Actions**:
1. Analyze what was built in Phase 5
2. Identify design pattern candidates:
   - Custom layout patterns (not standard design system)
   - Spacing decisions (contextual adjustments)
   - Component compositions (how primitives combine)
   - Responsive strategies (breakpoint behaviors)
   - Visual treatments (unique styling approaches)
   - State patterns (loading, error, empty)

3. Present pattern candidates with:
   - Pattern name and description
   - Suggested location: `patterns/components/`, `patterns/foundations/`, `patterns/layouts/`
   - Reusability assessment (high/medium/low)
   - Reason for documentation

4. **Wait for user to approve which patterns to save**

5. For approved patterns, document using the design-intent template:
   ```markdown
   ## [Pattern Name]

   **Context**: When this pattern applies
   **Decision**: What we do
   **When to Use**: Specific scenarios
   **Components**: Files/components involved
   **Why**: Rationale for the decision
   **Dependencies**: Related patterns or requirements
   ```

6. Mark all todos complete

7. Summarize:
   - What was built
   - Key design decisions made
   - Files created/modified
   - Patterns documented
   - Suggested next steps (tests, documentation, related features)

---

## Constitution Compliance

Throughout all phases, ensure work follows the project constitution (if present at `/design-intent/memory/constitution.md`):

- **Article I** (Simplicity): Start simple, evolve gradually
- **Article II** (Framework-first): Use design system components before custom
- **Article III** (Responsive): Mobile-first approach
- **Article IV** (Prototype): Mock data, happy paths for prototypes
- **Article V** (Feature-first): Features define WHAT, visuals define HOW
- **Article VI** (UI Quality): Microinteractions, visual hierarchy matter
- **Article VII** (Documentation): Document proven patterns

---

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

**File**: `/design-intent/diary/session-[YYYY-MM-DD].md`
**Status**: [Created new / Updated existing]

### Session Summary
- **Accomplishments**: [X] items documented
- **Key Decisions**: [X] implementation choices recorded
- **Next Priorities**: [X] tasks identified for next session

### Handoff Ready
This entry provides context for:
- ✓ Current project state
- ✓ Recent decisions and trade-offs
- ✓ Next session priorities
- ✓ Known issues and considerations
```

## When to Use

### End of Session (Primary)
- User says "let's wrap up" or similar
- Natural stopping point reached
- Before committing major work

### Major Milestone
- Feature completion
- Significant architectural decision
- Integration point established

### Handoff Situations
- Switching context to different feature
- Long break between sessions expected
- Complex decisions that need documentation

### User Request
- User explicitly asks for documentation
- Project review or status check needed
- Planning next development phase

## Integration Points

### Session Continuity
- Next session starts by reading latest diary entry
- Provides context for where to resume work
- Maintains momentum across sessions

### Git Workflow
- Create diary entries before major commits
- Reference diary in commit messages if helpful
- Document decisions that affect architecture

### Design Intent Relationship
- Note any design patterns established
- Reference any `/save-patterns` commands used
- Track custom components created

### Constitution Compliance
- Document how constitution principles were applied
- Note any trade-offs made for simplicity
- Record framework-first decisions

## Behavioral Notes

1. **Outcome-focused**: Document what was built, not how it was built
2. **Decision-focused**: Capture why choices were made, not just what was done
3. **Handoff-ready**: Write for someone else to continue the work
4. **Actionable**: Make priorities concrete and specific
5. **Honest**: Document both successes and known issues
6. **Pattern-aware**: Note design decisions that affect consistency

### When the user says "/design-intent:prototype" (args: "<component description> [--vary <1|2|3>] [--dir <output-dir>]")

Rapid UI prototyping — generates 3 visually distinct HTML/CSS components from a text prompt

# Prototype

Generate rapid UI prototypes following the **prototype** skill. Input: $ARGUMENTS

Generate all 3 artifacts in one pass — do not pause between them or ask for confirmation. The value is seeing 3 diverse approaches side-by-side.

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

## Not Recommended for Documentation
- Standard Fluent spacing tokens (already in design system)
- Default component behaviors (documented in Fluent)
```

## User Decision Process

After reviewing the summary:
1. **Review each suggestion** - Decide which patterns are worth preserving
2. **Request documentation** - "Document the CustomDataCard pattern"
3. **Provide guidance** - "Skip the spacing pattern, it's too specific"
4. **Manual control** - You decide what gets documented and where

## When to Use

- After completing a feature implementation
- When you've created custom components or patterns
- Before starting new features (to capture recent learning)
- When you want to build up your design intent library

## What Gets Documented

Only patterns you explicitly approve will be documented using the **design intent template** at `/design-intent/patterns/design-intent-template.md`.

**Must follow template structure exactly**:
- Use the template headings: Context, Decision, When to Use, Components, Why, Dependencies
- Follow the writing guidelines in the template
- Focus on design decisions, not implementation details
- Keep content concise and agent-friendly
- Apply the template test: "If this component changed, would this design intent become wrong?"

**Document only your design dialect**:
- Custom layout patterns and compositions
- Contextual spacing decisions that deviate from design system
- Component usage rules specific to your application
- Visual treatments that create your unique design voice

**Do NOT document design system artifacts**:
- Standard design tokens (colors, typography scales)
- Default component behaviors from Fluent UI
- Standard responsive breakpoints

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
✓ design-intent/patterns/design-intent-template.md
✓ design-intent/diary/session-template.md

### Next Steps
1. Review: design-intent/memory/constitution.md
2. Refine: design-intent/memory/project-vision.md (add specifics)
3. Start: /design-intent [visual reference or description]
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
