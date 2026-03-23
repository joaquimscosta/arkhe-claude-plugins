# PR Issue Resolver: Examples

Real-world scenarios showing the skill in action.

For quick start instructions, see [SKILL.md](SKILL.md).
For detailed workflow, see [WORKFLOW.md](WORKFLOW.md).

---

## Example 1: Standard PR with Mixed Feedback

### Scenario

A PR adding JWT authentication has 5 review comments from two reviewers.

### Command

```bash
/resolve-review 142
```

### Phase 1 — Context Gathering

Two Haiku agents fetch PR metadata and comments in parallel:

- PR #142: "Add JWT authentication middleware" — 4 files changed, CI passing
- 5 unresolved comments: 2 from @alice (security focus), 3 from @bob (code quality)

### Phase 2 — Parallel Verification

5 Sonnet agents verify each comment (all in one batch since <= 5):

| # | Comment | Verdict | Confidence |
|---|---------|---------|------------|
| 1 | @alice: "Token isn't validated for expiry" | CONFIRMED | 95 |
| 2 | @alice: "Missing CORS origin check" | FALSE-POSITIVE | 12 |
| 3 | @bob: "Extract token validation to a helper" | CONFIRMED | 82 |
| 4 | @bob: "Use `const` instead of `let` on line 23" | CONFIRMED | 55 |
| 5 | @bob: "Why not use Passport.js?" | QUESTION | — |

### Phase 3 — Triage Report

```
## Review Issue Triage — myorg/myapp PR #142
5 comments analyzed | 3 actionable (threshold: 80) | 1 false positive | 1 question

### CONFIRMED (2)
| # | Author | File:Line | Category | Confidence | Action |
|---|--------|-----------|----------|------------|--------|
| 1 | @alice | src/auth/middleware.ts:45 | Bug | 95 | Fix: add expiry check |
| 3 | @bob | src/auth/middleware.ts:30 | Code Quality | 82 | Refactor: extract helper |

### FALSE POSITIVE (1)
| # | Author | File:Line | Confidence | Reason |
|---|--------|-----------|------------|--------|
| 2 | @alice | src/auth/cors.ts:12 | 12 | CORS is configured in Express middleware upstream |

### FILTERED (1)
| # | Author | File:Line | Confidence | Reason |
|---|--------|-----------|------------|--------|
| 4 | @bob | src/auth/middleware.ts:23 | 55 | Style nit below threshold |

### QUESTIONS (1)
| # | Author | Comment | Suggested Response |
|---|--------|---------|-------------------|
| 5 | @bob | "Why not Passport.js?" | Custom middleware chosen for minimal footprint |
```

**User approves**: "Go ahead with all of it."

### Phase 4 — Apply Changes

```
Checking out PR #142...
[1/2] Fix: add token expiry validation (src/auth/middleware.ts:45)
  → Running tests... 12 passed
  → Committed: fix(auth): validate token expiry — addresses review comment on null handling
[2/2] Refactor: extract token validation helper (src/auth/middleware.ts:30)
  → Running tests... 12 passed
  → Committed: refactor(auth): extract validateToken helper — addresses review comment on code structure
```

### Phase 5 — Update PR

```
Pushed 2 commits to feature/jwt-auth
Replied to @alice comment #1: "Addressed in commit abc1234 — added expiry check"
Replied to @alice comment #2: "Thanks for flagging. CORS origin is configured in the Express
  middleware layer (see src/app.ts:15). The auth middleware runs after CORS is already applied."
Replied to @bob comment #3: "Addressed in commit def5678 — extracted to validateToken()"
Replied to @bob comment #5: "We chose custom middleware for minimal footprint — Passport.js
  adds 15 dependencies and we only need JWT verification."
Re-requested review from @alice, @bob
```

---

## Example 2: False Positive Heavy

### Scenario

A reviewer misunderstood the React component architecture and left 4 comments, 3 of which are false positives.

### Command

```bash
/resolve-review 87
```

### Phase 3 — Triage Report

```
## Review Issue Triage — myorg/frontend PR #87
4 comments analyzed | 1 actionable | 3 false positives

### CONFIRMED (1)
| # | Author | File:Line | Category | Confidence | Action |
|---|--------|-----------|----------|------------|--------|
| 3 | @charlie | src/hooks/useAuth.ts:22 | Bug | 88 | Fix: add cleanup in useEffect |

### FALSE POSITIVE (3)
| # | Author | File:Line | Confidence | Reason |
|---|--------|-----------|------------|--------|
| 1 | @charlie | src/components/Modal.tsx:15 | 10 | XSS concern — React auto-escapes JSX output |
| 2 | @charlie | src/components/Form.tsx:40 | 18 | "Missing validation" — handled by Zod schema on line 12 |
| 4 | @charlie | src/pages/Dashboard.tsx:8 | 20 | "Component re-renders too often" — already wrapped with React.memo |
```

### Phase 5 — Replies

The false positive replies are professional and evidence-based:

```
@charlie comment #1:
Thanks for flagging XSS concerns. React auto-escapes all values embedded in JSX,
so `{user.name}` is safe. We'd only need explicit sanitization if we were using
raw HTML injection APIs, which we don't use in this component. See React docs on
built-in XSS protection.

@charlie comment #2:
Good catch to look for validation — it's handled by the Zod schema defined on
line 12 of this file. The `formSchema.parse()` call on line 38 validates all
fields before submission. Let me know if the schema needs additional constraints.
```

---

## Example 3: Conflicting Reviewer Suggestions

### Scenario

Two reviewers disagree on error handling strategy for an API endpoint.

### Command

```bash
/resolve-review 203
```

### Phase 3 — Triage Report

```
## Review Issue Triage — myorg/api PR #203
3 comments analyzed | 1 actionable | 2 ambiguous

### CONFIRMED (1)
| # | Author | File:Line | Category | Confidence | Action |
|---|--------|-----------|----------|------------|--------|
| 1 | @alice | src/api/users.ts:67 | Bug | 91 | Fix: handle 404 case |

### AMBIGUOUS (2)
| # | Author | File:Line | Options |
|---|--------|-----------|---------|
| 2 | @alice | src/api/users.ts:45 | Use try/catch with typed errors (Alice's preference) |
| 3 | @bob | src/api/users.ts:45 | Use Result<T,E> pattern (Bob's preference) |

Note: Comments #2 and #3 conflict — both address error handling at the same location.
```

### User Decision

User is presented with both options:

```
Comments #2 and #3 conflict on error handling at src/api/users.ts:45:

Option A (@alice): try/catch with typed error classes
  + Familiar pattern, matches existing codebase
  - Verbose, error types can drift

Option B (@bob): Result<T,E> monad pattern
  + Type-safe, explicit error paths
  - New pattern, team unfamiliar

Which approach do you prefer?
```

User chooses: "Option A — matches what we already do."

### Phase 5 — Reply

```
@bob comment #3:
Thanks for the Result<T,E> suggestion — it's a solid pattern. After discussion,
we decided to stick with try/catch + typed errors to maintain consistency with
the rest of the API layer. We may revisit this pattern for future modules.
```

---

## Example 4: Out-of-Scope Suggestions

### Scenario

A reviewer leaves valid suggestions that are unrelated to the PR's purpose.

### Command

```bash
/resolve-review 156
```

### Phase 3 — Triage Report

```
## Review Issue Triage — myorg/api PR #156
4 comments analyzed | 1 actionable | 1 out-of-scope | 2 false positives

### CONFIRMED (1)
| # | Author | File:Line | Category | Confidence | Action |
|---|--------|-----------|----------|------------|--------|
| 1 | @dave | src/api/orders.ts:89 | Bug | 94 | Fix: handle empty cart |

### OUT-OF-SCOPE (1)
| # | Author | File:Line | Suggestion |
|---|--------|-----------|------------|
| 3 | @dave | src/api/orders.ts:12 | "This whole file needs better test coverage" |
```

### Phase 4-5 — Resolution

The out-of-scope suggestion gets a follow-up issue:

```bash
gh issue create --title "Improve test coverage for orders API" \
  --body "Identified during PR #156 review by @dave.

The orders API module currently has limited test coverage.
Suggested areas: edge cases for empty cart, payment failures, concurrent orders.

Ref: PR #156 review comment"
```

Reply:
```
@dave comment #3:
Valid point — I've created issue #234 to track test coverage improvements
for the orders module. Out of scope for this PR (focused on cart validation)
but definitely worth addressing.
```

---

## Example 5: File Mode — Local Review Report

### Scenario

A code review was generated locally using `/review:code-review` and saved to a file. The developer wants to resolve the findings without PR context.

### Command

```bash
/resolve-review reviews/code/2026-03-18_14-30-00_code-review.md
```

### Phase 1 — File Parsing

The Haiku agent parses the review file and extracts:

```
4 findings extracted from reviews/code/2026-03-18_14-30-00_code-review.md:
1. [Blocker] src/auth/middleware.ts:45 — JWT secret used without null check (Source: Security)
2. [Improvement] src/api/routes.ts:23 — Missing rate limit on public endpoint (Source: Bug Scan)
3. [Improvement] src/db/queries.ts:67 — N+1 query in user list endpoint (Source: Bug Scan)
4. [Nit] src/utils/format.ts:12 — Unused import (Source: CLAUDE.md)
```

### Phase 2-3 — Verification and Triage

Same verification flow as PR mode. The triage report omits PR-specific fields:

```
## Review Issue Triage — Local Review
4 findings analyzed | 3 actionable | 1 filtered

### CONFIRMED (3)
| # | File:Line | Category | Confidence | Action |
|---|-----------|----------|------------|--------|
| 1 | src/auth/middleware.ts:45 | Blocker | 95 | Fix: add env var validation |
| 2 | src/api/routes.ts:23 | Code Quality | 83 | Fix: add rate limiter |
| 3 | src/db/queries.ts:67 | Code Quality | 81 | Fix: use JOIN instead of N+1 |

### FILTERED (1)
| # | File:Line | Confidence | Reason |
|---|-----------|------------|--------|
| 4 | src/utils/format.ts:12 | 55 | Linter territory — below threshold |
```

### Phase 4 — Apply Changes

Fixes are applied to the current branch (no PR checkout):

```
Using current branch: feat/jwt-auth
[1/3] Fix: add JWT_SECRET validation (src/auth/middleware.ts:45)
  → Committed: fix(auth): validate JWT_SECRET env var — addresses review finding on null handling
[2/3] Fix: add rate limiter to public endpoint (src/api/routes.ts:23)
  → Committed: fix(api): add rate limit to public routes — addresses review finding on missing limits
[3/3] Fix: replace N+1 with JOIN (src/db/queries.ts:67)
  → Committed: fix(db): use JOIN for user list query — addresses review finding on N+1 pattern
```

### Phase 5 — Skipped

No PR to update in file mode. The fixes are committed locally for the user to push when ready.

---

## Common Patterns

1. **Most PRs have some false positives**: Expect 20-40% of comments to be filtered. This is normal — reviewers often flag concerns based on incomplete context.
2. **Confidence scoring prevents over-correction**: Without scoring, you'd blindly apply every suggestion. The threshold ensures only high-confidence issues get fixed.
3. **Questions deserve thoughtful responses**: Don't dismiss "Why?" questions — they often reveal misunderstandings that, if left unaddressed, lead to the same feedback on future PRs.
4. **File mode is great for self-review**: Run `/review:code-review` first, then `/resolve-review` on the report to fix findings before opening a PR.
5. **One commit per fix**: Keeps the git history clean and makes it easy for reviewers to see exactly what was changed for each comment.
