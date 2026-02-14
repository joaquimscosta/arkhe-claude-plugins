# Flyway Migration Consolidation Workflow

Step-by-step process for analyzing and consolidating Flyway migrations.

---

## Step 1: Discover Migration Files

Find all Flyway migration files in the project:

```
Glob: **/db/migration/V*__*.sql
Glob: **/resources/db/migration/V*__*.sql
Glob: **/db/migration/R*__*.sql           # Repeatable migrations
```

For each file:
- Extract version number from filename (V1, V2, ... V40)
- Extract description from filename (e.g., `V5__add_email_to_users.sql` → "add email to users")
- Sort by version number ascending

**Output**: Ordered list of migration files with version and description.

---

## Step 2: Analyze Each Migration

Read each migration file and classify its operations:

| Operation | What to Extract |
|-----------|----------------|
| `CREATE TABLE` | Table name, all columns (name, type, constraints), table-level constraints |
| `ALTER TABLE ADD COLUMN` | Table name, new column definition |
| `ALTER TABLE DROP COLUMN` | Table name, removed column |
| `ALTER TABLE ALTER COLUMN` | Table name, column modification (type change, nullability, default) |
| `ALTER TABLE ADD CONSTRAINT` | Constraint name, type (PK, FK, UNIQUE, CHECK), definition |
| `ALTER TABLE DROP CONSTRAINT` | Constraint name |
| `CREATE INDEX` | Index name, table, columns, uniqueness |
| `DROP INDEX` | Index name |
| `INSERT INTO` | Table name, row data (seed/reference data) |
| `UPDATE` | Table name, affected data |
| `DELETE` | Table name, affected rows |
| `CREATE TYPE` / `CREATE EXTENSION` | Custom type or extension definition |

For each migration, produce a brief summary:
```
V5__add_email_to_users.sql:
  - ALTER TABLE users ADD COLUMN email VARCHAR(100)
  - Affects: users
```

---

## Step 3: Infer Final Schema

Build the final schema by replaying all migrations in order:

### Schema Tracking Model

For each table, maintain:
- **Columns**: name, data type, nullability, default value, constraints
- **Table constraints**: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
- **Indexes**: name, columns, uniqueness
- **Created in**: original migration version
- **Modified in**: list of migration versions that changed it

### Resolution Rules

| Scenario | Resolution |
|----------|-----------|
| ADD COLUMN then DROP COLUMN | Column removed from final schema |
| ADD COLUMN → DROP → ADD again | Use the final ADD version |
| ALTER COLUMN type change | Use the final type |
| ADD CONSTRAINT then DROP | Constraint removed from final schema |
| ADD CONSTRAINT → DROP → ADD | Use the final constraint definition |
| Multiple DEFAULT changes | Use the final DEFAULT value |

### Verification

After replaying all migrations, produce a **final schema inventory**:
- Total tables with full column lists
- All constraints (PK, FK, UNIQUE, CHECK) with their definitions
- All indexes
- All custom types and extensions
- All seed data (final state)

---

## Step 4: Group Tables by Domain

Organize tables into logical business domains using these heuristics (in priority order):

### 4a. Table Name Prefixes

Group tables sharing a common prefix:
```
user_*, users, user_profiles, user_addresses → "User Management"
order_*, orders, order_lines → "Order Management"
product_*, products, categories → "Catalog"
```

### 4b. Foreign Key Clusters

Tables connected by FK relationships belong together:
- `order_lines.product_id → products.id` connects orders and products
- Assign join tables to the domain of the "owning" side (e.g., `user_roles` → User Management)

### 4c. Functional Grouping

| Pattern | Domain |
|---------|--------|
| Authentication/authorization tables | Security |
| Audit/history tables (`*_audit`, `*_log`) | Same domain as parent table |
| Configuration tables (`settings`, `config`) | Infrastructure |
| Reference/lookup tables (`status_types`, `country_codes`) | Reference Data |
| Scheduling/job tables (`scheduled_tasks`, `job_history`) | Infrastructure |

### 4d. Ambiguity Resolution

When a table could belong to multiple domains:
1. Use the strongest FK relationship as primary signal
2. If still ambiguous, **present options to the user** and ask them to decide
3. Document the decision in the analysis report

**Output**: Domain-to-tables mapping.

---

## Step 5: Resolve Dependencies

Determine migration creation order using foreign key dependencies.

### Topological Sort

1. Build a directed graph: edge from table A to table B if B has a FK referencing A
2. Topological sort produces creation order (referenced tables first)

### Special Cases

**Self-referential FKs** (e.g., `employees.manager_id → employees.id`):
```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manager_id BIGINT
);
ALTER TABLE employees ADD CONSTRAINT fk_employees_manager
    FOREIGN KEY (manager_id) REFERENCES employees(id);
```

**Circular cross-table FKs** (e.g., A references B, B references A):
```sql
-- Create both tables without the circular FK
CREATE TABLE table_a (id BIGSERIAL PRIMARY KEY, b_id BIGINT);
CREATE TABLE table_b (id BIGSERIAL PRIMARY KEY, a_id BIGINT);
-- Add FKs after both tables exist
ALTER TABLE table_a ADD CONSTRAINT fk_a_b FOREIGN KEY (b_id) REFERENCES table_b(id);
ALTER TABLE table_b ADD CONSTRAINT fk_b_a FOREIGN KEY (a_id) REFERENCES table_a(id);
```

**Cross-domain FKs** (e.g., `orders.customer_id → users.id`):
- The domain containing the referenced table must have a lower migration version
- Example: V2__user_management.sql before V4__order_management.sql

---

## Step 6: Generate Consolidated Migrations

### Migration Naming Convention

```
V1__infrastructure.sql
V2__user_management.sql
V3__catalog.sql
V4__order_management.sql
V5__reference_data.sql
V6__performance_indexes.sql
```

Adjust domain names and count based on the actual schema.

### SQL Generation Rules

**CREATE TABLE statements**:
- Use final column definitions (all ALTER TABLE changes applied)
- Include inline column constraints (NOT NULL, DEFAULT, CHECK where single-column)
- Add table-level constraints (PK, FK, UNIQUE, multi-column CHECK)
- Use explicit constraint names: `pk_{table}`, `fk_{table}_{column}`, `uk_{table}_{column}`, `chk_{table}_{description}`

**Foreign keys**:
- Include ON DELETE / ON UPDATE clauses (use final version)
- Place as table-level constraints, not inline
- Order tables so referenced tables appear first in the file

**Indexes**:
- Place at the end of the domain migration or in a separate V*__indexes.sql
- Use explicit names: `idx_{table}_{column}`
- Include unique indexes that aren't already covered by UNIQUE constraints

**Seed data**:
- Separate migration file (e.g., V5__reference_data.sql)
- Use ON CONFLICT DO NOTHING for idempotency
- Requires a UNIQUE constraint on the conflict target column(s)
- Preserve data values exactly as in the final state

**Custom types / extensions**:
- Place in V1__infrastructure.sql before any tables that use them
- Include `CREATE EXTENSION IF NOT EXISTS` for PostgreSQL extensions

### Example Output

```sql
-- V2__user_management.sql

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_email UNIQUE (email)
);

CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    bio TEXT,
    CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
```

---

## Step 7: Generate Analysis Report

Present this report to the user **before** generating any SQL files.

### Report Template

```markdown
## Flyway Migration Consolidation Report

### Current State
- **Total migrations**: N
- **Operations**: X CREATE TABLE, Y ALTER TABLE, Z INSERT
- **Total tables**: N
- **Domains identified**: N

### Per-Migration Summary

| Migration | Operations | Tables Affected |
|-----------|-----------|-----------------|
| V1__initial_schema.sql | CREATE TABLE users, orders | users, orders |
| V5__add_email.sql | ALTER TABLE users ADD COLUMN | users |
| ... | ... | ... |

### Domain Analysis

#### Domain Name (N tables)
- `table_a` — Created V1, modified V5, V12
- `table_b` — Created V3

[repeat for each domain]

### Proposed Consolidated Structure

| New Migration | Tables | Source Migrations |
|---------------|--------|-------------------|
| V1__infrastructure.sql | extensions, config | V0, V13 |
| V2__user_management.sql | users, profiles | V1, V5, V12, V18 |
| ... | ... | ... |

**Reduction**: N migrations → M migrations

### Assumptions & Ambiguities
1. [List any interpretation decisions made]
2. [List any ambiguous cases]

### Next Steps
1. Review domain groupings above
2. Confirm or adjust proposed structure
3. Request consolidated SQL generation
```

---

## Common Patterns

### Column Evolution

**Before** (5 migrations):
```sql
V1:  CREATE TABLE t (id SERIAL, name VARCHAR(50))
V5:  ALTER TABLE t ADD COLUMN email VARCHAR(100)
V12: ALTER TABLE t ALTER COLUMN email SET NOT NULL
V18: ALTER TABLE t ALTER COLUMN email TYPE VARCHAR(255)
V25: ALTER TABLE t ADD CONSTRAINT uk_t_email UNIQUE (email)
```

**After** (1 CREATE TABLE):
```sql
CREATE TABLE t (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(255) NOT NULL,
    CONSTRAINT uk_t_email UNIQUE (email)
);
```

### Constraint Evolution

**Before** (3 migrations):
```sql
V2:  CREATE TABLE products (id SERIAL, price DECIMAL(10,2))
V7:  ALTER TABLE products ADD CONSTRAINT chk_price CHECK (price >= 0)
V22: ALTER TABLE products DROP CONSTRAINT chk_price;
     ALTER TABLE products ADD CONSTRAINT chk_price_positive CHECK (price > 0)
```

**After** (1 CREATE TABLE):
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_price_positive CHECK (price > 0)
);
```

### FK Addition Over Time

**Before** (3 migrations):
```sql
V3:  CREATE TABLE profiles (id SERIAL, user_id INT)
V14: ALTER TABLE profiles ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
V20: ALTER TABLE profiles DROP CONSTRAINT fk_user;
     ALTER TABLE profiles ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

**After** (1 CREATE TABLE):
```sql
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    CONSTRAINT fk_profiles_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
```

### Seed Data Consolidation

**Before** (3 migrations):
```sql
V13: INSERT INTO roles (name) VALUES ('ADMIN'), ('USER')
V27: INSERT INTO roles (name) VALUES ('GUEST'), ('PREMIUM')
V32: DELETE FROM roles WHERE name = 'GUEST' AND id > (SELECT MIN(id) FROM roles WHERE name = 'GUEST')
```

**After** (1 idempotent migration):
```sql
INSERT INTO roles (name) VALUES
    ('ADMIN'),
    ('USER'),
    ('GUEST'),
    ('PREMIUM')
ON CONFLICT (name) DO NOTHING;
```
