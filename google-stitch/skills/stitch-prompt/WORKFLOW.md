# Authoring Stitch Prompts — Workflow

## 1. Parse Input Context
1. Detect source type (free text, spec file, revision request, image reference).
2. Extract:
   - App/screen name and primary intent.
   - Required components (cards, charts, forms, nav).
   - Style cues (color, tone, typography) and platform/responsiveness hints.
3. If prior session data exists (e.g., from Stitch Session Manager), merge palette/typography cues before rewriting.

## 2. Condense & Reframe
1. Rewrite the brief into a single-screen/single-goal directive using Stitch verbs (“Design/Create/Add/Update”).
2. Remove narrative filler, marketing copy, or implementation details irrelevant to UI layout.
3. Normalize terminology (use UI nouns like “sidebar”, “KPI cards”, “line chart”, “modal”).

## 3. Structure Output
1. Follow template sections:
   - **Heading sentence** summarizing the screen/app and platform.
   - **Layout bullets** (3–6) covering navigation, hierarchy, and key components.
   - **Style cues** (3–6) capturing palette, typography, density, tone.
   - **Constraints** highlighting responsiveness, export requirements, or iteration notes.
2. Keep bullets short (10–20 words) and action-oriented.
3. Maintain atomicity—if the brief mixes multiple screens, note the split and produce the highest-priority prompt first.

## 4. Validate for Stitch Compatibility
1. Word count should remain comfortably below 1,000 words (target <250).
2. Confirm inclusion of:
   - At least three concrete UI nouns/components.
   - Explicit style cues.
   - Clear intent statement (what to design/change).
3. Ensure instructions avoid:
   - Conversational filler (“please”, “thanks”).
   - Vague adjectives without context (“nice”, “modern”).
4. When revising existing prompts:
   - Specify which elements stay untouched.
   - Highlight only the delta (e.g., “Move KPI cards above chart”).

## 5. Finalize & Return
1. Present the final prompt in Markdown with short paragraphs or bullet lists for readability.
2. If major assumptions were made (e.g., inferred color palette), call them out succinctly.
3. Suggest next steps if the brief indicates additional screens (“Create separate prompt for Settings screen to maintain atomicity”).
