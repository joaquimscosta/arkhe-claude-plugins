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
