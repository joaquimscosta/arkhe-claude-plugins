# Workflow: Taskfile Setup

## Decision Flow

```
USER invokes taskfile-setup
    |
    v
Run detect_taskfile.py on project root
    |
    ├── task_binary.installed = false?
    │   └── Go to "Install Task"
    |
    ├── taskfile.exists = true?
    │   └── Go to "Phase 1: Audit"
    │
    └── taskfile.exists = false?
        └── Go to "Phase 2: Scaffold"
```

---

## Install Task

Show commands based on `os` field from detector:

| OS | Command |
|----|---------|
| macOS | `brew install go-task` |
| Linux (binary) | `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin` |
| Linux (apt) | `sudo snap install task --classic` |

**Important**: On macOS, `brew install task` may install `taskwarrior` instead. Always use `brew install go-task`.

After install, verify:
```bash
task --version
```

Re-run detector to confirm installation.

---

## Phase 1: Audit

### Step 1: Present Status Table

Display detection results as a formatted table:

```
| Component       | Status     | Detail                          |
|-----------------|------------|---------------------------------|
| task binary     | installed  | v3.40.1 at /opt/homebrew/bin/task |
| Taskfile        | found      | Taskfile.yml (version: 3)       |
| Tasks           | 18 tasks   | no includes                     |
| Ecosystems      | 3 detected | node (pnpm), jvm (gradle), docker |
| dotenv          | not config | 2 .env files found              |
| Existing runners| 2 found    | package.json scripts, gradlew   |
```

### Step 2: Present Violations

Group by severity (ERROR first, then WARNING, then INFO):

```
## Audit Results

### ERRORS
| Rule | Message | Task | Line | Fix |
|------|---------|------|------|-----|
| TF001 | Missing version: '3' | — | — | Add version declaration |

### WARNINGS
| Rule | Message | Task | Line | Fix |
|------|---------|------|------|-----|
| TF002 | No preconditions | deploy | 42 | Add preconditions |
| TF005 | Missing desc | build | 12 | Add desc field |

### INFO
| Rule | Message | Task | Line | Fix |
|------|---------|------|------|-----|
| TF006 | No dotenv config | — | — | Add dotenv declaration |
```

### Step 3: Offer Fixes

Use `AskUserQuestion` (multiSelect: true) listing each violation with its fix. User selects which to apply.

### Step 4: Per-Rule Fix Strategies

**TF001 — Missing version: '3'**
Add at the top of the file:
```yaml
version: "3"
```

**TF002 — No preconditions on deploy/publish tasks**
Add preconditions block:
```yaml
tasks:
  deploy:
    desc: Deploy to production
    preconditions:
      - sh: "test -n \"$ENV\""
        msg: "ENV must be set (staging or production)"
      - sh: "git diff --quiet"
        msg: "Uncommitted changes — commit or stash first"
    cmds:
      - # existing commands
```

**TF003 — No sources/generates on build tasks**
Add sources and generates:
```yaml
tasks:
  build:
    desc: Build the application
    sources:
      - "src/**/*"
    generates:
      - "dist/**/*"
    cmds:
      - # existing commands
```

**TF004 — Too many tasks in single file**
Propose splitting into includes. Show the suggested structure:
```
Taskfile.yml              # Root with includes + global vars
taskfiles/
  api.yml                 # API/backend tasks
  web.yml                 # Frontend tasks
  docker.yml              # Docker/compose tasks
  db.yml                  # Database tasks
```

Convert the root Taskfile:
```yaml
version: "3"

includes:
  api:
    taskfile: ./taskfiles/api.yml
    dir: ./api
  web:
    taskfile: ./taskfiles/web.yml
    dir: ./web
  docker:
    taskfile: ./taskfiles/docker.yml

tasks:
  dev:
    desc: Start all services in parallel
    deps:
      - api:dev
      - web:dev
```

**TF005 — Missing desc field**
Generate a desc from the task name and commands:
```yaml
tasks:
  lint:
    desc: Run linters
    cmds:
      - # existing commands
```

**TF006 — No dotenv config when .env files exist**
Add dotenv declaration at top level:
```yaml
version: "3"

dotenv: [".env.local", ".env"]
```

**Note**: dotenv is only supported in the root Taskfile, not in included files.

**TF007 — Hard-coded absolute paths**
Replace with variables:
```yaml
# Before
tasks:
  deploy:
    cmds:
      - /usr/local/bin/kubectl apply -f /home/user/k8s/

# After
vars:
  KUBECTL: kubectl
  K8S_DIR: ./k8s

tasks:
  deploy:
    cmds:
      - "{{.KUBECTL}} apply -f {{.K8S_DIR}}/"
```

**TF008 — deps used for sequential tasks**
This is INFO-level because `deps:` may be intentionally parallel. If the user confirms they want sequential ordering:
```yaml
# Before (parallel — may cause issues if order matters)
tasks:
  ci:
    deps: [lint, test, build]

# After (sequential — guaranteed order)
tasks:
  ci:
    desc: Run CI pipeline
    cmds:
      - task: lint
      - task: test
      - task: build
```

### Step 5: Verify

Re-run detector to confirm violations are resolved.

---

## Phase 2: Scaffold

### Step 1: Choose Pattern

Use `AskUserQuestion` to present options:

**Single-file (recommended for < 15 tasks)**:
- All tasks in one `Taskfile.yml`
- Flat namespace with `:` separators (e.g., `dev:api`, `test:web`)
- Top-level `vars:` for directory paths
- Easy to discover all tasks at a glance
- Follows the Nosilha project pattern

**Multi-file (recommended for 15+ tasks or monorepos)**:
- Root `Taskfile.yml` with `includes:`
- Per-concern files in `taskfiles/` directory
- Better separation of concerns
- Avoids namespace collisions in large projects

### Step 2: Choose Task Groups

Based on detected ecosystems, offer task groups via `AskUserQuestion` (multiSelect: true). Pre-select groups matching detected ecosystems.

### Step 3: Generate Taskfile

#### Single-File Pattern (Nosilha-style)

```yaml
version: "3"

vars:
  API_DIR: apps/api      # Adjust based on detected project structure
  WEB_DIR: apps/web

tasks:
  check:
    desc: Check prerequisites — detect missing tools
    silent: true
    cmds:
      - |
        missing=0
        check_tool() {
          if command -v "$1" &> /dev/null; then
            printf "  OK  %s\n" "$1"
          else
            printf "  MISSING  %s — install with: %s\n" "$1" "$2"
            missing=$((missing + 1))
          fi
        }
        echo "Checking prerequisites..."
        # Add check_tool calls per detected ecosystem
        if [ "$missing" -gt 0 ]; then
          echo "$missing tool(s) missing."
          exit 1
        else
          echo "All prerequisites installed."
        fi

  setup:
    desc: Full project setup
    cmds:
      - task: setup:deps
      # Add per-ecosystem setup subtasks

  setup:deps:
    desc: Install project dependencies
    cmds:
      - # Per-ecosystem install commands

  dev:
    desc: Start development servers
    deps:
      # Per-ecosystem dev tasks run in parallel

  test:
    desc: Run all tests
    cmds:
      # Per-ecosystem test tasks run sequentially

  lint:
    desc: Run all linters
    cmds:
      # Per-ecosystem lint tasks run sequentially

  clean:
    desc: Clean build artifacts
    cmds:
      # Per-ecosystem clean tasks
```

#### Multi-File Pattern

**Root Taskfile.yml:**
```yaml
version: "3"

includes:
  api:
    taskfile: ./taskfiles/api.yml
    dir: ./apps/api
  web:
    taskfile: ./taskfiles/web.yml
    dir: ./apps/web
  docker:
    taskfile: ./taskfiles/docker.yml

tasks:
  check:
    desc: Check prerequisites
    cmds:
      - task: api:check
      - task: web:check

  setup:
    desc: Full project setup
    cmds:
      - task: api:setup
      - task: web:setup

  dev:
    desc: Start all services in parallel
    deps:
      - api:dev
      - web:dev

  test:
    desc: Run all tests
    cmds:
      - task: api:test
      - task: web:test

  lint:
    desc: Run all linters
    cmds:
      - task: api:lint
      - task: web:lint

  clean:
    desc: Clean all build artifacts
    cmds:
      - task: api:clean
      - task: web:clean
```

---

## Ecosystem Templates

### Node.js / pnpm

```yaml
# For single-file, prefix with namespace (e.g., dev:web, test:web)
# For multi-file, these are standalone tasks in taskfiles/web.yml

tasks:
  dev:
    desc: Start dev server
    cmds:
      - pnpm dev

  build:
    desc: Build for production
    cmds:
      - pnpm build

  test:
    desc: Run tests
    cmds:
      - pnpm test

  lint:
    desc: Run ESLint
    cmds:
      - pnpm lint

  format:
    desc: Format code with Prettier
    cmds:
      - pnpm prettier --write .

  check:
    desc: Type-check with TypeScript
    cmds:
      - npx tsc --noEmit
```

Adjust commands for detected package manager (yarn, npm).

### JVM / Gradle

```yaml
tasks:
  build:
    desc: Build the project
    cmds:
      - ./gradlew build

  test:
    desc: Run tests
    cmds:
      - ./gradlew test

  lint:
    desc: Run linter checks
    cmds:
      - ./gradlew ktlintCheck    # Kotlin
      # or: ./gradlew checkstyleMain  # Java

  check:
    desc: Run all checks
    cmds:
      - ./gradlew check

  run:
    desc: Run the application
    cmds:
      - ./gradlew bootRun        # Spring Boot
      # or: ./gradlew run        # Plain application

  clean:
    desc: Clean build artifacts
    cmds:
      - ./gradlew clean
```

For Maven, replace `./gradlew` with `./mvnw` (or `mvn`).

### Python / uv

```yaml
tasks:
  setup:
    desc: Install dependencies
    run: once
    cmds:
      - uv sync --all-extras --dev

  dev:
    desc: Run development server
    deps: [setup]
    cmds:
      - uv run python -m app

  test:
    desc: Run tests with coverage
    deps: [setup]
    cmds:
      - uv run pytest -v --cov=src

  lint:
    desc: Lint and format code
    deps: [setup]
    cmds:
      - uv run ruff check --fix .
      - uv run ruff format .

  check:
    desc: Type-check with mypy
    deps: [setup]
    cmds:
      - uv run mypy src

  clean:
    desc: Clean Python artifacts
    cmds:
      - rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache
```

For pipenv/poetry, adjust commands accordingly.

### Docker / Docker Compose

```yaml
vars:
  COMPOSE_FILE: docker-compose.yml    # Adjust path if needed

tasks:
  up:
    desc: Start containers
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} up -d

  down:
    desc: Stop containers
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} down

  logs:
    desc: Follow container logs
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} logs -f {{.CLI_ARGS}}

  ps:
    desc: List running containers
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} ps

  restart:
    desc: Restart containers
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} restart {{.CLI_ARGS}}

  clean:
    desc: Stop and remove volumes
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} down -v --remove-orphans

  build:
    desc: Build Docker images
    cmds:
      - docker compose -f {{.COMPOSE_FILE}} build
```

### Generic (Always Available)

```yaml
tasks:
  setup:
    desc: Full project setup — install tools and dependencies
    cmds:
      - echo "Add setup steps for your project"

  check:
    desc: Check prerequisites
    silent: true
    cmds:
      - |
        echo "Checking prerequisites..."
        # Add checks here

  clean:
    desc: Clean build artifacts
    cmds:
      - echo "Add clean steps for your project"
```

---

## Verification

After scaffold or audit fixes:

1. Re-run detector:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/detect_taskfile.py <project-root>
   ```

2. List tasks:
   ```bash
   task --list
   ```

3. Show confirmation summary:
   ```
   | Step | Action | Result |
   |------|--------|--------|
   | Tool | task v3.40.1 | installed |
   | File | Taskfile.yml | created |
   | Tasks | 12 tasks | generated |
   | dotenv | .env.local, .env | configured |
   ```

4. Suggest next steps:
   - `task --list` to see all available tasks
   - `task check` to verify prerequisites
   - `task setup` to run initial setup
   - Commit `Taskfile.yml` (and `taskfiles/` if multi-file) to git
