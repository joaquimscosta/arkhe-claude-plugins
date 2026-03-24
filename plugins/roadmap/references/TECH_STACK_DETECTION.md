# Tech Stack Detection

Build file detection table and tech-stack-aware scanning patterns.

## Build File Detection

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

## Tech-Stack-Aware Module Scanning

### Java/Kotlin (Gradle/Maven)

```
apps/*/src/main/kotlin/**/*.kt OR apps/*/src/main/java/**/*.java
apps/*/src/test/**/*.kt OR apps/*/src/test/**/*.java
apps/*/src/main/resources/db/migration/*.sql
```

Count: entities, services, controllers, repositories, tests, migrations.

### JavaScript/TypeScript (Node)

```
src/components/**/*.tsx OR src/components/**/*.vue
src/pages/**/*.tsx OR src/app/**/page.tsx
src/hooks/**/*.ts
src/api/**/*.ts OR src/routes/**/*.ts
```

Count: components, pages, hooks, API routes.

### Python

```
src/**/*.py OR app/**/*.py
tests/**/*.py
migrations/**/*.py OR alembic/versions/*.py
```

Count: models, views/routes, services, tests, migrations.

### Go

```
cmd/**/*.go
internal/**/*.go OR pkg/**/*.go
*_test.go
```

Count: handlers, services, models, tests.

### Rust

```
src/**/*.rs
tests/**/*.rs
```

Count: modules, structs, traits, tests.

## Architecture-Specific Scanning (Architect Role)

When the architect role performs context discovery, these additional scans detect framework and architecture patterns.

### Framework Detection

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

### Architecture Pattern Detection

1. **Layered Architecture**: controller -> service -> repository
2. **Hexagonal/Ports & Adapters**: domain core + adapters
3. **Modular Monolith**: bounded contexts in single deployable
4. **Microservices**: multiple deployable services
5. **Event-Driven**: event publishers and consumers
6. **CQRS**: separate read/write models

Evidence to look for:
- Directory naming (`domain/`, `infrastructure/`, `application/`, `ports/`, `adapters/`)
- Import patterns (do services import from controllers? -> violation)
- Event classes/types
- Separate query/command handlers

### Database Pattern Detection

1. **ORM**: Entity classes, migration files
2. **Raw SQL**: Query files, SQL builders
3. **NoSQL**: Document models, collection access patterns
4. **Multi-tenancy**: Tenant ID columns, tenant filters
