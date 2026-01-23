# Architecture Verification Workflow

Verifies implementation matches `plan.md` architecture and `api-contract.md` definitions.

## Prerequisites

Required artifacts in spec directory:
- `plan.md` (REQUIRED) - Architecture design with key files, components, data flow
- `api-contract.md` (OPTIONAL) - API endpoint definitions

## Verification Checks

Execute checks in priority order. For each check, collect evidence with `file:line` references.

### Check 1: Key Files Exist (Confidence: 95%)

**Source:** `plan.md` → "Key Files" section

**Method:**
1. Parse key files list from plan.md
2. Glob for each expected file path
3. Record existence status

**Evidence:**
```
| File | Expected | Found | Status |
|------|----------|-------|--------|
```

### Check 2: Component Structure (Confidence: 85%)

**Source:** `plan.md` → "Components" or "Architecture" section

**Method:**
1. Parse component names and expected locations
2. Glob for matching directory/file structures
3. Grep for component exports and class definitions

**Evidence:**
```
| Component | Expected Location | Found | Status |
|-----------|------------------|-------|--------|
```

### Check 3: API Contract Accuracy (Confidence: 90%)

**Source:** `api-contract.md` (skip if not present)

**Method:**
1. Parse endpoint definitions (method, path, request/response shapes)
2. Grep for route definitions in implementation
3. Compare request/response types

**Patterns to search:**
- Express: `router.(get|post|put|delete|patch)\s*\(['"]`
- FastAPI: `@(app|router)\.(get|post|put|delete|patch)\s*\(['"]`
- Spring: `@(Get|Post|Put|Delete|Patch)Mapping`
- Controller files, route handlers

**Evidence:**
```
| Endpoint | Contract | Implementation | Status |
|----------|----------|----------------|--------|
| {method} {path} | {request} → {response} | {file:line} | {MATCH|MISMATCH|MISSING} |
```

### Check 4: Pattern Consistency (Confidence: 75%)

**Source:** `plan.md` → "Patterns" or existing codebase patterns

**Method:**
1. Identify patterns mentioned in plan (naming conventions, file organization, etc.)
2. Grep for pattern usage in new code
3. Compare against existing implementations

**Evidence:**
```
| Pattern | Expected | Found | Status |
|---------|----------|-------|--------|
```

### Check 5: UI-Contract Alignment (Confidence: 85%)

**Source:** `api-contract.md` ↔ Frontend type definitions

**Method:**
1. Parse response shapes from api-contract.md
2. Grep for corresponding TypeScript interfaces/types in frontend
3. Compare field names and types

**Patterns to search:**
- TypeScript: `interface\s+\w+`, `type\s+\w+`
- Frontend API calls, data fetching hooks

**Evidence:**
```
| Data Shape | Backend (contract) | Frontend (consumer) | Status |
|------------|-------------------|---------------------|--------|
```

### Check 6: Property Naming Consistency (Confidence: 80%)

**Source:** Cross-layer analysis

**Method:**
1. Extract property names from api-contract.md
2. Grep for same properties in backend models, database schemas, frontend types
3. Flag inconsistencies (e.g., `userId` vs `user_id` vs `UserId`)

**Evidence:**
```
| Concept | Backend | API | Frontend | DB | Status |
|---------|---------|-----|----------|----|---------|
```

### Check 7: Data Flow (Confidence: 75%)

**Source:** `plan.md` → "Data Flow" section

**Method:**
1. Parse expected data flow (e.g., UI → API → Service → Repository)
2. Trace import chains in implementation
3. Verify call graph matches expected flow

**Evidence:**
```
| Flow Step | Expected | Actual | Status |
|-----------|----------|--------|--------|
```

## Agent Strategy

| Check | Model | Rationale |
|-------|-------|-----------|
| Key files exist | haiku | Simple Glob operations |
| Component structure | haiku | Directory/file checks |
| API contract parsing | sonnet | Needs shape understanding |
| Pattern matching | sonnet | Requires codebase context |
| UI-Contract alignment | sonnet | Type comparison |
| Property naming | haiku | String matching |
| Data flow | sonnet | Import/call analysis |

## Confidence Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥85% | PASS | Verification complete |
| 65-84% | REVIEW | Flag for manual review |
| <65% | FAIL | Significant issues found |

## Output

Generate Architecture Alignment section of verification report:
- Summary score (weighted average of all checks)
- Per-check evidence tables
- Items flagged for manual review (confidence <75%)

## Error Handling

- Missing plan.md: FAIL with "Required artifact missing: plan.md"
- Missing api-contract.md: SKIP contract-related checks, note in report
- Parse errors: Flag specific section, continue with other checks
- No key files section in plan.md: SKIP check 1, reduce overall confidence
