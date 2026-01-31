# Authoring Stitch Prompts — Troubleshooting

## Anti-Patterns: What NOT to Include

Stitch generates UI layouts and visual designs—it does NOT implement backend logic, authentication, or technical infrastructure. Prompts must focus exclusively on visual/spatial concerns.

### ❌ NEVER Include These:

**Backend/Infrastructure:**
- Authentication flows (JWT, OAuth, Supabase Auth, login logic)
- API endpoints, rate limiting, caching strategies
- Database operations (queries, migrations, schema details)
- Server-side validation, error handling logic
- Security implementation (honeypot, CSRF tokens, spam prevention)

**Technical Performance Metrics:**
- Bundle sizes (`<15kb compressed`, `lightweight bundle`)
- Load times, timeout values (`<100ms feedback`, `120ms interaction`, `5-minute cache`)
- Performance budgets, optimization targets (`<30kb gzipped`)
- Network request limits, debounce intervals (`10/min per user`)

**Code-Level Implementation:**
- Library/framework names (Tailwind is OK in style cues, but NOT implementation details)
- Browser API specifics (Clipboard API fallback logic, Share API behavior)
- ARIA implementation details (prefer "keyboard navigation" over "ARIA live regions with role=alert")
- State management logic (optimistic UI rollback, local storage strategies)

**Compliance Implementation:**
- WCAG technical specifications (prefer "keyboard accessible" / "high contrast" over `WCAG 2.1 AA`, `Level A criterion 2.1.1`, `3:1 contrast minimum`)
- Browser support matrices (prefer "modern browsers" over `last 2 versions Chrome/Firefox/Safari/Edge`, `HTTPS required`)
- Legal/privacy implementation (GDPR cookie logic, consent workflows beyond UI)
- Platform parentheticals (remove `(iOS/Android)`, `(mobile/desktop)` in technical contexts)
- Implementation degradation logic (avoid "graceful degradation when native APIs unavailable", "fallback when clipboard unavailable")

### ✅ DO Include These:

**Visual/Spatial Concerns:**
- Layout structure (sidebar, header, cards, grids, modals, overlays)
- Component types (buttons, forms, charts, toggles, dropdowns, tooltips)
- Visual style (colors, typography, spacing, shadows, borders, icons)
- Interaction patterns (click, hover, drag, scroll animations)
- Accessibility goals (keyboard navigation, screen reader support, high contrast)
- Responsiveness (mobile-first, breakpoints, touch targets)

### Example: Before & After

**❌ WRONG (PRD-style with technical details):**
```
## Layout & Components
- **Share Button**: Native mobile share dialog (iOS/Android), fallback UI on desktop
- **Reactions**: Authentication requirement, JWT token validation, real-time count updates,
  optimistic UI, single selection per user with toggle-off capability
- **Copy Link**: Clipboard API with accessible fallback modal, visual + ARIA live region confirmation
- **Suggest Form**: Pre-filled contact form with rate-limiting (5/hour), honeypot spam protection

## Constraints & Behavior
- Supabase Auth integration required for reactions
- Performance: <15kb compressed bundle, <100ms interaction feedback, 5-minute caching
- Browser Support: Last 2 versions Chrome/Firefox/Safari/Edge, HTTPS required
- WCAG 2.1 AA compliance with focus indicators (3:1 contrast minimum), NVDA/JAWS/VoiceOver testing
- Graceful degradation when native APIs unavailable, clipboard action fallback modal
```

**✅ CORRECT (Stitch-optimized):**
```
Design a content engagement toolbar for cultural heritage pages optimized for mobile-first responsive design.

Include:
- Share button with native dialog (mobile) and Facebook/copy link options (desktop)
- Four emoji reactions (Love, Helpful, Interesting, Thank you) with counts
- Copy link button with one-click copy and confirmation toast
- Suggest improvement button opening contact form
- Print button for browser print dialog
- Related content grid (3-5 tag-matched items) below toolbar

Style: Clean, inviting, culturally respectful, Ocean Blue (#005A8D), Valley Green (#3E7D5A),
Bougainvillea Pink (#D90368), Sunny Yellow (#F7B801), Merriweather headings, Lato body text,
44px touch targets, subtle shadows.

Optimize for mobile-first (320px minimum), full keyboard navigation, screen reader support, dark mode.
```

**File saved as:**
`design-intent/google-stitch/toolbar/prompt-v1.md`

**Key Differences:**
- ❌ Removed: JWT, Supabase, API details, rate limiting, `<15kb bundle`, `<100ms feedback`, browser versions (`Last 2 versions...`), `WCAG 2.1 AA`, `3:1 contrast minimum`, `(iOS/Android)`, "graceful degradation", "clipboard action"
- ✅ Kept: UI components, visual style, colors, typography, accessibility goals (keyboard nav, screen readers, high contrast), responsiveness
- ❌ Removed: Multi-section headings (`## Layout & Components`, `## Constraints & Behavior`)
- ✅ Used: Single directive paragraph → bullets → style → constraints
- ❌ Removed: Implementation logic ("fallback when unavailable", "Clipboard API with fallback")
- ✅ Used: Simple UI terms ("copy link", "native share", "high contrast")

---

## Prompts Are Too Verbose
- **Symptom:** Output reads like marketing copy or exceeds a few paragraphs.
- **Fix:** Re-run the template with succinct bullets; drop storytelling sentences. Focus on layout nouns and style cues.
- **Tip:** If the source brief is wordy, summarize it first in plain bullet points, then rewrite.

## Missing Style Cues
- **Symptom:** Prompt lacks palette, typography, or tone guidance.
- **Fix:** Re-scan the source text for adjectives/colors; if absent, ask the user or pull from session context. Include 3–6 cues (palette + typography + density).
- **Tip:** When no cues exist, provide neutral defaults (e.g., “clean, neutral palette, sans-serif typography”) and note the assumption.

## Multi-Screen Prompts
- **Symptom:** User requests multiple screens/flows in a single brief.
- **Fix:** Split into separate prompts. Respond with the highest-priority screen and recommend follow-up prompts for the rest.
- **Tip:** Reference the Stitch Session Manager skill if the user already has a logged session.

## Split vs Combine Decision

**When to SPLIT into multiple prompts:**
- Multiple screens/pages mentioned (e.g., "Dashboard + Settings + Profile")
- >2 distinct user intents within single screen
- Components serve different user goals
- Total word count >150 words AND can be separated logically
- User wants to iterate on sections independently
- Different visual styles or user contexts

**When to COMBINE into single prompt:**
- Single cohesive component (e.g., login form with all fields)
- All actions serve one user goal
- Components tightly coupled (removing one breaks others)
- Total word count <150 words
- Rapid prototyping phase where cohesion matters

**Decision Examples:**

✅ **Split these:**
- "Article page with reading pane, comment section, and related content grid" → 3 prompts (3 intents: consume, engage, discover)
- "Dashboard + Settings + Profile pages" → 3 prompts (3 screens)
- "E-commerce product page with gallery, specs, reviews, and recommendations" → 3-4 prompts (multiple intents)
- "Toolbar with 6 actions + related content grid below" → 2 prompts (2 intents: engage + discover)

❌ **Don't split these:**
- "Login form with email, password, submit, forgot password link" → 1 prompt (1 intent: authenticate)
- "Toolbar with 5 action buttons" → 1 prompt (1 intent: actions, unless >150 words)
- "Contact form with name, email, message, submit" → 1 prompt (1 intent: contact)
- "Navigation header with logo, menu, search, user avatar" → 1 prompt (1 intent: navigate)

**How the Skill Handles Splits:**
1. Detects split points automatically (Step 1.5 in WORKFLOW.md)
2. Applies smart defaults (Step 1.6): split if >2 screens/intents, else combine
3. Generates prompt immediately with override hint
4. If split applied, generates first prompt + lists remaining prompts needed
5. User can request regeneration with different approach ("combine" or "split into N")

## Component Ambiguity
- **Symptom:** Input says “add charts” without specifying type.
- **Fix:** Choose a sensible default (bar/line chart) based on context and mention the assumption. Encourage the user to clarify if precision matters.

## Unclear Platform or Responsiveness
- **Symptom:** Prompt doesn't mention web vs. mobile or responsive behavior.
- **Fix:** Infer from context (e.g., mention of sidebar ⇒ desktop/web). If uncertain, produce a desktop-first prompt and highlight the assumption. Add responsive note in constraints.

## Image Modification Requests
- **Symptom:** User wants to change specific images but prompt is too vague or ambiguous.
- **Fix:** Identify exact images using spatial references ("the hero image at top", "profile photo in header", "product thumbnails in grid") and specify the precise change (resize, reposition, restyle, add effects). Coordinate image styling with theme when relevant.
- **Tip:** When multiple similar images exist, be explicit: "all profile thumbnails" vs "the profile photo in the user card". Include sizing, positioning, styling, and any effects (gradients, borders, opacity) in clear visual terms.

---

## Design Context Integration Issues

### Context Not Detected When Expected

**Symptom:** `design-intent/` directory exists but style cues don't reflect project type or design system.

**Causes:**
- AUTO-FILL markers not replaced in `constitution.md` (still contain `<!-- AUTO-FILL: ... -->`)
- Files created but not customized after running `/setup`
- Reading from wrong project root directory

**Fix:**
1. Check if `design-intent/memory/constitution.md` has actual values, not AUTO-FILL template markers
2. Run `/setup` in the project to auto-detect and fill values
3. Manually edit `constitution.md` to add Project Type and Design System values:
   ```markdown
   **Project Type:** Enterprise
   **Design System:** Fluent UI
   ```

### Wrong Context Injected

**Symptom:** Style cues mention wrong design system or project type (e.g., "Fluent UI" when using Material UI).

**Causes:**
- Outdated `constitution.md` after project changes
- Multiple design systems in `package.json` (fallback detection picked wrong one)
- Incorrect values entered in constitution.md

**Fix:**
1. Update `design-intent/memory/constitution.md` with correct values
2. Re-run `/setup` to re-detect project configuration
3. Manually specify style cues in input to override: "Use Material Design style, not Fluent"

### Want to Override Detected Context

**Symptom:** User wants different style than what design context suggests (e.g., playful style for an Enterprise project).

**Fix:** Explicitly state desired style in the input. User-provided cues take precedence over injected context:
- Input: "Create a playful, colorful dashboard" → overrides "enterprise-grade, professional"
- Input: "Use Material Design patterns" → overrides detected Fluent UI

### Design Context Not Available (Working Standalone)

**Symptom:** No design context detected, prompts use default neutral style cues.

**Expected Behavior:** This is normal. The skill works standalone when:
- No `design-intent/` directory exists
- `constitution.md` exists but has AUTO-FILL markers (not customized)
- `package.json` doesn't contain recognizable design system dependencies

**Note:** Standalone mode is valid. Default style cues ("clean, modern, neutral palette") work for any project. Users can always provide specific style cues in their input.

---

## MCP Integration Issues

### MCP Tools Not Detected After Authoring

**Symptom:** After authoring a prompt, the skill doesn't offer MCP generation even though you set up the Stitch MCP server.

**Causes:**
- MCP server not configured in `.mcp.json`
- Stitch API access not approved (403 errors)
- Claude Code session needs restart

**Fix:**
1. Run `/stitch-setup` to verify MCP configuration
2. Check MCP status: `claude mcp list`
3. If not configured, add to your project's `.mcp.json` (see plugin README)
4. Restart Claude Code to reload MCP servers

**Note:** Stitch API requires preview/allowlist access from Google.

### Generation Failed After Authoring

**Symptom:** MCP generation was offered and accepted, but screens failed to generate.

**Causes:**
- Authentication expired
- Project ID not set or invalid
- Stitch service issue

**Fix:**
1. Refresh credentials: `gcloud auth application-default login`
2. Verify project ID: Check `STITCH_PROJECT_ID` environment variable
3. Try again: `/stitch-generate @{prompt-file-path}`
4. Check Stitch service at [stitch.withgoogle.com](https://stitch.withgoogle.com)

### Want MCP But Not Set Up

**Symptom:** User wants automated generation but MCP is not configured.

**Fix:**
1. Run `/stitch-setup` for guided setup
2. Or manually: `npx @_davideast/stitch-mcp init`
3. After setup, authored prompts will automatically offer generation
