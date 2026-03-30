---
description: >
  Comprehensive verification with automated quality gates, confession gathering, and
  confidence-based issue filtering. Default: self-review with gates. --deep: multi-agent
  review via code-reviewer agent. Use before committing, after fixing bugs, or to validate
  feature completeness.
argument-hint: "[--deep] [specific aspect to verify]"
---

# Double-Check Verification

Ultrathink!

Systematically verify the work just completed to ensure quality and completeness.

**Parse arguments from:** `$ARGUMENTS`
- If arguments contain `--deep`, enable **deep mode** (multi-agent review) and strip `--deep` from focus area
- Remaining text is the **focus area** (optional)

---

## Step 1: Scope Detection

Establish what was completed and what ecosystem this project uses.

1. **Check git status**: !`git status --short`
2. **Check staged changes**: !`git diff --cached --stat`
3. **Check unstaged changes**: !`git diff --stat`
4. **Check recent commits** (if no uncommitted changes): !`git log -3 --oneline`
5. **Check todo list**: Review any in-progress or recently completed todos
6. **Detect ecosystem**: !`ls package.json Makefile pyproject.toml build.gradle build.gradle.kts pom.xml 2>/dev/null || true`

**Scope Summary**: Summarize what will be verified (files changed, features affected, ecosystem detected).
If the user specified a focus area, prioritize that scope.

---

## Step 2: Backpressure Gates

Before reasoning-based review, run automated quality checks. Auto-detect available commands based on the ecosystem detected in Step 1.

### Detection

**Node.js** (if `package.json` exists):
!`node -e "try{const s=require('./package.json').scripts||{};console.log(JSON.stringify({test:s.test||null,lint:s.lint||s['lint:check']||null,typecheck:s.typecheck||s['type-check']||s.tsc||null,build:s.build||null}))}catch(e){}" 2>/dev/null`

**Python** (if `pyproject.toml` exists):
!`grep -c '\[tool\.pytest' pyproject.toml 2>/dev/null && echo "pytest detected" || true`
!`grep -c '\[tool\.ruff' pyproject.toml 2>/dev/null && echo "ruff detected" || true`
!`grep -c '\[tool\.mypy' pyproject.toml 2>/dev/null && echo "mypy detected" || true`

**JVM** (if `gradlew` or `pom.xml` exists):
!`test -f gradlew && echo "gradle" || (test -f pom.xml && echo "maven") || echo "none"`

**Makefile** (if `Makefile` exists):
!`grep -E '^(test|lint|check|build)[[:space:]]*:' Makefile 2>/dev/null | cut -d: -f1 || true`

### Execution

Run each detected gate command. For gates that don't exist, mark as `SKIP`. If a gate takes longer than 60 seconds, note `TIMEOUT`.

- **Node.js**: `npm test` / `npm run lint` / `npm run typecheck` / `npm run build`
- **Python**: `python -m pytest` / `ruff check .` / `mypy .`
- **JVM (Gradle)**: `./gradlew check`
- **JVM (Maven)**: `mvn test -q`
- **Makefile**: `make test` / `make lint` / `make build`

### Gate Results

Present results in a table:

| Gate | Command | Result | Details |
|------|---------|--------|---------|
| Tests | ... | PASS/FAIL/SKIP/TIMEOUT | ... |
| Lint | ... | PASS/FAIL/SKIP/TIMEOUT | ... |
| Types | ... | PASS/FAIL/SKIP/TIMEOUT | ... |
| Build | ... | PASS/FAIL/SKIP/TIMEOUT | ... |

Gate failures are **informational, not blocking** — they become high-priority inputs for the review. Always proceed to Step 3.

---

## Step 3: Confession Gathering

Gather signals about known shortcuts, assumptions, or uncertainties from the builder's work. These focus the review on areas most likely to have issues.

**Source 1 — Commit message signals:**
!`git log -10 --oneline 2>/dev/null | grep -iE "(WIP|hack|todo|fixme|temp|workaround|shortcut|quick.fix|placeholder|stub|skip|NOCOMMIT)" || true`

**Source 2 — TODOs in changed files:**
!`git diff --name-only HEAD~3 2>/dev/null | head -20 | xargs grep -nHi -E "(TODO|FIXME|HACK|WORKAROUND|XXX|NOCOMMIT)" 2>/dev/null | head -15 || true`

**Source 3 — Active todos:** Review any in-progress todo items.

### Builder Confessions Block

If signals found, format as:

```
## Builder Confessions (Auto-Gathered)
- **Commit signals**: [matched commit messages]
- **TODOs in changed files**: [file:line — comment]
- **Active todos**: [relevant items]
```

If no signals found: "No builder confessions detected. Proceeding with standard review."

Confessions are passed to the reviewer in Step 4 as focus areas — not as issues themselves.

---

## Step 4: Review

### Default Mode (self-review)

Verify from four angles, prioritizing areas flagged by gate failures (Step 2) and confessions (Step 3):

**Completeness Check**
- Does the implementation address all requirements?
- Are there any TODO comments or placeholder code left?
- Were all requested changes made?

**Correctness Check**
- Does the logic handle expected inputs correctly?
- Are there edge cases that could cause failures?
- Do error paths behave appropriately?

**Integration Check**
- Does this work with existing code?
- Are there breaking changes to existing functionality?
- Do imports, exports, and dependencies align?

**Quality Check**
- Is the code readable and maintainable?
- Does it follow project conventions (check CLAUDE.md)?
- Are there obvious simplifications?

**Confidence Scoring**: Rate each potential issue 0-100:

| Score | Meaning |
|-------|---------|
| 0-25  | Likely false positive or pre-existing issue |
| 26-50 | Possible issue, but may be a nitpick |
| 51-75 | Real issue, but may not happen often in practice |
| 76-89 | Verified real issue that will impact functionality |
| 90-100| Confirmed critical issue requiring immediate fix |

**Only report issues with confidence >= 75.**

### Deep Mode (`--deep`)

Delegate the review to a specialist agent for Critic-Actor separation (the builder should not review their own work).

Use the **Agent tool** to spawn the `code-reviewer` agent:
- `subagent_type`: `core:code-reviewer`
- `description`: "Review completed work with gate context"

Provide the agent with:
1. The **scope summary** from Step 1
2. The **gate results** from Step 2 (especially any failures)
3. The **builder confessions** from Step 3
4. The **diff content**: `git diff` and `git diff --cached`
5. The **focus area** (if specified by user)

Instruct the agent: "Pay special attention to areas flagged by builder confessions and gate failures. Return grouped findings with confidence scores."

**Graceful degradation**: If the Agent tool is unavailable or the agent cannot be spawned, fall back to the default self-review mode above and note: "Agent dispatch unavailable — running self-review mode."

---

## Step 5: Synthesis

Merge all results into the final output.

### Verification Results

**Scope Verified:** [files/features reviewed]

**Goal:** [restate the original goal]

**Mode:** [Default | Deep (code-reviewer agent)]

**Status:** [PASSED | ISSUES FOUND | GATES FAILED]

**Gate Results:**

| Gate | Status | Details |
|------|--------|---------|
| Tests | ✅/❌/SKIP | ... |
| Lint | ✅/❌/SKIP | ... |
| Types | ✅/❌/SKIP | ... |
| Build | ✅/❌/SKIP | ... |

**Verification Summary:**

| Angle | Status | Notes |
|-------|--------|-------|
| Completeness | ✅/❌ | ... |
| Correctness | ✅/❌ | ... |
| Integration | ✅/❌ | ... |
| Quality | ✅/❌ | ... |

**Issues (if any):**

| Source | Severity | Confidence | Issue | Fix Recommendation |
|--------|----------|------------|-------|--------------------|
| Gate | Critical | 100% | Tests failing: ... | Fix test ... |
| Review | Critical | 95% | [description] | [fix] |
| Confession | Moderate | 82% | TODO at file:line | [fix] |

**Confession Analysis** (if confessions were gathered):
Note which confessions led to real findings and which were acceptable.

**Conclusion:**
[Summary and recommendation to proceed or revise]
