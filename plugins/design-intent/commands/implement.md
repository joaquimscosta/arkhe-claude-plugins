---
description: Execute the implementation plan, coordinating both engineering and design aspects of the feature
argument-hint: [feature-name] (defaults to current branch)
---

# /implement

**Purpose**: Execute the implementation plan, coordinating both engineering and design aspects of the feature

**Usage**: `/implement` or `/implement <feature-name>`

## What This Command Does

1. **Derives Feature Name** - Gets feature name from git branch or explicit argument
2. **Detects Spec System** - Searches for specs in priority order (Design-Intent, then SpecKit)
3. **Loads Appropriate Specs** - Based on detected system
4. **Executes Implementation**:
   - **Design-Intent** → Uses design-intent-specialist workflow
   - **SpecKit** → Uses task-driven or phase-based workflow
5. **Smart Quality Review** - Only runs design-reviewer agents if UI work detected

---

## Feature Name Derivation

The command derives the feature name using this logic:

1. **If argument provided**: Use the explicit feature name
   - `/implement user-auth` → feature = `user-auth`

2. **If no argument**: Extract from current git branch
   - `feat/001-user-auth` → `001-user-auth` (strips type prefix only)
   - `fix/login-bug` → `login-bug` (strips type prefix)
   - `feature/dashboard` → `dashboard` (strips type prefix)

3. **Branch parsing rules**:
   - Remove common prefixes: `feat/`, `fix/`, `feature/`, `refactor/`, `chore/`, `docs/`, `test/`
   - Keep numbered prefixes intact (e.g., `001-dashboard` stays as-is)
   - Result is the feature slug used to locate specs

4. **Fallback**: If on `main` or `master` without argument, prompt for feature name

---

## Spec System Detection

The command searches for specs in this priority order:

| Priority | Location | Spec System | Required Files |
|----------|----------|-------------|----------------|
| 1 | `design-intent/specs/{feature}/` | Design-Intent | `implementation-plan.md` |
| 2 | `plan/specs/{feature}/` | SpecKit | `plan.md` |
| 3 | `specs/{feature}/` | SpecKit | `plan.md` |

### Detection Algorithm

```
1. Get git repository root
2. Derive feature name (from argument or branch)
3. Check design-intent/specs/{feature}/implementation-plan.md
   → If exists: SPEC_SYSTEM = "design-intent"
4. Else check plan/specs/{feature}/plan.md
   → If exists: SPEC_SYSTEM = "speckit", SPEC_PATH = "plan/specs/{feature}"
5. Else check specs/{feature}/plan.md
   → If exists: SPEC_SYSTEM = "speckit", SPEC_PATH = "specs/{feature}"
6. If none found: Show error with guidance
```

---

## Implementation Strategy

### **Design-Intent Workflow**

When `design-intent/specs/{feature}/` is detected:

For UI implementation, follow the design-intent-specialist workflow:

- **Existing design intent review** - Check established patterns for consistency
- **Sectional decomposition** - Break complex UI into manageable sections (header, nav, main, footer)
- **Detailed analysis** - Focus on layout, spacing, typography, responsiveness per section
- **Conflict resolution** - Handle conflicts between plan specs and existing design intent patterns
- **Component reuse** - Leverage existing components where appropriate

See `skills/design-intent-specialist/SKILL.md` for detailed implementation guidance.

### **SpecKit Workflow**

When `plan/specs/{feature}/` or `specs/{feature}/` is detected:

#### If `tasks.md` exists (Task-Driven)

1. Load `plan.md` for implementation context and guidance
2. Load `tasks.md` and parse the task list
3. For each uncompleted task (`- [ ]`):
   - Announce: "Implementing: {task description}"
   - Execute the implementation
   - Mark task complete: Update `- [ ]` to `- [x]` in `tasks.md`
4. After all tasks complete, summarize progress

#### If only `plan.md` exists (Phase-Based)

1. Load `plan.md` for implementation guidance
2. Extract phases/sections from the plan
3. Implement each phase sequentially
4. Report progress after each phase

#### SpecKit Implementation Approach

- Use general implementation patterns (not design-intent-specialist by default)
- Follow the technical approach specified in `plan.md`
- Respect any constraints from `spec.md` if present
- May optionally use design-intent-specialist if plan involves significant UI work

### **For Backend/Logic Components**

For backend implementation (both spec systems):

- **API endpoints** - Server logic, data handling, business rules
- **Database changes** - Schema updates, migrations, queries
- **Testing** - Unit tests, integration tests, component tests
- **Architecture** - Project structure, configuration, dependencies

### **Coordination Approach**

- **Sequential implementation** - Design components first (they define data needs), then backend
- **Iterative refinement** - Build, test, refine each component
- **Integration points** - Ensure frontend and backend work together seamlessly

---

## Design Implementation Behavior

When implementing visual components, follow the design-intent-specialist workflow (see `skills/design-intent-specialist/SKILL.md`):

### **Conflict Resolution**

When implementation plan conflicts with existing design intent:

1. **Implement the plan faithfully** - Follow the implementation plan specifications
2. **Flag conflicts clearly** - "Plan specifies 16px spacing, but our design intent uses 12px for this pattern"
3. **Ask for user guidance** - "Should I follow the plan exactly, or adapt to use our established spacing?"
4. **Suggest implications** - "If we use the plan spacing, should this become our new standard?"

### **Section-by-Section Implementation**

For complex UI components, automatically breaks down into:

- **Layout**: Component structure, grid systems, positioning
- **Spacing**: Margins, padding, gaps between elements
- **Typography**: Font weights, sizes, line heights, text treatments
- **Responsiveness**: How each section adapts across breakpoints
- **Visual treatment**: Colors, shadows, borders, hover states

---

## Smart Quality Review

Quality review is triggered based on spec content analysis.

### UI Detection Logic

Before launching design-reviewer agents, scan the spec files for UI-related content.

**UI Keywords (case-insensitive)**:

| Category | Keywords |
|----------|----------|
| Components | component, button, form, input, modal, dialog, dropdown, menu, navbar, sidebar, header, footer, card, panel, table, list, grid, tab, accordion, tooltip, toast |
| Visual/Design | layout, design, visual, style, css, scss, styled, color, theme, dark mode, icon, animation, transition, hover, responsive, breakpoint |
| Frontend | react, vue, angular, jsx, tsx, html, fluent, material, tailwind, UI, frontend, page, screen, view, navigation |

**Detection Rule**:

Run design-reviewer agents if:
- **≥3 different keyword categories** are matched, OR
- **≥5 total keyword matches** across all categories

Otherwise, skip the quality review phase (purely backend spec).

### Review Focuses (When Triggered)

Launch 3 design-reviewer agents in parallel:

1. **Visual Consistency**
   - "Review for design token compliance, spacing adherence, typography correctness, visual hierarchy"

2. **Accessibility/Responsiveness**
   - "Review for ARIA implementation, keyboard navigation, responsive breakpoints, touch targets"

3. **Pattern Adherence**
   - "Review for design intent pattern compliance, component consistency, naming conventions"

### Review Process

1. Each reviewer uses confidence scoring (only issues >=80 reported)
2. Consolidate findings by severity:
   - **Critical (>=90)**: Must fix - accessibility violations, broken layouts
   - **Important (80-89)**: Should fix - inconsistencies, minor UX issues
3. Present findings to user with options:
   - **Fix now**: Address issues before completing
   - **Fix later**: Document as known issues, proceed
   - **Proceed as-is**: Accept current state
4. Address issues based on user decision

---

## Prerequisites

Before running `/implement`, ensure specs exist in one of these locations:

### Design-Intent Specs

- `design-intent/specs/{feature}/feature-spec.md` - Feature specification
- `design-intent/specs/{feature}/implementation-plan.md` - Implementation plan (required)

Create with: `/feature` → `/plan`

### SpecKit Specs

- `plan/specs/{feature}/spec.md` or `specs/{feature}/spec.md` - Specification
- `plan/specs/{feature}/plan.md` or `specs/{feature}/plan.md` - Implementation plan (required)
- `plan/specs/{feature}/tasks.md` or `specs/{feature}/tasks.md` - Task list (optional)

Create with: `/speckit.specify` → `/speckit.plan` → `/speckit.tasks`

---

## Error Handling

### No Specs Found

```
Error: No specs found for feature "{feature}"

Searched locations:
- design-intent/specs/{feature}/ (not found)
- plan/specs/{feature}/ (not found)
- specs/{feature}/ (not found)

To create specs:
- Design-Intent: Run /feature then /plan
- SpecKit: Run /speckit.specify then /speckit.plan
```

### Incomplete Specs

```
Warning: Found spec directory at {location} but missing required files

Missing: {missing_file}

Please complete spec creation before implementation.
```

### Branch Detection Failure

```
Warning: Could not derive feature from branch "{branch}"

You are on a main/master branch or the branch name format is not recognized.

Options:
1. Provide feature name explicitly: /implement <feature-name>
2. Switch to a feature branch: git checkout feat/your-feature
```

---

## Output

Complete feature implementation including:

- **Working UI components** that match plan specifications (if applicable)
- **Backend functionality** that supports the feature requirements
- **Responsive behavior** across all breakpoints (if UI work)
- **Consistent design** that follows established patterns
- **Tested functionality** ready for user feedback
- **Integration** between frontend and backend components
- **Quality review results** (if UI work detected) with any issues addressed or documented
- **Updated tasks.md** with completed tasks marked (if SpecKit with tasks.md)

---

## When to Use

- After completing `/feature` and `/plan` workflow (Design-Intent)
- After completing `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` workflow (SpecKit)
- When implementation plan is approved and ready to execute
- When you want coordinated full-stack feature delivery
- When you need both design and engineering aspects handled together

---

## Relationship to Other Commands

### Design-Intent Workflow
- **Follows `/plan`** - Executes the implementation plan created by `/plan`
- **Uses design-intent-specialist skill** - See `skills/design-intent-specialist/SKILL.md`
- **Prepares for `/diary`** - Creates complete feature ready for session documentation

### SpecKit Workflow
- **Follows `/speckit.plan`** - Executes the plan created by SpecKit
- **Works with `/speckit.tasks`** - Can track and update task completion
- **General implementation** - Does not require design-intent-specialist

---

## Usage Examples

```bash
# Auto-detect from branch (recommended)
/implement

# Branch: feat/001-dashboard with design-intent specs
# → Detects design-intent/specs/001-dashboard/
# → Uses design-intent-specialist workflow
# → Runs UI review (UI content detected)

# Branch: feat/002-auth with SpecKit specs
# → Detects plan/specs/002-auth/
# → Loads plan.md + tasks.md
# → Implements tasks sequentially, marks complete
# → Skips review (backend-only content)

# Explicit feature name (overrides branch)
/implement user-auth
```
