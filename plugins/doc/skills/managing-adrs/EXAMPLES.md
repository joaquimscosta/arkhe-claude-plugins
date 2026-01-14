# ADR Examples

This document provides real-world examples of Architecture Decision Records for various scenarios.

## Example 1: Minimal ADR - Simple Decision

A straightforward decision with minimal sections.

```markdown
# ADR-0001: Use TypeScript for Frontend Development

## Status
Accepted

## Date
2026-01-10

## Context and Problem Statement
We are starting a new React application and need to decide on the primary
programming language. The team has mixed experience with JavaScript and
TypeScript.

## Decision
We will use TypeScript for all frontend development because it provides
better tooling, catches errors at compile time, and improves code
maintainability for our growing codebase.

## Consequences

**Positive:**
- Type safety catches bugs before runtime
- Better IDE support with autocomplete and refactoring
- Self-documenting code through type definitions
- Easier onboarding for new developers

**Negative:**
- Initial learning curve for developers new to TypeScript
- Slightly longer compilation times
- Additional configuration complexity
```

---

## Example 2: Full MADR - Database Selection

A complex decision using the full MADR 4.0 template.

```markdown
# ADR-0003: Use PostgreSQL for Primary Data Storage

## Status
Accepted

## Date
2026-01-10

## Decision Makers
- @jcosta (Tech Lead)
- @msilva (Backend Engineer)
- @rferreira (DBA)

## Technical Story
Relates to: #142 (Database selection for user management)

## Context and Problem Statement
Our e-commerce platform needs a primary database for storing user accounts,
orders, products, and inventory. We expect to handle 50,000 daily active
users with peaks of 5,000 concurrent connections during sales events.
The solution must support complex queries, ACID transactions, and integrate
with our existing Java/Spring Boot backend.

## Decision Drivers
- ACID compliance is mandatory for financial transactions
- Complex reporting queries across multiple tables
- Team has 8+ years of relational database experience
- Budget constraints favor open-source solutions
- Need for horizontal read scaling during peak traffic
- Must integrate with existing Spring Data JPA

## Considered Options
1. PostgreSQL with read replicas
2. MongoDB
3. Amazon Aurora PostgreSQL
4. CockroachDB

## Decision Outcome
Chosen option: "PostgreSQL with read replicas", because it provides the
best balance of ACID compliance, query flexibility, cost efficiency, and
aligns with our team's expertise.

### Consequences

**Positive:**
- Full ACID transaction support for order processing
- Excellent query optimizer handles complex reporting
- Team can be immediately productive
- Large ecosystem of tools and extensions
- Read replicas handle peak traffic
- $0 licensing cost

**Negative:**
- Manual setup for read replica failover
- Schema migrations require careful planning with downtime
- Write scaling limited to vertical (larger instances)

## Pros and Cons of the Options

### PostgreSQL with read replicas

PostgreSQL 16 with AWS RDS, using read replicas for scaling.

- Good, because ACID compliant with full transaction support
- Good, because team has deep expertise (8+ years)
- Good, because excellent query optimizer for complex JOINs
- Good, because open-source with no licensing costs
- Good, because mature Spring Data JPA integration
- Neutral, because requires manual replica configuration
- Bad, because write scaling requires vertical growth
- Bad, because migrations may need maintenance windows

### MongoDB

Document database with flexible schema.

- Good, because horizontal scaling is built-in
- Good, because flexible schema for evolving requirements
- Bad, because no multi-document ACID transactions (until recent versions)
- Bad, because team lacks experience (< 1 year)
- Bad, because complex JOINs require aggregation pipeline
- Bad, because Spring Data MongoDB has different patterns

### Amazon Aurora PostgreSQL

AWS managed PostgreSQL-compatible database.

- Good, because PostgreSQL compatible (easy migration)
- Good, because automatic failover and scaling
- Good, because managed service reduces ops burden
- Bad, because significantly higher cost (~3x RDS PostgreSQL)
- Bad, because vendor lock-in to AWS
- Neutral, because learning curve for Aurora-specific features

### CockroachDB

Distributed SQL database with PostgreSQL compatibility.

- Good, because horizontally scalable writes
- Good, because PostgreSQL wire protocol compatible
- Good, because automatic sharding and rebalancing
- Bad, because team has no experience
- Bad, because subtle SQL compatibility differences
- Bad, because higher resource requirements
- Bad, because less mature ecosystem

## More Information

- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- Internal: Database benchmarks in `/docs/benchmarks/db-comparison.md`
- Supersedes: None (initial decision)
```

---

## Example 3: Framework Migration - Supersession

An ADR that supersedes a previous decision.

```markdown
# ADR-0012: Migrate from Redux to React Query for Server State

## Status
Accepted

Supersedes: [ADR-0004](0004-use-redux-for-state-management.md)

## Date
2026-01-10

## Decision Makers
- @jcosta (Tech Lead)
- @asousa (Frontend Lead)

## Context and Problem Statement
Our Redux store has grown to manage both UI state and server state,
leading to complex action creators, excessive boilerplate, and cache
invalidation challenges. Server state (data fetched from APIs) has
different requirements than UI state (form inputs, modal visibility).
We need a cleaner separation of concerns.

## Decision Drivers
- Reduce boilerplate for data fetching (currently 100+ lines per endpoint)
- Improve cache management and automatic refetching
- Simplify error and loading state handling
- Keep Redux for true UI state (modals, forms, preferences)

## Considered Options
1. React Query for server state + Redux for UI state
2. SWR for server state + Redux for UI state
3. RTK Query (Redux Toolkit Query)
4. Continue with current Redux setup

## Decision Outcome
Chosen option: "React Query for server state + Redux for UI state",
because it provides the best developer experience for data fetching
while maintaining Redux for genuinely global UI state.

### Consequences

**Positive:**
- 70% reduction in data-fetching boilerplate
- Automatic background refetching and cache invalidation
- Built-in loading, error, and stale states
- DevTools for debugging queries
- Clearer separation: React Query = server, Redux = UI

**Negative:**
- Two state management patterns to understand
- Migration effort across 45+ components
- Some edge cases need custom query functions

## More Information

- Migration guide: `/docs/migrations/redux-to-react-query.md`
- Related: [ADR-0004](0004-use-redux-for-state-management.md) (superseded)
```

---

## Example 4: API Versioning with Confirmation

An ADR including the Confirmation section for validation.

```markdown
# ADR-0008: Use URL Path Versioning for REST API

## Status
Accepted

## Date
2026-01-10

## Decision Makers
- @jcosta (Tech Lead)
- @backend-team

## Context and Problem Statement
Our public REST API needs versioning to allow breaking changes while
maintaining backward compatibility for existing clients. Mobile apps
in particular cannot be forced to update immediately.

## Decision Drivers
- Clear version identification for debugging
- Easy to implement in API gateway and routing
- Cacheable by CDN (unlike header-based versioning)
- Simple for developers to understand and use

## Considered Options
1. URL path versioning (`/api/v1/users`)
2. Query parameter versioning (`/api/users?version=1`)
3. Header versioning (`Accept: application/vnd.api+json;version=1`)
4. Content negotiation (`Accept: application/vnd.api.v1+json`)

## Decision Outcome
Chosen option: "URL path versioning", because it provides the clearest
developer experience, works naturally with REST principles, and is
easily cacheable.

### Consequences

**Positive:**
- Version immediately visible in URL
- Works with all HTTP clients without modification
- CDN-friendly for caching
- Easy to route in API gateway

**Negative:**
- Slightly longer URLs
- Risk of "version explosion" if not managed

## Confirmation

To verify this decision is correctly implemented:

1. **URL Structure**: All API endpoints follow `/api/v{N}/resource` pattern
2. **Version Header**: Response includes `X-API-Version: 1` header
3. **Documentation**: OpenAPI spec includes version in base path
4. **Deprecation**: Old versions return `Deprecation` header when sunset planned
5. **Gateway Config**: Kong/Nginx routes correctly to versioned backends

## More Information

- API Design Guidelines: `/docs/api-guidelines.md`
- OpenAPI Spec: `/api/openapi.yaml`
```

---

## Example 5: Authentication Strategy

A security-focused ADR.

```markdown
# ADR-0006: Use Supabase Auth with ES256 JWT Algorithm

## Status
Accepted

## Date
2026-01-10

## Decision Makers
- @jcosta (Tech Lead)
- @security-team

## Technical Story
Relates to: #89 (User authentication implementation)

## Context and Problem Statement
We need authentication for our web and mobile applications. The solution
must support email/password, social login (Google, GitHub), and provide
JWT tokens for API authorization. We want to avoid building auth from
scratch due to security complexity.

## Decision Drivers
- Security: Must follow current best practices
- Time-to-market: Need auth working within 2 weeks
- Cost: Budget-conscious, prefer pay-as-you-scale
- Integration: Must work with Spring Boot backend
- Mobile: Support for React Native apps

## Considered Options
1. Supabase Auth
2. Auth0
3. Firebase Authentication
4. Custom implementation with Spring Security

## Decision Outcome
Chosen option: "Supabase Auth", because it provides a complete
authentication solution with generous free tier, excellent developer
experience, and integrates well with our PostgreSQL database.

### Consequences

**Positive:**
- Complete auth solution in days, not weeks
- Built-in email templates and magic links
- Row-level security integrates with PostgreSQL
- Generous free tier (50,000 MAU)
- ES256 (asymmetric) algorithm for JWT signing

**Negative:**
- Vendor dependency for critical feature
- Limited customization compared to custom solution
- Must use Supabase's JWT structure

## More Information

- Supabase Auth Docs: https://supabase.com/docs/guides/auth
- JWT Configuration: See [ADR-0007](0007-es256-jwt-algorithm.md)
- Security Review: `/docs/security/auth-review.md`
```

---

## Example 6: Monorepo Tooling

A build/tooling decision.

```markdown
# ADR-0002: Use Nx for Monorepo Build Orchestration

## Status
Accepted

## Date
2025-12-26

## Context and Problem Statement
Our project contains a Next.js frontend and Spring Boot backend in the
same repository. We need unified build orchestration to run tasks across
both, enable caching, and support affected-only builds in CI.

## Decision Drivers
- Need single command to build/test both frontend and backend
- Polyglot support (TypeScript + Kotlin/Java)
- Intelligent caching for faster CI
- Affected commands for PR builds

## Considered Options
1. Nx
2. Turborepo
3. No monorepo tool (manual scripts)

## Decision Outcome
Chosen option: "Nx", because it's the only tool that supports both
JavaScript/TypeScript AND JVM projects through its plugin architecture.

### Consequences

**Positive:**
- Unified CLI: `nx run-many -t build` for both
- Cross-language dependency graph
- Task caching reduces CI time by 60%
- Affected commands for faster PR builds

**Negative:**
- Additional configuration files
- Learning curve for team
- Node.js required for all builds

## More Information

- Nx Gradle Plugin: https://nx.dev/nx-api/gradle
- Configuration: See `nx.json` and `project.json` files
```

---

## Quick Reference: Section Purposes

| Section | Purpose | Required? |
|---------|---------|-----------|
| Status | Current state of decision | Yes |
| Date | When decision was made | Yes |
| Decision Makers | Who made the decision | No |
| Technical Story | Link to issue/spec | No |
| Context | Background and situation | Yes |
| Decision Drivers | Forces influencing choice | No |
| Considered Options | Alternatives evaluated | No |
| Decision Outcome | What was decided and why | Yes |
| Consequences | Trade-offs (positive/negative) | Yes |
| Pros and Cons | Detailed option analysis | No |
| Confirmation | How to verify implementation | No |
| More Information | Links and references | No |

---

## Related Resources

- [SKILL.md](SKILL.md) - Quick reference
- [WORKFLOW.md](WORKFLOW.md) - Detailed methodology
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error handling
