# Authoring Stitch Prompts — Workflow

## 1. Parse Input Context
1. Detect source type (free text, spec file, revision request, image reference, image modification request).
2. Extract:
   - App/screen name and primary intent.
   - Required components (cards, charts, forms, nav).
   - Style cues (color, tone, typography) and platform/responsiveness hints.
   - Language requirements (default English, or specify target language).

   **Color Specification Strategies:**
   - Specific hex codes: When brand colors are defined (#005A8D, #228B22)
   - Named colors: For common colors (Ocean Blue, Forest Green, Slate Gray)
   - Mood-based: When exact colors unknown ("warm tones", "cool palette", "vibrant accents")
   - Hybrid: Combine both approaches ("deep blue like #0066CC", "warm beige background")

3. If prior session data exists (e.g., from Stitch Session Manager), merge palette/typography cues before rewriting.

## 1.5. Detect Split Points

Analyze whether the input should generate 1 prompt or multiple prompts:

1. **Screen Count Check**:
   - Count distinct screens/pages mentioned (e.g., "Dashboard + Settings", "Login, Signup, Reset")
   - IF >1 screen → Plan N prompts (1 per screen)

2. **Component Clustering** (for single screen):
   - List all major components/sections
   - Group by semantic relationship:
     * Navigation cluster (header, sidebar, footer, menu)
     * Primary content cluster (main area, content pane, feed)
     * Interaction cluster (forms, buttons, toolbars, action panels)
     * Discovery cluster (related content, recommendations, search results)
     * Overlay cluster (modals, drawers, tooltips, popovers)

3. **Intent Analysis**:
   - For each cluster, identify user intent ("What is the user trying to accomplish?")
   - Count distinct intents:
     * 1 intent → Keep together (1 prompt)
     * 2 intents → Evaluate split (see threshold rules)
     * 3+ intents → Always split

4. **Split Threshold Rules**:
   - IF 2 intents AND any of:
     * Combined word count >150 words
     * Components can be developed independently
     * Different visual styles or user contexts
   → Recommend split

5. **Smart Defaults** (when split detected):
   - Apply automatic decision rules
   - Generate prompt immediately with override hint
   - User can request regeneration with different approach

## 1.6. Apply Split Strategy (Smart Defaults)

When split detected, apply automatic decision rules (never block execution):

**Decision Rules:**
1. **Multiple screens** (>1) → Always split
2. **Single screen with multiple intents:**
   - IF >2 distinct intents → Split
   - IF 2 intents AND (word count >150 OR components independently developable OR different visual styles) → Split
   - Otherwise → Combine

**If SPLIT applied:**
1. Order prompts by user flow (navigation → content → actions → discovery)
2. Generate highest-priority prompt first
3. Save as: `{component-slug}-v1.md`
4. Present prompt inline with note:
   ```
   ---
   Additional prompts needed:
   2. [Intent name]: [brief description]
      → Will save as: {component-slug}-v1.md
   3. [Intent name]: [brief description]
      → Will save as: {component-slug}-v1.md

   💡 To combine into 1 prompt instead, say "combine" or "regenerate as single prompt"
   ```

**If COMBINE applied:**
1. Generate single comprehensive prompt with all components
2. Save as: `{component-slug}-v1.md`
3. Add note at end:
   ```
   💡 To split into separate prompts, say "split into N prompts" or specify grouping
   ```

**User Override:**
User can request alternative approach at any time:
- "Combine those into 1 prompt"
- "Split that into 3 separate prompts"
- "Regenerate as [N] prompts: [grouping]"
- "Keep first prompt, regenerate second as..."

## 2. Condense & Reframe
1. Rewrite the brief into a single-screen/single-goal directive using Stitch verbs ("Design/Create/Add/Update").
2. **Aggressively filter non-UI concerns**—remove ALL:
   - Backend implementation (auth flows, JWT, API endpoints, Supabase/database details)
   - Technical performance metrics (bundle sizes, cache durations, rate limits, timeouts)
   - Code-level specifications (library names, browser APIs, ARIA implementation details)
   - Error handling logic (retry strategies, fallback flows, optimistic UI rollback)
   - Security/compliance implementation (honeypot details, token validation, spam prevention)
3. **Retain ONLY visual/spatial UI concerns**:
   - Layout structure (sidebar, header, cards, grids, modals)
   - Component types (buttons, forms, charts, toggles, tooltips)
   - Visual style (colors, typography, spacing, shadows, borders)
   - User interaction patterns (click, hover, scroll, drag)
   - Responsiveness and accessibility goals (mobile-first, keyboard nav, screen readers)
   - Image specifications (placement, sizing, styling, effects)
4. Normalize terminology (use UI nouns like "sidebar", "KPI cards", "line chart", "modal").
5. **Enforce template format**: Output must be single directive paragraph + bullet list + style cues—NOT multi-section headings like "## Layout & Components" or "## Constraints & Behavior".
6. **For image modification requests**:
   - Identify which specific image(s) to target (hero image, profile photos, product thumbnails, background images, icons)
   - Specify the precise change (resize, reposition, replace, restyle, add effects, apply filters, adjust opacity)
   - Coordinate with theme when relevant (e.g., "apply blue tint to match palette", "rounded corners matching button style")
   - Use precise language: "the hero image at top" not just "the image"
   - For multiple similar images, be explicit: "all profile thumbnails" vs "the profile photo in the header"

## 2.5. Apply Language Requirements

1. If user specifies target language (e.g., "in Spanish", "French version", "convert to German"):
   - Note language in directive sentence: "Design a [Spanish] login form..." or "Design a login form with Spanish text..."
   - Translate all UI text labels in component bullets to target language (button labels, field labels, link text, headings)
   - Maintain English for technical UI terms (button, modal, sidebar, card, form, etc.)
   - Example: "email field labeled 'Correo electrónico'" not "correo electrónico field"
2. Default to English if no language specified.
3. For multi-language requests (multiple languages for same design):
   - Recommend separate prompts per language
   - Suggest naming convention: `{component-slug}-{lang-code}-v{version}.md` (e.g., `login-form-es-v1.md`, `login-form-fr-v1.md`)

## 3. Structure Output
1. Follow template sections:
   - **Heading sentence** summarizing the screen/app and platform.
   - **Layout bullets** (3–6) covering navigation, hierarchy, and key components.
   - **Style cues** (3–6) capturing palette, typography, density, tone.
   - **Constraints** highlighting responsiveness, export requirements, or iteration notes.
2. Keep bullets short (10–20 words) and action-oriented.
3. Maintain atomicity—if the brief mixes multiple screens, note the split and produce the highest-priority prompt first.
4. **If split strategy active** (from Step 1.6):
   - Generate ONLY the first prompt in current output
   - Derive component slug from the GENERATED PROMPT's header
   - Save as: `{component-slug}-v{version}.md`
   - After the prompt, add note listing remaining prompts:
     ```
     ---
     Additional prompts needed:
     2. [Intent name]: [brief description]
        → Will save as: {component-slug}-v1.md
     3. [Intent name]: [brief description]
        → Will save as: {component-slug}-v1.md
     ...
     ```
   - User can request subsequent prompts explicitly

## 3.5. Post-Processing Cleanup

Before validation, apply final cleanup to remove edge-case technical details:

1. **Strip forbidden patterns**:
   - Performance metrics: Remove `<Nkb`, `bundle size`, `compressed`, `Nms feedback/timeout`
   - Compliance specs: Replace `WCAG X.X XX` with "accessible", "high contrast", or "screen reader support"
   - Implementation logic: Remove "graceful degradation", "fallback when X unavailable", "retry strategies"
   - Platform parentheticals: Remove `(iOS/Android)`, `(Chrome/Firefox/Safari/Edge)` — use "mobile/desktop" without OS names
   - API-specific terms: Replace "clipboard action" → "copy", "native mobile share dialog" → "native share"

2. **Condense verbose bullets**:
   - If any bullet exceeds 25 words, condense to 10-20 words using:
     - Em-dashes for sublists (e.g., "grid with thumbnails, titles, excerpts" → "grid—thumbnails, titles, excerpts")
     - Parallel structure (e.g., "displaying 3-5 articles in responsive grid" → "3-5 articles, responsive grid")
     - Remove redundant phrases ("that triggers", "that opens", "that displays" → direct nouns)

3. **Simplify constraint language**:
   - "graceful degradation when native APIs unavailable" → remove entirely
   - "WCAG 2.1 AA compliance with NVDA/JAWS testing" → "screen reader support"
   - "Last 2 versions Chrome/Firefox/Safari/Edge" → "modern browsers"
   - "<15kb compressed bundle" → remove entirely

## 4. Validate for Stitch Compatibility
1. **Strict word count**: Target <250 words (absolute max 400). If over 250, condense further.
2. **Format validation**:
   - Output must have NO `##` markdown headings (headings = wrong format).
   - Must match template: directive sentence → bullet list → style cues → constraints.
   - Compare structure against EXAMPLES.md (e.g., Example 1, lines 16-24) to ensure format matches.
3. **Content validation**—confirm inclusion of:
   - At least three concrete UI nouns/components (cards, sidebar, buttons, chart, etc.).
   - Explicit style cues (3-6 descriptors: colors, typography, spacing, mood).
   - Clear intent statement using Stitch verbs (Design/Create/Add/Update...).
   - Bullets average 10-20 words each (max 25 words per bullet).
4. **Technical filter check**—ensure output contains ZERO:
   - Backend/auth terms (JWT, Supabase, API, token, auth flow, rate limiting).
   - Performance metrics (bundle size, cache duration, `<Nkb`, `Nms`, timeout values, compressed).
   - Code implementation (library names, ARIA implementation details, Clipboard API specifics).
   - Error handling logic (retry, fallback, rollback, validation strategies, graceful degradation).
   - Compliance specs in format `WCAG X.X XX` (use "accessible", "high contrast", "screen reader support" instead).
   - Platform parentheticals like `(iOS/Android)`, `(Chrome/Firefox/Safari)` (use "mobile", "desktop", "modern browsers").
   - Verbose implementation phrases ("that triggers", "that opens", "when unavailable").
5. Ensure instructions avoid:
   - Conversational filler ("please", "thanks", "maybe").
   - Vague adjectives without context ("nice", "modern" alone without specifics).
6. When revising existing prompts:
   - Specify which elements stay untouched.
   - Highlight only the delta (e.g., "Move KPI cards above chart").

## 5. Finalize & Return
1. Present the final prompt in Markdown with short paragraphs or bullet lists for readability.
2. If major assumptions were made (e.g., inferred color palette), call them out succinctly.
3. Suggest next steps if the brief indicates additional screens (“Create separate prompt for Settings screen to maintain atomicity”).
