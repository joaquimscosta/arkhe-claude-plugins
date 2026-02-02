# Detailed Workflow

Complete conversion process for transforming Google Stitch exports into React components.

## Table of Contents

- [Phase 1: Load Project Context](#phase-1-load-project-context)
- [Phase 2: Scan Stitch Exports](#phase-2-scan-stitch-exports)
- [Phase 3: Map to Project Design System](#phase-3-map-to-project-design-system)
- [Phase 4: Conflict Detection](#phase-4-conflict-detection)
- [Phase 5: Component Generation](#phase-5-component-generation)
- [Stitch Code Format Reference](#stitch-code-format-reference)
- [Output Structure](#output-structure)

---

## Phase 1: Load Project Context

**This step is mandatory before any conversion.**

### Steps

1. **Read constitution**
   ```
   /design-intent/memory/constitution.md
   ```
   Extract: simplicity principles, framework-first mandate, responsive requirements

2. **Scan patterns directory**
   ```
   /design-intent/patterns/
   ```
   List all `.md` files and extract key decisions

3. **Detect design system**
   - Check `package.json` for UI libraries
   - Common systems: Fluent UI, Material UI, Chakra, Tailwind
   - Note: Stitch outputs Tailwind - may need conversion

4. **Report findings**
   ```
   Project Context:
   - Design System: Fluent UI v9
   - Existing patterns: 5 found
     - button-styling.md: 8px radius, primary/secondary variants
     - card-layout.md: 16px padding, subtle shadow
     - spacing-scale.md: 8px base unit
     - typography-scale.md: Inter font, 14px base
     - animation-timing.md: 200ms ease-out transitions
   - Constitution: Framework-first, mobile-first responsive
   ```

---

## Phase 2: Scan Stitch Exports

### Export Structure

Stitch generates paired HTML + PNG files:

```
design-intent/google-stitch/{feature}/
├── exports/                    # Core output
│   ├── 01-layout-{name}.html
│   ├── 01-layout-{name}.png
│   ├── 02-component-{name}.html
│   ├── 02-component-{name}.png
│   └── ...
├── prompt-v{N}.md              # Source prompts (context)
├── wireframes/                 # Input mockups (optional)
└── design-dna.md               # Design context (optional, from MCP)
```

### Extraction Checklist

For each HTML file:

- [ ] **Tailwind config** - Custom theme extensions
- [ ] **Color palette** - Extract from config `colors` section
- [ ] **Typography** - Font families, sizes from config
- [ ] **Spacing** - Custom spacing values
- [ ] **Custom CSS** - Animations, keyframes from `<style>` tags
- [ ] **DOM structure** - Component hierarchy
- [ ] **Icons** - Material Symbols usage
- [ ] **Interactive states** - Hover, focus, active classes

### Processing Order

1. Start with layout files (`01-layout-*`)
2. Process component files in numbered order
3. Cross-reference PNG files for visual verification

---

## Phase 3: Map to Project Design System

### Component Decomposition

Break Stitch screens into smaller, reusable parts:

```
Stitch Screen: Dashboard Layout
├── Header (reuse existing if available)
├── Sidebar Navigation (reuse or create)
├── Content Area
│   ├── Page Title (atomic)
│   ├── Filter Bar (composite)
│   └── Data Grid (reuse existing)
└── Footer (optional)
```

### Token Mapping

Convert Stitch Tailwind tokens to project tokens:

| Stitch (Tailwind) | Fluent UI | CSS Variables |
|-------------------|-----------|---------------|
| `bg-blue-500` | `colorBrandBackground` | `--color-primary` |
| `text-gray-900` | `colorNeutralForeground1` | `--text-primary` |
| `rounded-lg` | `borderRadiusMedium` | `--radius-md` |
| `p-4` | `spacingHorizontalM` | `--space-4` |
| `shadow-md` | `shadow8` | `--shadow-md` |

### Component Mapping

Check each Stitch element against existing patterns:

```
Stitch Element: Card with gradient header
├── Check: card-layout.md pattern exists?
│   └── Yes: Reuse, extend for gradient
├── Check: Fluent UI Card component?
│   └── Yes: Use as base
└── Result: Extend Fluent Card with custom header
```

### Gap Analysis

Identify elements needing custom components:

```
Custom Components Needed:
1. GradientHeader - No pattern match, requires custom CSS
2. AnimatedCounter - Uses Stitch keyframe animation
3. MultiStateButton - 6 visual states beyond standard
```

---

## Phase 4: Conflict Detection

### Detection Points

Compare at each layer:

1. **Spacing** - Stitch padding/margins vs pattern spacing
2. **Colors** - Stitch palette vs design tokens
3. **Typography** - Font sizes/weights vs type scale
4. **Borders** - Radius values vs pattern standards
5. **Animations** - Timing/easing vs motion guidelines

### Conflict Report Format

```markdown
## Design Conflicts Detected

### 1. Border Radius
**Stitch**: 4px (`rounded`)
**Pattern**: 8px (button-styling.md)
**Elements affected**: All buttons, cards

### 2. Primary Color
**Stitch**: #3B82F6 (blue-500)
**Pattern**: #0078D4 (Fluent brand)
**Elements affected**: CTAs, links, focus states

### Options for Each
1. Follow Stitch - Use exported values
2. Use pattern - Adapt to existing standard
3. Hybrid - Use Stitch for new components, pattern for existing

**Please select approach for each conflict.**
```

### Resolution Recording

After user decision:

```tsx
// CONFLICT RESOLUTION: Border radius
// Decision: Use pattern (8px)
// Reason: Maintain consistency with existing components
// Date: YYYY-MM-DD
```

---

## Phase 5: Component Generation

### File Structure

```
src/components/{feature}/
├── index.ts                    # Re-exports
├── types.ts                    # Shared interfaces
├── tokens.ts                   # Extracted design tokens
├── {MainComponent}.tsx         # Screen-level component
├── {SubComponent1}.tsx         # Decomposed parts
├── {SubComponent2}.tsx
└── {SubComponent}.styles.ts    # If using CSS-in-JS
```

### Component Template

```tsx
/**
 * CUSTOM COMPONENT: ComponentName
 * Source: {stitch-screen-name}.html
 * Base: @fluentui/react-components/Card (if applicable)
 * Reason: Required gradient background not available in base
 * Created: YYYY-MM-DD
 *
 * Original Reference: design-intent/google-stitch/{feature}/exports/{screen}.png
 */

import React from 'react';
import { tokens } from './tokens';
import type { ComponentNameProps } from './types';

export const ComponentName: React.FC<ComponentNameProps> = ({
  // props
}) => {
  return (
    // JSX
  );
};
```

### Tokens File Template

```ts
/**
 * Design tokens extracted from Stitch export
 * Source: design-intent/google-stitch/{feature}/exports/
 *
 * These tokens bridge Stitch output to project design system.
 * Map to existing design tokens where possible.
 */

// Colors from Stitch tailwind.config
export const stitchColors = {
  primary: '#3B82F6',      // blue-500 -> maps to colorBrandBackground
  secondary: '#6B7280',    // gray-500 -> maps to colorNeutralForeground2
  background: '#F9FAFB',   // gray-50 -> maps to colorNeutralBackground2
} as const;

// Spacing (convert from Tailwind to px)
export const stitchSpacing = {
  xs: '4px',   // p-1
  sm: '8px',   // p-2
  md: '16px',  // p-4
  lg: '24px',  // p-6
  xl: '32px',  // p-8
} as const;

// Typography
export const stitchTypography = {
  fontFamily: 'Inter, system-ui, sans-serif',
  sizes: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
  },
} as const;
```

### Types File Template

```ts
/**
 * TypeScript interfaces for {Feature} components
 * Generated from Stitch export analysis
 */

export interface ComponentNameProps {
  /** Primary content */
  title: string;
  /** Optional description */
  description?: string;
  /** Click handler */
  onClick?: () => void;
}

export interface SubComponentProps {
  // ...
}
```

---

## Stitch Code Format Reference

### Typical Stitch HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Screen Name</title>
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            primary: '#3B82F6',
            // Custom colors
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
          },
        },
      },
    };
  </script>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
  <style>
    /* Custom animations */
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .animate-fadeIn {
      animation: fadeIn 0.3s ease-out;
    }
  </style>
</head>
<body class="bg-gray-50">
  <!-- Component markup -->
</body>
</html>
```

### Key Elements to Extract

1. **`tailwind.config`** - Theme customizations
2. **`<style>` blocks** - Custom CSS, animations
3. **`<body>` content** - Component markup
4. **Material Symbols** - Icon usage patterns

---

## Output Structure

### Final Deliverables

1. **React components** - TypeScript, properly typed
2. **Design tokens** - Bridging Stitch to project
3. **Type definitions** - Full TypeScript coverage
4. **Conflict log** - Documented resolutions
5. **Pattern suggestions** - New patterns to document

### Quality Checklist

- [ ] All components use project design system where possible
- [ ] Custom components have documentation headers
- [ ] Tokens map to existing design tokens
- [ ] Responsive behavior implemented (mobile-first)
- [ ] Conflicts documented and resolved
- [ ] Visual fidelity verified against PNG references
