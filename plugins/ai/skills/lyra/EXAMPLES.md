# Lyra Examples

Before/after examples demonstrating prompt optimization techniques.

---

## Quick Mode Selection Guide

| Original Prompt | Suggested Mode | Why |
|-----------------|---------------|-----|
| "Summarize this" | BASIC | Simple task, clear intent |
| "Help me write a business plan" | DETAIL | Complex, needs clarification |
| "Fix this bug" | DETAIL | Needs context gathering |
| "Translate to Spanish" | BASIC | Straightforward transformation |
| "Design a system for..." | DETAIL | Architecture needs exploration |

---

## Example 1: Simple Request (BASIC Mode)

### Input
```
/lyra BASIC Write a marketing email
```

### Before
```
Write a marketing email
```

### After
```
You are an experienced email marketing copywriter specializing in conversion-focused content.

Write a marketing email with the following structure:

1. **Subject Line**: Attention-grabbing, under 50 characters
2. **Preview Text**: Compelling hook, 40-90 characters
3. **Body**:
   - Opening hook (1-2 sentences)
   - Value proposition (2-3 bullet points)
   - Social proof or benefit (1 paragraph)
   - Clear call-to-action
4. **Closing**: Professional sign-off

Tone: Professional yet personable
Length: 150-200 words for body content

Please specify or I'll create a general product promotion email:
- Product/service being promoted
- Target audience
- Primary benefit to highlight
- Desired action (click, buy, sign up)
```

### What Changed
- Added copywriter role for expertise
- Specified exact email structure
- Defined tone and length constraints
- Listed required information with fallback

---

## Example 2: Technical Request (DETAIL Mode)

### Input
```
/lyra DETAIL for Claude Help me debug this code
```

### DETAIL Mode Questions Asked

**Q1: Outcome** - "What specific result are you looking for?"
> User selected: "Problem solving"

**Q2: Constraints** - "Any requirements for the output?"
> User selected: "Specific format"

**Q3: Audience** - "Who will use this AI output?"
> User selected: "Technical audience"

### Before
```
Help me debug this code
```

### After (Optimized for Claude)
```
<role>
You are a senior software engineer with expertise in debugging and code review.
</role>

<task>
Help me debug the code I'll provide. Follow this systematic approach:
</task>

<debugging_process>
1. **Understand**: Describe what the code is trying to accomplish
2. **Identify**: Locate the specific issue(s) causing unexpected behavior
3. **Explain**: Describe why each issue occurs (root cause analysis)
4. **Fix**: Provide corrected code with inline comments explaining changes
5. **Prevent**: Suggest how to avoid similar issues in the future
</debugging_process>

<output_format>
## Issue Summary
[One-line description of the problem]

## Root Cause
[Detailed explanation of why this happens]

## Solution
```[language]
// Corrected code with comments
```

## Prevention Tips
- [Tip 1]
- [Tip 2]
</output_format>

<context>
Please share:
- The code experiencing issues
- The expected behavior
- The actual behavior (error messages, incorrect output)
- Language/framework version if relevant
</context>
```

### What Changed
- Added debugging expert role
- Specified systematic 5-step approach
- Used Claude's XML tag structure
- Defined clear output format
- Listed required context explicitly

---

## Example 3: Creative Request

### Input
```
/lyra BASIC for ChatGPT Write a story
```

### Before
```
Write a story
```

### After (Optimized for ChatGPT)
```
ROLE: You are a creative fiction writer with a talent for engaging narratives.

TASK: Write a short story following this structure:

1. Opening Hook (1 paragraph): Draw the reader in immediately
2. Character Introduction: Establish protagonist with specific details
3. Conflict: Introduce the central tension or challenge
4. Rising Action: 2-3 events that escalate stakes
5. Climax: The pivotal moment of highest tension
6. Resolution: Satisfying conclusion that addresses the conflict

REQUIREMENTS:
- Length: 500-800 words
- Point of View: Third person limited
- Genre: [Specify or I'll choose contemporary fiction]
- Tone: Engaging and emotionally resonant

OPTIONAL INPUTS (provide any that apply):
- Preferred genre (fantasy, mystery, romance, sci-fi, etc.)
- Character type or name
- Setting (time period, location)
- Theme to explore
- Any elements that must be included
```

### What Changed
- Added creative writer role
- Specified story structure framework
- Defined length and POV constraints
- Listed optional customization inputs
- Used ChatGPT's structured format preference

---

## Example 4: Platform Comparison

Same prompt optimized for different platforms:

### Original
```
Compare React and Vue for my next project
```

### Optimized for Claude
```
<role>
You are a senior frontend architect with production experience in both React and Vue.
</role>

<context>
I need to choose between React and Vue for my next web application project.
</context>

<task>
Provide a comprehensive comparison to help me make an informed decision.
</task>

<comparison_framework>
Analyze both frameworks across these dimensions:

1. **Learning Curve**: Time to productivity, documentation quality
2. **Performance**: Bundle size, runtime performance, optimization options
3. **Ecosystem**: Libraries, tools, community packages
4. **Developer Experience**: Tooling, debugging, IDE support
5. **Scalability**: Large app management, code organization
6. **Job Market**: Demand, salary trends, company adoption
7. **Long-term Viability**: Backing, roadmap, community health
</comparison_framework>

<output_format>
For each dimension:
- Winner: [React/Vue/Tie]
- React: [Strengths and limitations]
- Vue: [Strengths and limitations]
- My take: [Nuanced recommendation]

Final recommendation based on common project types:
- Small/medium apps: [Recommendation]
- Large enterprise apps: [Recommendation]
- Team with existing experience: [Recommendation]
</output_format>
```

### Optimized for ChatGPT
```
ROLE: Senior frontend architect with 5+ years experience in React and Vue

TASK: Compare React and Vue to help me choose for my next project

COMPARISON CRITERIA (evaluate both):
1. Learning Curve - Documentation, ramp-up time
2. Performance - Speed, bundle size
3. Ecosystem - Libraries, tools available
4. Developer Experience - Tooling, debugging
5. Scalability - Large application management
6. Job Market - Demand, salaries
7. Future Outlook - Roadmap, backing

OUTPUT FORMAT:
| Criteria | React | Vue | Winner |
|----------|-------|-----|--------|
| ... | ... | ... | ... |

SUMMARY:
- Choose React if: [conditions]
- Choose Vue if: [conditions]

MY RECOMMENDATION:
[Based on typical use cases, provide clear guidance]
```

### Optimized for Gemini
```
I need to decide between React and Vue for my next web project. As someone exploring both options, help me understand the tradeoffs.

Please approach this comparison from multiple angles:

**Developer Perspective**: Which is easier to learn? More enjoyable to use daily?

**Architect Perspective**: Which scales better? Handles complexity?

**Business Perspective**: Which has better hiring pool? Long-term stability?

**Pragmatist Perspective**: Which gets the job done with less friction?

For each perspective, share:
- Key insights
- Potential blind spots in that view
- Real-world examples if possible

Then synthesize these viewpoints:
- What patterns emerge across perspectives?
- What does this suggest for different project types?
- If you had to choose for a typical mid-sized web app in 2024, which would you lean toward and why?

I appreciate nuanced thinking over definitive answers. The goal is to understand tradeoffs, not find a "winner."
```

### Key Differences

| Aspect | Claude | ChatGPT | Gemini |
|--------|--------|---------|--------|
| Structure | XML tags | Tables/lists | Flowing prose |
| Role | Detailed in tags | One-line header | Implied |
| Output | Explicit format | Table format | Synthesis-focused |
| Tone | Direct, systematic | Structured, clear | Exploratory, nuanced |

---

## Example 5: Mode Comparison

Same prompt in BASIC vs DETAIL mode:

### Original
```
Help me prepare for a job interview
```

### BASIC Mode Output
```
You are a career coach specializing in interview preparation.

Help me prepare for a job interview by providing:

1. **Common Questions** (10 questions with approach tips):
   - Behavioral questions (STAR method)
   - Technical/role-specific questions
   - Questions about the candidate

2. **Preparation Checklist**:
   - Research tasks
   - Practice exercises
   - Day-before preparation
   - Day-of preparation

3. **Red Flags to Avoid**:
   - Common mistakes
   - Body language issues
   - Answer pitfalls

4. **Questions to Ask Them**:
   - 5 thoughtful questions for the interviewer

Please share the role/company if you want specific guidance, otherwise I'll provide general best practices.
```

### DETAIL Mode Output (After Questions)

**Questions answered:**
- Outcome: "Clear deliverable" (preparation materials)
- Constraints: "Specific format" (structured checklist)
- Audience: "Specific role" → User specified: "Software engineer at FAANG"

```
You are a FAANG technical interview coach with experience preparing candidates for Google, Amazon, Meta, Apple, and Microsoft.

Help me prepare for a software engineering interview with a comprehensive preparation plan.

## Interview Components to Address

### 1. Coding Interviews
- Data structures: Arrays, strings, trees, graphs, heaps
- Algorithms: Sorting, searching, dynamic programming, recursion
- Practice approach: LeetCode strategy, pattern recognition
- Time management: How to pace a 45-minute coding session

### 2. System Design (If applicable for level)
- Framework for approaching design questions
- Key concepts: Scalability, reliability, consistency
- Common questions: URL shortener, news feed, chat system
- Diagram and communication approach

### 3. Behavioral Interviews (Leadership Principles / Core Values)
- STAR method with FAANG-specific adaptations
- How to map experiences to company values
- 5-7 stories that cover major themes
- Handling "Tell me about a time when you failed"

### 4. Company-Specific Preparation
- Research checklist
- Recent news and products to know
- Team/role specific preparation

## Output Format

Provide a 2-week preparation plan:
- Week 1 daily schedule
- Week 2 daily schedule
- Mock interview recommendations
- Day-before checklist
- Day-of routine

## My Current Context
[Share: Target company, role level, interview timeline, current preparation status]
```

### Comparison

| Aspect | BASIC | DETAIL |
|--------|-------|--------|
| Length | ~150 words | ~300 words |
| Specificity | General | FAANG-specific |
| Structure | Generic sections | Role-tailored components |
| Context | Minimal | Gathered through questions |
| Applicability | Any interview | Specific to software + FAANG |

---

## Example 6: --research Flag Usage

### Without --research
```
/lyra BASIC Write API documentation
```

Outputs optimization based on built-in knowledge of documentation best practices.

### With --research
```
/lyra BASIC --research Write API documentation
```

**Research performed:**
- WebSearch: "API documentation best practices 2025"
- WebSearch: "developer-friendly API docs examples"

**Findings incorporated:**
- OpenAPI/Swagger integration recommendations
- Interactive "try it" functionality
- Error response documentation emphasis
- SDK/code sample requirements
- Recent trends in API doc tooling (Mintlify, ReadMe, etc.)

### Optimized Output (with research)
```
You are a technical writer specializing in developer documentation with expertise in modern API documentation standards.

Create API documentation following current industry best practices (2024-2025).

## Documentation Structure

### 1. Overview
- API purpose and use cases
- Authentication methods
- Base URL and environments
- Rate limits and quotas

### 2. Quick Start
- Get-started-in-5-minutes guide
- First API call example
- Common use case walkthrough

### 3. Endpoint Reference
For each endpoint:
- Method and path
- Description
- Request parameters (path, query, body)
- Request example (curl + SDK)
- Response schema with examples
- Error responses with remediation
- Interactive "Try It" section if possible

### 4. Guides
- Authentication deep dive
- Pagination handling
- Webhook integration
- Error handling patterns
- Best practices

### 5. SDK & Code Samples
- Available SDKs
- Copy-paste examples in multiple languages
- Runnable code snippets

## Modern Documentation Elements
- OpenAPI 3.1 spec for tooling compatibility
- Dark mode support
- Search functionality
- Version selector
- Changelog/API updates section

## Tools to Consider
- Mintlify, ReadMe, Redocly for hosted docs
- Stoplight, SwaggerHub for API-first design
- Postman collections for interactive testing

Please provide your API details and I'll create comprehensive documentation.
```

### When to Use --research

| Scenario | Use --research? |
|----------|-----------------|
| Quick prompt cleanup | No |
| Domain you know well | No |
| Emerging technology | Yes |
| Industry best practices | Yes |
| Current trends matter | Yes |
| Speed is priority | No |

---

## Quick Reference: Optimization Patterns

### Pattern 1: Add Role
```
Before: "Write a report"
After:  "You are a business analyst. Write a report..."
```

### Pattern 2: Specify Output
```
Before: "Summarize this"
After:  "Summarize this in 3 bullet points, each under 20 words"
```

### Pattern 3: Add Context
```
Before: "Help with my code"
After:  "Help with my Python code. I'm building a REST API using FastAPI..."
```

### Pattern 4: Define Constraints
```
Before: "Write a story"
After:  "Write a 500-word story in third person, mystery genre, set in 1920s London"
```

### Pattern 5: Structure Complex Tasks
```
Before: "Plan my project"
After:  "Create a project plan with: 1) Milestones, 2) Tasks per milestone, 3) Dependencies, 4) Timeline"
```

### Pattern 6: Request Reasoning
```
Before: "Which option is best?"
After:  "Analyze each option's pros/cons, then recommend the best choice with reasoning"
```
