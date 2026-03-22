# Examples: Taskfile Setup

## Example 1: Greenfield Node.js Project (No Taskfile)

### Detection Output

```json
{
  "task_binary": {"installed": true, "path": "/opt/homebrew/bin/task", "version": "3.40.1"},
  "taskfile": {"exists": false},
  "ecosystems": [
    {"ecosystem": "node", "package_manager": "pnpm", "root": "."}
  ],
  "env_files": [".env.local"],
  "existing_runners": {"makefile": false, "justfile": false, "package_json_scripts": true, "gradlew": false},
  "os": "macos"
}
```

### Scaffold Session

**Status**: Task installed, no Taskfile found, Node.js/pnpm detected.

**User chooses**: Single-file pattern, task groups: dev, build, test, lint, format, check, setup, clean.

### Generated Taskfile.yml

```yaml
version: "3"

dotenv: [".env.local", ".env"]

tasks:
  setup:
    desc: Install dependencies
    run: once
    cmds:
      - pnpm install

  dev:
    desc: Start development server
    deps: [setup]
    cmds:
      - pnpm dev

  build:
    desc: Build for production
    deps: [setup]
    cmds:
      - pnpm build

  test:
    desc: Run tests
    deps: [setup]
    cmds:
      - pnpm test

  lint:
    desc: Run ESLint
    deps: [setup]
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

  clean:
    desc: Clean build artifacts
    cmds:
      - rm -rf dist .next node_modules/.cache
```

---

## Example 2: Monorepo with JVM + Node.js (Multi-file)

### Detection Output

```json
{
  "task_binary": {"installed": true, "path": "/opt/homebrew/bin/task", "version": "3.40.1"},
  "taskfile": {"exists": false},
  "ecosystems": [
    {"ecosystem": "node", "package_manager": "pnpm", "root": "apps/web"},
    {"ecosystem": "jvm", "build_tool": "gradle-kotlin", "root": "apps/api"},
    {"ecosystem": "docker", "has_dockerfile": true, "has_compose": true, "root": "."}
  ],
  "env_files": [],
  "existing_runners": {"makefile": false, "justfile": false, "package_json_scripts": true, "gradlew": true},
  "os": "macos"
}
```

### Scaffold Session

**Status**: Task installed, no Taskfile, 3 ecosystems detected (monorepo).

**User chooses**: Multi-file pattern (recommended for monorepo).

### Generated Files

**Taskfile.yml** (root):
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

**taskfiles/api.yml**:
```yaml
version: "3"

tasks:
  setup:
    desc: API setup
    cmds:
      - echo "API dependencies managed by Gradle"

  dev:
    desc: Start API server
    cmds:
      - ./gradlew bootRun

  test:
    desc: Run API tests
    cmds:
      - ./gradlew test

  lint:
    desc: Run Kotlin linter
    cmds:
      - ./gradlew ktlintCheck

  clean:
    desc: Clean API build artifacts
    cmds:
      - ./gradlew clean
```

**taskfiles/web.yml**:
```yaml
version: "3"

tasks:
  setup:
    desc: Install web dependencies
    run: once
    cmds:
      - pnpm install

  dev:
    desc: Start web dev server
    deps: [setup]
    cmds:
      - pnpm dev

  test:
    desc: Run web tests
    deps: [setup]
    cmds:
      - pnpm test

  lint:
    desc: Run ESLint
    deps: [setup]
    cmds:
      - pnpm lint

  clean:
    desc: Clean web build artifacts
    cmds:
      - rm -rf .next node_modules/.cache
```

**taskfiles/docker.yml**:
```yaml
version: "3"

tasks:
  up:
    desc: Start containers
    cmds:
      - docker compose up -d

  down:
    desc: Stop containers
    cmds:
      - docker compose down

  logs:
    desc: Follow container logs
    cmds:
      - docker compose logs -f {{.CLI_ARGS}}

  clean:
    desc: Stop and remove volumes
    cmds:
      - docker compose down -v --remove-orphans
```

---

## Example 3: Existing Taskfile with Violations

### Detection Output with Audit

```json
{
  "task_binary": {"installed": true, "path": "/opt/homebrew/bin/task", "version": "3.40.1"},
  "taskfile": {
    "exists": true, "path": "Taskfile.yml", "version": "3",
    "task_count": 12, "has_includes": false, "include_count": 0, "has_dotenv": false,
    "tasks": [
      {"name": "build", "has_desc": true, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": true, "has_status": false, "line": 8},
      {"name": "deploy", "has_desc": false, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": false, "has_status": false, "line": 15},
      {"name": "test", "has_desc": false, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": false, "has_status": false, "line": 22}
    ]
  },
  "env_files": [".env", ".env.local"],
  "audit": {
    "violations": [
      {"rule": "TF002", "severity": "WARNING", "message": "Task 'deploy' has no preconditions (safety-critical task)", "task": "deploy", "line": 15},
      {"rule": "TF003", "severity": "WARNING", "message": "Task 'build' has no sources/generates (no up-to-date checks)", "task": "build", "line": 8},
      {"rule": "TF005", "severity": "WARNING", "message": "Task 'deploy' is missing a 'desc:' field", "task": "deploy", "line": 15},
      {"rule": "TF005", "severity": "WARNING", "message": "Task 'test' is missing a 'desc:' field", "task": "test", "line": 22},
      {"rule": "TF006", "severity": "INFO", "message": "No 'dotenv:' config but 2 .env file(s) found"}
    ],
    "summary": {"total": 5, "errors": 0, "warnings": 4, "info": 1}
  }
}
```

### Audit Report

```
## Audit Results — 5 violations (4 warnings, 1 info)

### WARNINGS
| Rule  | Message                              | Task   | Line | Fix                        |
|-------|--------------------------------------|--------|------|----------------------------|
| TF002 | No preconditions on safety task      | deploy | 15   | Add preconditions block    |
| TF003 | No sources/generates on build task   | build  | 8    | Add sources/generates      |
| TF005 | Missing desc field                   | deploy | 15   | Add desc                   |
| TF005 | Missing desc field                   | test   | 22   | Add desc                   |

### INFO
| Rule  | Message                              | Fix                                  |
|-------|--------------------------------------|--------------------------------------|
| TF006 | No dotenv, 2 .env files found       | Add dotenv: [".env.local", ".env"]   |
```

**User selects**: TF005 (both), TF006 to fix. Skips TF002 and TF003 for now.

### After Fixes

- Added `desc: Deploy application` to deploy task
- Added `desc: Run tests` to test task
- Added `dotenv: [".env.local", ".env"]` at top level
- Re-ran detector: 2 violations remaining (TF002, TF003)

---

## Example 4: Nosilha-Style Full-Stack Project

### Context

Full-stack project with API (Spring Boot/Gradle), web (Next.js/pnpm), Docker Compose for PostgreSQL, and infrastructure (Terraform).

### Detection Output

```json
{
  "taskfile": {"exists": false},
  "ecosystems": [
    {"ecosystem": "node", "package_manager": "pnpm", "root": "apps/web"},
    {"ecosystem": "jvm", "build_tool": "gradle-kotlin", "root": "apps/api"},
    {"ecosystem": "docker", "has_dockerfile": true, "has_compose": true, "root": "."}
  ],
  "env_files": [],
  "existing_runners": {"makefile": false, "justfile": false, "package_json_scripts": true, "gradlew": true}
}
```

### User Chooses Single-File Pattern

### Generated Taskfile.yml

```yaml
version: "3"

vars:
  API_DIR: apps/api
  WEB_DIR: apps/web
  DOCKER_COMPOSE: infrastructure/docker/docker-compose.yml

tasks:
  check:
    desc: Check prerequisites — detect missing tools
    silent: true
    cmds:
      - |
        missing=0
        check_tool() {
          if command -v "$1" &> /dev/null; then
            printf "  OK  %-10s %s\n" "$1" "$(eval "$3")"
          else
            printf "  MISSING  %-10s install with: %s\n" "$1" "$2"
            missing=$((missing + 1))
          fi
        }
        echo "Checking prerequisites..."
        echo ""
        check_tool "docker"   "brew install --cask docker"  "docker --version | head -1"
        check_tool "node"     "nvm install --lts"           "node --version"
        check_tool "pnpm"     "npm install -g pnpm"         "pnpm --version"
        check_tool "java"     "sdk install java"            "java --version 2>&1 | head -1"
        echo ""
        if [ "$missing" -gt 0 ]; then
          echo "$missing tool(s) missing."
          exit 1
        else
          echo "All prerequisites installed."
        fi

  setup:
    desc: Full-stack setup
    cmds:
      - task: setup:api
      - task: setup:web

  setup:api:
    desc: API setup — copy env template if missing
    cmds:
      - |
        if [ ! -f {{.API_DIR}}/.env.local ]; then
          cp {{.API_DIR}}/.env.local.example {{.API_DIR}}/.env.local
          echo "Created {{.API_DIR}}/.env.local from template"
        else
          echo "{{.API_DIR}}/.env.local already exists, skipping"
        fi

  setup:web:
    desc: Web setup — install dependencies
    dir: "{{.WEB_DIR}}"
    cmds:
      - pnpm install

  dev:
    desc: Start API + web in parallel
    deps:
      - dev:api
      - dev:web

  dev:api:
    desc: Start API server (auto-starts database)
    dir: "{{.API_DIR}}"
    cmds:
      - ./gradlew bootRun --args='--spring.profiles.active=local'

  dev:web:
    desc: Start web dev server
    dir: "{{.WEB_DIR}}"
    cmds:
      - pnpm dev

  dev:db:
    desc: Start database only
    cmds:
      - docker compose -f {{.DOCKER_COMPOSE}} up -d

  test:
    desc: Run all tests
    cmds:
      - task: test:api
      - task: test:web

  test:api:
    desc: Run API tests
    dir: "{{.API_DIR}}"
    cmds:
      - ./gradlew test

  test:web:
    desc: Run web tests
    dir: "{{.WEB_DIR}}"
    cmds:
      - pnpm test

  lint:
    desc: Run all linters
    cmds:
      - task: lint:api
      - task: lint:web

  lint:api:
    desc: Run Kotlin linter
    dir: "{{.API_DIR}}"
    cmds:
      - ./gradlew ktlintCheck

  lint:web:
    desc: Run ESLint
    dir: "{{.WEB_DIR}}"
    cmds:
      - pnpm lint

  stop:
    desc: Stop database container
    cmds:
      - docker compose -f {{.DOCKER_COMPOSE}} down

  clean:
    desc: Clean build artifacts
    cmds:
      - task: clean:api
      - task: clean:web

  clean:api:
    desc: Clean API build artifacts
    dir: "{{.API_DIR}}"
    cmds:
      - ./gradlew clean

  clean:web:
    desc: Clean web build artifacts
    dir: "{{.WEB_DIR}}"
    cmds:
      - rm -rf .next node_modules/.cache
```

---

## Example 5: Already-Perfect Taskfile

### Detection Output

```json
{
  "task_binary": {"installed": true, "path": "/opt/homebrew/bin/task", "version": "3.40.1"},
  "taskfile": {
    "exists": true, "path": "Taskfile.yml", "version": "3",
    "task_count": 15, "has_includes": false, "include_count": 0, "has_dotenv": true,
    "tasks": [
      {"name": "setup", "has_desc": true, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": false, "has_status": false, "line": 8},
      {"name": "dev", "has_desc": true, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": true, "has_status": false, "line": 14},
      {"name": "test", "has_desc": true, "has_preconditions": false, "has_sources": false, "has_generates": false, "has_deps": false, "has_status": false, "line": 22},
      {"name": "build", "has_desc": true, "has_preconditions": false, "has_sources": true, "has_generates": true, "has_deps": false, "has_status": false, "line": 30}
    ]
  },
  "audit": {
    "violations": [],
    "summary": {"total": 0, "errors": 0, "warnings": 0, "info": 0}
  }
}
```

### Result

```
Taskfile audit complete — no violations found.

Your Taskfile.yml follows best practices:
  - version: '3' declared
  - All 15 tasks have desc fields
  - dotenv configured
  - Build tasks have sources/generates

No changes needed.
```
