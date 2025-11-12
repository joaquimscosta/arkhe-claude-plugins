# Google Stitch Prompt Examples

This file provides before/after examples demonstrating how to transform natural language
or structured specs into optimized Stitch-ready prompts.

Claude uses these examples as reference for tone, structure, and style when authoring new prompts.

---

## Example 1 — SaaS Analytics Dashboard

**Input (natural language):**
> We need a web dashboard for our SaaS platform with metrics like MRR and churn rate.
> It should feel professional but not boring, and show charts and cards for KPIs.

**Optimized Stitch Prompt:**
> Design a responsive web dashboard for a SaaS analytics app.  
> Include:  
> - Left sidebar with logo and navigation (Overview, MRR, Churn, Cohorts, Settings)  
> - Top header with search, notifications, and user avatar  
> - Main dashboard with KPI cards (MRR, Active Users, Churn Rate, ARPU)  
> - Line chart for revenue over time and a table of recent subscriptions  
> Style: clean, minimal, enterprise-grade, neutral background with deep blue accents, sans-serif typography, subtle shadows.  
> Optimize for desktop first, single-column layout on mobile.

---

## Example 2 — Mobile Banking App (screen-based)

**Input (short brief):**
> Create a mobile banking interface with account overview, transaction list, and payments.

**Optimized Stitch Prompt:**
> Design a mobile banking app with the following screens:  
> - **Accounts Overview:** balance summary, account cards, quick links for transfers  
> - **Transactions:** scrollable list with categories, amounts, and icons  
> - **Payments:** form for bill payment with amount, payee, and schedule fields  
> Style: modern, clean, deep teal accents, white background, geometric sans-serif type.  
> Use consistent 8px spacing and smooth animations between screens.

---

## Example 3 — Dashboard Spec File Conversion

**Input (`specs/marketing.md`):**
```markdown
# Marketing Analytics Dashboard
- Sidebar: Campaigns, Performance, Budgets
- Header: date range filter, search, notifications
- Main: performance chart + campaign cards
- Style: editorial, warm beige background, bold serif headings
````

**Optimized Stitch Prompt:**

> Create a marketing analytics dashboard for a web app.
> Include:
>
> * Left sidebar with navigation (Campaigns, Performance, Budgets)
> * Top header with date range filter, search, and notifications
> * Main area with line chart of campaign performance and a 3-column grid of campaign cards
>   Style: editorial, warm beige background, bold serif headings, clean spacing, subtle shadows.
>   Optimize for desktop; single-column layout for mobile export.

---

## Example 4 — Prompt Refinement (iterative edit)

**Input (user revision):**

> On the dashboard, move the KPI cards above the chart and add a dropdown to filter by region.

**Optimized Stitch Prompt:**

> On the dashboard screen, reposition KPI cards above the revenue chart.
> Add a small dropdown labeled “Region” aligned right in the chart header.
> Maintain existing typography, colors, and layout proportions.
> Avoid regenerating the sidebar or other elements.

---

## Example 5 — Prompt with Image Reference

**Input:**

> Use the uploaded wireframe as base for a habit tracker app.
> Keep bottom navigation, but make it more colorful and rounded.

**Optimized Stitch Prompt:**

> Use the uploaded wireframe as the base layout for a mobile habit-tracking app.
> Retain bottom navigation with four icons, add subtle labels underneath.
> Use rounded cards for daily habits with progress rings.
> Style: friendly, pastel purple and teal color palette, playful rounded typography, light shadows.
> Focus on a calm, approachable tone suitable for everyday use.

---

## Example 6 — Form-Based Workflow

**Input (semi-structured spec):**

```yaml
screen: Onboarding
steps:
  - Welcome
  - Personal Info Form
  - Confirmation
theme: light, minimal, blue accents
layout: centered card
```

**Optimized Stitch Prompt:**

> Design a 3-step onboarding flow for a web app.
> Include:
>
> * Step 1: Welcome screen with app logo and “Get Started” button
> * Step 2: Personal info form with name, email, and password fields
> * Step 3: Confirmation screen with success message and login link
>   Style: light, minimal, blue accents, centered card layout, rounded inputs, soft shadows.
>   Ensure consistent transitions between steps.

---

## Usage Notes

When testing this Skill, you can use these example inputs directly:

```bash
Optimize this input into a Google Stitch prompt:
"A dashboard for subscription analytics with revenue chart and customer table."
```

Claude should automatically invoke the **authoring-stitch-prompts** Skill and return a concise, directive, and visually structured Stitch-ready output.

---

## Example 7 — Multi-Prompt Split (Dashboard + Settings)

**Input (natural language):**
> Create a SaaS app with a dashboard showing metrics and a settings page for user preferences.

**Split Detection & Auto-Application:**
> This input contains 2 distinct screens:
> 1. Dashboard (metrics visualization)
> 2. Settings page (user preferences)
>
> Applying smart default: Generate as 2 separate prompts for better atomicity.

**Optimized Prompt 1 (Dashboard):**
> Design a responsive web dashboard for a SaaS analytics app.
> Include: left sidebar (logo, navigation links), top header (search, notifications, user avatar), main section with KPI cards (MRR, Active Users, Churn Rate, ARPU), line chart for revenue over time.
> Style: clean, minimal, enterprise-grade, neutral background with deep blue accents, sans-serif typography, subtle shadows.
> Optimize for desktop first, single-column layout on mobile.

**File Created:**
`.google-stitch/prompts/dashboard-v1.md`

**Note:**
```
---
Additional prompts needed:
2. Settings page: User preferences with profile, notifications, billing
   → Will save as: settings-v1.md
```

**Optimized Prompt 2 (Settings):**
> Design a settings page for user preferences in a SaaS app.
> Include: left sidebar (Profile, Notifications, Billing, Security), main area with form sections for each category, save/cancel buttons at bottom.
> Style: clean, minimal, neutral background, deep blue accents, sans-serif typography, clear section dividers.
> Optimize for desktop, stack sections on mobile.

**File Created:**
`.google-stitch/prompts/settings-v1.md`

---

## Example 8 — Single Screen, Multiple Intents

**Input:**
> Article page with reading pane, comment section, and related articles grid.

**Split Detection:**
> This input contains 3 distinct intents:
> 1. Content consumption (reading pane)
> 2. User engagement (comment section)
> 3. Content discovery (related articles grid)
>
> Recommendation: Generate as 3 separate prompts for better atomicity.
> Proceed with split? [Split / Combine]

**User Response:** Split

**Optimized Prompt 1 (Reading Pane):**
> Design a reading pane for long-form article content on web.
> Include: article title, author byline with avatar, publish date, featured image, formatted text with headings and paragraphs, inline images.
> Style: editorial, serif headings (Georgia), sans-serif body (Helvetica), generous line spacing (1.6), max-width 720px, cream background.
> Optimize for readability, responsive images.

**Optimized Prompt 2 (Comment Section):**
> Design a comment section below article content.
> Include: comment count header, comment thread with avatars and timestamps, nested replies (1 level), "Add Comment" form with textarea and submit button.
> Style: clean, minimal, neutral gray background, sans-serif typography, subtle borders between comments.
> Optimize for threaded discussions, keyboard navigation.

**Optimized Prompt 3 (Related Articles Grid):**
> Design a related articles grid at page bottom.
> Include: "Related Articles" heading, 3-column grid (stack on mobile) with thumbnail, title, excerpt (80 chars), read time badge.
> Style: clean, neutral background, subtle card shadows, sans-serif typography, Ocean Blue (#005A8D) accents.
> Optimize for mobile-first responsive layout.

**Files Created:**
- `.google-stitch/prompts/reading-pane-v1.md`
- `.google-stitch/prompts/comments-v1.md`
- `.google-stitch/prompts/related-grid-v1.md`

---

## Example 9 — Keep Together (Single Intent)

**Input:**
> Login form with email, password, submit button, "Forgot password?" link, and "Sign up" link.

**Split Detection:**
> This input contains 1 intent:
> 1. User authentication (login workflow)
>
> All components serve a single goal. Recommendation: Keep as 1 prompt.

**Optimized Prompt:**
> Design a login form for a web app.
> Include: centered card with logo, email input field, password input field, "Sign In" button, "Forgot password?" link below, "Don't have an account? Sign up" link at bottom.
> Style: clean, modern, centered layout, Ocean Blue (#005A8D) primary button, rounded inputs, subtle card shadow.
> Optimize for mobile-first, full keyboard navigation.

**File Created:**
`.google-stitch/prompts/login-form-v1.md`

---

## Example 10 — Language Localization

**Input:**
> Convert the login form prompt to Spanish

**Optimized Prompt:**
> Design a login form for a web app with Spanish text.
> Include: centered card with logo, email input field labeled "Correo electrónico", password input field labeled "Contraseña", "Iniciar sesión" button, "¿Olvidaste tu contraseña?" link below, "¿No tienes cuenta? Regístrate" link at bottom.
> Style: clean, modern, centered layout, Ocean Blue (#005A8D) primary button, rounded inputs, subtle card shadow.
> Optimize for mobile-first, full keyboard navigation.

**File Created:**
`.google-stitch/prompts/login-form-es-v1.md`

**Note:** Technical UI terms (button, input field, card) remain in English—only user-facing labels are translated.

---

## Example 11 — Image Modification

**Input (Scenario 1):**
> On the dashboard, make the hero image smaller and add a subtle gradient overlay to match the blue theme

**Optimized Prompt:**
> On the dashboard screen, resize the hero image to 60% width, add a subtle blue-to-transparent gradient overlay (Ocean Blue #005A8D at 20% opacity).
> Maintain existing layout proportions for other elements.
> Ensure image coordinates with the deep blue accent theme and modern aesthetic.

**File Updated:**
`.google-stitch/prompts/dashboard-v2.md`

---

**Input (Scenario 2):**
> Replace all profile thumbnails with rounded versions and add a blue border

**Optimized Prompt:**
> Update all user profile thumbnails to circular shape (border-radius: 50%).
> Apply consistent 2px border in Ocean Blue (#005A8D).
> Maintain existing thumbnail sizes and grid layout.

**File Updated:**
`.google-stitch/prompts/user-grid-v2.md`

**Note:** Image modifications should be specific (which images), precise (what changes), and coordinated with the overall theme.

---

## Example 12 — Minimal Input (High-Level)

**Input (very minimal):**
> A professional project management dashboard

**Optimized Prompt:**
> Design a responsive web dashboard for a professional project management tool.
> Include: left sidebar with navigation (Projects, Tasks, Team, Reports), top header with search and notifications, main area with project cards showing status and progress bars, task timeline chart below cards.
> Style: clean, professional, neutral gray background with blue accents, modern sans-serif typography, organized grid layout, subtle shadows.
> Optimize for desktop first, mobile-responsive single-column layout.

**Note:** Stitch accepts minimal inputs—adjectives like "professional" guide visual direction when specific details aren't provided. The skill infers common patterns for the app type.

**File Created:**
`.google-stitch/prompts/pm-dashboard-v1.md`

---

## Example 13 — Micro-Refinements (Small Changes)

**Input (Scenario 1):**
> Change the primary button color to green

**Optimized Prompt:**
> Update the primary "Sign In" button color to Forest Green (#228B22).
> Maintain all other colors, layout, and typography.

**File Updated:**
`.google-stitch/prompts/login-form-v2.md`

---

**Input (Scenario 2):**
> Move the search bar to the left side of the header

**Optimized Prompt:**
> Reposition the search bar to the left side of the header, before the logo.
> Keep all other header elements (notifications, user avatar) in current positions.

**File Updated:**
`.google-stitch/prompts/header-v3.md`

**Note:** Micro-refinements focus on single, specific changes while explicitly maintaining all other existing elements.

---

## Example 14 — Multi-Component Dashboard (Single File Format)

**Input:**
> Create an analytics dashboard with KPI cards at the top, a revenue chart on the left, and a subscriptions table on the right

**Detection:**
- Multiple components: KPI cards, revenue chart, subscriptions table (3 components)
- Full page keyword: "dashboard"
- Multiple regions: top section, left side, right side
- Total: 4 prompts (layout + 3 components) - within 6-prompt limit ✓
- **Generates single file with --- separators**

**File Generated:** `.google-stitch/prompts/analytics-dashboard-v1.md`

**File Content:**

```markdown
<!-- Layout: Analytics Dashboard -->
Design a web dashboard page for SaaS analytics overview.

Include:
- Top section with key performance metrics (4-column grid spanning full width, cards displaying primary KPIs)
- Main content area with revenue analytics chart (below metrics, left side 60% width, interactive time controls)
- Side panel with recent subscription activity (right of chart, 40% width, scrollable list)

Interactions:
- Metric cards filter chart and activity panel when clicked
- Chart time range selector updates entire page data
- Activity panel scrolls independently from main content

Style: clean dashboard aesthetic, ample whitespace, card-based sections, subtle depth

Optimize for desktop-first responsive layout, smooth transitions between filtered states

---

<!-- Component: KPI Metrics -->
Design metric cards displaying key SaaS performance indicators.

Include:
- Four cards showing revenue, active users, churn rate, and MRR
- Each card with large primary number, label, and delta percentage
- Sparkline chart showing 7-day trend below each metric
- Color-coded delta indicators (green for positive, red for negative)
- Clickable cards that act as filters

Style: minimal cards, light background, prominent numbers, subtle borders, blue accent for positive trends

Optimize for responsive 4-column grid on desktop, 2-column on tablet, single-column on mobile

---

<!-- Component: Revenue Chart -->
Design an interactive line chart for monthly revenue tracking.

Include:
- Line chart with monthly data points for current year
- Time range selector (7D, 30D, 90D, 1Y, All)
- Hover tooltips showing exact values and dates
- Y-axis with formatted currency labels
- Vertical grid lines for readability
- Highlighted current month with annotation

Style: clean chart design, blue line color, light gray gridlines, smooth curves, professional typography

Optimize for responsive scaling, touch-friendly hover states on mobile

---

<!-- Component: Subscription Activity -->
Design a subscription activity table showing recent changes.

Include:
- Scrollable list of recent subscriptions (upgrades, downgrades, cancellations)
- Each row with user avatar, name, action type, plan name, and timestamp
- Status badges (upgraded, downgraded, cancelled) with color coding
- Sort controls for date and action type
- Show 10 items with "Load more" button at bottom

Style: compact table design, neutral backgrounds, green/yellow/red status badges, small avatar thumbnails

Optimize for fixed height with internal scrolling, responsive single-column on mobile
```

**Presentation:**
```
📄 File: analytics-dashboard-v1.md

Contains 4 prompts (within 6-prompt limit ✓):
  • Layout: Analytics Dashboard
  • Component: KPI Metrics
  • Component: Revenue Chart
  • Component: Subscription Activity

Usage:
  1. Copy entire file → Paste into Stitch → Generates complete page
  2. OR copy specific component section for targeted refinement
```

**Key Points:**
- Single file contains all prompts separated by `---`
- HTML comment labels for easy navigation
- Layout uses generic terms (no file references)
- Each prompt independently usable when separated
- File can be copy-pasted directly into Stitch
- Total 4 prompts stays within Stitch's 6-screen limit

---

## Example 15 — Two-Region Landing Page (Single File Format)

**Input:**
> Landing page with hero section and feature highlights grid below it

**Detection:**
- Multiple components: hero section, feature grid (2 components)
- Full page keyword: "landing page"
- Multiple regions: hero, features section
- Total: 3 prompts (layout + 2 components) - within 6-prompt limit ✓
- **Generates single file with --- separators**

**File Generated:** `.google-stitch/prompts/landing-page-v1.md`

**File Content:**

```markdown
<!-- Layout: Landing Page -->
Design a responsive web landing page for SaaS product marketing.

Include:
- Hero section with headline and primary call-to-action (full width, above fold, centered content)
- Feature highlights grid below hero (3-column layout on desktop, icon-led feature descriptions)

Interactions:
- Hero CTA button scrolls smoothly to feature section when clicked
- Feature cards expand slightly on hover to reveal more detail

Style: modern design, bold typography, vibrant blue gradient hero background, white feature section

Optimize for mobile-first responsive design, single-column stacked layout on mobile, smooth scroll behavior

---

<!-- Component: Hero Section -->
Design a hero section for SaaS product landing page.

Include:
- Large headline emphasizing main value proposition
- Supporting subheadline with brief product description
- Primary CTA button ("Start Free Trial") with high contrast
- Secondary text link below CTA ("See demo video")
- Product screenshot or illustration on right side (desktop only)

Style: bold sans-serif headline, vibrant blue gradient background, white text, prominent orange CTA button, clean spacing

Optimize for centered single-column on mobile, two-column on desktop with text left and image right

---

<!-- Component: Feature Grid -->
Design a feature highlights grid showcasing product capabilities.

Include:
- Three feature cards in horizontal grid layout
- Each card with icon, feature title, short description (2-3 sentences)
- Icons in circular backgrounds with brand color
- Cards with subtle shadow and rounded corners
- Equal height cards with consistent spacing

Style: clean white cards, subtle shadows, blue circular icon backgrounds, dark text, generous padding

Optimize for 3-column grid on desktop, 2-column on tablet, single-column on mobile, equal card heights
```

**Presentation:**
```
📄 File: landing-page-v1.md

Contains 3 prompts (within 6-prompt limit ✓):
  • Layout: Landing Page
  • Component: Hero Section
  • Component: Feature Grid

Usage:
  1. Copy entire file → Paste into Stitch → Generates complete page
  2. OR copy specific component section for targeted refinement
```

**Key Points:**
- Simpler example with just 3 total prompts shows scalability
- Single file contains all prompts separated by `---`
- Layout describes high-level interactions (CTA scroll, hover effects)
- Component prompts add specific implementation details
- File can be copy-pasted directly into Stitch

---

## Example 16 — Large Multi-Component Split (>6 Prompts)

**Input:**
> Create an admin panel with navigation sidebar, dashboard overview, user management table, role permissions matrix, system settings form, audit logs viewer, and notification center

**Detection:**
- Multiple components: navigation, dashboard, users, roles, settings, audit logs, notifications (7 components)
- Full page keyword: "admin panel"
- Total: 8 prompts (layout + 7 components) - **exceeds 6-prompt limit** ⚠️
- **Generates multiple part files**

**File Generated Part 1:** `.google-stitch/prompts/admin-panel-part1-v1.md`

**File Content:**

```markdown
<!-- Layout: Admin Panel -->
Design a comprehensive web admin panel for application management.

Include:
- Left sidebar with navigation menu (fixed width 240px, icons + labels for Dashboard, Users, Roles, Settings, Logs, Notifications)
- Top header bar spanning full width (breadcrumbs, search, user profile dropdown)
- Main content area for active section (right of sidebar, responsive width, scrollable content)

Interactions:
- Sidebar navigation highlights active section
- Main content area updates when navigation items clicked
- Header breadcrumbs reflect current section hierarchy
- All data tables support sorting, filtering, and pagination

Style: clean enterprise interface, neutral gray sidebar (#F8F9FA), white main area, Ocean Blue (#005A8D) accents, modern sans-serif typography

Optimize for desktop-first layout, collapsible sidebar on tablet, hamburger menu on mobile

---

<!-- Component: Navigation Sidebar -->
Design a navigation sidebar for admin panel.

Include:
- Logo and app name at top
- Vertical menu with 6 items (Dashboard, Users, Roles, Settings, Logs, Notifications)
- Each item with icon and label
- Active state highlighting
- Collapse/expand toggle button at bottom
- Version number at footer

Style: light gray background (#F8F9FA), dark text (#212529), Ocean Blue (#005A8D) active state, icons from modern icon set, 16px spacing between items

Optimize for fixed positioning, smooth transitions on hover/active, keyboard navigation support

---

<!-- Component: Dashboard Overview -->
Design an admin dashboard overview with key metrics.

Include:
- 4 metric cards in horizontal row (Total Users, Active Sessions, System Health, Storage Used)
- Each card with large number, label, trend indicator (up/down arrow), and sparkline chart
- Activity timeline below cards showing recent admin actions
- System status panel on right (server status, database status, API status with colored indicators)

Style: white card backgrounds, subtle shadows, Ocean Blue (#005A8D) for positive trends, red for alerts, green for healthy status

Optimize for responsive 4-column grid on desktop, 2-column on tablet, single-column on mobile

---

<!-- Component: User Management Table -->
Design a user management table with actions.

Include:
- Search and filter controls above table (search by name/email, filter by role/status)
- Table columns: Avatar, Name, Email, Role, Status, Last Login, Actions
- Inline actions per row (Edit, Delete, Reset Password icons)
- Bulk actions toolbar when rows selected (Delete, Export, Change Role)
- Pagination controls at bottom (showing 25 per page, total count)
- "Add New User" button at top right

Style: clean table design, alternating row colors, hover highlight, Ocean Blue (#005A8D) action icons, status badges (green Active, gray Inactive, red Suspended)

Optimize for responsive table with horizontal scroll on mobile, sticky header row

---

<!-- Component: Role Permissions Matrix -->
Design a role permissions configuration matrix.

Include:
- Roles as rows (Admin, Manager, Editor, Viewer, Guest)
- Permission categories as columns (Users, Content, Settings, Reports, System)
- Checkbox toggles at intersections for granular permissions
- "Select All" checkboxes for rows and columns
- Save/Cancel buttons at bottom
- Permission descriptions on hover tooltips

Style: grid layout with borders, checkboxes in Ocean Blue (#005A8D), alternating row backgrounds, clear visual hierarchy

Optimize for wide desktop layout, simplified mobile view with expandable role sections

---

<!-- Component: System Settings Form -->
Design a system settings configuration form.

Include:
- Tabbed sections (General, Security, Email, Integrations, Advanced)
- Each tab with relevant form fields (text inputs, toggles, dropdowns, file uploads)
- Field validation indicators and help text
- "Save Changes" and "Reset to Defaults" buttons at bottom
- Change notification banner when unsaved changes present

Style: clean form layout, single-column with labels above fields, Ocean Blue (#005A8D) for toggle switches, subtle borders, clear section dividers

Optimize for vertical scroll, sticky save buttons, responsive single-column on mobile
```

**Presentation:**
```
📄 File: admin-panel-part1-v1.md

Contains 6 prompts (Stitch limit reached ✓):
  • Layout: Admin Panel
  • Component: Navigation Sidebar
  • Component: Dashboard Overview
  • Component: User Management Table
  • Component: Role Permissions Matrix
  • Component: System Settings Form

⚠️ This page requires 8 total prompts - additional components in part2
```

---

**File Generated Part 2:** `.google-stitch/prompts/admin-panel-part2-v1.md`

**File Content:**

```markdown
<!-- Component: Audit Logs Viewer -->
Design an audit logs viewer with filtering and search.

Include:
- Date range selector at top (preset ranges: Today, Last 7 Days, Last 30 Days, Custom)
- Filter controls (by user, action type, resource type, severity level)
- Log entries table with columns: Timestamp, User, Action, Resource, Details, IP Address
- Expandable rows showing full event details in JSON format
- Export button for filtered results (CSV, JSON formats)
- Real-time log streaming toggle

Style: monospace font for log details, color-coded severity badges (green Info, yellow Warning, red Error), compact table design, dark text on light background

Optimize for horizontal scroll on narrow screens, sticky filter controls, efficient rendering for large datasets

---

<!-- Component: Notification Center -->
Design a notification center panel for system alerts.

Include:
- Notification list with timestamps and icons (newest first)
- Notification types: System alerts, user activity, security events, scheduled tasks
- Mark as read/unread toggle per notification
- "Mark all as read" and "Clear all" buttons at top
- Filter by notification type dropdown
- Unread count badge
- Individual notification actions (View Details, Dismiss, Snooze)

Style: card-based list layout, unread notifications with blue left border, icons color-coded by type (blue info, yellow warning, red critical), relative timestamps

Optimize for scrollable panel with lazy loading, real-time updates via WebSocket, mobile-friendly tap targets
```

**Presentation:**
```
📄 File: admin-panel-part2-v1.md

Contains 2 prompts (remainder):
  • Component: Audit Logs Viewer
  • Component: Notification Center

⚠️ Warning: Use part1 first in Stitch, then part2 in separate session
Total: 8 prompts across 2 files
```

**Usage Workflow:**
```
Step 1: Copy admin-panel-part1-v1.md → Paste into Stitch
        → Generates layout + first 5 components (6 screens)

Step 2: Copy admin-panel-part2-v1.md → Paste into Stitch
        → Generates remaining 2 components

Result: Complete 8-screen admin panel (processed in 2 batches)
```

**Key Points:**
- Demonstrates automatic splitting when >6 prompts detected
- Part 1 always includes layout + first 5 components (6 total)
- Part 2 contains remaining components (max 6 per part)
- Clear warnings about sequential processing requirement
- Each file independently copy-pasteable into Stitch
- Part numbering makes processing order explicit
- Total prompt count communicated clearly to user