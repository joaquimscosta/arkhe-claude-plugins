---
description: Analyze recent work and suggest design patterns that should be preserved as design intent
---

# /document-design-intent

**Purpose**: Analyze recent work and suggest design patterns that should be preserved as design intent

**Usage**: `/document-design-intent`

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
