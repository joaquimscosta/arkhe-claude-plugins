# Code Review Workflow

Detailed review checklists, agent prompt templates, scoring rubric, report template, and GitHub comment format.

---

## Multi-Agent Pipeline Details

### Agent Prompt Templates

Each Phase 2 reviewer agent receives this shared context preamble:

```
You are reviewing code changes. Here is your context:

CLAUDE.md FILES:
{claude_md_summaries from Phase 1 Agent A}

CHANGE SUMMARY:
{summary from Phase 1 Agent B}

DIFF CONTENT:
{full diff}

FALSE POSITIVES TO SKIP:
- Pre-existing issues not introduced in the changes
- Issues that linters, typecheckers, or compilers would catch
- Pedantic nitpicks a senior engineer wouldn't flag
- Framework-handled concerns
- General quality issues unless explicitly required in CLAUDE.md
- Style preferences matching existing codebase conventions
- Real issues on lines the author did not modify
- Something that looks like a bug but is not actually a bug
- Changes in functionality that are likely intentional
- Issues explicitly silenced in code (lint-ignore comments)

Return findings in this format (one per finding):

Finding: {description}
File: {path}:{line}
Category: {your category}
Reason: {why this was flagged, cite evidence}
Suggested fix: {code snippet, if applicable}

If no issues found, return: "No issues found."
```

#### Reviewer 1 — CLAUDE.md Compliance

```
Your role: Audit code changes for compliance with the project's CLAUDE.md guidelines.

Rules:
- Only flag items SPECIFICALLY called out in a CLAUDE.md file
- Double-check that the CLAUDE.md actually requires what you are flagging
- CLAUDE.md is guidance for Claude as it writes code — not all instructions are applicable during code review
- If an issue is silenced in code (lint-ignore comment), do not flag it
- Use Category: CLAUDE.md

Focus on: naming conventions, architecture patterns, forbidden patterns, required practices, testing requirements, and any explicit "NEVER" or "ALWAYS" rules in the CLAUDE.md files.
```

#### Reviewer 2 — Bug Scanner

```
Your role: Shallow scan for obvious bugs in the code changes ONLY.

Rules:
- Focus on LARGE bugs — ignore small issues and nitpicks
- Only look at the diff content — do NOT read extra context beyond the changes
- Ignore issues that a linter, typechecker, or compiler would catch (missing imports, type errors, formatting)
- Ignore pre-existing issues on unchanged lines
- Use Category: Bug

Focus on: null/undefined errors, off-by-one errors, logic inversions, missing error handling on critical paths, incorrect API usage, broken control flow, data loss scenarios.
```

#### Reviewer 3 — Git Blame/History Analyzer

```
Your role: Analyze git blame and history of modified files to identify issues in historical context.

Rules:
- Read git blame for each modified file to understand the history
- Read recent commits touching these files for context
- Use Category: History

Focus on: reverted changes being re-introduced, recently-fixed bugs in the same area, breaking patterns established by previous authors, ignoring guidance from previous PR comments, modifying areas that were specifically stabilized.

Commands to use:
- git blame {file} — for each modified file
- git log --oneline -10 -- {file} — recent history per file
- git log --all --oneline --grep="fix" -- {file} — find previous fixes
```

#### Reviewer 4 — Security Reviewer

```
Your role: Security-focused scan of code changes.

Rules:
- Only report HIGH confidence exploitable findings
- Do not flag theoretical or speculative security issues
- Use Category: Security

Focus on:
- Input validation: SQL injection, XSS, command injection, path traversal
- Authentication/authorization: bypasses, missing checks, privilege escalation
- Secrets: hardcoded API keys, tokens, passwords, credentials in code
- Data exposure: PII in logs, verbose error messages, sensitive data in responses
- Cryptographic issues: weak algorithms, improper key management
- SSRF, open redirects, insecure deserialization
```

#### Reviewer 5 — Code Comments Compliance (conditional)

```
Your role: Ensure code changes comply with guidance in code comments.

Rules:
- Only launch if modified files contain substantive comments: // NOTE:, // IMPORTANT:, // INVARIANT:, // SAFETY:, // TODO:, // HACK:, // WARNING:
- Check that changes respect the intent documented in those comments
- Use Category: Comments

Focus on: violated invariants, ignored safety notes, broken assumptions documented in comments, TODO items that are now relevant to the change.
```

### Agent Output Format

Each reviewer returns structured findings. Example:

```
Finding: JWT secret read from environment without validation — if missing, jwt.verify() silently accepts any token
File: src/auth/middleware.ts:45
Category: Security
Reason: process.env.JWT_SECRET used directly without null check. jwt.verify(token, undefined) is a known bypass.
Suggested fix:
const secret = process.env.JWT_SECRET;
if (!secret) throw new Error('JWT_SECRET environment variable is required');
const decoded = jwt.verify(token, secret);
```

### Phase Transition Logic

- **Phase 1 → Phase 2**: Wait for both Haiku agents to complete. If Agent A finds no CLAUDE.md files, skip Reviewer 1 (CLAUDE.md compliance). If Agent B indicates Low risk + test-only/docs-only change, consider running fewer reviewers.
- **Phase 2 → Phase 3**: Collect all findings from all reviewers. Deduplicate: if two reviewers flag the same file:line, keep the more detailed finding. If no findings from any reviewer, skip Phase 3 and generate a clean report.
- **Phase 3 → Phase 4**: Filter findings below 80. If all filtered, generate clean report.
- **Phase 4 → Phase 5**: Report always generated. Phase 5 only runs if `--post-to-pr` flag was set.
- **Phase 5 → Phase 6**: Phase 6 always runs (unless Skill tool unavailable).

### Error Handling

- If a reviewer agent fails (timeout, error): continue with results from successful agents. Add note to report: "Note: {reviewer-name} did not complete. Partial review."
- If ALL reviewers fail: fall back to single-agent review — analyze the diff directly using the Hierarchical Review Framework below.
- If a scoring agent fails for a finding: default that finding's score to 75 (conservative — just below threshold).

---

## Hierarchical Review Framework

Reference material for review agents and single-agent fallback.

### 1. Architectural Design & Integrity (Critical)

- Evaluate if the design aligns with existing architectural patterns and system boundaries
- Assess modularity and adherence to Single Responsibility Principle
- Identify unnecessary complexity — could a simpler solution achieve the same goal?
- Verify the change is atomic (single, cohesive purpose) not bundling unrelated changes
- Check for appropriate abstraction levels and separation of concerns

### 2. Functionality & Correctness (Critical)

- Verify the code correctly implements the intended business logic
- Identify handling of edge cases, error conditions, and unexpected inputs
- Detect potential logical flaws, race conditions, or concurrency issues
- Validate state management and data flow correctness
- Ensure idempotency where appropriate

### 3. Security (Non-Negotiable)

- Verify all user input is validated, sanitized, and escaped (XSS, SQLi, command injection prevention)
- Confirm authentication and authorization checks on all protected resources
- Check for hardcoded secrets, API keys, or credentials
- Assess data exposure in logs, error messages, or API responses
- Validate CORS, CSP, and other security headers where applicable
- Review cryptographic implementations for standard library usage

### 4. Maintainability & Readability (High Priority)

- Assess code clarity for future developers
- Evaluate naming conventions for descriptiveness and consistency
- Analyze control flow complexity and nesting depth
- Verify comments explain 'why' (intent/trade-offs) not 'what' (mechanics)
- Check for appropriate error messages that aid debugging
- Identify code duplication that should be refactored

### 5. Testing Strategy & Robustness (High Priority)

- Evaluate test coverage relative to code complexity and criticality
- Verify tests cover failure modes, security edge cases, and error paths
- Assess test maintainability and clarity
- Check for appropriate test isolation and mock usage
- Identify missing integration or end-to-end tests for critical paths

### 6. Performance & Scalability (Important)

- **Backend**: Identify N+1 queries, missing indexes, inefficient algorithms
- **Frontend**: Assess bundle size impact, rendering performance, Core Web Vitals
- **API Design**: Evaluate consistency, backwards compatibility, pagination strategy
- Review caching strategies and cache invalidation logic
- Identify potential memory leaks or resource exhaustion

### 7. Dependencies & Documentation (Important)

- Question necessity of new third-party dependencies
- Assess dependency security, maintenance status, and license compatibility
- Verify API documentation updates for contract changes
- Check for updated configuration or deployment documentation

---

## Diff-Context Awareness

Go beyond the diff to detect cross-file impacts:

### Context Probes

| Trigger in Diff | Context Action |
|-----------------|----------------|
| Function/method signature changed | Search for callers outside the diff using Grep |
| Export removed or renamed | Check all importers across the codebase |
| Database schema changed | Verify migration has rollback; check ORM models |
| API response structure changed | Search for downstream consumers |
| Shared type/interface modified | Find all files using that type |
| Config key added/renamed | Check deployment configs, CI/CD, and docs |

### When to Ask Questions vs. Assert

- If context outside the diff could justify the change, use **[Question]** not **[Blocker]**
- Example: "Is this timeout intentionally set to 0, or should it use the default?"
- Only assert a finding as Blocker when you can verify the issue from the diff + context probes

---

## False Positive Filtering

Apply these rules before finalizing findings. Discard any finding that matches a hard exclusion.

### Hard Exclusions

1. **Style-only issues** — defer to linters (formatting, import order, trailing whitespace)
2. **Theoretical performance** — do not flag without measurable impact or Big-O degradation
3. **Subjective preferences** — discard if you cannot cite a named engineering principle
4. **Test-only file issues** — do not flag patterns in test files that don't affect production code
5. **Framework-handled concerns** — do not flag concerns handled by the framework's security model
6. **Missing features not in scope** — do not flag features the changes didn't intend to add
7. **Consistent naming** — do not nitpick naming that matches the existing codebase convention
8. **Established patterns** — do not flag code patterns used elsewhere in the codebase as issues
9. **Code outside the diff** — do not report on unchanged code unless directly impacted by the change
10. **Vague suggestions** — discard any finding that says "could be improved" without specific impact

### Signal Quality Criteria

For each remaining finding, verify:
1. Is there a concrete, demonstrable impact (bug, security risk, performance degradation, maintenance burden)?
2. Can you name the engineering principle being violated?
3. Is the suggestion actionable with a specific fix (not just "consider improving")?
4. Would a senior engineer confidently raise this in a PR review?

If any answer is "no," suppress the finding.

---

## Confidence Scoring (0-100 Scale)

### Scoring Rubric

| Score | Meaning | Examples |
|-------|---------|----------|
| 90-100 | Certain — clear bug, vulnerability, or violation with evidence | SQL injection via string interpolation; missing null check causing crash; explicit CLAUDE.md violation |
| 75-89 | Strong evidence — very likely real, important and impactful | Missing error handling on critical API call; potential race condition in concurrent path; N+1 query |
| 50-74 | Moderate — verified but minor or nitpick | Naming that's unclear but functional; could be slow at scale without metrics |
| 25-49 | Weak — might be real, unable to verify | Speculative concern; pattern that "seems wrong" without evidence |
| 0-24 | False positive — doesn't hold up to scrutiny | Pre-existing issue; framework-handled concern; linter territory |

### Threshold & Triage Mapping

| Score | Action | Triage Level |
|-------|--------|--------------|
| 90-100 | Report | Blocker (if severity warrants) or Improvement |
| 80-89 | Report | Improvement or Question |
| Below 80 | Filter out | Do not include in report |

### Deduplication

If two reviewers flag the same issue (same file:line or overlapping concern):
- Keep the higher-confidence version
- Merge context from both if complementary
- Do not report the same issue twice

---

## Communication Principles

### Actionable Feedback
Provide specific, actionable suggestions. Include file path and line number for every finding.

### Before/After Code Blocks
Blocker and Improvement findings must include code showing current state and suggested fix:

```
Current (`file:line`):
  code here

Suggested:
  improved code here
```

### Explain the "Why"
When suggesting changes, explain the underlying engineering principle:
- **Security**: OWASP Top 10, defense-in-depth, least privilege
- **Design**: Specific SOLID principle, DRY, KISS, YAGNI
- **Performance**: Big-O impact, specific metric or query pattern
- **Testing**: Test pyramid, test isolation, coverage strategy

### Constructive Tone
Maintain objectivity and assume good intent. The goal is net improvement, not perfection.

---

## Report Template

```markdown
# Pragmatic Code Review Report

**Date**: {ISO 8601 date}
**Branch**: {current branch name}
**Commit**: {short commit hash}
**Reviewer**: Claude Code (multi-agent code review)
**Review Mode**: Multi-Agent Orchestration ({N} reviewers, confidence threshold: 80)

## PR Assessment

| Attribute | Value |
|-----------|-------|
| **Risk Level** | {Low / Medium / High / Critical} |
| **Change Type** | {Feature / Bugfix / Refactor / Config / Test-only / Docs} |
| **Atomicity** | {Atomic / Mixed — consider splitting} |
| **Breaking Changes** | {None / Yes — description} |

---

## Summary

[Overall assessment: Is this change a net positive? High-level observations about the approach, architecture, and quality.]

## Findings

### Blockers

- **[Blocker]** `{file}:{line}` — {Description} (Confidence: {N}/100, Source: {category})
  - **Principle**: {Named engineering principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`

### Improvements

- **[Improvement]** `{file}:{line}` — {Suggestion and rationale} (Confidence: {N}/100, Source: {category})
  - **Principle**: {Named engineering principle}
  - **Current**: `{code snippet}`
  - **Suggested**: `{fix snippet}`

### Questions

- **[Question]** `{file}:{line}` — {Clarification needed} (Source: {category})

### Praise

- **[Praise]** `{file}:{line}` — {What was done well and why it matters}

### Nitpicks

- **[Nit]** `{file}:{line}` — {Minor detail}

## Verdict

- **Recommendation**: {Approve / Request Changes / Approve with Nits}
- **Risk Level**: {Low / Medium / High / Critical}
- **Blockers**: {count}
- **Improvements**: {count}
- **Questions**: {count}
- **Nits**: {count}
```

---

## GitHub PR Comment Format

Used in Phase 5 when `--post-to-pr` is enabled. Keep comments brief and link to code with full SHA.

### Comment Template

```markdown
### Code review

Found {N} issues:

1. {brief description} ({source}: "{evidence or CLAUDE.md quote}")

{link to file with full SHA and line range}

2. {brief description} ({source}: "{evidence}")

{link to file with full SHA and line range}

---

Generated with [Claude Code](https://claude.ai/code)

<sub>If this review was useful, react with :+1:. Otherwise, react with :-1:.</sub>
```

### Clean Review Comment

```markdown
### Code review

No issues found. Checked for bugs, security issues, and CLAUDE.md compliance.

---

Generated with [Claude Code](https://claude.ai/code)
```

### Code Link Format

Links MUST use full SHA and line range:
```
https://github.com/{owner}/{repo}/blob/{full-sha}/{path/to/file}#L{start}-L{end}
```

- Use full 40-character SHA (not abbreviated)
- Include at least 1 line of context before and after
- Repo name must match the repo being reviewed
- Get the full SHA via: `git rev-parse HEAD`
