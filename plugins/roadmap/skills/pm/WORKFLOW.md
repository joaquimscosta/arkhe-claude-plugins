# PM Skill — Workflow

Detailed discovery protocol and mode workflows for the Product Manager skill.

## Context Discovery Protocol

Run the shared context discovery protocol in [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md). Execute all phases in order before any analysis. Earlier sources override later ones.

## Mode Workflows

### `stories <feature>`

1. Run context discovery
2. **Scope preamble** — Auto-run a scope assessment before generating stories. Present under a `## Scope Assessment` heading:
   - **User Value** — How does this feature serve end users?
   - **Project Fit** — Does it align with project goals and current phase?
   - **Dependencies** — What existing modules/features does it depend on?
   - **Effort Estimate** — Rough sizing (S / M / L / XL)
   - **Risks** — What could go wrong?
   - **Recommendation** — Build now / Defer / Needs research / Reject
3. **Gate** — If the scope recommendation is **Reject** or **Needs research**, stop here. Present the scope assessment and explain why story generation is premature. Do NOT proceed to story generation.
4. Identify personas from project context
5. Identify the target feature area in the codebase
6. Generate user stories grouped by priority:
   - **Must Have** — Core functionality
   - **Should Have** — Important but not critical
   - **Could Have** — Nice to have
7. For each story, include:
   - Persona, action, benefit
   - Given/When/Then acceptance criteria
   - Edge cases relevant to the project domain
   - Dependencies on other features

### `prioritize`

1. Run context discovery
2. Inventory all candidate features from:
   - Gap analyses
   - Unstarted specs
   - Known issues
   - User requests
3. Score each feature:
   - **User Value**: High / Medium / Low
   - **Effort**: Small (< 1 day) / Medium (1-3 days) / Large (3+ days)
   - **Dependencies**: None / Some / Blocked
4. Assign MoSCoW category
5. Produce ranked table

### `scope <feature>`

1. Run context discovery
2. Analyze the feature against project context:
   - **User Value** — Who benefits? What problem does it solve?
   - **Project Fit** — Does it align with project goals and current phase?
   - **Dependencies** — What must exist first?
   - **Overlap Check** — Does any existing spec already cover this?
   - **Effort Estimate** — S / M / L with justification
   - **Risks** — What could go wrong from a product perspective?
3. Deliver recommendation: Build now / Defer / Needs research / Reject

### `validate`

1. Run context discovery
2. Extract project goals from documentation
3. Scan codebase for implementation evidence
4. Cross-reference goals vs reality:
   - Features built that aren't in scope
   - Scope items with no implementation
   - Partial implementations
5. Produce validation report with gaps and recommendations

### `needs`

1. Run context discovery
2. Extract user profiles from project context
3. Identify pain points from:
   - Gap analyses
   - Research documents
   - Issue trackers
4. Map pain points to: Severity, Current Solution, Proposed Solution
5. Identify unmet needs not yet addressed
6. Generate validation questions

### `compare <A> vs <B>`

1. Run context discovery
2. Identify both options in project context
3. Score each across: User Value, Effort, Dependencies, Risk, Long-term fit
4. Consider project-specific constraints
5. Deliver clear recommendation with rationale

### `next`

1. Run context discovery (thorough — read gap analyses and specs)
2. Cross-reference:
   - Unclosed gaps
   - Unstarted specs
   - Module maturity imbalances
   - Frontend-backend parity gaps
3. Recommend 1-3 features with:
   - Rationale (why now?)
   - Effort estimate
   - Dependencies
   - Suggested order

## Output Conventions

### Personas

If project context defines personas, use them consistently. If not, derive from the project's target users:

```
| Persona | Description | Key Needs |
|---------|-------------|-----------|
| ... | ... | ... |
```

### Story Format

```
### US-{N}: {Title}

**As a** {persona},
**I want to** {action},
**So that** {benefit}.

#### Acceptance Criteria

- **Given** {precondition}
  **When** {action}
  **Then** {expected result}
```

### Scope Assessment Format

```
## Scope Assessment: {feature}

### User Value
{Why does this matter to the user?}

### Project Fit
{Does this align with current goals? Which phase?}

### Dependencies
{What must exist before this can be built?}

### Effort Estimate
{S / M / L with justification}

### Risks
{Product risks, not technical risks}

### Open Questions
{What needs clarification?}

### Recommendation
{Build now / Defer to Phase N / Needs research / Reject}
```

---

## Deep Pipeline (`--deep`)

When `$ARGUMENTS` contains `--deep`, execute this multi-agent pipeline instead of the conversational mode workflows above. This produces reviewed, confidence-scored artifacts.

### Phase 1: Context Gathering (Haiku Agent)

Launch a **Haiku agent** to run the full context discovery protocol:

**Agent prompt**: "Run the context discovery protocol from CONTEXT_DISCOVERY.md. Return a structured summary including: project name, tech stack, personas, module inventory with maturity levels, documentation inventory (categorized), key constraints, and current phase/milestone. Be thorough but concise."

Provide the agent with the content of [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md).

### Phase 2: PM Analysis (Sonnet Agent)

Launch a **Sonnet agent** to produce the PM artifact for the requested mode.

**Agent prompt**: "You are a product manager. Using the context summary from Phase 1, produce a {mode} artifact for {feature/topic}. Use templates from TEMPLATES.md. After your analysis, append a Builder Confessions block."

Provide the agent with:
- Phase 1 context summary
- The content of [TEMPLATES.md](../../references/TEMPLATES.md) (PM section)
- The PM lane rules from [LANE_DISCIPLINE.md](../../references/LANE_DISCIPLINE.md)

**Builder Confessions block** (required at end of output):

```markdown
## Builder Confessions
- **Assumption**: {what was assumed without verification}
- **Uncertainty**: {areas where confidence is low}
- **Shortcut**: {where a deeper analysis was skipped}
- **Missing data**: {what couldn't be found in the codebase}
```

### Phase 3: Architect Feasibility Check (Haiku Agent)

**Only for `scope` and `stories` modes.** Skip for other modes.

Launch a **Haiku agent** to review the PM artifact from an architect's perspective:

**Agent prompt**: "You are a systems architect reviewing a PM artifact. Check for: unrealistic effort estimates (compare against actual codebase complexity), missing technical dependencies (what infrastructure must exist?), incorrect assumptions about existing capabilities, acceptance criteria that are technically infeasible. Return a structured feasibility report."

Provide the agent with:
- Phase 2 PM artifact
- Phase 1 context summary (especially module inventory)

### Phase 4: Confidence Scoring (Haiku Agent)

Launch a **Haiku agent** using the `roadmap-critic` agent's scoring rubric:

**Agent prompt**: "You are a quality critic. Score each section of this PM artifact 0-100. Read the Builder Confessions block first and focus scrutiny on confessed areas. For `stories` mode: score each acceptance criterion for testability (can you write a Given/When/Then test?). For `scope` mode: incorporate the architect feasibility findings. Use the scoring rubric: 90-100 = strong evidence, 70-89 = include with [NEEDS VALIDATION], 50-69 = appendix only, below 50 = exclude."

Provide the agent with:
- Phase 2 PM artifact (including Builder Confessions)
- Phase 3 architect feasibility report (if applicable)
- The `roadmap-critic` scoring rubric

**Filter**: Remove or flag sections scoring below 70.

### Phase 5: Output

1. Present the final artifact to the user with confidence annotations
2. Include a summary of critic findings (high-priority issues, confession analysis)
3. If architect feasibility flagged issues, present them as a separate "Technical Feasibility Notes" section
4. Save to `{output_dir}/requirements/{filename}.md` (ask user to confirm)

### Deep Pipeline Summary

| Phase | Agent | Model | Purpose |
|-------|-------|-------|---------|
| 1 | Context Gatherer | Haiku | Run CONTEXT_DISCOVERY.md, return structured context |
| 2 | PM Analyst | Sonnet | Produce artifact + Confession Block |
| 3 | Architect Feasibility | Haiku | Technical feasibility check (scope/stories only) |
| 4 | Confidence Scoring | Haiku | Score 0-100, filter below 70, confession-aware |
| 5 | Output | -- | Present with annotations, save |
