# Architect Skill — Workflow

Detailed pattern analysis and mode workflows for the System Architect skill.

## Context Discovery Protocol

Same priority-based discovery as PM and Roadmap skills. Architecture-specific additions:

### Architecture-Specific Discovery

After standard discovery, perform these additional scans:

#### Detect Framework Patterns

**Spring Boot / Spring Modulith:**
- Grep for `@SpringBootApplication`, `@ApplicationModule`, `@RestController`
- Scan for `application.yaml` / `application.properties`
- Check for Flyway/Liquibase migrations

**Next.js / React:**
- Check for `next.config.js`, `app/` directory (App Router), `pages/` (Pages Router)
- Scan for component patterns, hooks, context providers

**Django / Flask / FastAPI:**
- Check for `settings.py`, `urls.py` (Django) or app factory patterns (Flask/FastAPI)
- Scan for models, views/routes, serializers

**Go (standard library / Gin / Echo):**
- Check for `main.go`, `cmd/` pattern
- Scan for handler, service, repository patterns

**Rust (Actix / Axum):**
- Check for `Cargo.toml` workspace structure
- Scan for module hierarchy, trait patterns

#### Detect Architecture Patterns

1. **Layered Architecture**: controller → service → repository
2. **Hexagonal/Ports & Adapters**: domain core + adapters
3. **Modular Monolith**: bounded contexts in single deployable
4. **Microservices**: multiple deployable services
5. **Event-Driven**: event publishers and consumers
6. **CQRS**: separate read/write models

Evidence to look for:
- Directory naming (`domain/`, `infrastructure/`, `application/`, `ports/`, `adapters/`)
- Import patterns (do services import from controllers? → violation)
- Event classes/types
- Separate query/command handlers

#### Detect Database Patterns

1. **ORM**: Entity classes, migration files
2. **Raw SQL**: Query files, SQL builders
3. **NoSQL**: Document models, collection access patterns
4. **Multi-tenancy**: Tenant ID columns, tenant filters

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
