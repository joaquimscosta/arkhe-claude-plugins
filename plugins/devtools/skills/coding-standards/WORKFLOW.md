# Coding Standards Workflow

## Phase 1: Detection

Run the detection script on the target project:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/detect_standards.py <project-root> [--standards-path <path>]
```

### Output Interpretation

| JSON Key | Meaning |
|----------|---------|
| `standards_repo.found` | Whether coding-standards repo was located |
| `devtools_local` | Stored config from `.claude/devtools.local.md` (null if first run) |
| `ecosystems` | Detected project stacks (jvm, node) |
| `comparison` | Per-file status: match, modified, missing, extra |
| `compliance.score_percent` | Overall compliance percentage |

### Routing Decision

```
standards_repo.found = false?
  → Ask user for path via AskUserQuestion, re-run detector

devtools_local = null AND compliance.total_installed = 0?
  → Route to Bootstrap

devtools_local != null?
  → AskUserQuestion: "Update to latest standards?" or "Audit drift?"
    → Update or Audit

compliance.total_installed > 0 AND devtools_local = null?
  → AskUserQuestion: "Detected existing rules. Audit first or bootstrap fresh?"
```

---

## Phase 2A: Bootstrap

### Step 1: Confirm Ecosystems

Present detected ecosystems and let user confirm which rule categories to install:

```
AskUserQuestion (multiSelect: true):
  "Which rule categories should we install?"
  Options based on detected ecosystems:
  - "Backend (8 rules)" — if JVM detected
  - "Frontend (4 rules)" — if Node.js detected
  - "Infrastructure (2 rules)" — always offered
```

### Step 2: Collect Project Paths

Ask for project-specific paths that replace TODO markers in templates:

```
AskUserQuestion:
  "What is your API/backend directory?" [default from ecosystem detection or "apps/api"]
  "What is your web/frontend directory?" [default from ecosystem detection or "apps/web"]
```

Only ask questions relevant to selected ecosystems:
- JVM selected → ask for API directory
- Node.js selected → ask for web directory
- Both → ask for both

### Step 3: Copy Templates

#### Rules → `.claude/rules/{category}/`

Create directories and copy selected rule files:

```bash
mkdir -p .claude/rules/backend .claude/rules/frontend .claude/rules/infrastructure
```

Copy each `.md` file from `templates/claude-rules/{category}/` to `.claude/rules/{category}/`.

Rules require NO TODO replacement — they use `paths:` frontmatter which is generic.

If a file already exists, use AskUserQuestion:
- "Replace" — overwrite with template
- "Skip" — keep existing
- "Show diff" — display differences before deciding

#### Configs → project root

Copy from `templates/configs/` to project root. For each config:

1. Read template content
2. Apply path substitutions (see TODO Marker Map below)
3. If file exists: offer merge/replace/skip
4. Write file

#### Hooks → `.claude/hooks/`

```bash
mkdir -p .claude/hooks
```

Copy `auto-lint.sh` and `settings.json` from `templates/claude-hooks/`.

Apply path substitution to `auto-lint.sh`.

If `.claude/settings.json` already exists, MERGE the hooks section rather than replacing. Read existing settings, add the hook entries from the template, write back.

### Step 4: TODO Marker Replacement

When copying config files, apply these substitutions:

| File | Default Value | Replace With |
|------|---------------|-------------|
| `lefthook.yml` | `apps/web` (all occurrences) | User's web directory |
| `lefthook.yml` | `apps/api` (all occurrences) | User's API directory |
| `Taskfile.yml` | `API_DIR: apps/api` | `API_DIR: {user_api_dir}` |
| `Taskfile.yml` | `WEB_DIR: apps/web` | `WEB_DIR: {user_web_dir}` |
| `eslint.config.mjs` | `internalPattern: ["^@/.+"]` | User's import pattern (or keep default) |
| `auto-lint.sh` | `*/apps/web/*.ts\|*/apps/web/*.tsx` | User's web directory |

Use simple string replacement — the defaults are literal strings:

```python
content = template_content.replace("apps/web", user_web_dir)
content = content.replace("apps/api", user_api_dir)
```

#### Ecosystem-Selective Stripping

If only JVM is selected (no Node.js):
- Skip copying: `.prettierrc`, `eslint.config.mjs`, `auto-lint.sh`, `settings.json`
- In `lefthook.yml`: remove eslint and prettier hook sections
- In `Taskfile.yml`: remove web-related tasks (setup:web, dev:web, test:web, lint:web, build:web)

If only Node.js is selected (no JVM):
- In `lefthook.yml`: remove ktlint and detekt hook sections
- In `Taskfile.yml`: remove api-related tasks (setup:api, dev:api, test:api, lint:api, build:api)

Claude handles this stripping during the copy phase by reading the template, removing irrelevant sections, then writing.

### Step 5: Post-Bootstrap

1. Make hooks executable:
   ```bash
   chmod +x .claude/hooks/auto-lint.sh
   ```

2. Install git hooks (if lefthook is available):
   ```bash
   lefthook install
   ```

3. Write `.claude/devtools.local.md`:
   ```yaml
   ---
   coding_standards_path: /absolute/path/to/coding-standards
   last_bootstrap: 2026-04-04
   ecosystems: [jvm, nodejs]
   project_paths:
     api_dir: apps/api
     web_dir: apps/web
   ---

   # Devtools Local Configuration

   Stores local configuration for the devtools plugin coding-standards skill.
   This file contains machine-local paths — do not commit to version control.
   ```

4. Add `.claude/devtools.local.md` to `.gitignore` if not already present.

5. Re-run detector and present verification summary:
   ```
   ## Bootstrap Complete

   | Category | Installed | Total |
   |----------|-----------|-------|
   | Rules | 14 | 14 |
   | Configs | 5 | 5 |
   | Hooks | 2 | 2 |

   Compliance: 100%
   ```

---

## Phase 2B: Update

### Step 1: Load Configuration

Read `.claude/devtools.local.md` for:
- `coding_standards_path` — where to find templates
- `project_paths` — for TODO marker replacement on new files
- `ecosystems` — which categories are relevant

### Step 2: Show Comparison

Present the `comparison` section from detector output grouped by action needed:

```
## Standards Update Available

### New Files (in standards but not installed)
| File | Category |
|------|----------|
| backend/error-handling.md | rules |

### Modified (template changed since install)
| File | Category |
|------|----------|
| backend/testing-patterns.md | rules |
| lefthook.yml | configs |

### Your project matches the latest standards for all other files.
```

For "modified" configs, note that differences may be due to expected customization (TODO replacements). Show the actual diff before asking.

### Step 3: User Selection

```
AskUserQuestion (multiSelect: true):
  "Which updates should we apply?"
  - "Add backend/error-handling.md (new rule)"
  - "Update backend/testing-patterns.md (show diff first)"
  - "Skip all"
```

For modified files, use Read tool to show both versions before user decides.

### Step 4: Apply Updates

- New files: copy with TODO replacement using stored project_paths
- Modified files: replace with new template content (user confirmed after seeing diff)
- Apply same TODO marker substitutions as bootstrap

### Step 5: Update Timestamp

Update `.claude/devtools.local.md` frontmatter:
```yaml
last_update: 2026-04-04
```

---

## Phase 2C: Audit

### Step 1: Run Detection (Read-Only)

Use the `comparison` and `compliance` sections from detector output. No files are modified.

### Step 2: Present Compliance Report

```
## Coding Standards Audit

Compliance: 12/14 rules, 3/5 configs, 1/2 hooks — 76%

### Rules
| File | Category | Status |
|------|----------|--------|
| architecture.md | backend | Match |
| api-patterns.md | backend | Match |
| error-handling.md | backend | MISSING |
| testing-patterns.md | backend | Modified |
| ... | ... | ... |

### Configs
| File | Status | Notes |
|------|--------|-------|
| .editorconfig | Match | |
| lefthook.yml | Modified | Expected (paths customized) |
| Taskfile.yml | Modified | Expected (paths customized) |
| eslint.config.mjs | Match | |
| .prettierrc | MISSING | |

### Hooks
| File | Status |
|------|--------|
| auto-lint.sh | Installed, executable |
| settings.json | MISSING |
```

### Step 3: Offer Resolution

```
AskUserQuestion:
  "Would you like to fix missing/outdated items?"
  - "Yes, start Update workflow"
  - "No, audit only"
```

If user chooses Update, transition to Phase 2B with the comparison data already loaded.

---

## Ecosystem-to-Template Mapping

| Detected Ecosystem | Rules | Configs | Hooks |
|-------------------|-------|---------|-------|
| JVM only | backend + infrastructure | .editorconfig, lefthook.yml, Taskfile.yml | none |
| Node.js only | frontend + infrastructure | all 5 | both |
| JVM + Node.js | all 14 | all 5 | both |
| Neither | infrastructure only | .editorconfig, Taskfile.yml | none |

Infrastructure rules are always included regardless of ecosystem.
