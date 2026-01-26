# SDLC Develop Examples

> **Note:** All examples use the default path `arkhe/specs/`. If you configure a custom `specs_dir` in `.arkhe.yaml`, paths will use your configured value instead (e.g., `plan/arkhe/specs/`).

## Full Pipeline (Interactive)

```bash
/develop add user authentication
```

**What happens:**
1. Executes all 6 phases with user checkpoints
2. Creates: `arkhe/specs/01-user-auth/` with spec.md, plan.md, tasks.md
3. Implements the feature
4. Validates and summarizes

**Output:**
```
arkhe/specs/01-user-auth/
├── spec.md       # Requirements & acceptance criteria
├── plan.md       # Architecture & design decisions
└── tasks.md      # Full ticket breakdown
```

---

## Plan Only

```bash
/develop create plan for dashboard feature --plan-only
```

**What happens:**
1. Executes Phases 0-2 only
2. Saves spec.md and plan.md to `arkhe/specs/02-dashboard/`
3. Stops without implementing

**Output:**
```
Spec saved to `arkhe/specs/02-dashboard/`

Files created:
- spec.md (requirements)
- plan.md (architecture)

Run `/develop @arkhe/specs/02-dashboard/` when ready to implement.
```

---

## Resume Existing Spec

```bash
/develop @arkhe/specs/01-user-auth/
```

**What happens:**
1. Loads existing spec and plan from path
2. Asks which phase to continue from
3. Skips completed phases

**Interaction:**
```
Found existing spec: 01-user-auth
Status: Architecture complete (Phase 2)

Which phase would you like to continue from?
1. Phase 3: Workstreams (generate tasks)
2. Phase 4: Implementation (start coding)
3. Phase 0: Start fresh
```

---

## Autonomous Mode

```bash
/develop add logout button --auto
```

**What happens:**
1. Executes all phases without checkpoints
2. Makes reasonable default decisions
3. Reports everything at the end
4. Creates: `arkhe/specs/03-logout-button/`

**Use when:**
- Simple, well-understood features
- You trust the default architecture choices
- You want minimal interaction

---

## With Deep Validation

```bash
/develop refactor payment service --validate
```

**What happens:**
1. Standard 6-phase pipeline
2. In Phase 4, includes opus-level deep validation
3. Scores implementation 0-100
4. Reports detailed findings

**Validation output:**
```
Deep Validation Results:
- Score: 87/100 (Medium-High Confidence)
- Issues found:
  - Missing error handling for timeout scenario
  - Test coverage at 75% (below 80% target)
- Recommendations:
  - Add timeout handling in PaymentProcessor.process()
  - Add unit tests for edge cases
```

---

## Specific Phase Only

```bash
/develop @arkhe/specs/01-user-auth/ --phase=4
```

**What happens:**
1. Loads existing spec from path
2. Executes only Phase 4 (implementation)
3. Skips all other phases
4. Useful for re-running implementation after plan changes

---

## First Run (Configuration)

```bash
/develop add shopping cart
```

**If no `.arkhe.yaml` exists:**

```
No configuration found. Let me set up SDLC preferences.

Where should specs be saved?
1. arkhe/specs/ (Recommended)
2. .sdlc/
3. docs/specs/
4. Custom path...

Use numbered prefixes (01-, 02-)?
1. Yes (Recommended)
2. No
```

**Creates `.arkhe.yaml`:**
```yaml
develop:
  specs_dir: arkhe/specs
  numbering: true
  ticket_format: full
```

---

## Interaction Modes Comparison

| Mode | Checkpoints | Use Case |
|------|-------------|----------|
| Interactive (default) | 5 checkpoints | Full control, review each phase |
| `--auto` | None | Trust defaults, minimal interaction |
| `--plan-only` | 2 checkpoints | Design now, implement later |
| `--phase=N` | 1 checkpoint | Re-run specific phase |

---

## Spec Directory Examples

After multiple features:

```
arkhe/specs/
├── 01-user-auth/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 02-dashboard/
│   ├── spec.md
│   └── plan.md        # --plan-only stopped here
├── 03-logout-button/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── 04-payment-refactor/
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── proofs/        # Validation artifacts (if --validate)
        └── validation-report.md
```
