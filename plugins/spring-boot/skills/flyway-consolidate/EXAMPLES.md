# Flyway Migration Consolidation Examples

Complete before/after examples demonstrating consolidation patterns.

---

## Example 1: Simple Table Evolution

A single table modified across 6 migrations.

### Before: 6 Migrations

**V1__create_users.sql**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL
);
```

**V5__add_email_to_users.sql**
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(100);
```

**V12__make_email_required.sql**
```sql
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);
```

**V18__add_timestamps.sql**
```sql
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
```

**V30__increase_email_length.sql**
```sql
ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(255);
```

**V35__add_password.sql**
```sql
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL;
ALTER TABLE users ADD CONSTRAINT uk_users_username UNIQUE (username);
```

### After: 1 Consolidated Migration

**V1__user_management.sql**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_email UNIQUE (email)
);
```

**Result**: 6 migrations → 1, all ALTER TABLE eliminated, schema identical.

---

## Example 2: Multi-Domain Consolidation

12 tables across 25 migrations consolidated into 5 domain-based files.

### Before: Migration Summary

| Migration | Operation | Tables |
|-----------|-----------|--------|
| V1 | CREATE TABLE | users, roles |
| V2 | CREATE TABLE | categories |
| V3 | CREATE TABLE | products |
| V4 | INSERT INTO | roles (ADMIN, USER) |
| V5 | CREATE TABLE | user_roles (join) |
| V6 | ALTER TABLE | users ADD email |
| V7 | CREATE TABLE | orders |
| V8 | CREATE TABLE | order_lines |
| V9 | ALTER TABLE | products ADD category_id + FK |
| V10 | ALTER TABLE | users ALTER email NOT NULL |
| V11 | CREATE TABLE | addresses |
| V12 | ALTER TABLE | orders ADD address_id + FK |
| V13 | CREATE INDEX | idx_products_category |
| V14 | ALTER TABLE | products ADD price CHECK > 0 |
| V15 | CREATE TABLE | order_status_history |
| V16 | INSERT INTO | roles (MODERATOR) |
| V17 | ALTER TABLE | users ADD created_at, updated_at |
| V18 | ALTER TABLE | orders ADD total_amount |
| V19 | CREATE TABLE | product_images |
| V20 | ALTER TABLE | order_lines ADD unit_price |
| V21 | CREATE INDEX | idx_orders_user |
| V22 | ALTER TABLE | addresses ADD is_default |
| V23 | ALTER TABLE | products ADD stock_quantity |
| V24 | CREATE TABLE | reviews |
| V25 | CREATE INDEX | idx_reviews_product |

### Domain Analysis

| Domain | Tables | Source Migrations |
|--------|--------|-------------------|
| User Management | users, roles, user_roles, addresses | V1, V5, V6, V10, V11, V17, V22 |
| Catalog | categories, products, product_images, reviews | V2, V3, V9, V13, V14, V19, V23, V24, V25 |
| Order Management | orders, order_lines, order_status_history | V7, V8, V12, V15, V18, V20, V21 |
| Reference Data | (seed data) | V4, V16 |

### After: 5 Consolidated Migrations

**V1__user_management.sql**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_email UNIQUE (email)
);

CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT uk_roles_name UNIQUE (name)
);

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    street VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_addresses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**V2__catalog.sql**
```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    category_id BIGINT,
    CONSTRAINT chk_products_price CHECK (price > 0),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE product_images (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    url VARCHAR(512) NOT NULL,
    CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    rating INT NOT NULL,
    comment TEXT,
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
```

**V3__order_management.sql**
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    address_id BIGINT,
    total_amount DECIMAL(12,2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_orders_address FOREIGN KEY (address_id) REFERENCES addresses(id)
);

CREATE TABLE order_lines (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_lines_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_lines_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE order_status_history (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_order_status_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_orders_user ON orders(user_id);
```

**V4__reference_data.sql**
```sql
INSERT INTO roles (name) VALUES
    ('ADMIN'),
    ('USER'),
    ('MODERATOR')
ON CONFLICT (name) DO NOTHING;
```

**Result**: 25 migrations → 4 files, domain-grouped, all ALTER TABLE eliminated.

---

## Example 3: Complex FK Dependencies

Tables with cross-domain foreign keys requiring careful ordering.

### Before

```sql
-- V1: Users table
CREATE TABLE users (id BIGSERIAL PRIMARY KEY, name VARCHAR(255));

-- V4: Organizations table
CREATE TABLE organizations (id BIGSERIAL PRIMARY KEY, name VARCHAR(255));

-- V8: Users belong to organizations (FK added later)
ALTER TABLE users ADD COLUMN org_id BIGINT;
ALTER TABLE users ADD CONSTRAINT fk_users_org
    FOREIGN KEY (org_id) REFERENCES organizations(id);

-- V15: Projects reference both
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    org_id BIGINT NOT NULL,
    owner_id BIGINT NOT NULL
);

-- V16: Add FKs to projects
ALTER TABLE projects ADD CONSTRAINT fk_projects_org
    FOREIGN KEY (org_id) REFERENCES organizations(id);
ALTER TABLE projects ADD CONSTRAINT fk_projects_owner
    FOREIGN KEY (owner_id) REFERENCES users(id);
```

### After: Dependency-Ordered Consolidation

```sql
-- V1__organizations.sql (no dependencies)
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- V2__users.sql (depends on organizations)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    org_id BIGINT,
    CONSTRAINT fk_users_org FOREIGN KEY (org_id) REFERENCES organizations(id)
);

-- V3__projects.sql (depends on both)
CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,
    org_id BIGINT NOT NULL,
    owner_id BIGINT NOT NULL,
    CONSTRAINT fk_projects_org FOREIGN KEY (org_id) REFERENCES organizations(id),
    CONSTRAINT fk_projects_owner FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

**Key**: Migration order follows FK dependency chain: organizations → users → projects.

---

## Example 4: Seed Data Made Idempotent

### Before: Non-Idempotent Seed Data

```sql
-- V10__add_countries.sql
INSERT INTO countries (code, name) VALUES ('US', 'United States');
INSERT INTO countries (code, name) VALUES ('CA', 'Canada');
INSERT INTO countries (code, name) VALUES ('UK', 'United Kingdom');

-- V20__add_more_countries.sql
INSERT INTO countries (code, name) VALUES ('DE', 'Germany');
INSERT INTO countries (code, name) VALUES ('FR', 'France');

-- V28__fix_country_name.sql
UPDATE countries SET name = 'United Kingdom of Great Britain' WHERE code = 'UK';
```

### After: Idempotent Consolidated Seed Data

**V1__reference_tables.sql** (schema)
```sql
CREATE TABLE countries (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

**V5__reference_data.sql** (seed data)
```sql
INSERT INTO countries (code, name) VALUES
    ('US', 'United States'),
    ('CA', 'Canada'),
    ('UK', 'United Kingdom of Great Britain'),
    ('DE', 'Germany'),
    ('FR', 'France')
ON CONFLICT (code) DO NOTHING;
```

**Notes**:
- The UK name uses the final corrected value from V28
- `ON CONFLICT (code) DO NOTHING` makes this safe to run repeatedly
- Schema and data are in separate migrations
