# Documentation Generation Workflows

Step-by-step processes for generating different documentation types.

## Workflow 1: README Generation

### Step 1: Analyze the Project

```bash
# Gather project context
- Read package.json / pyproject.toml / Cargo.toml
- Identify main entry points
- List key dependencies
- Check for existing documentation
```

### Step 2: Identify Key Sections

| Section | Source |
|---------|--------|
| Description | Package manifest, main module docstring |
| Features | Exported functions, key capabilities |
| Installation | Package manager, dependencies |
| Quick Start | Main entry point, minimal example |
| Configuration | Config files, environment variables |
| API | Public exports, function signatures |

### Step 3: Write Each Section

**Description**: Extract from package manifest or infer from code purpose.

**Features**: List 3-7 key capabilities, use bullet points.

**Installation**:
```bash
# npm
npm install package-name

# pip
pip install package-name
```

**Quick Start**: Provide minimal working example (5-10 lines).

**Configuration**: Table format for options.

### Step 4: Validate

- [ ] Can a new developer get started in 5 minutes?
- [ ] Are all prerequisites listed?
- [ ] Do code examples work?

---

## Workflow 2: API Documentation

### Step 1: Inventory Endpoints/Functions

```
Scan for:
- REST endpoints (@app.route, router.get, etc.)
- Public functions (exported, non-underscore prefixed)
- Classes and methods
```

### Step 2: Extract Metadata

For each endpoint/function:

| Field | Source |
|-------|--------|
| Path/Name | Decorator, function name |
| Method | HTTP method or function type |
| Parameters | Function arguments, type hints |
| Returns | Return type, response schema |
| Description | Docstring, comments |

### Step 3: Generate OpenAPI Spec

```yaml
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: User list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### Step 4: Add Examples

Include request/response examples for each endpoint:

```json
// Request
GET /users?limit=10

// Response
{
  "users": [...],
  "total": 100,
  "page": 1
}
```

---

## Workflow 3: Code Documentation (Inline)

### Step 1: Identify Documentation Gaps

```bash
# Find undocumented functions
- Public functions without docstrings
- Complex logic without comments
- Non-obvious parameter purposes
```

### Step 2: Write Docstrings

**Python (Google style)**:
```python
def process_data(items: List[Item], config: Config) -> Result:
    """Process items according to configuration.

    Args:
        items: List of items to process.
        config: Processing configuration options.

    Returns:
        Result object containing processed data and metadata.

    Raises:
        ValidationError: If items contain invalid data.
    """
```

**TypeScript (TSDoc)**:
```typescript
/**
 * Process items according to configuration.
 *
 * @param items - List of items to process
 * @param config - Processing configuration options
 * @returns Result object containing processed data
 * @throws ValidationError if items contain invalid data
 */
```

### Step 3: Add Inline Comments

For complex logic only:
```python
# Use binary search for O(log n) lookup in sorted data
index = bisect.bisect_left(sorted_items, target)
```

---

## Workflow 4: Architecture Documentation

### When to Use docs-architect Agent

For comprehensive architecture docs, delegate to the agent:

```
Use the docs-architect agent to create architecture documentation for [system]
```

### Quick Architecture Overview (DIY)

For simpler overviews:

#### Step 1: Identify Components

```
- Services / Modules
- Data stores
- External integrations
- Communication patterns
```

#### Step 2: Create Component Diagram

```mermaid
graph TB
    subgraph Frontend
        UI[React App]
    end
    subgraph Backend
        API[API Gateway]
        Auth[Auth Service]
        Core[Core Service]
    end
    subgraph Data
        DB[(PostgreSQL)]
        Cache[(Redis)]
    end
    UI --> API
    API --> Auth
    API --> Core
    Core --> DB
    Core --> Cache
```

#### Step 3: Document Each Component

| Component | Purpose | Tech Stack | Dependencies |
|-----------|---------|------------|--------------|
| API Gateway | Request routing | Express.js | Auth, Core |
| Auth Service | Authentication | Passport.js | DB |
| Core Service | Business logic | Node.js | DB, Cache |

---

## Workflow 5: Configuration Documentation

### Step 1: Scan Configuration Sources

```
- Environment variables
- Config files (.env, config.yaml, etc.)
- Command-line arguments
- Default values in code
```

### Step 2: Create Configuration Table

| Variable | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| `DATABASE_URL` | string | - | Yes | PostgreSQL connection string |
| `REDIS_URL` | string | `localhost:6379` | No | Redis connection string |
| `LOG_LEVEL` | enum | `info` | No | Logging level (debug, info, warn, error) |

### Step 3: Add Validation Rules

```yaml
# Example validation
DATABASE_URL:
  format: postgresql://user:pass@host:port/db
  required: true
  sensitive: true

LOG_LEVEL:
  allowed_values: [debug, info, warn, error]
  default: info
```

---

## Workflow 6: CI/CD Documentation Setup

### GitHub Actions Workflow

```yaml
name: Generate Documentation

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'api/**'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate API docs
        run: |
          npm run generate:docs

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

## Quality Validation Checklist

### Before Delivering Documentation

- [ ] **Accuracy**: Code examples tested and working
- [ ] **Completeness**: All public APIs documented
- [ ] **Clarity**: No jargon without explanation
- [ ] **Currency**: Matches current code version
- [ ] **Examples**: Practical, copy-paste ready
- [ ] **Navigation**: Clear structure, linked sections

### Common Issues to Avoid

| Issue | Solution |
|-------|----------|
| Outdated examples | Run examples before including |
| Missing edge cases | Document error conditions |
| Jargon overload | Define terms on first use |
| Wall of text | Use tables, lists, code blocks |
| No quick start | Add 5-minute getting started |
