# Troubleshooting

Common issues and solutions when converting Google Stitch exports to React components.

---

## Issue: Stitch Export Directory Not Found

### Symptoms

```
Error: Cannot find design-intent/google-stitch/{feature}/exports/
```

### Cause

Stitch exports haven't been generated or are in unexpected location.

### Solution

1. **Verify export location**
   ```
   design-intent/google-stitch/{feature}/exports/
   ```

2. **Check for alternative structures**
   - Some projects use `stitch-exports/` instead
   - Exports might be at project root

3. **Generate exports if missing**
   Use `/stitch-generate` to create exports from prompts.

### Workaround

Provide the explicit path to Stitch HTML files:
```
"Convert the Stitch export at /path/to/screen.html"
```

---

## Issue: No Pattern Directory Found

### Symptoms

```
Cannot find /design-intent/patterns/ directory
```

### Cause

Project hasn't been initialized with design intent structure.

### Solution

Run setup to create structure:
```
/setup
```

### Workaround

Proceed without patterns - the skill will note:
```
No existing patterns found. Will generate components without pattern constraints.
```

---

## Issue: Tailwind Config Not Extractable

### Symptoms

- Colors show as raw Tailwind classes (e.g., `bg-blue-500`)
- Custom theme values missing
- Tokens not properly mapped

### Cause

Stitch HTML uses inline Tailwind CDN without custom config, or config is malformed.

### Solution

1. **Check HTML for tailwind.config**
   ```html
   <script>
     tailwind.config = {
       theme: {
         extend: {
           // Should have custom values here
         },
       },
     };
   </script>
   ```

2. **If missing, use Tailwind defaults**
   Map standard Tailwind values to project tokens:

   | Tailwind | Fluent UI |
   |----------|-----------|
   | blue-500 | colorBrandBackground |
   | gray-900 | colorNeutralForeground1 |
   | rounded-lg | borderRadiusMedium |

3. **Check design-dna.md**
   The MCP may have extracted tokens to `design-dna.md` file.

---

## Issue: Custom Animations Not Working

### Symptoms

- Animations from Stitch don't play in React
- Keyframes not applied
- Timing feels different

### Cause

CSS keyframes need to be converted to CSS-in-JS format.

### Solution

**Stitch CSS:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
```

**Fluent UI makeStyles:**
```tsx
const useStyles = makeStyles({
  fadeIn: {
    animationName: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    animationDuration: '0.3s',
    animationTimingFunction: 'ease-out',
  },
});
```

**Alternative - Global CSS:**

Create a `stitch-animations.css` file:
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

Import in component:
```tsx
import './stitch-animations.css';

// Use in JSX
<div style={{ animation: 'fadeIn 0.3s ease-out' }}>
```

---

## Issue: Material Symbols Icons Not Mapping

### Symptoms

- Stitch uses Material Symbols: `<span class="material-symbols-outlined">home</span>`
- No equivalent Fluent UI icon found

### Cause

Material Symbols icon names don't match Fluent UI icon names.

### Solution

1. **Use icon mapping table**

   | Material Symbol | Fluent Icon |
   |-----------------|-------------|
   | home | Home24Regular |
   | settings | Settings24Regular |
   | person | Person24Regular |
   | trending_up | ArrowTrending24Regular |
   | search | Search24Regular |
   | menu | Navigation24Regular |

2. **For unmapped icons, keep Material Symbols**
   ```tsx
   // Install: npm install material-symbols
   import 'material-symbols';

   <span className="material-symbols-outlined">
     specific_icon_name
   </span>
   ```

3. **Consider custom SVG icons**
   Export from Material Symbols and create React components.

---

## Issue: Responsive Behavior Not Matching

### Symptoms

- Desktop layout works
- Mobile view broken or doesn't match PNG

### Cause

Stitch uses Tailwind responsive prefixes (`md:`, `lg:`) that need conversion.

### Solution

**Stitch Tailwind:**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

**React with CSS:**
```tsx
<div style={{
  display: 'grid',
  gridTemplateColumns: '1fr', // Mobile default
  '@media (min-width: 768px)': {
    gridTemplateColumns: 'repeat(2, 1fr)',
  },
  '@media (min-width: 1024px)': {
    gridTemplateColumns: 'repeat(3, 1fr)',
  },
}}>
```

**React with Fluent UI makeStyles:**
```tsx
const useStyles = makeStyles({
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    '@media (min-width: 768px)': {
      gridTemplateColumns: 'repeat(2, 1fr)',
    },
    '@media (min-width: 1024px)': {
      gridTemplateColumns: 'repeat(3, 1fr)',
    },
  },
});
```

---

## Issue: PNG Reference and Code Don't Match

### Symptoms

- Generated React looks different from reference PNG
- Layout or spacing seems off

### Cause

1. Stitch may have generated different variants
2. Browser rendering differences
3. Font not loaded in React

### Solution

1. **Verify HTML matches PNG**
   - Open Stitch HTML in browser
   - Compare to PNG side-by-side
   - Note any differences

2. **Check font loading**
   ```tsx
   // Ensure fonts match Stitch
   import '@fontsource/inter/400.css';
   import '@fontsource/inter/500.css';
   import '@fontsource/inter/700.css';
   ```

3. **Compare at same viewport**
   - Stitch PNG might be at specific resolution
   - Match browser window to PNG dimensions

4. **Use browser dev tools**
   - Inspect Stitch HTML element sizes
   - Match in React output

---

## Issue: Conflict Resolution Unclear

### Symptoms

- Multiple conflicts detected
- Unsure which takes precedence
- User hasn't provided guidance

### Cause

Skill requires explicit user decision for conflicts.

### Solution

1. **Present conflicts clearly**
   ```
   ## Conflicts Requiring Decision

   1. Border Radius: Stitch 4px vs Pattern 8px
   2. Primary Color: Stitch #3B82F6 vs Pattern #0078D4

   Please choose for each: [Stitch] or [Pattern] or [Hybrid]
   ```

2. **Provide recommendations**
   ```
   Recommended: Use Pattern values for consistency
   Exception: Use Stitch if this is a new design direction
   ```

3. **Wait for explicit decision**
   Do not proceed with conversion until conflicts are resolved.

---

## Issue: Component Hierarchy Too Flat

### Symptoms

- Single large component file
- Hard to maintain or reuse parts
- Doesn't follow project structure

### Cause

Skill generated monolithic component instead of decomposing.

### Solution

1. **Request decomposition**
   ```
   "Break this component into smaller, reusable parts"
   ```

2. **Follow project patterns**
   - Check existing component structure
   - Match naming conventions
   - Use same folder organization

3. **Decomposition guidelines**
   - **Atomic**: Single-purpose (Button, Icon, Input)
   - **Composite**: Combined atomics (FormField, Card, ListItem)
   - **Layout**: Structure (Header, Sidebar, PageLayout)
   - **Screen**: Full pages (Dashboard, Settings)

---

## Issue: TypeScript Types Missing or Wrong

### Symptoms

- `any` types used
- Props not properly typed
- Type errors in IDE

### Cause

Type generation skipped or incorrect inference.

### Solution

1. **Request explicit types**
   ```
   "Generate full TypeScript interfaces for all components"
   ```

2. **Check types.ts file**
   - Should exist in component directory
   - Should export all interfaces

3. **Verify prop types match usage**
   ```tsx
   // types.ts
   export interface CardProps {
     title: string;
     description?: string;
     onClick?: () => void;
   }

   // Card.tsx
   export const Card: React.FC<CardProps> = ({
     title,
     description,
     onClick,
   }) => {
     // Implementation
   };
   ```

---

## Issue: Stitch Skill Not Auto-Invoking

### Symptoms

- Mentioned Stitch exports but skill didn't activate
- Got generic response instead of conversion

### Cause

Context didn't trigger skill detection.

### Solution

Use explicit trigger phrases:

- "Convert the Stitch export to React"
- "Process design-intent/google-stitch/{feature}/"
- "Stitch to React: {feature name}"
- "Generate React components from Stitch HTML"

Or reference files directly:
```
"Convert design-intent/google-stitch/dashboard/exports/01-layout.html to React"
```

---

## Getting Help

If issues persist:

1. **Check project setup**
   - `/design-intent/` directory exists
   - Design system detected correctly
   - Patterns documented

2. **Verify Stitch exports**
   - HTML files are valid
   - PNG references exist
   - tailwind.config present

3. **Review constitution**
   - `/design-intent/memory/constitution.md`
   - Check for project-specific guidelines

4. **Create diary entry**
   - Document the issue
   - Run `/diary` to capture context
