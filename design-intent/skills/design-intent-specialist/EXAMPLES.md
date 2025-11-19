# Examples

Real-world examples of the Design Intent Specialist skill in action.

---

## Example 1: Screenshot to Implementation

### User Input

```
/design [attaches screenshot of a dashboard card]
```

### Skill Response

**Pattern Check:**
```
Existing patterns to consider:
- card-hover-states.md: 200ms ease transitions, subtle elevation on hover
- spacing-sections.md: 48px between major sections
No existing card component pattern found.
```

**Reference Analysis:**
```
Analyzing screenshot...

Extracted elements:
- Card with rounded corners (8px radius)
- White background with subtle shadow
- 16px internal padding
- Title: 16px semibold
- Value: 32px bold
- Subtitle: 12px regular, muted color
- Trend indicator with arrow icon
```

**Implementation:**

```tsx
import { Card, Text, tokens } from '@fluentui/react-components';
import { ArrowUp16Regular } from '@fluentui/react-icons';

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  trend,
  trendLabel,
}) => {
  return (
    <Card
      style={{
        padding: tokens.spacingHorizontalL,
        borderRadius: tokens.borderRadiusMedium,
        boxShadow: tokens.shadow4,
        transition: 'box-shadow 200ms ease', // From card-hover-states pattern
      }}
    >
      <Text size={400} weight="semibold">{title}</Text>
      <Text size={800} weight="bold">{value}</Text>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <ArrowUp16Regular style={{ color: tokens.colorPaletteGreenForeground1 }} />
        <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
          {trend} {trendLabel}
        </Text>
      </div>
    </Card>
  );
};
```

**Notes:**
- Applied existing `card-hover-states` pattern for transition
- Used Fluent UI tokens for consistency
- No conflicts detected

---

## Example 2: Figma URL with Conflict

### User Input

```
/design https://figma.com/file/abc123/Dashboard?node-id=42
```

### Skill Response

**Pattern Check:**
```
Existing patterns to consider:
- page-header-template.md: Back button left, title center, actions right
- button-sizing.md: Primary actions use "large" size
```

**Reference Analysis (via MCP):**
```
Fetching Figma design...

Page header extracted:
- Title: Left-aligned, 24px bold
- Actions: Right-aligned, medium-sized buttons
- No back button present
```

**Conflict Detected:**

```markdown
## Design Conflict Detected

**Element**: Page header layout
**Reference**: Title left-aligned, no back button
**Existing Pattern**: Back button left, title center (page-header-template.md)

### Options

1. **Follow reference** - Left-aligned title, no back button
2. **Use existing pattern** - Add back button, center title
3. **Hybrid** - Keep left-aligned title, add back button

### Recommendation

Since this appears to be a top-level page (no parent to navigate back to),
following the reference makes sense. However, if this is a detail page,
the back button pattern should apply.

**Is this a top-level or detail page?**
```

### User Response

"It's a top-level dashboard page, so no back button needed."

### Continued Implementation

```tsx
export const DashboardHeader: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px 24px',
    }}>
      <Text size={700} weight="bold">Analytics Dashboard</Text>
      <div style={{ display: 'flex', gap: '8px' }}>
        <Button appearance="secondary" size="medium">Export</Button>
        <Button appearance="primary" size="medium">Add Widget</Button>
      </div>
    </div>
  );
};
```

**Note:** Deviated from `page-header-template` pattern as this is a top-level page. Consider documenting "top-level-header" as a separate pattern.

---

## Example 3: Description-Based Implementation

### User Input

```
/design Create a settings page similar to the profile page layout,
with a sidebar for navigation and main content area for forms.
```

### Skill Response

**Pattern Check:**
```
Existing patterns to consider:
- sidebar-layout.md: 240px fixed sidebar, responsive collapse at 768px
- form-spacing.md: 24px between form sections, 16px between fields
- page-header-template.md: Back button for detail pages
```

**Implementation Plan:**
```
Based on existing patterns:
1. Use sidebar-layout pattern (240px sidebar)
2. Apply form-spacing pattern (24px sections, 16px fields)
3. Include page-header with back button (detail page pattern)
```

**Implementation:**

```tsx
export const SettingsPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar - from sidebar-layout pattern */}
      <aside style={{
        width: '240px',
        borderRight: `1px solid ${tokens.colorNeutralStroke1}`,
        padding: tokens.spacingVerticalL,
      }}>
        <nav>
          <NavItem icon={<Person24Regular />} active>Profile</NavItem>
          <NavItem icon={<Shield24Regular />}>Security</NavItem>
          <NavItem icon={<Alert24Regular />}>Notifications</NavItem>
          <NavItem icon={<Apps24Regular />}>Integrations</NavItem>
        </nav>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: tokens.spacingHorizontalXXL }}>
        {/* Header - from page-header-template pattern */}
        <PageHeader
          backHref="/profile"
          title="Settings"
        />

        {/* Form sections - from form-spacing pattern */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <FormSection title="Personal Information">
            <Field label="Display Name">
              <Input />
            </Field>
            <Field label="Email">
              <Input type="email" />
            </Field>
          </FormSection>

          <FormSection title="Preferences">
            <Field label="Language">
              <Dropdown />
            </Field>
            <Field label="Timezone">
              <Dropdown />
            </Field>
          </FormSection>
        </div>
      </main>
    </div>
  );
};
```

**Patterns Applied:**
- ✅ sidebar-layout.md - 240px sidebar width
- ✅ form-spacing.md - 24px between sections
- ✅ page-header-template.md - Back button included

---

## Example 4: Iteration/Vibe Coding

### Initial Implementation

User provides screenshot, skill implements dashboard grid.

### User Feedback Round 1

"The cards feel too spread out, can we tighten the spacing?"

### Skill Response

```tsx
// Before
<div style={{ display: 'grid', gap: '24px' }}>

// After
<div style={{ display: 'grid', gap: '16px' }}>
```

Updated. The cards now have 16px gap instead of 24px.

### User Feedback Round 2

"Better! But the text in the cards is a bit small for a dashboard."

### Skill Response

```tsx
// Before
<Text size={400}>{value}</Text>

// After
<Text size={600}>{value}</Text>
```

Increased metric values from size 400 to 600.

### User Feedback Round 3

"Perfect! Let's keep this."

### Skill Response

Implementation complete.

**Patterns to consider documenting:**
- Dashboard grid: 16px gap (tighter than standard 24px)
- Dashboard metrics: size 600 for values

Would you like me to run `/document-design-intent` to capture these patterns?

---

## Example 5: Complex Full-Page Design

### User Input

```
/design [attaches full dashboard mockup with header, sidebar, and data grid]
```

### Skill Response

**Breaking down into sections:**

```
I'll implement this full-page design section by section:

1. Header (navigation, user menu)
2. Sidebar (navigation menu)
3. Main content (data grid with filters)

Let me start with the header...
```

**Section 1: Header**
[Implements header component]

**Section 2: Sidebar**
[Implements sidebar with navigation]

**Section 3: Main Content**
[Implements data grid with filters]

**Final Assembly:**

```tsx
export const DashboardPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <DashboardHeader />
      <div style={{ display: 'flex', flex: 1 }}>
        <DashboardSidebar />
        <DashboardContent />
      </div>
    </div>
  );
};
```

**Summary:**
- 3 custom components created
- Applied 2 existing patterns
- 1 conflict resolved (user chose reference over pattern)
- Responsive behavior: sidebar collapses at 768px
