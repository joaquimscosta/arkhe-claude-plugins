---
description: Generate Google Stitch-ready prompts from briefs or spec files using the authoring skill
argument-hint: <brief or @/path/to/spec>
---

# Prompt Command

Convert natural-language descriptions, revision notes, or spec files into Stitch-optimized prompts. This command gathers your preferences before generating to ensure the output matches your vision.

## Usage

```bash
/prompt "Design a fintech dashboard with KPI cards and charts"
/prompt @specs/mobile-app.md
/prompt "Move the KPI cards above the chart and add a region filter"
```

Attach files or reference repository paths as needed; the Skill will read them before rewriting the prompt.

## Inputs

- `$ARGUMENTS`: user-provided brief, iteration note, or file path(s) to parse.
- Attached files (optional): wireframes, specs, or references to include during analysis.

## Interactive Flow

For new prompt generation (not revisions), this command asks about your preferences:

1. **Component Selection** - Which UI components to include
2. **Style Preferences** - Visual style (Enterprise, Consumer, Minimal, etc.)
3. **Structure Decision** - Combined file or split by component

Select "Quick generation" at the first question to skip all questions and use smart defaults.

**Questions are skipped when:**
- Input is a revision request (starts with "change", "update", "move", "adjust")
- User selects "Quick generation"
- Single component detected (structure question only)

---

## Execution

### Step 1: Detect Request Type

Check if `$ARGUMENTS` is a revision request:
- If starts with: "change", "update", "move", "adjust", "resize", "reposition", "modify"
- → Skip all questions, invoke skill directly with `$ARGUMENTS`

### Step 2: Check for Design Context

Look for `design-intent/memory/constitution.md`:
- If found: Extract Project Type and Design System for style defaults
- If not found: Proceed without context

### Step 3: Analyze Brief for Components

Parse `$ARGUMENTS` to identify UI components mentioned:
- Navigation elements (sidebar, header, menu, tabs)
- Content areas (cards, grids, tables, lists)
- Data visualization (charts, graphs, metrics, KPIs)
- Interactive elements (forms, buttons, modals, dialogs)
- Media (images, video, galleries)

### Step 4: Ask Questions (Interactive)

**Question 1: Component Selection**

Present detected components and ask user which to include:

```
I detected these components from your brief:

• [Component 1]: [brief description]
• [Component 2]: [brief description]
• [Component 3]: [brief description]

Which components should I include in the Stitch prompt?

Options:
→ All components (recommended)
→ Select specific components
→ Add more components
→ Quick generation (skip all questions, use smart defaults)
```

If user selects "Quick generation": Skip to Step 5 with defaults.
If user selects "Select specific": Present checkboxes for each component.
If user selects "Add more": Accept additional component descriptions.

**Question 2: Style Preferences**

Ask about visual style:

```
What visual style should these prompts target?

Options:
→ Enterprise (professional, data-dense, formal)
→ Consumer (friendly, approachable, vibrant)
→ Minimal (clean, simple, lots of whitespace)
→ Playful (colorful, fun, animated feel)
→ Custom (describe your preference)
→ Use detected: [Project Type + Design System] (if design-intent found)
```

**Question 3: Structure Decision** (only if multiple components)

```
How should I structure the output for [N] components?

Options:
→ Combined (single file with layout + all components)
→ Split (separate prompt per component)
→ Auto-detect (let skill decide based on complexity)
```

### Step 5: Build Structured Input

Compile user selections into structured format:

```
Brief: [original $ARGUMENTS]
Components: [comma-separated list of selected components]
Style: [chosen style option]
Structure: [Combined/Split/Auto]
```

### Step 6: Invoke Skill

Invoke the Skill tool with skill name "google-stitch:authoring-stitch-prompts" with the structured input above.

The skill will:
- Use specified components (skip auto-detection if provided)
- Apply style choice directly (override design context if specified)
- Respect structure preference (skip split detection if specified)

### Step 7: Present Results

Display generated prompt(s) with:
- File path(s) created
- Component breakdown
- Style cues applied
- Next steps for using in Stitch

---

## Style Mapping

| Style Choice | Stitch Style Cues |
|--------------|-------------------|
| Enterprise | enterprise-grade, professional, data-dense, clean sans-serif typography |
| Consumer | friendly, approachable, vibrant accents, generous whitespace |
| Minimal | clean, minimal, ample whitespace, subtle shadows, restrained palette |
| Playful | playful, colorful, fun, animated feel, rounded corners, bold typography |

---

## Examples

**Interactive generation:**
```
User: /prompt "dashboard for fitness app"
Claude: [Asks 3 questions about components, style, structure]
User: [Selects: All components, Consumer style, Combined]
Claude: [Generates prompt with friendly, approachable style cues]
```

**Quick generation:**
```
User: /prompt "e-commerce product page"
Claude: [Asks first question]
User: Quick generation (skip all questions)
Claude: [Generates with smart defaults]
```

**Revision (questions skipped):**
```
User: /prompt "change the header to sticky and add a search bar"
Claude: [Skips questions, generates revision prompt directly]
```
