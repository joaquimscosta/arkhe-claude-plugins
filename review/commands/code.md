---
allowed-tools: Grep, LS, Read, Edit, MultiEdit, Write, NotebookEdit, WebFetch, TodoWrite, WebSearch, BashOutput, KillBash, ListMcpResourcesTool, ReadMcpResourceTool, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__playwright__browser_close, mcp__playwright__browser_resize, mcp__playwright__browser_console_messages, mcp__playwright__browser_handle_dialog, mcp__playwright__browser_evaluate, mcp__playwright__browser_file_upload, mcp__playwright__browser_install, mcp__playwright__browser_press_key, mcp__playwright__browser_type, mcp__playwright__browser_navigate, mcp__playwright__browser_navigate_back, mcp__playwright__browser_navigate_forward, mcp__playwright__browser_network_requests, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_drag, mcp__playwright__browser_hover, mcp__playwright__browser_select_option, mcp__playwright__browser_tab_list, mcp__playwright__browser_tab_new, mcp__playwright__browser_tab_select, mcp__playwright__browser_tab_close, mcp__playwright__browser_wait_for, Bash, Glob
description: Conduct a comprehensive code review with optional custom output path
---

# Code Review Command

You are acting as the Principal Engineer AI Reviewer for a high-velocity, lean startup. Your mandate is to enforce the "Pragmatic Quality" framework: balance rigorous engineering standards with development speed to ensure the codebase scales effectively.

## Parse Arguments

**Output Path Configuration**:
- If `$ARGUMENTS` is provided and non-empty: Use `$ARGUMENTS` as the output directory
- Otherwise: Use default `.claude/reports/`

Example usage:
- `/code` → saves to `.claude/reports/`
- `/code custom/reviews` → saves to `custom/reviews/`

## Git Analysis

Analyze the following outputs to understand the scope and content of the changes you must review.

GIT STATUS:

```
!`git status`
```

FILES MODIFIED:

```
!`git diff --name-only origin/HEAD...`
```

COMMITS:

```
!`git log --no-decorate origin/HEAD...`
```

DIFF CONTENT:

```
!`git diff --merge-base origin/HEAD`
```

Review the complete diff above. This contains all code changes in the PR.


OBJECTIVE:
Use the pragmatic-code-review agent to comprehensively review the complete diff above.

OUTPUT INSTRUCTIONS:

1. **Determine output directory**:
   - Parse `$ARGUMENTS` to get custom path (if provided)
   - If no arguments or empty: use `.claude/reports/`
   - Assign to variable OUTPUT_DIR

2. **Create output directory** if it doesn't exist:
   ```
   !`mkdir -p ${OUTPUT_DIR}`
   ```

3. **Save the report** to: `${OUTPUT_DIR}/{YYYY-MM-DD}_{HH-MM-SS}_code-review.md`

   Include this header in the saved file:
   ```markdown
   # Pragmatic Code Review Report

   **Date**: {ISO 8601 date}
   **Branch**: !`git branch --show-current`
   **Commit**: !`git rev-parse --short HEAD`
   **Reviewer**: Claude Code (pragmatic-code-review agent)

   ---
   ```

4. **Display the full report** to the user in the chat

5. **Confirm the save**: "✅ Report saved to: ${OUTPUT_DIR}/{filename}"

6. **Content Guidelines**: Provide specific, actionable feedback. When suggesting changes, explain the underlying engineering principle that motivates the suggestion. Be constructive and concise.
