# Lyra 4-D Methodology Workflow

Complete guide to the four-phase prompt optimization process.

## Overview

```
Input → DECONSTRUCT → DIAGNOSE → DEVELOP → DELIVER → Optimized Prompt
         (Analyze)     (Audit)    (Build)   (Format)
```

---

## Phase 1: DECONSTRUCT

**Goal**: Understand what the user actually wants.

### 1.1 Intent Extraction

Identify the core action:

| Intent Type | Signals | Example |
|-------------|---------|---------|
| **Create** | "write", "generate", "draft", "create" | "Write a marketing email" |
| **Transform** | "convert", "translate", "reformat" | "Convert this to bullet points" |
| **Analyze** | "review", "analyze", "evaluate" | "Review this code for bugs" |
| **Explain** | "explain", "describe", "teach" | "Explain quantum computing" |
| **Solve** | "fix", "debug", "help with" | "Help me fix this error" |
| **Decide** | "compare", "choose", "recommend" | "Compare React vs Vue" |

### 1.2 Entity Mapping

Extract key elements:

```
Subject:    What is the prompt about?
Object:     What should be produced?
Context:    What background is relevant?
Audience:   Who will consume the output?
Constraints: What limitations exist?
```

### 1.3 Information Audit

Categorize available information:

| Category | Status | Action |
|----------|--------|--------|
| **Explicit** | Provided | Preserve exactly |
| **Implicit** | Inferable | Make explicit |
| **Missing** | Unknown | Ask or use defaults |
| **Conflicting** | Contradictory | Clarify |

### 1.4 Deconstruct Checklist

- [ ] Identified primary intent (verb)
- [ ] Identified subject matter
- [ ] Identified desired output type
- [ ] Noted any context clues
- [ ] Noted any constraints mentioned
- [ ] Flagged missing critical information

---

## Phase 2: DIAGNOSE

**Goal**: Identify what's wrong with the original prompt.

### 2.1 Clarity Audit

Score each dimension (1-5):

| Dimension | Score 1 (Poor) | Score 5 (Excellent) |
|-----------|----------------|---------------------|
| **Specificity** | "Write something" | "Write a 500-word blog post about X" |
| **Completeness** | Missing key details | All necessary info provided |
| **Structure** | Stream of consciousness | Logical, organized sections |
| **Actionability** | Vague goal | Clear deliverable defined |
| **Context** | No background | Rich, relevant context |

### 2.2 Common Issues

**Vagueness**
- Problem: "Help me with my code"
- Missing: What code? What help? What language?

**Scope creep**
- Problem: "Write docs, add tests, refactor, and deploy"
- Issue: Multiple unrelated tasks in one prompt

**Assumed knowledge**
- Problem: "Use the standard format"
- Missing: What format? Define explicitly.

**Output ambiguity**
- Problem: "Summarize this article"
- Missing: How long? What format? What focus?

**Missing constraints**
- Problem: "Write a marketing email"
- Missing: Tone? Length? CTA? Audience?

### 2.3 Diagnosis Template

```
ORIGINAL: [User's prompt]

ISSUES IDENTIFIED:
1. [Issue type]: [Specific problem]
2. [Issue type]: [Specific problem]

MISSING INFORMATION:
- [Required element 1]
- [Required element 2]

PRIORITY: [High/Medium/Low] - [Reason]
```

---

## Phase 3: DEVELOP

**Goal**: Build the optimized prompt using appropriate techniques.

### 3.1 Technique Selection Matrix

| Request Type | Primary Techniques | Secondary Techniques |
|--------------|-------------------|---------------------|
| **Creative** | Multi-perspective, Tone setting | Few-shot examples, Constraints |
| **Technical** | Constraint-based, Precision | Step-by-step, Validation |
| **Educational** | Few-shot, Structured | Progressive complexity |
| **Analytical** | Framework-based, Systematic | Chain-of-thought |
| **Complex** | Decomposition, CoT | Meta-prompting |

### 3.2 Core Techniques

#### Role Assignment

Define who the AI should be:

```markdown
You are a [specific role] with expertise in [domain].
Your task is to [action] for [audience].
```

**Effective roles:**
- "Senior technical writer with 10 years experience"
- "Marketing strategist specializing in B2B SaaS"
- "Code reviewer focusing on security and performance"

**Avoid:**
- Generic roles: "You are a helpful assistant"
- Unrealistic roles: "You are the world's best everything"

#### Context Layering

Build context in layers:

```markdown
## Background
[What the AI needs to know about the situation]

## Current State
[Relevant existing information or constraints]

## Goal
[What success looks like]
```

#### Output Specification

Define the deliverable precisely:

```markdown
## Output Requirements
- Format: [markdown/JSON/code/prose]
- Length: [word count or sections]
- Structure: [outline or template]
- Tone: [professional/casual/technical]
```

#### Decomposition

Break complex tasks into steps:

```markdown
Complete this task in phases:

1. First, [analyze/gather/review]...
2. Then, [process/organize/draft]...
3. Finally, [refine/format/deliver]...
```

### 3.3 Advanced Techniques

#### Chain-of-Thought (CoT)

For reasoning-heavy tasks:

```markdown
Work through this step-by-step:
1. Identify the key factors
2. Analyze each factor's impact
3. Consider interactions between factors
4. Draw conclusions based on analysis
5. Provide recommendations

Show your reasoning at each step.
```

#### Few-Shot Examples

For pattern-following tasks:

```markdown
Here are examples of the desired format:

Example 1:
Input: [sample input]
Output: [sample output]

Example 2:
Input: [sample input]
Output: [sample output]

Now apply this pattern to: [actual input]
```

#### Multi-Perspective

For comprehensive analysis:

```markdown
Analyze this from multiple perspectives:
- Technical feasibility
- Business impact
- User experience
- Risk factors

Then synthesize into a recommendation.
```

#### Constraint Optimization

For bounded outputs:

```markdown
Requirements:
- Must include: [required elements]
- Must not include: [prohibited elements]
- Length: exactly [N] words/sentences
- Format: [specific structure]
```

### 3.4 Platform-Specific Optimizations

#### Claude

Claude responds well to:
- XML-style tags for structure
- Long, detailed context
- Explicit reasoning requests
- Nuanced instructions

```markdown
<context>
[Background information]
</context>

<task>
[What to do]
</task>

<output_format>
[Expected structure]
</output_format>
```

#### ChatGPT/GPT-4

ChatGPT responds well to:
- System message for role setting
- Clear numbered steps
- Explicit output format
- Concise instructions

```markdown
ROLE: [Specific expert role]

TASK: [Clear, direct instruction]

FORMAT:
1. [Section 1]
2. [Section 2]
3. [Section 3]

CONSTRAINTS:
- [Constraint 1]
- [Constraint 2]
```

#### Gemini

Gemini responds well to:
- Creative exploration
- Comparative analysis
- Multi-modal prompts (when applicable)
- Iterative refinement

```markdown
Explore this topic from multiple angles:

Consider:
- [Angle 1]
- [Angle 2]
- [Angle 3]

Then provide a synthesized view that balances all perspectives.
```

### 3.5 Development Checklist

- [ ] Selected appropriate techniques for request type
- [ ] Assigned specific, relevant role
- [ ] Provided necessary context
- [ ] Specified output format clearly
- [ ] Added constraints where needed
- [ ] Applied platform-specific optimizations
- [ ] Verified all issues from DIAGNOSE are addressed

---

## Phase 4: DELIVER

**Goal**: Format and present the optimized prompt effectively.

### 4.1 Output Structure

#### BASIC Mode Output

```markdown
## Optimized Prompt

[The complete optimized prompt in a code block]

## What Changed
- [Change 1]: [Brief explanation]
- [Change 2]: [Brief explanation]
```

#### DETAIL Mode Output

```markdown
## Optimized Prompt

[The complete optimized prompt in a code block]

## Key Improvements
- [Improvement 1]: Added [what] for [why]
- [Improvement 2]: Clarified [what] to [achieve]

## Techniques Applied
- **Role Assignment**: [How it was used]
- **Context Layering**: [How it was used]
- **[Other technique]**: [How it was used]

## Pro Tip
[Platform-specific advice or usage suggestion]
```

### 4.2 Formatting Guidelines

**Code blocks for prompts**
- Always wrap optimized prompt in code block
- Makes copy-paste easy
- Preserves formatting

**Highlight changes**
- Explicitly state what changed
- Explain the reasoning briefly
- Connect changes to improvements

**Keep explanations concise**
- Users want the prompt, not an essay
- Bullet points over paragraphs
- Focus on actionable insights

### 4.3 Quality Checklist

Before delivering:

- [ ] Optimized prompt is complete and standalone
- [ ] Prompt is in a code block for easy copying
- [ ] Changes are clearly listed
- [ ] No placeholder text remains ([brackets])
- [ ] Length is appropriate for complexity
- [ ] Platform-specific formatting applied
- [ ] Pro tip adds genuine value

### 4.4 Delivery Template

```markdown
## Optimized Prompt

```
[Complete prompt ready to use]
```

## What Changed
- **Added role definition**: Establishes expertise and perspective
- **Specified output format**: Removes ambiguity about deliverable
- **Added context**: Provides necessary background for quality response
- **Included constraints**: Bounds the response appropriately

## Pro Tip
[One actionable piece of advice for using this prompt effectively]
```

---

## Quick Reference

### Mode Selection Guide

| Situation | Recommended Mode |
|-----------|-----------------|
| Quick question, simple optimization | BASIC |
| Complex task, multiple requirements | DETAIL |
| First time using Lyra | DETAIL |
| Repeat optimization of similar prompts | BASIC |
| Unclear about requirements | DETAIL |

### Technique Quick Reference

| Need | Technique |
|------|-----------|
| Better role clarity | Role Assignment |
| More background info | Context Layering |
| Specific deliverable | Output Specification |
| Complex multi-step task | Decomposition |
| Reasoning required | Chain-of-Thought |
| Pattern to follow | Few-Shot Examples |
| Multiple viewpoints | Multi-Perspective |
| Bounded output | Constraint Optimization |

### Platform Quick Reference

| Platform | Key Strength | Optimization Focus |
|----------|--------------|-------------------|
| Claude | Long context, nuance | XML tags, detailed context |
| ChatGPT | Structured output | Clear steps, explicit format |
| Gemini | Creative exploration | Multiple angles, synthesis |
| Universal | Broad compatibility | Role + context + output pattern |
