# Detailed Workflow

Complete implementation process for the Design Intent Specialist skill.

## Phase 1: Mandatory Design Intent Check

**This step is non-negotiable before any implementation.**

### Steps

1. **Locate patterns directory**
   ```
   /design-intent/patterns/
   ```

2. **Read all pattern files**
   - Scan for `.md` files in the patterns directory
   - Extract key design decisions from each

3. **Report findings**
   ```
   Existing patterns to consider:
   - page-header-template.md: Back navigation + responsive action buttons
   - card-hover-states.md: 200ms ease transitions, subtle elevation
   - spacing-sections.md: 48px between major sections
   ```

4. **Note potential impacts**
   - Which patterns might apply to this implementation
   - Potential conflicts to watch for

### If No Patterns Exist

Report: "No existing design intent patterns found. Will establish new patterns based on this implementation."

---

## Phase 2: Visual Reference Analysis

### Reference Types

| Type | How to Process |
|------|----------------|
| Screenshot | Analyze visual elements directly |
| Figma URL | Use MCP to extract design tokens (if available) |
| Video | Extract key frames for analysis |
| Description | Parse for UI elements and patterns |

### Analysis Checklist

For each reference, extract:

- [ ] **Layout structure** - Grid, flexbox, positioning
- [ ] **Color palette** - Primary, secondary, accent, backgrounds
- [ ] **Typography** - Headings, body, captions, weights
- [ ] **Spacing** - Margins, padding, gaps
- [ ] **Component types** - Buttons, cards, inputs, etc.
- [ ] **Interactive states** - Hover, focus, active, disabled
- [ ] **Responsive hints** - Breakpoint behaviors if visible

### Conflict Detection

Compare reference elements against existing patterns:

```
Reference: 8px card padding
Existing pattern: 12px card padding (card-spacing.md)
→ FLAG for user guidance
```

---

## Phase 3: Section Decomposition

For complex/full-page designs, break into manageable sections.

### Standard Sections

1. **Header**
   - Navigation elements
   - Branding/logo
   - User controls (profile, settings)
   - Search functionality

2. **Side Navigation** (if present)
   - Menu items and hierarchy
   - Active/inactive states
   - Collapse/expand behavior
   - Icons and labels

3. **Main Content**
   - Primary content area
   - Data display (tables, cards, lists)
   - Forms and inputs
   - Empty/loading states

4. **Footer** (if present)
   - Secondary links
   - Metadata
   - Legal/copyright

### Per-Section Analysis

For each section, document:

```markdown
## Section: Header

### Layout
- Flexbox row, space-between
- Fixed height: 64px
- Full width with 24px horizontal padding

### Spacing
- Gap between nav items: 16px
- Logo margin-right: 32px

### Typography
- Logo: 20px, semibold
- Nav items: 14px, regular

### Responsiveness
- < 768px: Hamburger menu
- ≥ 768px: Horizontal nav

### Visual Treatment
- Background: neutral-white
- Border-bottom: 1px neutral-stroke
- Nav hover: primary-brand underline
```

---

## Phase 4: Implementation

### Implementation Order

1. **Structure first** - HTML/JSX skeleton
2. **Layout second** - Flexbox/Grid positioning
3. **Spacing third** - Margins, padding, gaps
4. **Typography fourth** - Font sizes, weights
5. **Colors fifth** - Background, text, borders
6. **Interactivity last** - Hover, transitions, animations

### Component Selection Priority

```
1. Existing project components (from /design-intent/patterns/)
      ↓ not available
2. Fluent UI components (query MCP if available)
      ↓ not suitable
3. Custom component (document with header comment)
```

### Custom Component Documentation

When creating custom components:

```tsx
/**
 * CUSTOM COMPONENT: CustomMetricCard
 * Base: @fluentui/react-components/Card
 * Reason: Required gradient background and custom icon positioning
 * Created: 2024-01-15
 *
 * Design Reference: dashboard-v2.png, top-left KPI section
 */

export const CustomMetricCard: React.FC<CustomMetricCardProps> = ({
  // ...
}) => {
  // Implementation
};
```

---

## Phase 5: Conflict Resolution

### Resolution Flow

```
Conflict Detected
      ↓
Implement Reference (what user requested)
      ↓
Flag Conflict Clearly
      ↓
Ask User for Guidance
      ↓
Document Decision
```

### Conflict Report Template

```markdown
## Design Conflict Detected

**Element**: Card padding
**Reference**: 8px padding
**Existing Pattern**: 12px padding (card-spacing.md)

### Options

1. **Follow reference** - Use 8px for this implementation
2. **Use existing pattern** - Adapt to 12px padding
3. **Update pattern** - Make 8px the new standard

### Recommendation

[Your recommendation based on context]

**Which approach would you prefer?**
```

### After User Decision

- If updating pattern: Modify the pattern file
- If exception: Document why in code comments
- If new standard: Create new pattern file

---

## Phase 6: Iteration Support

### Vibe Coding Flow

Support rapid refinement cycles:

1. **User feedback** - "Make the spacing tighter"
2. **Quick adjustment** - Modify specific values
3. **Show result** - Display updated implementation
4. **Repeat** - Until user satisfied

### Common Refinement Requests

| Request | Typical Action |
|---------|----------------|
| "Too much whitespace" | Reduce padding/margins by 25-50% |
| "Buttons too small" | Increase to next size tier |
| "Text hard to read" | Increase contrast or font size |
| "Feels cramped" | Add spacing, increase gaps |
| "More modern look" | Reduce borders, add subtle shadows |

### Track Changes

Keep a mental note of refinements for potential pattern documentation:

```
Original: 16px gap
Refined to: 12px gap
User comment: "Tighter feels better for data-dense views"
→ Consider documenting as pattern for data-dense layouts
```

---

## Constitution Integration

Ensure implementation follows project constitution:

- **Article I** (Simplicity) - Start simple, add complexity only if needed
- **Article II** (Framework-first) - Use Fluent UI before custom solutions
- **Article III** (Responsive) - Mobile-first, all breakpoints
- **Article IV** (Prototype) - Mock data, happy paths
- **Article V** (Feature-first) - Features define what, references define how
- **Article VI** (UI Quality) - Microinteractions, visual hierarchy
- **Article VII** (Documentation) - Document proven patterns

---

## Output Expectations

Deliver:

1. **Working implementation** - Functional React components
2. **Accurate visuals** - Matches reference closely
3. **Responsive behavior** - Works across breakpoints
4. **Pattern consistency** - Uses established patterns
5. **Conflict documentation** - Clear notes on any deviations
6. **Custom component tracking** - Documented in code headers
