# Troubleshooting Workflow Orchestration

Common issues and solutions when using orchestration tools.

## Choosing the Wrong Tool

### Problem: Used `/workflow` for a simple task
**Symptoms:** Excessive overhead, slow execution, unnecessary complexity.

**Solution:** For single-function changes or simple tasks, skip orchestration and provide direct implementation. Orchestration is for multi-component coordination.

### Problem: Used `/think` when `/workflow` was needed
**Symptoms:** Got analysis but no implementation, reasoning without action.

**Solution:** `/think` is for reasoning and decisions. Use `/workflow` when you need actual implementation across multiple files/components.

### Problem: Task is stuck in analysis
**Symptoms:** Deep thinking but no progress, endless exploration.

**Solution:** Set clear boundaries. If analysis is complete, transition to `/workflow` for execution. Ask: "Do we understand the problem enough to act?"

---

## Workflow Execution Issues

### Problem: Gating rejects valid requests
**Symptoms:** Requests declined that should proceed.

**Solutions:**
1. Provide more context in the request
2. Break down vague requests into specific asks
3. Include relevant file paths or component names

**Example fix:**
```
Bad:  /workflow make it better
Good: /workflow refactor the UserService to use dependency injection
```

### Problem: Context discovery misses relevant files
**Symptoms:** Implementation doesn't follow existing patterns.

**Solutions:**
1. Mention specific files or patterns to consider
2. Reference CLAUDE.md guidelines
3. Add `--research` to find related patterns

### Problem: Too much sequential execution
**Symptoms:** Slow workflow, tasks running one at a time.

**Solutions:**
1. Review the plan - are dependencies real?
2. Some tasks may be falsely marked as dependent
3. Consider if subtasks can be parallelized

### Problem: Validation is too strict/lenient
**Symptoms:** Good work flagged as issues, or problems missed.

**Solutions:**
- Too strict: Focus on objective issues only
- Too lenient: Add `--deep` for more thorough analysis
- Consider what truly blocks vs. what's a nice-to-have

---

## Performance Issues

### Problem: Workflow takes too long
**Symptoms:** Extended wait times, timeout concerns.

**Solutions:**
1. Remove unnecessary flags (don't use all three unless needed)
2. Break large tasks into smaller workflows
3. Use haiku for gating/routing, save opus for deep analysis

### Problem: Too many agents spawned
**Symptoms:** Confusion, conflicting changes, resource exhaustion.

**Solutions:**
1. Combine related tasks into single agent assignments
2. Ensure wave planning groups appropriately
3. Review if all tasks are truly necessary

---

## Quality Issues

### Problem: Output doesn't match expectations
**Symptoms:** Implementation differs from what was requested.

**Solutions:**
1. Clarify requirements in the initial request
2. Use `--validate` to add quality gates
3. Provide success criteria explicitly

### Problem: Code doesn't follow project conventions
**Symptoms:** Style inconsistencies, pattern violations.

**Solutions:**
1. Ensure context discovery found CLAUDE.md
2. Reference specific conventions in request
3. Add examples of expected patterns

### Problem: Missing edge cases
**Symptoms:** Implementation works for happy path only.

**Solutions:**
1. Mention edge cases explicitly in request
2. Use `--deep` for more thorough analysis
3. Add `--validate` to catch missing scenarios

---

## Flag-Related Issues

### Problem: `--research` returns irrelevant results
**Symptoms:** Web search adds noise, not value.

**Solutions:**
1. Be specific about what to research
2. Skip `--research` if internal patterns are sufficient
3. Constrain research scope in the request

### Problem: `--deep` is too slow
**Symptoms:** Analysis takes much longer than expected.

**Solutions:**
1. Use `--deep` only for genuinely complex decisions
2. Consider if sonnet-level analysis would suffice
3. Reserve opus for validation, not all phases

### Problem: `--validate` catches too much
**Symptoms:** Validation flags subjective issues.

**Solutions:**
1. Focus on high-signal criteria (bugs, blockers, violations)
2. Skip style and preference issues
3. Trust linters and tests for mechanical checks

---

## Integration Issues

### Problem: Conflict between `/workflow` and `/think` outputs
**Symptoms:** Analysis and implementation don't align.

**Solutions:**
1. Run `/think` first for decisions
2. Use conclusions to inform `/workflow` request
3. Reference thinking output in workflow request

### Problem: `deep-think-partner` and workflow don't coordinate
**Symptoms:** Duplicate analysis, conflicting recommendations.

**Solutions:**
1. Use one or the other for a given phase
2. `deep-think-partner` for strategic decisions
3. `/workflow` for execution after decisions are made

---

## Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Unclear request | Add specific file paths and success criteria |
| Missing context | Reference CLAUDE.md or key files |
| Too slow | Remove unnecessary flags |
| Too shallow | Add `--deep` flag |
| No quality check | Add `--validate` flag |
| Wrong tool | Check decision matrix in EXAMPLES.md |
| Stuck in analysis | Transition to `/workflow` for execution |
| Over-engineered | Use inline guidance for simple tasks |

## Getting Help

If orchestration isn't working as expected:

1. Check if the task actually needs orchestration (simple tasks don't)
2. Review the decision matrix in [EXAMPLES.md](EXAMPLES.md)
3. Ensure the request is specific and actionable
4. Consider breaking complex requests into phases
5. Use `/discuss` to talk through the approach first
