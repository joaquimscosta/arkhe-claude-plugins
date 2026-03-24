# Architect Skill — Workflow

Detailed pattern analysis and mode workflows for the System Architect skill.

## Context Discovery Protocol

Run the shared context discovery protocol in [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md). Then perform architecture-specific scans from [TECH_STACK_DETECTION.md](../../references/TECH_STACK_DETECTION.md) § Architecture-Specific Scanning.

## Mode Workflows

### `module <name>`

1. Run context discovery
2. Glob all source files in the target module:
   - `**/name/**/*.{kt,java,ts,tsx,py,go,rs}` (adapt to detected stack)
3. Read key files:
   - Entry points (controllers, handlers, routes)
   - Domain model (entities, models, types)
   - Service layer (business logic)
   - Repository/data access
   - Tests
4. Produce module analysis:
   - Directory structure tree
   - Domain model table (entities, value objects, events)
   - API surface (endpoints with methods)
   - Dependencies (imports from other modules)
   - Maturity assessment using shared scale
   - Specific recommendations

### `api <feature>`

1. Run context discovery
2. Find existing API patterns:
   - Grep for controller/handler/route definitions
   - Identify URL structure, versioning, auth patterns
   - Check request/response DTO patterns
   - Look for validation approach
   - Find error handling patterns
3. Analyze the target feature area
4. Produce API design guidance:
   - Endpoint table (method, path, request, response)
   - Auth requirements
   - Pagination approach (if list endpoints)
   - Error response format
   - How it fits with existing patterns

### `data-model <feature>`

1. Run context discovery
2. Find existing data patterns:
   - Read migration files or schema definitions
   - Identify entity/model base classes
   - Check naming conventions (snake_case, camelCase)
   - Find relationship patterns (FK, embedded, JSONB)
   - Look for audit fields (created_at, updated_at)
3. Analyze the target feature
4. Produce data model guidance:
   - Table/collection structure
   - Column types and constraints
   - Relationships
   - Indexes for expected queries
   - Migration strategy
   - Consistency with existing models

### `boundaries`

1. Run context discovery
2. Map all modules and their public interfaces
3. Analyze coupling:
   - Direct imports between modules
   - Shared types/entities
   - Database-level coupling (shared tables)
   - Event-based communication
4. Identify violations:
   - Controllers importing from other modules' internals
   - Shared mutable state
   - Circular dependencies
5. Produce boundary analysis:
   - Dependency graph (text or Mermaid)
   - Violations list with file paths
   - Coupling score per module pair
   - Recommendations

### `patterns`

1. Run context discovery
2. Sample files across modules:
   - 2-3 controllers/handlers
   - 2-3 services
   - 2-3 repositories/data access
   - 2-3 entity/model definitions
   - 2-3 test files
3. Extract patterns:
   - Layering approach
   - DTO mapping
   - Error handling
   - Validation
   - Testing strategy
4. Produce pattern catalog with examples from actual code

### `decisions`

1. Run context discovery
2. Find all ADRs:
   - Glob `docs/adr/**/*.md`, `docs/decisions/**/*.md`, `plan/decisions/**/*.md`
3. For each decision:
   - Extract the decision and its rationale
   - Search codebase for implementation evidence
   - Classify: Implemented / Partially Implemented / Not Implemented / Superseded
4. Produce traceability table

### `review <module>`

1. Run full `module <name>` analysis
2. Additionally assess:
   - Code quality indicators (complexity, duplication)
   - Test coverage (ratio of test files to source files)
   - API design quality (RESTful conventions, consistency)
   - Data model quality (normalization, indexing)
   - Module isolation (boundary violations)
   - Event handling (if applicable)
3. Produce structured review:
   - Per-area assessment table
   - Prioritized recommendations (fix now / improve / nice to have)
   - Risks and trade-offs

### `frontend <feature>`

1. Run context discovery
2. Analyze existing frontend patterns:
   - Component organization (atomic, feature-based, etc.)
   - State management (Redux, Context, Zustand, signals, etc.)
   - Data fetching (hooks, loaders, RSC, etc.)
   - Styling approach (CSS modules, Tailwind, styled-components, etc.)
   - Routing structure
3. Analyze the target feature
4. Produce frontend guidance:
   - Component hierarchy (tree)
   - Data flow diagram
   - State management approach
   - Responsive considerations
   - Integration points with existing components

## Output Templates

### Module Analysis

```
## Module: {name}

### Structure
{directory tree}

### Domain Model
| Type | Name | Fields | Notes |
|------|------|--------|-------|

### API Surface
| Method | Path | Auth | Notes |
|--------|------|------|-------|

### Dependencies
- Depends on: {modules}
- Depended by: {modules}

### Maturity: {level}
{justification}

### Recommendations
1. {prioritized recommendations}
```

### Boundary Analysis

```
## Module Boundary Analysis

### Dependency Graph
{Mermaid diagram or text representation}

### Violations
| Source | Target | Type | File | Recommendation |
|--------|--------|------|------|----------------|

### Module Coupling
| Module A | Module B | Coupling Type | Strength |
|----------|----------|---------------|----------|
```

---

## Deep Pipeline (`--deep`)

When `$ARGUMENTS` contains `--deep`, execute this multi-agent pipeline with Adversarial Review. A red team agent actively tries to break the proposed architecture.

### Phase 1: Context Gathering (Haiku Agent)

Launch a **Haiku agent** to run the full context discovery protocol plus architecture-specific scanning:

**Agent prompt**: "Run the context discovery protocol from CONTEXT_DISCOVERY.md, then perform architecture-specific scans from TECH_STACK_DETECTION.md. Return: project name, tech stack, detected architecture pattern, module inventory with dependencies, established patterns (layering, DTOs, events), ADR inventory, and key architectural constraints."

Provide the agent with [CONTEXT_DISCOVERY.md](../../references/CONTEXT_DISCOVERY.md) and [TECH_STACK_DETECTION.md](../../references/TECH_STACK_DETECTION.md).

### Phase 2: Architecture Analysis (Sonnet Agent)

Launch a **Sonnet agent** to produce the architecture artifact for the requested mode.

**Agent prompt**: "You are a systems architect. Using the context from Phase 1, produce a {mode} artifact for {target}. Use templates from TEMPLATES.md. Every design must extend existing patterns, not introduce new ones. After your analysis, append a Builder Confessions block."

Provide the agent with:
- Phase 1 context summary
- The content of [TEMPLATES.md](../../references/TEMPLATES.md) (System Architect section)
- The architect lane rules from [LANE_DISCIPLINE.md](../../references/LANE_DISCIPLINE.md)

**Builder Confessions block** (required at end of output):

```markdown
## Builder Confessions
- **Assumption**: {what was assumed without verification}
- **Uncertainty**: {areas where confidence is low}
- **Shortcut**: {where a deeper analysis was skipped}
- **Missing data**: {what couldn't be found in the codebase}
```

### Phase 3: Red Team Adversary (Sonnet Agent)

Launch a **Sonnet agent** to adversarially review the architecture proposal.

**Agent prompt**: "You are a penetration tester and chaos engineer. Your job is to BREAK this architecture. You are rewarded for finding problems, not for approving. Attack the proposed design across these vectors:

1. **Scaling bottlenecks**: What breaks at 10x, 100x traffic?
2. **Single points of failure**: What happens when component X goes down?
3. **Boundary violations**: Does this design violate existing module boundaries?
4. **Data integrity risks**: Can data be corrupted, lost, or inconsistent?
5. **Security gaps**: Auth bypass, injection, data exposure?
6. **Missing error handling**: What happens on timeout, invalid input, partial failure?
7. **Migration risks**: How does this change affect existing data and code?
8. **Pattern drift**: Does this introduce patterns inconsistent with the codebase?

For each finding, provide: the attack vector, the failure scenario, the severity (Critical/High/Medium/Low), and a suggested mitigation."

Provide the agent with:
- Phase 2 architecture artifact (including Builder Confessions)
- Phase 1 context summary (especially existing patterns and module inventory)

### Phase 4: Confidence Scoring (Haiku Agent)

Launch a **Haiku agent** to score the architecture artifact informed by the red team findings:

**Agent prompt**: "Score each section of this architecture artifact 0-100. Read the Builder Confessions first and focus on confessed areas. Incorporate the Red Team findings: sections with unmitigated Critical/High findings get max score of 60. Use rubric: 90-100 = strong evidence, 70-89 = include with [NEEDS VALIDATION], 50-69 = appendix only, below 50 = exclude."

Provide the agent with:
- Phase 2 architecture artifact (including Confessions)
- Phase 3 red team findings

**Filter**: Flag sections scoring below 70.

### Phase 5: Output

1. Present the architecture artifact with confidence annotations
2. Include a **Red Team Findings** section with severity-sorted issues
3. Include a **Confession Analysis** section (confessed vs unconfessed issues)
4. For each red team finding, show: the attack vector, the failure scenario, and suggested mitigation
5. Save to `{output_dir}/architecture/{filename}.md` (ask user to confirm)

### Deep Pipeline Summary

| Phase | Agent | Model | Purpose |
|-------|-------|-------|---------|
| 1 | Context Gatherer | Haiku | Context discovery + architecture scanning |
| 2 | Architecture Analyst | Sonnet | Produce artifact + Confession Block |
| 3 | Red Team Adversary | Sonnet | Try to break the architecture |
| 4 | Confidence Scoring | Haiku | Score using confessions + adversary findings, filter below 70 |
| 5 | Output | -- | Present with red team findings + annotations, save |
