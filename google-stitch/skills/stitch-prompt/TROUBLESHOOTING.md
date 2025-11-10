# Authoring Stitch Prompts — Troubleshooting

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

## Component Ambiguity
- **Symptom:** Input says “add charts” without specifying type.
- **Fix:** Choose a sensible default (bar/line chart) based on context and mention the assumption. Encourage the user to clarify if precision matters.

## Unclear Platform or Responsiveness
- **Symptom:** Prompt doesn’t mention web vs. mobile or responsive behavior.
- **Fix:** Infer from context (e.g., mention of sidebar ⇒ desktop/web). If uncertain, produce a desktop-first prompt and highlight the assumption. Add responsive note in constraints.
