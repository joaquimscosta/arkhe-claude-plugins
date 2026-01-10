---
description: Execute the implementation plan, coordinating both engineering and design aspects of the feature
argument-hint: [feature-name] (defaults to current branch)
---

# /implement

**Purpose**: Execute the implementation plan, coordinating both engineering and design aspects of the feature

**Usage**: `/implement`

## What This Command Does

1. **Reads Implementation Plan** - Loads the current feature's implementation plan from `/design-intent/specs/[feature]/implementation-plan.md`
2. **Analyzes Scope** - Identifies visual/UI components vs. backend/logic components
3. **Coordinates Implementation** - Uses appropriate approaches for different aspects:
   - **Design Intent Specialist skill** for visual/UI components
   - **General implementation** for backend, logic, testing, architecture
4. **Maintains Consistency** - Ensures design implementation follows established patterns
5. **Delivers Complete Feature** - Handles full-stack implementation in coordinated workflow

## Implementation Strategy

### **For Visual/UI Components**

For UI implementation, follow the design-intent-specialist workflow:

- **Existing design intent review** - Check established patterns for consistency
- **Sectional decomposition** - Break complex UI into manageable sections (header, nav, main, footer)
- **Detailed analysis** - Focus on layout, spacing, typography, responsiveness per section
- **Conflict resolution** - Handle conflicts between plan specs and existing design intent patterns
- **Component reuse** - Leverage existing components where appropriate

See `skills/design-intent-specialist/SKILL.md` for detailed implementation guidance.

### **For Backend/Logic Components**

For backend implementation:

- **API endpoints** - Server logic, data handling, business rules
- **Database changes** - Schema updates, migrations, queries
- **Testing** - Unit tests, integration tests, component tests
- **Architecture** - Project structure, configuration, dependencies

### **Coordination Approach**

- **Sequential implementation** - Design components first (they define data needs), then backend
- **Iterative refinement** - Build, test, refine each component
- **Integration points** - Ensure frontend and backend work together seamlessly

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

## Prerequisites

Before running `/implement`:

- Feature spec exists at `/design-intent/specs/[feature]/feature-spec.md`
- Implementation plan exists at `/design-intent/specs/[feature]/implementation-plan.md`
- Implementation plan has been reviewed and approved

## Output

Complete feature implementation including:

- **Working UI components** that match plan specifications
- **Backend functionality** that supports the feature requirements
- **Responsive behavior** across all breakpoints
- **Consistent design** that follows established patterns
- **Tested functionality** ready for user feedback
- **Integration** between frontend and backend components
- **Quality review results** with any issues addressed or documented

## Quality Review

After implementation completes, launch 3 design-reviewer agents in parallel:

### Review Focuses

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

## When to Use

- After completing `/feature` and `/plan` workflow
- When implementation plan is approved and ready to execute
- When you want coordinated full-stack feature delivery
- When you need both design and engineering aspects handled together

## Relationship to Other Commands

- **Follows `/plan`** - Executes the implementation plan created
- **Uses design-intent-specialist workflow** - See `skills/design-intent-specialist/SKILL.md`
- **Prepares for `/diary`** - Creates complete feature ready for session documentation
