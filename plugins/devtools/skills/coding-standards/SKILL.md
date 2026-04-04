---
name: coding-standards
description: >-
  Bootstrap, update, or audit a project against a centralized coding-standards
  repository. Copies Claude rules, config templates (EditorConfig, Prettier,
  ESLint, Lefthook, Taskfile), and hooks into projects with ecosystem-aware
  selection and path customization. Use when user mentions "coding standards",
  "bootstrap rules", "update rules", "audit standards", "install coding
  standards", "sync standards", "check rule drift", "coding-standards setup",
  or "apply coding standards".
disable-model-invocation: true
---

# Coding Standards

Bootstrap, update, or audit project configuration against the deznode coding-standards repository.

## Pre-flight

Run detection script to assess current state:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/detect_standards.py <project-root> [--standards-path <path>]
```

If `standards_repo.found` is false, ask user for the coding-standards repo path via AskUserQuestion.

## Decision Flow

```
standards_repo.found?
├── No → Ask for path, re-run detector
└── Yes
    ├── No installed rules/configs AND no devtools_local → Bootstrap
    ├── devtools_local exists → AskUserQuestion: Update or Audit?
    └── Has installed rules but no devtools_local → Offer Audit first
```

## Operations

### Bootstrap (first-time setup)
1. Confirm detected ecosystems (JVM → backend rules, Node.js → frontend rules, infra always)
2. Collect project paths (API dir, web dir) via AskUserQuestion
3. Copy templates → `.claude/rules/`, configs → root, hooks → `.claude/hooks/`
4. Replace TODO markers with actual paths
5. Run `lefthook install`, `chmod +x` hooks, write `.claude/devtools.local.md`

### Update (sync to latest)
1. Load config from `.claude/devtools.local.md`
2. Show comparison: new, modified, removed files
3. User selects updates to apply (with diff preview)
4. Apply and update `last_update` timestamp

### Audit (read-only drift check)
1. Present compliance score and per-file status table
2. Offer to route to Update if issues found

See [WORKFLOW.md](WORKFLOW.md) for detailed steps.
See [EXAMPLES.md](EXAMPLES.md) for usage examples.
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

## Key Rules

- **Never overwrite without asking** — always offer merge/replace/skip
- **Detect first** — run script before any file operations
- **Ecosystem-aware** — only copy relevant templates for detected stack
- **Non-destructive** — configs are expected to be customized; "modified" status in audit is informational
