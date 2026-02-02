# Doc Co-Authoring Troubleshooting

Common issues and solutions for the doc-coauthoring workflow.

## Workflow Issues

### User Wants to Skip Stages

**Problem**: User is impatient and wants to skip Context Gathering or Reader Testing.

**Solution**: Offer to work freeform while explaining the trade-off.

```
"We can absolutely skip this stage. Just know that [stage purpose].
Want to proceed freeform, or would a shorter version of this stage work?"
```

For Reader Testing specifically: The Streamlined Collaborative workflow skips this stage by design for code documentation.

---

### User Provides Too Little Context

**Problem**: User gives one-sentence answers and won't elaborate.

**Solution**: Ask more specific questions:

- Instead of "Tell me about the project" → "What problem does this solve?"
- Instead of "Who's the audience?" → "Will technical or non-technical people read this?"
- Offer multiple choice: "Is this for (a) internal team, (b) external stakeholders, or (c) public documentation?"

---

### User Provides Too Much Context

**Problem**: User info-dumps extensively, making it hard to synthesize.

**Solution**: Summarize and confirm:

```
"Based on what you've shared, here's what I understand:
- Key goal: X
- Main audience: Y
- Constraints: Z

Is this accurate? Anything critical I'm missing?"
```

---

### User Wants to Edit Doc Directly

**Problem**: User makes changes directly instead of asking for edits.

**Solution**: Accept it gracefully:

```
"I see you've made changes. I'll incorporate your edits and keep your style
in mind for the remaining sections."
```

Read the document to learn their preferences and apply them going forward.

---

### Brainstorming Produces Too Many Options

**Problem**: 20 options overwhelms the user.

**Solution**: Pre-group or prioritize:

```
"Here are the options grouped by theme:

**Core functionality** (pick 2-3):
1. ...
2. ...

**Nice to have** (pick 0-2):
3. ...
4. ...

Which categories matter most for your audience?"
```

---

### User Struggles with Curation

**Problem**: User says "looks good" without specific selections.

**Solution**: Ask targeted follow-up:

```
"Great! To make sure I capture your intent:
- Are there any points you definitely want included?
- Any that feel redundant or off-topic?
- Anything important that's missing?"
```

---

## Code Documentation Issues

### Missing Package Manifest

**Problem**: No package.json, pyproject.toml, or similar file exists.

**Solution**: Ask user for key project info:

- Project name and description
- Main dependencies
- Entry points
- Target audience (beginner/advanced developers)

---

### Code Examples Don't Work

**Problem**: Generated examples have syntax errors or don't match actual API.

**Solution**:
1. Read the actual source code to verify API signatures
2. Test examples mentally against the codebase
3. Include imports and setup code
4. Ask user to verify examples work

---

### API Spec Doesn't Match Implementation

**Problem**: OpenAPI spec has endpoints that don't exist or wrong parameters.

**Solution**:
1. Scan actual route definitions in code
2. Extract parameters from function signatures
3. Check for type hints/annotations
4. Cross-reference with any existing documentation

---

### Architecture Diagram Too Complex

**Problem**: System has too many components to diagram clearly.

**Solution**: Create layered diagrams:

1. High-level system overview (3-5 boxes)
2. Detailed diagrams per subsystem
3. Data flow diagrams for specific use cases

Ask user which level of detail they need.

---

## Reader Testing Issues

### No Sub-Agent Access

**Problem**: Testing in claude.ai web interface without sub-agent capability.

**Solution**: Guide user through manual testing:

1. Provide specific questions to ask
2. Explain how to open a fresh Claude conversation
3. Tell them what to look for in responses
4. Have them report back issues found

---

### Reader Claude Answers Correctly but Verbosely

**Problem**: Fresh Claude understands the doc but provides long-winded answers.

**Solution**: This is fine - it means the doc works. Focus on cases where:
- Claude misunderstands key concepts
- Claude makes incorrect assumptions
- Claude can't answer from the doc alone

---

### Testing Reveals Major Gaps

**Problem**: Reader Testing surfaces fundamental problems, not just minor tweaks.

**Solution**: Loop back to Stage 2 for affected sections:

```
"Reader Claude struggled with [section]. Let's revisit it:
1. What key information was missing?
2. What assumptions did we make that aren't stated?

I'll draft a revised version addressing these gaps."
```

---

## General Issues

### Conversation Running Long

**Problem**: Too many iterations, user losing patience.

**Solution**: Offer shortcuts:

```
"We've been through several iterations. Options:
1. Move forward with current version (good enough)
2. One more focused pass on [specific section]
3. Skip to final review

What works best for you?"
```

---

### User Wants Different Format

**Problem**: User wants output in format not covered by patterns (e.g., Wiki, Notion).

**Solution**: Adapt the patterns:

1. Ask for an example of their preferred format
2. Map the standard sections to their format
3. Maintain the collaborative process with their format as output

---

### Document Needs Visuals

**Problem**: Doc would benefit from diagrams, but user hasn't provided any.

**Solution**: Offer to create Mermaid diagrams:

```
"This section might benefit from a diagram. I can create a Mermaid diagram
showing [proposed visual]. Would that help?"
```

Use the diagramming skill if available.

---

### Conflicting Requirements

**Problem**: User states requirements that contradict each other.

**Solution**: Surface the conflict explicitly:

```
"I notice a potential tension:
- You mentioned [requirement A]
- But also [requirement B]

These might conflict because [reason]. How would you like to resolve this?"
```

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| User impatient | Offer to streamline or skip |
| Too little context | Ask specific questions |
| Too much context | Summarize and confirm |
| User edits directly | Accept and learn from their style |
| Too many options | Group and prioritize |
| Examples broken | Verify against actual code |
| Testing reveals gaps | Loop back to refinement |
| Long conversation | Offer exit ramps |
| Format mismatch | Adapt patterns to their format |
| Needs visuals | Offer Mermaid diagrams |
