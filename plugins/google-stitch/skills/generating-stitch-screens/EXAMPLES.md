# Generating Stitch Screens — Examples

## Example 1: Basic Single-Prompt Generation

**Input:** User has a single-component prompt file.

**Prompt File:** `design-intent/google-stitch/login/prompt-v1.md`
```markdown
<!-- Component: Login Form -->
Design a login form for a web app.
Include: centered card with logo, email input field, password input field, "Sign In" button, "Forgot password?" link below, "Don't have an account? Sign up" link at bottom.
Style: clean, modern, centered layout, Ocean Blue (#005A8D) primary button, rounded inputs, subtle card shadow.
Optimize for mobile-first, full keyboard navigation.
```

**Generation Flow:**
1. Parse: 1 section found — Component: Login Form
2. Create project: "Login Design"
3. Generate: `generate_screen_from_text` with login form prompt
4. Fetch: `fetch_screen_image` -> `exports/login-form.png`

**Output:**
```
Stitch Generation Complete

Project: Login Design
Feature: login/

Screens (1/1):
  1. Component: Login Form -> exports/login-form.png

Directory:
  design-intent/google-stitch/login/
  ├── prompt-v1.md
  └── exports/
      └── login-form.png
```

---

## Example 2: Multi-Prompt File (Layout + Components)

**Input:** Dashboard prompt file with layout and 3 components.

**Prompt File:** `design-intent/google-stitch/dashboard/prompt-v1.md`
```markdown
<!-- Layout: Analytics Dashboard -->
Design a web dashboard page for SaaS analytics overview.
[...layout prompt...]

---

<!-- Component: KPI Metrics -->
Design metric cards displaying key performance indicators.
[...component prompt...]

---

<!-- Component: Revenue Chart -->
Design an interactive line chart for monthly revenue tracking.
[...component prompt...]

---

<!-- Component: Subscription Activity -->
Design a subscription activity table showing recent changes.
[...component prompt...]
```

**Generation Flow:**
1. Parse: 4 sections found (1 layout + 3 components)
2. Create project: "Dashboard Design"
3. Generate screens sequentially:
   ```
   [1/4] Generating: Layout: Analytics Dashboard...
   [2/4] Generating: Component: KPI Metrics...
   [3/4] Generating: Component: Revenue Chart...
   [4/4] Generating: Component: Subscription Activity...
   ```
4. Fetch images for all 4 screens

**Output:**
```
Stitch Generation Complete

Project: Dashboard Design
Feature: dashboard/

Screens (4/4):
  1. Layout: Analytics Dashboard        -> exports/analytics-dashboard.png
  2. Component: KPI Metrics             -> exports/kpi-metrics.png
  3. Component: Revenue Chart           -> exports/revenue-chart.png
  4. Component: Subscription Activity   -> exports/subscription-activity.png

Directory:
  design-intent/google-stitch/dashboard/
  ├── prompt-v1.md
  └── exports/
      ├── analytics-dashboard.png
      ├── kpi-metrics.png
      ├── revenue-chart.png
      └── subscription-activity.png
```

---

## Example 3: Split File Generation (Part Files)

**Input:** Admin panel with 8 prompts split across 2 files.

**Files:**
- `admin-panel/prompt-v1-part1.md` (6 prompts)
- `admin-panel/prompt-v1-part2.md` (2 prompts)

**Generation Flow:**
1. Detect part files in feature directory
2. Process part1 first (6 screens), then part2 (2 screens)
3. All exports saved to same `exports/` directory

**Output:**
```
Stitch Generation Complete

Project: Admin Panel Design
Feature: admin-panel/

Screens (8/8) from 2 part files:

Part 1 (prompt-v1-part1.md):
  1. Layout: Admin Panel                -> exports/admin-panel.png
  2. Component: Navigation Sidebar      -> exports/navigation-sidebar.png
  3. Component: Dashboard Overview      -> exports/dashboard-overview.png
  4. Component: User Management Table   -> exports/user-management-table.png
  5. Component: Role Permissions Matrix -> exports/role-permissions-matrix.png
  6. Component: System Settings Form    -> exports/system-settings-form.png

Part 2 (prompt-v1-part2.md):
  7. Component: Audit Logs Viewer       -> exports/audit-logs-viewer.png
  8. Component: Notification Center     -> exports/notification-center.png

Directory:
  design-intent/google-stitch/admin-panel/
  ├── prompt-v1-part1.md
  ├── prompt-v1-part2.md
  └── exports/
      ├── admin-panel.png
      ├── navigation-sidebar.png
      ├── dashboard-overview.png
      ├── user-management-table.png
      ├── role-permissions-matrix.png
      ├── system-settings-form.png
      ├── audit-logs-viewer.png
      └── notification-center.png
```

---

## Example 4: Generation from Raw Text (/stitch-generate)

**User runs:**
```
/stitch-generate "landing page for SaaS product"
```

**Flow:**
1. Detect raw text input (not a file path)
2. Invoke `authoring-stitch-prompts` skill to author prompt file
3. Skill creates: `design-intent/google-stitch/landing/prompt-v1.md`
4. Parse authored prompt (3 sections: layout + hero + feature grid)
5. Generate screens via MCP
6. Fetch images

**Output:**
```
Stitch Generation Complete

Authored: design-intent/google-stitch/landing/prompt-v1.md
Project: Landing Design
Feature: landing/

Screens (3/3):
  1. Layout: Landing Page    -> exports/landing-page.png
  2. Component: Hero Section -> exports/hero-section.png
  3. Component: Feature Grid -> exports/feature-grid.png

Directory:
  design-intent/google-stitch/landing/
  ├── prompt-v1.md
  └── exports/
      ├── landing-page.png
      ├── hero-section.png
      └── feature-grid.png
```

---

## Example 5: Generation with Code Fetching

**User runs:**
```
/stitch-generate @design-intent/google-stitch/dashboard/prompt-v1.md
```
**User requests:** "Also fetch the generated code"

**Additional Step:** After image fetching, code is also fetched for each screen.

**Output:**
```
Stitch Generation Complete

Project: Dashboard Design
Feature: dashboard/

Screens (4/4):
  1. Layout: Analytics Dashboard        -> exports/analytics-dashboard.png
  2. Component: KPI Metrics             -> exports/kpi-metrics.png
  3. Component: Revenue Chart           -> exports/revenue-chart.png
  4. Component: Subscription Activity   -> exports/subscription-activity.png

Code fetched for all screens.

Directory:
  design-intent/google-stitch/dashboard/
  ├── prompt-v1.md
  ├── exports/
  │   ├── analytics-dashboard.png
  │   ├── kpi-metrics.png
  │   ├── revenue-chart.png
  │   └── subscription-activity.png
  └── code/
      ├── analytics-dashboard/
      ├── kpi-metrics/
      ├── revenue-chart/
      └── subscription-activity/
```

---

## Example 6: Partial Failure with Retry Guidance

**Input:** 4-screen dashboard prompt file.

**Generation Flow:**
1. Screens 1-2 generate successfully
2. Screen 3 fails (timeout)
3. Screen 4 generates successfully
4. Retry screen 3 — still fails

**Output:**
```
Stitch Generation: 3/4 screens

Succeeded:
  1. Layout: Analytics Dashboard        -> exports/analytics-dashboard.png
  2. Component: KPI Metrics             -> exports/kpi-metrics.png
  4. Component: Subscription Activity   -> exports/subscription-activity.png

Failed:
  3. Component: Revenue Chart           -> Error: Generation timeout after retry

To retry failed screens, run:
  /stitch-generate @design-intent/google-stitch/dashboard/prompt-v1.md

Or generate the specific component manually in Stitch using the prompt from the file.
```
