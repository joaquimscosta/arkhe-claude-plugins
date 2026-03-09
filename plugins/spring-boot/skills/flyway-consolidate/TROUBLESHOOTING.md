# Flyway Consolidation Troubleshooting

Common issues when using the flyway-consolidate skill.

---

## Migration Discovery Issues

### No migrations found

**Symptoms**: Glob returns empty results.

**Cause**: Migration files are not in the expected location or don't follow Flyway naming conventions.

**Fix**:
- Verify migration directory: default is `src/main/resources/db/migration/`
- Check file naming: must match `V*__*.sql` (versioned) or `R*__*.sql` (repeatable)
- Custom migration locations are configured in `application.yml` under `spring.flyway.locations`

### Repeatable migrations (R__) not included

**Cause**: The skill focuses on versioned migrations (`V*__*.sql`) for consolidation.

**Fix**: Repeatable migrations are typically kept as-is since they're idempotent by design. If you need to consolidate them, mention it explicitly.

---

## Schema Analysis Issues

### Circular foreign key dependencies

**Symptoms**: Cannot determine a valid creation order for tables.

**Fix**: The skill handles circular FKs by:
1. Creating tables without the circular FK constraint
2. Adding the constraint via `ALTER TABLE` after both tables exist

If the circular dependency is not detected, flag the specific tables.

### Column type ambiguity from ALTER chains

**Symptoms**: Final column type unclear after multiple ALTER TABLE modifications.

**Cause**: A column was created, altered, and renamed across multiple migrations.

**Fix**: The skill applies migrations in version order to determine the final state. If the result looks wrong, verify by checking the actual database schema as the source of truth.

---

## Safety Issues

### Accidentally running on a production database

**Symptoms**: Consolidated migrations would destroy production migration history.

**Fix**: This skill is **pre-production only**. Never apply consolidated migrations to a database with existing Flyway history. Check:
- `flyway_schema_history` table exists → production database, do NOT consolidate
- The skill warns about this constraint in its "When to Use" section

### Seed data not idempotent

**Symptoms**: INSERT statements fail on re-run with duplicate key errors.

**Fix**: The skill generates idempotent seed data using `ON CONFLICT DO NOTHING` (PostgreSQL) or equivalent. If using MySQL, ensure `INSERT IGNORE` or `REPLACE INTO` is used.

---

## Output Issues

### Domain grouping seems wrong

**Symptoms**: Tables assigned to unexpected domains.

**Fix**: Domain grouping uses heuristics (table prefixes, FK clusters). The skill presents groupings for confirmation before generating SQL. Reassign tables when prompted.

### Generated SQL missing constraints

**Cause**: Some constraints (CHECK, UNIQUE) may be lost if they were added via ALTER TABLE and the migration was ambiguous.

**Fix**: Compare the generated schema against the original by running both sets of migrations against an empty database. Report any discrepancies.
