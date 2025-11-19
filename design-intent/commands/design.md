---
description: Create accurate frontend implementation from visual references while maintaining design consistency
---

# /design

**Purpose**: Create accurate frontend implementation from visual references while maintaining design consistency

**Usage**: `/design [reference]`

**Examples**:
- `/design [screenshot]` - Implement from screenshot
- `/design [Figma URL]` - Implement from Figma design
- `/design user profile page similar to Settings` - Implement from description

## What This Command Does

1. **Invokes Design Intent Specialist Skill** - Activates the specialized skill for visual accuracy
2. **Analyzes Reference** - Processes the provided visual reference (image, Figma, video, or description)
3. **Reviews Existing Design Intent** - Reads current design patterns for consistency
4. **Breaks Down Complex Designs** - For full-page designs, decomposes into sections (header, navigation, main content, footer)
5. **Implements Section by Section** - Focuses on each section individually for better accuracy
6. **Creates Implementation** - Builds accurate frontend code that matches the reference
7. **Maintains Consistency** - Applies established design patterns and component reuse

## When to Use

- You have visual references that need accurate implementation
- You want to implement designs that match existing patterns
- You need the specialist's visual parsing capabilities
- You're creating new features that should align with established design intent

## What the Specialist Will Do

- Parse and understand your visual reference
- Review existing design intent documentation
- **For complex designs**: Break down into logical sections (header, navigation, main content, footer)
- **For each section**: Analyze layout, spacing, typography, responsiveness, and visual treatment
- Create implementation using established components where possible
- Focus on precise details: exact spacing, font weights, responsive behavior per section
- Maintain visual consistency with existing patterns
- Return implementation ready for review/iteration

## Reference Types Supported

- **Screenshots**: UI mockups, design comps, reference apps
- **Figma Links**: Direct Figma design URLs
- **Videos**: Screen recordings or design walkthroughs
- **Descriptions**: Text descriptions with optional reference to existing patterns

## Implementation Approach

### For Complex/Full-Page Designs
The specialist will automatically break down the design into sections and implement each with focus on:
- **Layout**: Component structure, grid systems, positioning
- **Spacing**: Margins, padding, gaps between elements
- **Typography**: Font weights, sizes, line heights, text treatments
- **Responsiveness**: How each section adapts across breakpoints
- **Visual treatment**: Colors, shadows, borders, hover states

### Section-by-Section Implementation
1. **Header**: Navigation, branding, user controls
2. **Left/Side Navigation**: Menu items, hierarchies, states
3. **Main Content**: Primary content area, data display, forms
4. **Footer**: Secondary links, metadata, additional actions

## Output

The specialist will create working frontend implementation that:
- Matches the visual reference accurately with precise attention to details
- Implements responsive behavior for each section
- Uses existing components and patterns where appropriate
- Maintains consistency with established design intent
- Is ready for further iteration and refinement
