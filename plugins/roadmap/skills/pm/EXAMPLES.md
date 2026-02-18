# PM Skill — Examples

Usage examples across different project types.

## Example 1: User Stories for a Web App

**Input:** `/roadmap:pm stories authentication`

**Output:**

```
### US-1: Sign Up with Email

**As a** new user,
**I want to** create an account with my email and password,
**So that** I can access protected features.

#### Acceptance Criteria

- **Given** I am on the sign-up page
  **When** I enter a valid email and password
  **Then** my account is created and I am logged in

- **Given** I enter an email that is already registered
  **When** I submit the form
  **Then** I see an error message saying the email is taken

### US-2: Log In

**As a** returning user,
**I want to** log in with my email and password,
**So that** I can resume where I left off.

#### Acceptance Criteria

- **Given** I have an existing account
  **When** I enter correct credentials
  **Then** I am logged in and redirected to the dashboard

- **Given** I enter incorrect credentials
  **When** I submit the form
  **Then** I see an error message and can retry
```

## Example 2: Prioritization Matrix

**Input:** `/roadmap:pm prioritize`

**Output:**

```
## Feature Prioritization

| Rank | Feature | MoSCoW | User Value | Effort | Dependencies | Status |
|------|---------|--------|-----------|--------|--------------|--------|
| 1 | Email Auth | Must | High | M | None | Ready |
| 2 | User Profile | Must | High | S | Auth | Ready |
| 3 | Dashboard | Must | High | L | Auth, Profile | Ready |
| 4 | Search | Should | Medium | M | Catalog | Ready |
| 5 | Notifications | Should | Medium | M | Auth | Blocked |
| 6 | Dark Mode | Could | Low | S | Design Tokens | Ready |
```

## Example 3: Scope Assessment

**Input:** `/roadmap:pm scope real-time-notifications`

**Output:**

```
## Scope Assessment: Real-Time Notifications

### User Value
Users want timely feedback when actions complete or when they
receive messages. Currently they must refresh manually.

### Project Fit
Aligns with Phase 2 engagement goals. Not MVP-critical but
improves retention.

### Dependencies
- Auth system (must know who to notify)
- WebSocket or SSE infrastructure
- Notification preferences storage

### Effort Estimate
**Large (3+ days)** — Requires new infrastructure (WebSocket server),
database table for preferences, and frontend notification center.

### Risks
- WebSocket connections may not scale well on current hosting
- Push notifications require service worker setup
- Notification fatigue if not well-designed

### Open Questions
- Email notifications too, or just in-app?
- What events should trigger notifications?
- Should users control notification frequency?

### Recommendation
**Defer to Phase 2** — Not MVP-critical. Design the notification
events now (as domain events) so the system is ready when we build this.
```

## Example 4: Compare Two Approaches

**Input:** `/roadmap:pm compare SSR vs CSR`

**Output:**

```
## Comparison: SSR vs CSR

| Dimension | SSR (Server-Side Rendering) | CSR (Client-Side Rendering) |
|-----------|---------------------------|---------------------------|
| User value | Faster first paint, better SEO | Richer interactions |
| Effort | Medium — framework handles most | Small — simpler setup |
| Dependencies | Server runtime required | Static hosting sufficient |
| Risk | Server costs, caching complexity | SEO limitations, slow first paint |
| Long-term fit | Better for content-heavy pages | Better for app-like interactions |

### Recommendation

**SSR** — The project has public-facing content that benefits from SEO
and fast first paint. Use CSR for interactive dashboard sections only.
This hybrid approach (Next.js App Router) gives both benefits.
```

## Example 5: Next Recommendation

**Input:** `/roadmap:pm next`

**Output:**

```
## What to Build Next

### 1. Error Boundaries and Loading States
**Why now:** API endpoints exist but the frontend has no error handling.
Users see blank screens on failures.
**Effort:** Small (< 1 day)
**Dependencies:** None

### 2. User Profile Page
**Why now:** Auth is complete but users can't view or edit their profile.
This is the most requested feature in the gap analysis.
**Effort:** Medium (1-3 days)
**Dependencies:** Auth (complete)

### 3. Search
**Why now:** Catalog has 50+ items but no way to find them quickly.
Search is the highest-value feature remaining.
**Effort:** Medium (1-3 days)
**Dependencies:** Catalog API (complete)
```

## Example 6: Needs Analysis

**Input:** `/roadmap:pm needs`

**Output:**

```
## User Needs Analysis

### User Profiles
| Persona | Description | Key Needs |
|---------|-------------|-----------|
| New User | First-time visitor | Simple onboarding, clear value prop |
| Power User | Daily active user | Speed, keyboard shortcuts, bulk actions |
| Admin | Team manager | User management, analytics, audit trail |

### Pain Points
| Pain Point | Severity | Current Solution | Proposed Solution |
|-----------|----------|-----------------|-----------------|
| No search | High | Manual scrolling | Full-text search |
| Slow load | Medium | Users wait | SSR + caching |
| No mobile | High | Pinch-zoom desktop | Responsive redesign |

### Unmet Needs
- Offline access for mobile users
- Bulk export of data
- Keyboard-driven navigation

### Validation Questions
- How often do users access from mobile? (analytics needed)
- What are the top 5 search queries users would make?
- Do admins need real-time dashboards or are daily reports sufficient?
```

## Zero-Config Example

When no `.arkhe.yaml` or `.arkhe/roadmap/` exists, the skill discovers context dynamically:

```
[Reading CLAUDE.md... found project description and conventions]
[Reading README.md... found tech stack and setup instructions]
[Detected build file: package.json → Node.js/TypeScript project]
[Found docs/: 3 markdown files]
[Found src/: 12 modules]

Ready. What would you like to analyze?
```
