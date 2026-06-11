# Phase 1: Requirements

**Goal**: Understand what needs to be built

**Model tier**: sonnet

---

## Actions

### 1. Clarify Feature Request

If feature is unclear, ask user for:
- What problem are they solving?
- What should the feature do?
- Any constraints or requirements?

### 2. Identify Underspecified Aspects

Review and document gaps in:
- Edge cases and error handling
- Integration points and scope boundaries
- Design preferences and backward compatibility
- Performance and security needs

### 3. Document Requirements

Create structured requirements:

```markdown
## Functional Requirements

### FR-001: [Requirement Title]
**Description:** [What the system should do]
**Acceptance Criteria:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

### FR-002: [Next Requirement]
...
```

### 4. Define Constraints

Document:
- Performance requirements (quantified, e.g., "<200ms response time")
- Security considerations
- Backward compatibility needs
- Dependencies on external systems

### 5. UI Work Detection

After gathering requirements, scan for UI-related keywords in the feature request and requirements:

**UI Keywords:**
- Layout: `UI`, `page`, `screen`, `layout`, `view`, `route`
- Components: `component`, `button`, `form`, `modal`, `dialog`, `panel`, `card`
- Design: `design`, `frontend`, `style`, `CSS`, `Tailwind`, `animation`
- Visual: `icon`, `image`, `color`, `theme`, `responsive`

**If UI keywords detected:**

Set `ui_work_detected = true` and use `AskUserQuestion`:
- **header**: "Design Assets"
- **question**: "This feature involves UI work ([list detected keywords]). How would you like to handle design assets?"
- **options** (these are sibling routes — the user picks one; AskUserQuestion allows at most 4 options, so the Claude Design link lives under "existing designs"):
  - { label: "Ideate with live prototype gallery (Recommended for exploration)", description: "Generate 3 visual variations and pick a direction in a live browser gallery (design-intent + devtools plugins)" }
  - { label: "Generate Stitch prompts", description: "Create design prompts using authoring-stitch-prompts skill" }
  - { label: "I have a design reference", description: "Provide a Figma/Stitch export path or a Claude.ai design/share link" }
  - { label: "Skip design workflow", description: "Implement UI directly without Stitch" }

**Response handling:**

- **Ideate with live prototype gallery**:
  1. **Preflight:** check the live-preview CLI is available — `command -v arkhe-preview`. If it is NOT found (or the `design-intent:prototype` skill is unavailable), tell the user: *"The live prototype gallery needs the `devtools` (arkhe-preview CLI) and `design-intent` plugins. Falling back to a text-based visual direction summary."* Then capture a short textual visual direction (style, layout, tone) from the user and set `visual_direction_captured = true` with `visual_direction_source = "text"`. Skip the gallery steps.
  2. If available: invoke `Skill` tool with `skill: "design-intent:prototype"`, passing the UI requirements as the component description. The prototype skill serves a live gallery and **ends its turn** so the user can click a favorite.
  3. **On the next turn** (after the user replies), resolve the pick using the prototype skill's pick-capture protocol: read the prototype `manifest.json`, then `manifest.state_dir/events.jsonl`, and find the most recent event with `action === "select-variant"`. (See `design-intent/skills/prototype/SKILL.md` → "Next-Turn Pick Capture".)
  4. Record the picked variant's style name and artifact path. Set `visual_direction_captured = true`, `visual_direction_source = "prototype"`, `prototype_artifact_path = [picked .html path]`, and `prototype_manifest_path = [manifest.json path]`.
  5. If no `select-variant` event exists, the user did not click — fall back to their terminal text as the visual direction.
- **Generate Stitch prompts**:
  1. Invoke `Skill` tool with `skill: "authoring-stitch-prompts"`
  2. Pass requirements as context
  3. Store generated prompts path for Phase 2
  4. Set `stitch_prompts_generated = true`
- **I have a design reference**:
  1. Ask what they have: a file/export **path** (Figma/Stitch), or a **Claude.ai design/share link**.
  2. **If a path:** store for plan.md `## Design Assets` section; set `existing_designs_path = [user provided path]`.
  3. **If a Claude Design link:** attempt `WebFetch` on the URL to capture the design intent (layout, components, styling). **If WebFetch fails or the link is auth-gated** (Claude.ai share links often require auth), ask them to paste a screenshot path or a short textual description instead. Set `design_link_ref = [url]` and `design_link_notes = [fetched text | screenshot path | description]`.
- **Skip**:
  1. Set `skip_stitch_workflow = true`
  2. Continue without Stitch integration

### 6. Save Requirements

After documenting requirements, persist to spec.md immediately:

1. **Read existing spec.md** from `{spec_path}/spec.md`
2. **Update with requirements:**
   - Functional Requirements (FR-XXX format)
   - Acceptance criteria for each requirement
   - Constraints and assumptions
   - UI work detection results (if applicable)
   - **Visual Direction** (if `ui_work_detected`): write the `## Visual Direction` section capturing the chosen route and its outcome:
     - Prototype route → picked variant style name + `prototype_artifact_path`
     - Claude Design link route → `design_link_ref` + `design_link_notes`
     - Text fallback → the captured textual direction
     - (Stitch / existing-designs routes are already recorded via Phase 2's `## Design Assets`; note the route here for traceability.)
3. **Write updated spec.md** using [spec.md.template](../templates/spec.md.template)
4. **Log:** "Requirements saved to `{spec_path}/spec.md`"

**Rationale:** Saving after Phase 1 ensures requirements are not lost if session ends before Phase 2.

---

## User Checkpoint

**Gate: Tier 2** ⚠️ (RECOMMENDED - skippable with `--auto`)

Present requirements summary:
1. List of FR-XXX requirements with acceptance criteria
2. Identified constraints
3. Any remaining questions or assumptions

**Ask using AskUserQuestion:**

Present requirements summary, then use `AskUserQuestion` tool:
- **header**: "Requirements"
- **question**: "[FR-XXX list summary with key acceptance criteria]. How would you like to proceed?"
- **options**:
  - { label: "APPROVE", description: "Proceed to architecture design" }
  - { label: "REVIEW", description: "Show me more details" }
  - { label: "MODIFY", description: "I want to change requirements" }
  - { label: "CANCEL", description: "Stop here" }

**Response Handling:**
- **APPROVE**: Proceed to Phase 2
- **REVIEW**: Show full requirements details, then re-present this checkpoint
- **MODIFY**: Allow user to modify requirements, then re-present
- **CANCEL**: Stop pipeline

**STOP: Unless `--auto` is set, WAIT for user response before proceeding to Phase 2.**

---

## Output

Phase 1 produces:
- Functional requirements (FR-XXX format)
- Acceptance criteria for each requirement
- Constraints and assumptions
- Resolved clarifications

**Next:** Proceed to [PHASE-2-ARCHITECTURE.md](PHASE-2-ARCHITECTURE.md)
