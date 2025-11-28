---
description: Execute the implementation plan, coordinating both engineering and design aspects of the feature
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
Invokes Design Intent Specialist skill with:
- **Existing design intent review** - Checks established patterns for consistency
- **Sectional decomposition** - Breaks complex UI into manageable sections (header, nav, main, footer)
- **Detailed analysis** - Focuses on layout, spacing, typography, responsiveness per section
- **Conflict resolution** - Handles conflicts between plan specs and existing design intent patterns
- **Component reuse** - Leverages existing components where appropriate

### **For Backend/Logic Components**
Uses general agent for:
- **API endpoints** - Server logic, data handling, business rules
- **Database changes** - Schema updates, migrations, queries
- **Testing** - Unit tests, integration tests, component tests
- **Architecture** - Project structure, configuration, dependencies

### **Coordination Approach**
- **Sequential implementation** - Design components first (they define data needs), then backend
- **Iterative refinement** - Build, test, refine each component
- **Integration points** - Ensure frontend and backend work together seamlessly

## Design Implementation Behavior

When implementing visual components, follows the same workflow as `/design` command:

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

## When to Use

- After completing `/feature` and `/plan` workflow
- When implementation plan is approved and ready to execute
- When you want coordinated full-stack feature delivery
- When you need both design and engineering aspects handled together

## Relationship to Other Commands

- **Follows `/plan`** - Executes the implementation plan created
- **Uses `/design` workflow** - Same design implementation approach for visual components
- **Prepares for `/diary`** - Creates complete feature ready for session documentation
