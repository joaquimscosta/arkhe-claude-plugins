---
description: >
  Ultra-deep multi-perspective analysis for complex tasks. Analyzes from Architect, Research,
  Coder, and Tester viewpoints before synthesizing a recommendation. Use for: system design,
  implementation decisions, or problems requiring thorough analysis.
  Example: "/ultrathink design a caching layer for our API"
argument-hint: "<complex task requiring multi-perspective analysis>"
---

# Ultra-Deep Analysis

Analyze the following task from multiple expert perspectives, then synthesize into a cohesive recommendation.

**Task:** $ARGUMENTS

---

## Process

1. **Restate the problem** - Confirm understanding in 2-3 sentences
2. **Analyze from four perspectives** - Each perspective surfaces different concerns
3. **Synthesize insights** - Combine into a unified view
4. **Deliver actionable output** - Concrete recommendations or implementation

---

## Output Format

### 1. Problem Restatement

Confirm understanding of the task. What are we solving? What constraints exist?

### 2. Perspective Analysis

**Architect Perspective**
- High-level approach and system design considerations
- Trade-offs, patterns, and architectural implications
- How this fits into the broader system

**Research Perspective**
- Relevant patterns, precedents, or industry knowledge
- How similar problems are solved elsewhere
- External resources or documentation to consider

**Coder Perspective**
- Implementation approach and technical details
- Code-level concerns, edge cases, error handling
- Specific files, functions, or modules involved

**Tester Perspective**
- Validation strategy and test scenarios
- What could go wrong, failure modes
- How to verify correctness and prevent regressions

### 3. Synthesis

Combine the four perspectives into a unified analysis:
- Where do perspectives align?
- Where do they conflict, and how to resolve?
- What's the recommended approach given all viewpoints?

### 4. Final Recommendation

Actionable output: steps, code, commands, or decisions.

### 5. Open Questions (if any)

Remaining uncertainties or items needing user input.

---

## Guidelines

- Take time to think deeply from each perspective before synthesizing
- Perspectives should surface genuinely different concerns, not repeat the same points
- The synthesis should resolve tensions between perspectives, not just summarize them
- Final recommendation should be concrete and actionable
