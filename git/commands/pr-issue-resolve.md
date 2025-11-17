---
description: Analyze and resolve GitHub PR review suggestions systematically
argument-hint: <PR-number or URL>
---

# PR Issue Resolver

Analyze and systematically resolve suggested changes in GitHub Pull Request: $ARGUMENTS

Use the GitHub CLI (`gh`) for all GitHub-related tasks.

## Process

### 1. Fetch PR Context

Gather complete PR information in parallel:
- Use `gh pr view $ARGUMENTS` to get PR details (title, description, base/head branches, status)
- Use `gh pr diff $ARGUMENTS` to understand the changes introduced
- Use `gh pr comment list $ARGUMENTS` or `gh api` to retrieve all review comments and inline suggestions

### 2. Analyze and Categorize Comments

Review all comments and categorize them:
- **Bugs/Issues**: Critical problems that break functionality or edge cases
- **Code Changes**: Suggestions for refactoring, async/await, algorithm improvements
- **Style/Nitpicks**: Variable naming, formatting, code clarity
- **Questions**: Requests for clarification or explanation
- **Approvals**: General positive feedback

Identify threaded discussions and resolved/unresolved status.

### 3. Plan Resolutions

For each suggestion:
- Break down into actionable fixes
- Prioritize: **Blockers (bugs) → Features → Style → Questions**
- Consider edge cases, performance, security, and compatibility
- Check for related dependencies (linked issues, other PRs, codebase impact)
- Ask clarification questions if suggestions are ambiguous

Create a resolution plan that minimizes changes and avoids regressions.

### 4. Apply Changes

Execute the plan:
- Checkout the PR branch: `gh pr checkout $ARGUMENTS`
- Apply fixes in small, incremental commits with clear messages
  - Example: `fix(auth): handle null tokens per review suggestion`
- For each change:
  - Edit code as planned
  - Test the specific change
  - Commit immediately with descriptive message

### 5. Test and Verify

Before pushing:
- Run all relevant tests (unit, integration, e2e)
- Verify linting and type checking pass
- Run builds to ensure no compilation errors
- Manual testing if automated tests are insufficient
- Add new tests if suggestions involve bugs or new behavior

### 6. Update PR and Request Re-Review

Finalize the resolution:
- Push updated commits to the PR head branch
- Reply to each comment: `gh pr comment` with "Addressed in commit XYZ"
- Update PR description if major changes were made
- Re-request reviews: `gh pr review --request <username>`
- Ensure no merge conflicts remain
- Update labels if needed (e.g., "ready-for-review")

## Notes

- Keep commits small and focused on individual suggestions
- Reference the review comment or suggestion in commit messages
- For out-of-scope suggestions, create follow-up issues instead
- Document any assumptions or constraints in PR comments
