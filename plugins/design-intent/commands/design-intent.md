---
description: Guided UI/visual development with structured exploration, architecture design, and quality review
argument-hint: Optional visual reference (screenshot, Figma URL) or description
---

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
   - Feature spec reference
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
