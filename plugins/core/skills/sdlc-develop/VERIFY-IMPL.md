# Implementation Verification Workflow

Verifies implementation meets `spec.md` requirements and `tasks.md` acceptance criteria.

## Prerequisites

Required artifacts in spec directory:
- `spec.md` (REQUIRED) - Requirements with FR-XXX identifiers and acceptance criteria
- `tasks.md` (OPTIONAL) - Task breakdown with acceptance criteria

## Verification Checks

Execute checks in priority order. For each check, collect evidence with `file:line` references.

### Check 1: Requirements Coverage (Confidence: 90%)

**Source:** `spec.md` → FR-XXX requirements

**Method:**
1. Parse all FR-XXX requirements from spec.md
2. Extract requirement descriptions and acceptance criteria
3. For each requirement:
   - Grep for keywords/identifiers in implementation code
   - Grep for test files covering the requirement
   - Map to specific `file:line` evidence

**Evidence:**
```
| ID | Requirement | Code Evidence | Test Evidence | Status |
|----|-------------|---------------|---------------|--------|
| FR-001 | {title} | {file:line} | {test file:line} | {COVERED|PARTIAL|MISSING} |
```

### Check 2: Acceptance Criteria Met (Confidence: 95%)

**Source:** `tasks.md` → Task acceptance criteria

**Method:**
1. Parse tasks and their acceptance criteria from tasks.md
2. For each criterion:
   - Grep for test assertions matching the criterion
   - Verify test exists and tests the specific behavior

**Patterns to search:**
- Jest/Vitest: `(it|test)\s*\(['"](.*?)['"]`
- Pytest: `def test_`, `assert`
- JUnit: `@Test`, `assert`

**Evidence:**
```
| Task | Criterion | Test Evidence | Status |
|------|-----------|---------------|--------|
| T-01 | {criterion} | {test file:line, assertion} | {MET|NOT_MET|NO_TEST} |
```

### Check 3: No Placeholder Code (Confidence: 98%)

**Source:** Changed files (git diff)

**Method:**
1. Get list of files changed since spec creation (or all implementation files)
2. Grep for placeholder patterns:
   - `TODO`, `FIXME`, `XXX`, `HACK`
   - `throw new Error("Not implemented")`
   - `pass  # TODO`, `...` (Python)
   - `panic!("not implemented")` (Rust)
   - Empty function bodies

**Patterns:**
```regex
TODO|FIXME|XXX|HACK
throw\s+new\s+Error\s*\(\s*["']Not implemented
NotImplementedError
\.\.\.  # Python ellipsis
panic!\s*\(\s*["']not implemented
```

**Evidence:**
```
| File | Line | Content | Type |
|------|------|---------|------|
| {file} | {line} | {snippet} | {TODO|FIXME|STUB} |
```

### Check 4: Tests Pass (Confidence: 95%)

**Source:** Test execution

**Method:**
1. Detect test framework (package.json, pytest.ini, pom.xml, etc.)
2. Run test suite
3. Capture pass/fail counts
4. Note any failures with file:line

**Execution:**
- npm/yarn/pnpm: `npm test` or `yarn test`
- pytest: `pytest --tb=short`
- Maven: `mvn test`
- Gradle: `./gradlew test`

**Evidence:**
```
| Test Suite | Total | Passed | Failed | Skipped |
|------------|-------|--------|--------|---------|
| {suite} | {N} | {N} | {N} | {N} |

Failed tests:
- {test name} ({file:line}): {failure reason}
```

### Check 5: RULE ZERO Compliance (Confidence: 90%)

**Source:** Git diff, implementation files

**RULE ZERO:** Implementation must be complete, not stubbed or deferred.

**Method:**
1. **Git diff verified:** Check files modified match expected from plan.md
2. **No stubs:** Verify Check 3 passed (no TODOs/FIXMEs in changed files)
3. **Tests pass:** Verify Check 4 passed
4. **Recommendations implemented:** Cross-reference any recommendations from Phase 4 review

**Evidence:**
```
RULE ZERO Compliance:
- [ ] Files modified: {count} files (matches plan: {yes/no})
- [ ] No placeholder code: {PASS/FAIL}
- [ ] Tests passing: {pass}/{total}
- [ ] Phase 4 recommendations addressed: {N/A or status}
```

## Agent Strategy

| Check | Model | Rationale |
|-------|-------|-----------|
| Requirements parsing | sonnet | Semantic understanding |
| Keyword mapping | haiku | Pattern matching |
| Test assertion mapping | sonnet | Needs test context |
| Placeholder detection | haiku | Regex patterns |
| Test execution | - | Bash command |
| RULE ZERO synthesis | sonnet | Cross-check analysis |

## Confidence Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥85% | PASS | Implementation verified |
| 65-84% | REVIEW | Flag gaps for review |
| <65% | FAIL | Significant gaps found |

## Output

Generate Implementation Completeness section of verification report:
- Summary score (weighted average)
- Requirements coverage table
- Acceptance criteria table
- RULE ZERO checklist
- Items flagged for manual review

## Error Handling

- Missing spec.md: FAIL with "Required artifact missing: spec.md"
- Missing tasks.md: SKIP acceptance criteria check, note in report
- No FR-XXX in spec.md: FAIL with "spec.md missing FR-XXX requirements format"
- Test execution fails: Capture error, continue with other checks
- No test framework detected: SKIP test execution, reduce confidence
