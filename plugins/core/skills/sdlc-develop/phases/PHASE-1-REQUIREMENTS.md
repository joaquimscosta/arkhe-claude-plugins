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
- **options**:
  - { label: "Generate Stitch prompts (Recommended)", description: "Create design prompts using authoring-stitch-prompts skill" }
  - { label: "I have existing designs", description: "Provide Figma/Stitch export locations" }
  - { label: "Skip design workflow", description: "Implement UI directly without Stitch" }

**Response handling:**
- **Generate Stitch prompts**:
  1. Invoke `Skill` tool with `skill: "authoring-stitch-prompts"`
  2. Pass requirements as context
  3. Store generated prompts path for Phase 2
  4. Set `stitch_prompts_generated = true`
- **Existing designs**:
  1. Ask user for asset paths (Figma URL, Stitch exports directory)
  2. Store paths for use in plan.md `## Design Assets` section
  3. Set `existing_designs_path = [user provided path]`
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

**STOP: Unless `--auto` is set, WAIT for user response before proceeding to Phase 2.**

---

## Output

Phase 1 produces:
- Functional requirements (FR-XXX format)
- Acceptance criteria for each requirement
- Constraints and assumptions
- Resolved clarifications

**Next:** Proceed to [PHASE-2-ARCHITECTURE.md](PHASE-2-ARCHITECTURE.md)
