# PR Issue Resolver: Detailed Workflow

Detailed methodology for multi-agent review resolution, including agent prompt templates, scoring rubric, and reply formats.

For quick start instructions, see [SKILL.md](SKILL.md).

---

## Input Mode Detection

### PR Mode

Detect when `$ARGUMENTS` is a PR number or URL:

```
123                                    → PR number
https://github.com/org/repo/pull/123   → extract PR number from URL
gh pr view 123                         → verify PR exists
```

Required: `gh auth status` must succeed with repo access.

### File Mode

Detect when `$ARGUMENTS` is a file path:

```
reviews/code/2026-03-18_code-review.md → relative path
/absolute/path/to/review.md            → absolute path
./review-report.md                     → current directory
```

Verify the file exists with Read tool. Parse findings from the report.

**Supported report formats**:
- Code-review skill reports (`review/skills/code-review/` template): look for `## Findings` section with `**[Blocker]**`, `**[Improvement]**`, `**[Question]**` markers
- Generic markdown: look for numbered/bulleted lists with file:line references
- Plain text: extract actionable items with file references

---

## Phase 1 — Agent Prompt Templates

### Agent A — PR Metadata (Haiku)

```
You are extracting PR metadata for review resolution.

Run these commands and return a structured summary:

1. PR details:
   gh pr view {number} --json number,title,body,baseRefName,headRefName,state,author,reviewRequests,statusCheckRollup

2. Diff (file names only for overview):
   gh pr diff {number} --name-only

3. Full diff (for verification context):
   gh pr diff {number}

Return:
- PR title and description summary
- Base and head branches
- Author
- CI status: pass/fail/pending/none
- Files changed (list)
- Review requestees (who needs to re-approve)
```

### Agent B — Comment Extraction (Haiku)

```
You are extracting all review comments from a GitHub PR for resolution.

Fetch comments from BOTH endpoints (they are different):

1. Inline review comments (attached to specific code lines):
   gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate

2. General issue comments (not attached to code):
   gh api repos/{owner}/{repo}/issues/{number}/comments --paginate

For each comment, extract:
- id: the comment ID (needed for replies)
- author: who wrote it
- type: "inline" or "general"
- file: file path (inline only)
- line: line number (inline only)
- body: full comment text
- resolved: true/false (check if the review thread is resolved)
- has_suggestion: true if body contains a ```suggestion code block
- created_at: timestamp

Filter OUT:
- Comments by the PR author (self-comments)
- Bot comments (CI status, coverage reports)
- Already-resolved threads
- Pure approval comments ("LGTM", "Looks good", thumbs up)

Return: structured JSON-like list of actionable comments, sorted by file path.
```

### File Mode Agent (Haiku)

```
You are parsing a code review report file to extract actionable findings.

Read the file and extract each finding with:
- description: what the issue is
- file: file path referenced
- line: line number (if available)
- category: Blocker / Improvement / Question / Nit (from report markers)
- suggested_fix: code suggestion (if provided)
- source: which reviewer/category found it (if available)

Skip:
- Praise items
- Informational notes without actionable suggestions
- Summary/metadata sections

Return: structured list of actionable findings.
```

---

## Phase 2 — Verification Agent Template

### Sonnet Verification Agent

Each verification agent receives one comment/finding and returns a verdict.

```
You are verifying a review comment against the actual codebase.

REVIEW COMMENT:
{comment body}

REFERENCED FILE (50 lines of context):
{file content around the referenced line}

PR DIFF (or branch diff):
{relevant diff section}

PR DESCRIPTION:
{PR title and body summary}

YOUR TASK:
1. Read the actual code — do NOT rely solely on the comment's claims
2. Determine if the issue described actually exists in the code
3. Check if the suggestion would actually improve the code
4. Consider whether the current approach might be intentional

RETURN (all fields required):
Verdict: CONFIRMED | FALSE-POSITIVE | AMBIGUOUS
Category: Blocker | Bug | Code Quality | Style | Question
Confidence: 0-100 (see rubric below)
Evidence: What you checked and what you found. Be specific — cite code lines.
Suggested resolution: Either a specific code change, a response to post, or options if ambiguous.

FALSE POSITIVE INDICATORS (skip these):
- Reviewer misunderstood the code or missed surrounding context
- Concern is handled by the framework (e.g., XSS in React, CSRF in Rails)
- Suggestion contradicts established codebase patterns
- Issue is pre-existing and not introduced by this PR
- Concern is purely stylistic with no functional impact
- Reviewer's suggestion would actually introduce a bug
- The "issue" is a deliberate design choice documented in comments

AMBIGUOUS INDICATORS (mark as AMBIGUOUS, not FALSE-POSITIVE):
- Multiple valid approaches exist
- Best practice is genuinely debatable
- Reviewer and code author may have different valid perspectives
- Performance trade-off with no clear winner

CONFIDENCE RUBRIC:
- 0-24: False positive — doesn't hold up to code inspection
- 25-49: Plausible concern but likely misunderstanding
- 50-74: Valid observation but minor or nitpick
- 75-89: Real issue, important, impacts functionality
- 90-100: Critical — confirmed bug, security hole, or data loss risk
```

### Batching Strategy

For PRs with many comments (>5):
- Batch verification agents into groups of 5
- Launch each batch in parallel
- Wait for batch to complete before launching next
- This prevents overwhelming the system with too many concurrent agents

For PRs with 5 or fewer comments, launch all agents in parallel.

---

## Comment Categorization Taxonomy

| Category | Examples | Priority |
|----------|----------|----------|
| **Blocker** | Security vulnerabilities, runtime crashes, API contract breaks, data loss | 1 (highest) |
| **Bug** | Off-by-one errors, null handling, race conditions, incorrect logic | 2 |
| **Code Quality** | Refactoring, performance improvements, pattern adherence | 3 |
| **Style** | Variable naming, formatting, comment clarity | 4 |
| **Question** | Requests for explanation, rationale, or documentation | 5 (lowest) |

---

## False Positive Filtering Rules

Apply before including any finding in the triage report.

### Hard Exclusions

1. **Reviewer misread the code**: The concern describes behavior that doesn't match what the code actually does
2. **Framework-handled**: The concern is addressed by the framework's built-in protections (React XSS, Django CSRF, Spring Security)
3. **Already addressed**: The code already handles the concern in a way the reviewer missed (e.g., validation happens upstream)
4. **Pre-existing**: The issue exists on unchanged lines and was not introduced by this PR
5. **Codebase convention**: The code follows an established pattern used elsewhere in the project
6. **Linter territory**: Formatting, import order, whitespace — defer to automated tools
7. **Intentional choice**: Comments or commit messages indicate the approach was deliberate

### Signal Quality Check

For remaining findings, verify:
1. Is there a concrete, demonstrable impact?
2. Is the suggestion actionable with a specific fix?
3. Would a senior engineer confidently raise this?

If any answer is "no," lower the confidence score accordingly.

---

## Confidence Scoring — Detailed Rubric

| Score | Meaning | Examples |
|-------|---------|----------|
| 90-100 | **Certain** — clear bug or vulnerability with evidence | Missing null check causing crash; SQL injection via string concat; auth bypass |
| 75-89 | **Strong** — very likely real, important | Missing error handling on critical path; potential race condition; N+1 query |
| 50-74 | **Moderate** — verified but minor or debatable | Naming could be clearer; slightly inefficient but functional; style preference |
| 25-49 | **Weak** — plausible but unverifiable | "This might fail under load"; pattern that "seems wrong" without evidence |
| 0-24 | **False positive** — doesn't survive scrutiny | Reviewer misread code; framework handles it; pre-existing issue |

**Threshold**: Filter out all findings scoring below **80**.

If a verification agent fails (timeout, error), default the finding's score to **80** (conservative — keep it in the report rather than silently dropping a potential real issue).

---

## Triage Report Template

```markdown
## Review Issue Triage — {owner}/{repo} PR #{number}
{N} comments analyzed | {M} actionable (threshold: 80) | {K} false positives filtered

### CONFIRMED ({count})
| # | Author | File:Line | Category | Confidence | Recommended Action |
|---|--------|-----------|----------|------------|-------------------|
| 1 | @reviewer | src/auth.ts:45 | Bug | 92 | Fix: add null check before access |
| 2 | @reviewer | src/api.ts:12 | Code Quality | 85 | Refactor: extract validation |

### FALSE POSITIVE ({count})
| # | Author | File:Line | Confidence | Reason |
|---|--------|-----------|------------|--------|
| 3 | @reviewer | src/db.ts:33 | 15 | Handled by ORM validation layer |

### AMBIGUOUS ({count})
| # | Author | File:Line | Options |
|---|--------|-----------|---------|
| 4 | @reviewer | src/config.ts:78 | A: Use env var / B: Keep hardcoded default |

### QUESTIONS ({count})
| # | Author | Comment | Suggested Response |
|---|--------|---------|-------------------|
| 5 | @reviewer | "Why not use X here?" | Explain: Y was chosen because... |

---
**Next step**: Approve this plan to proceed with fixes, or modify individual items.
```

---

## Resolution Planning

### Priority Ordering

Apply fixes in this order to minimize cascading issues:

1. **Blockers** — security, crashes, data loss
2. **Bugs** — logic errors, null handling
3. **Code Quality** — refactoring, performance
4. **Style** — naming, formatting
5. **Questions** — respond with explanations

### Edge Cases

**Conflicting suggestions**: Two reviewers suggest different approaches.
- Mark as AMBIGUOUS
- Present both options with pros/cons
- Let user decide before implementing
- If reviewers are available, suggest asking for consensus in a thread

**Regression risk**: A fix would solve one issue but break another.
- Flag in the triage report: "Warning: this fix may affect [related functionality]"
- Suggest mitigations (additional tests, guard clauses)
- Let user decide whether the trade-off is acceptable

**Out-of-scope suggestions**: Valid but unrelated to this PR.
- Acknowledge the suggestion
- Create a follow-up issue: `gh issue create --title "..." --body "Identified during PR #X review"`
- Reply with: "Valid suggestion — created follow-up issue #Y"

**Multiple options offered**: Reviewer suggests "Option A: ... or Option B: ...".
- Present all options to the user
- Do NOT choose autonomously
- Include pros/cons for each if available

**Reviewer unavailable**: Need clarification but reviewer is unresponsive.
- Document your interpretation in the reply
- Proceed with the safest approach
- Note: "Proceeding with [approach] based on [reasoning]. Happy to adjust if you had something else in mind."

### Commit Message Format

```
fix(scope): brief description — addresses review comment on [topic]
```

Examples:
```
fix(auth): validate token expiry before access — addresses review comment on null handling
fix(api): add rate limit headers to response — addresses review comment on missing headers
refactor(db): extract query builder — addresses review comment on code duplication
```

One commit per fix. Reference the review comment topic, not the comment ID (IDs are opaque to readers).

---

## Comment Reply Formats

### Inline Review Comments (Code-Level)

Reply in-thread using the GitHub API:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies \
  -f body="Addressed in commit \`abc1234\` — added null check before token access.

The validation now throws early if the token is expired, preventing the downstream NPE."
```

### General PR Comments (Issue-Level)

GitHub issue comments do NOT support threading. Post a **single consolidated response** with anchor links:

```markdown
Thanks for the thorough review! Here's the resolution for each item:

### Re: [Null check on token](#issuecomment-12345)
Addressed in commit `abc1234` — added validation before access.

### Re: [Rate limit headers](#issuecomment-12346)
Addressed in commit `def5678` — added X-RateLimit-* headers to all API responses.

### Re: [Extract query builder](#issuecomment-12347)
Created follow-up issue #89 — valid suggestion but out of scope for this PR.

### Re: [Why not use Redis here?](#issuecomment-12348)
We chose PostgreSQL advisory locks because [reason]. The trade-off is [X] but it avoids [Y]. Happy to discuss further.
```

### False Positive Reply Template

```markdown
Thanks for flagging this. I investigated and this is actually handled by [specific mechanism]:

- [Evidence: code trace, test output, or documentation reference]
- [Why the current approach is correct]

Let me know if I'm missing something.
```

### Deferred Reply Template

```markdown
Valid suggestion — I've created follow-up issue #{number} to track this.

This is out of scope for the current PR because [reason], but it's worth addressing separately.
```

---

## Research for Ambiguous Suggestions

When a suggestion is marked AMBIGUOUS and involves debatable patterns:

1. Use `/core:research` to investigate best practices:
   ```
   /core:research [topic — e.g., "error handling patterns in TypeScript async functions"]
   ```

2. Research when:
   - Multiple valid solutions exist and you're unsure which is best
   - Reviewer and author disagree on approach
   - You're unfamiliar with a suggested library, API, or pattern
   - The suggestion involves architecture or design decisions

3. Include research findings in the PR comment:
   ```markdown
   I researched this and found that [finding]. Based on [source/pattern],
   I went with [approach] because [reasoning]. The alternative ([other approach])
   would [trade-off].
   ```

---

## Phase Transition Logic

- **Phase 1 → Phase 2**: Wait for all Phase 1 agents. If zero actionable comments, report "Nothing to resolve" and stop.
- **Phase 2 → Phase 3**: Collect all verdicts. Deduplicate: if two findings reference the same file:line, merge them. If all agents fail, fall back to manual sequential verification.
- **Phase 3 → Phase 4**: User must explicitly approve the plan. Do not proceed without approval.
- **Phase 4 → Phase 5**: After all approved changes are committed, push and reply. If tests fail on any fix, stop and report — do not push broken code.
- **File mode**: Skip Phase 5 entirely (no PR to update). Optionally commit fixes to the current branch.

### Error Handling

- **Agent timeout**: Continue with results from successful agents. Note in report: "Note: verification for comment #{id} did not complete."
- **All agents fail**: Fall back to sequential verification — read the code yourself and assess each comment directly.
- **gh CLI failure**: Check `gh auth status`. If rate-limited, wait and retry. If permission denied, inform the user.
- **Merge conflict on push**: Rebase the branch and retry. If conflicts persist, inform the user.
