# Evidence-Based Quality Gates

Companion guide to the Wave Quality Gates in Phase 4. Defines evidence requirements
and rationalization prevention for each gate.

**Core principle:** No completion claim without fresh verification evidence.

---

## The Iron Rule

Every quality gate check must produce **fresh command output in the current context**.
Cached results, remembered outputs, and assumptions are not valid evidence.

If you haven't run the command THIS wave, you cannot claim it passes.

---

## Per-Gate Evidence Requirements

| # | Gate | Command | Required Evidence | NOT Sufficient |
|---|------|---------|-------------------|----------------|
| 1 | Task completion | Read tasks.md from disk | Quoted content showing `Status: COMPLETED` for each wave task | "I updated it earlier", TaskList memory |
| 2 | File evidence | `git diff --stat` | Full command output showing changed files | "I know which files I changed" |
| 3 | Tests green | Run test suite (project-specific) | Full output with pass/fail counts and exit code | Previous run, "should pass", linter output |
| 4 | No placeholders | Grep changed files for TODO/FIXME/NotImplementedError | Full grep output (should be empty) | "I didn't add any" |
| 5 | Acceptance criteria | Map criteria to code | file:line reference for each criterion | "The code implements it" |
| 6 | Confessions recorded | Read wave-context.md | Quoted confession block for each task | "I'll write them later" |

---

## Rationalization Prevention

Common thoughts that indicate a gate is about to be skipped without evidence.
If you catch yourself thinking any of these, **STOP and run the verification**.

| Rationalization | Reality |
|----------------|---------|
| "Tests should pass because I only changed X" | Run the tests. Side effects exist. |
| "No placeholders because I didn't add any" | Run the grep. Prove it. |
| "Files match because I followed the plan" | Run `git diff --stat`. Plans drift. |
| "Acceptance criteria met because the code implements it" | Show file:line. "Implements" is not evidence. |
| "I'm confident this passes" | Confidence is not evidence. |
| "Just this once we can skip" | No exceptions. Every gate, every wave. |
| "The linter passed, so tests pass too" | Linter is not the test suite. |
| "The agent reported success" | Verify independently. Reports can be wrong. |
| "I already checked this" | Check again. Fresh evidence only. |
| "Partial check is enough" | Partial proves nothing about the whole. |

---

## Escalation Protocol

Quality gates are not strictly binary. When a gate cannot be evaluated:

| Status | Meaning | Action |
|--------|---------|--------|
| **PASS** | Fresh evidence confirms gate passes | Proceed to next gate |
| **FAIL** | Fresh evidence shows gate fails | Fix issue, re-run check with fresh output |
| **BLOCKED** | Cannot produce evidence (no test framework, no grep target, CI unavailable) | Escalate to user with explanation. Do not force-pass. |
| **NEEDS_CONTEXT** | Missing information to evaluate (unclear acceptance criteria, ambiguous requirement) | Escalate to user with specific question. Do not assume. |

**Rules:**
- Never force-pass a BLOCKED gate
- Never guess at a NEEDS_CONTEXT gate
- Always explain what prevented evaluation
- User may override with explicit approval (documented in wave-context.md)

---

## Evidence Capture Format

When recording gate results, include the actual evidence:

```markdown
### Gate Results — Wave {N}

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | Task completion | PASS | tasks.md: T-04 COMPLETED, T-05 COMPLETED |
| 2 | File evidence | PASS | git diff --stat: 4 files changed, 127 insertions(+), 12 deletions(-) |
| 3 | Tests green | PASS | npm test: 47 passing, 0 failing (exit 0) |
| 4 | No placeholders | PASS | grep TODO/FIXME: 0 matches in changed files |
| 5 | Acceptance criteria | PASS | AC-1: src/auth.ts:42, AC-2: src/auth.ts:78, AC-3: tests/auth.test.ts:15 |
| 6 | Confessions | PASS | wave-2-context.md: T-04 confession recorded, T-05 confession recorded |
```
