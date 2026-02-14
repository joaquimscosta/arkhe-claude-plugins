---
description: Analyze, verify, and resolve GitHub PR review suggestions with a trust-but-verify approach and research-driven decisions
argument-hint: <PR-number or URL>
---

# PR Issue Resolver

Analyze and systematically resolve suggested changes in GitHub Pull Request: $ARGUMENTS

Use the GitHub CLI (`gh`) for all GitHub-related tasks.

## Core Principle: Trust but Verify

**Never assume a review comment is correct.** Reviewers can be wrong — suggestions may be based on misunderstanding the code, outdated patterns, or false assumptions. For every suggestion:

1. **Read the actual code** before accepting any claim
2. **Verify the issue exists** by reproducing it or tracing the logic
3. **Research best practices** when the right approach is unclear
4. **Push back professionally** when a suggestion is a false positive

## Process

### 1. Fetch PR Context

Gather complete PR information in parallel:

- Use `gh pr view $ARGUMENTS` to get PR details (title, description, base/head branches, status, author)
- Use `gh pr diff $ARGUMENTS` to understand the changes introduced
- Use `gh pr comment list $ARGUMENTS` or `gh api` to retrieve all review comments and inline suggestions
- Note CI/CD status and any existing test failures

### 2. Categorize Comments

Review all comments and categorize them:

| Category | Examples |
|----------|----------|
| **Blocker** | Security issues, runtime errors, API contract breaks |
| **Bug/Logic** | Off-by-one errors, null handling, race conditions |
| **Code Quality** | Refactoring, performance, pattern improvements |
| **Style/Clarity** | Variable naming, formatting, comments |
| **Question** | Requests for explanation or rationale |
| **Approval** | Positive feedback, LGTM |

Identify threaded discussions and resolved/unresolved status.

### 3. Verify Each Suggestion

**This is the critical step.** For each non-approval comment:

**a) Read the referenced code.** Open the file and understand the context around the suggestion. Don't rely solely on the diff snippet in the comment.

**b) Assess validity:**

- **Confirmed issue**: The code actually has the problem described. Proceed to resolution.
- **False positive**: The reviewer misunderstood the code, missed context, or the concern doesn't apply. Respond with evidence.
- **Ambiguous**: Multiple valid interpretations exist, or best practice is debatable. Research before deciding.

**c) For false positives**, reply professionally with evidence:
```
Thanks for flagging this. I investigated and this is actually handled by [specific mechanism]:

- [Evidence: test output, code trace, or documentation reference]
- [Why the current approach is correct]

Let me know if I'm missing something.
```

**d) For ambiguous suggestions**, use `/core:research` to determine best practice:
```
/core:research [topic — e.g., "error handling patterns in TypeScript async functions"]
```

Research when:
- The suggestion involves debatable patterns (error handling, naming conventions, architecture choices)
- Multiple valid solutions exist and you're unsure which is best
- You're unfamiliar with a suggested library, API, or pattern
- Reviewer and author disagree on approach

Document research findings in your PR comment when responding.

### 4. Plan Resolutions

For each **confirmed** suggestion:

- Break down into actionable fixes
- Prioritize: **Blockers → Bugs → Code Quality → Style → Questions**
- Consider side effects, regressions, and dependencies
- Check for related dependencies (linked issues, other PRs, codebase impact)

Create a resolution plan that minimizes changes and avoids regressions.

**Edge cases to handle:**
- **Conflicting suggestions**: Different reviewers disagree — research the topic, present findings, and ask for consensus before implementing
- **Regression risk**: A suggestion would fix one thing but break another — flag this in comments with evidence
- **Out-of-scope**: Suggestion is valid but unrelated to this PR — create a follow-up issue with `gh issue create` and link it
- **Reviewer unavailable**: If clarification is needed but reviewer is unresponsive, document your interpretation and proceed with the safest approach

### 5. Apply Changes

Execute the plan:

- Checkout the PR branch: `gh pr checkout $ARGUMENTS`
- For each resolution (in priority order):
  1. Edit code as planned
  2. Run targeted tests to verify the fix
  3. Confirm no regressions in related functionality
  4. Commit immediately with descriptive message referencing the suggestion
     - Example: `fix(auth): validate token expiry — addresses review comment on null handling`

### 6. Test and Verify

Before pushing:

- Run all relevant tests (unit, integration, e2e)
- Verify linting and type checking pass
- Run builds to ensure no compilation errors
- Manual testing if automated tests are insufficient
- Add new tests if suggestions involve bugs or new behavior

If tests fail, investigate root cause — don't skip or force-pass.

### 7. Update PR and Request Re-Review

Finalize the resolution:

- Push updated commits to the PR head branch
- Reply to each comment with resolution status:
  - **Resolved**: "Addressed in commit `abc1234` — [brief description of change]"
  - **False positive**: Evidence-based explanation (see template in step 3c)
  - **Deferred**: "Created follow-up issue #xyz — [reason for deferring]"
- Update PR description if major changes were made
- Re-request reviews: `gh pr review --request <username>`
- Ensure no merge conflicts remain

## Notes

- Keep commits small and focused on individual suggestions
- Reference the review comment in commit messages
- Never blindly apply a suggested code change — verify it's correct first
- For out-of-scope suggestions, create follow-up issues instead
- When in doubt, research with `/core:research` before implementing
- Document assumptions and research findings in PR comments
