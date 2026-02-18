# PM Skill — Workflow

Detailed discovery protocol and mode workflows for the Product Manager skill.

## Context Discovery Protocol

Execute this protocol before any analysis. Earlier sources override later ones.

### Phase 1: Configuration Check

1. Read `.arkhe.yaml` from project root
2. Extract `roadmap.output_dir` (default: `arkhe/roadmap`)
3. Extract `roadmap.context_dir` (default: `.arkhe/roadmap`)
4. Extract `roadmap.status_file` (default: `docs/PROJECT-STATUS.md`)

### Phase 2: Rich Context

If `{context_dir}` exists:

1. Read `{context_dir}/project.md` — Extract:
   - Project name and description
   - Target users / personas
   - Domain constraints
   - Project phases and milestones
   - Key terminology

2. Read `{context_dir}/documents.md` — Extract:
   - Document map (key docs and their roles)
   - Where to find planning docs, specs, gap analyses

3. Read `{context_dir}/architecture.md` — Extract:
   - Tech stack
   - Module boundaries
   - Key patterns

### Phase 3: Project Identity

Read `CLAUDE.md` and `README.md` from the project root. Extract:
- Project purpose and scope
- Conventions and constraints
- Tech stack indicators
- Architecture overview

### Phase 4: Documentation Scan

Glob for planning and documentation:

```
docs/**/*.md
plan/**/*.md
specs/**/*.md
arkhe/specs/*/spec.md
```

Categorize findings:
- **Status docs**: PROJECT-STATUS.md, roadmap.md, changelog
- **Gap analyses**: gap-analysis.md, missing features
- **Specs**: spec.md files in spec directories
- **ADRs**: Architecture Decision Records
- **Research**: Technical research documents

### Phase 5: Build File Detection

Detect tech stack from build files:

| File | Stack |
|------|-------|
| `build.gradle.kts` / `build.gradle` | Java/Kotlin (Gradle) |
| `pom.xml` | Java/Kotlin (Maven) |
| `package.json` | JavaScript/TypeScript (Node) |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml` / `setup.py` | Python |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |

### Phase 6: Codebase Structure

Glob for directory structure to understand module boundaries:

```
apps/*
src/*
packages/*
libs/*
modules/*
```

For each discovered module, note its name and contents.

## Mode Workflows

### `stories <feature>`

1. Run context discovery
2. Identify personas from project context
3. Identify the target feature area in the codebase
4. Generate user stories grouped by priority:
   - **Must Have** — Core functionality
   - **Should Have** — Important but not critical
   - **Could Have** — Nice to have
5. For each story, include:
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
