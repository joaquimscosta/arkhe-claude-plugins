# Troubleshooting Guide

Common issues when creating tutorials and how to resolve them.

---

## Table of Contents

1. [Mode Selection Issues](#mode-selection-issues)
2. [Content Quality Issues](#content-quality-issues)
3. [Output Format Issues](#output-format-issues)
4. [Validation Failures](#validation-failures)
5. [Language/Framework Specific](#languageframework-specific)
6. [Video Package Issues](#video-package-issues)
7. [SEO & Metadata Issues](#seo--metadata-issues)

---

## Mode Selection Issues

### Issue: Unclear which mode to use

**Symptoms:**
- User request doesn't clearly match Quick Start, Deep Dive, or Workshop
- Multiple depth indicators present
- Ambiguous scope

**Root Cause:**
Input doesn't fit neatly into keyword patterns or length criteria.

**Solution:**
1. Default to **Deep Dive** mode (most versatile)
2. State the assumption explicitly to the user:
   ```
   "I'll create a Deep Dive tutorial (45 min) since the scope seems
   intermediate. Let me know if you'd prefer a Quick Start or
   Workshop Series instead."
   ```
3. Allow user to override if needed

**Prevention:**
- Use the 3 clarifying questions if genuinely ambiguous
- Prefer Deep Dive over guessing wrong mode

---

### Issue: User wants different mode than selected

**Symptoms:**
- User says "that's too long" or "I need something shorter"
- User requests more depth than provided

**Solution:**
1. Acknowledge and switch modes immediately
2. Adjust outline and content accordingly
3. Example response:
   ```
   "Got it! I'll switch to Quick Start mode (5-10 min) with a
   more concise structure."
   ```

**Mode Adjustment Guide:**
- Quick Start → Deep Dive: Expand sections 3-5x, add variations and troubleshooting
- Deep Dive → Quick Start: Condense to 4-5 sections, single example, brief challenge
- Deep Dive → Workshop: Split into 3-5 parts, each with progressive complexity
- Workshop → Deep Dive: Merge parts into one comprehensive tutorial

---

## Content Quality Issues

### Issue: Tutorial feels too long or overwhelming

**Symptoms:**
- Word count exceeds expected range (Quick Start > 1000 words, Deep Dive > 3000 words)
- Too many concepts introduced at once
- User feedback: "This is too much"

**Root Cause:**
Trying to cover too much scope in one tutorial.

**Solutions:**

**Option 1: Collapse optional content**
```markdown
<details><summary>Advanced: Customization Options</summary>

[Optional advanced content here]

</details>
```

**Option 2: Move to appendix**
Create an "Advanced Topics" or "Additional Considerations" section at the end.

**Option 3: Switch modes**
- If Deep Dive is too long → Quick Start
- If Quick Start is cramming too much → Deep Dive
- If Deep Dive is trying to cover series-level content → Workshop

**Option 4: Extract to separate tutorial**
Split into two tutorials:
- Current: Core concept
- New: Advanced application

**Prevention:**
- Stick to mode's time estimate
- Focus on one core concept
- Use "Next Steps" to point to advanced topics

---

### Issue: Missing runnable code examples

**Symptoms:**
- Validation warnings about missing code blocks
- Examples are pseudo-code or incomplete
- No expected output shown

**Root Cause:**
Theory-heavy writing without practical demonstration.

**Solution:**
1. **Add minimal runnable example** in Section 3
2. **Show expected output** after every code block
3. **Verify logic** before including (or mark as pseudo-code)

**Template for code blocks:**
```markdown
### Example: [Description]

```[language]
# Code that actually runs
```

**Expected Output:**
```
Exact output user should see
```

> 💡 **Tip:** Brief practical pointer
```

**Prevention:**
- Lead with code, explain after
- Always show output
- Test examples when possible

---

### Issue: Audience mismatch (too basic or too advanced)

**Symptoms:**
- Content assumes too much prior knowledge
- Or explains concepts the target audience already knows
- User says "I already know this" or "I don't understand"

**Root Cause:**
Audience level not clearly defined or followed.

**Solution:**

**If too basic:**
1. Remove elementary explanations
2. Increase pace
3. Focus on intermediate/advanced patterns
4. Add prerequisites section pointing to beginner resources

**If too advanced:**
1. Add prerequisite explanations
2. Break down complex concepts
3. Include analogies and mental models
4. Provide links to foundational tutorials

**Prevention:**
- State audience level clearly in metadata
- Ask clarifying questions if audience is unclear
- Check terminology matches audience level

---

### Issue: Confusing structure or flow

**Symptoms:**
- Concepts introduced before dependencies
- Jumps between topics without clear transitions
- No clear progression from simple → complex

**Root Cause:**
Not following the template structure or logical ordering.

**Solution:**
1. **Follow template strictly:**
   - Concept Overview (why)
   - Minimal Example (what)
   - Guided Steps (how)
   - Challenge (apply)
2. **Check dependencies:**
   - Concept A must be explained before using it in Concept B
3. **Add transitions:**
   ```markdown
   Now that we've covered [previous], let's build on that with [next]...
   ```
4. **Use progress checks** to reinforce understanding before moving forward

**Prevention:**
- Draft outline before writing
- Review flow: each section should naturally lead to next
- Test with "can the reader follow this?" mindset

---

## Output Format Issues

### Issue: Code blocks missing language tags

**Symptoms:**
- Validation warning: "code blocks without language tags"
- Syntax highlighting not working

**Root Cause:**
Using ``` without specifying language.

**Solution:**
Always specify language:
```markdown
✅ Correct:
```python
code here
```

❌ Wrong:
```
code here
```
```

**Common language tags:**
- `python`, `javascript`, `java`, `kotlin`
- `bash`, `shell`, `sh`
- `yaml`, `json`, `xml`
- `dockerfile`
- `jsx`, `tsx` (for React)

---

### Issue: Internal links are broken

**Symptoms:**
- Validation warning about broken links
- Links don't navigate to correct section

**Root Cause:**
Anchor text doesn't match header format.

**Solution:**
GitHub-flavored Markdown converts headers to anchors by:
1. Lowercasing
2. Replacing spaces with hyphens
3. Removing punctuation (except hyphens)

**Examples:**
```markdown
## 1. What You'll Build
Link to: #1-what-youll-build

## Troubleshooting & Common Pitfalls
Link to: #troubleshooting--common-pitfalls

## Step 1: Setup
Link to: #step-1-setup
```

**Prevention:**
- Use simple header text
- Test links in preview
- Avoid special characters in headers

---

### Issue: Numbered sections are non-sequential

**Symptoms:**
- Validation warning: "Section numbering is non-sequential: [1, 2, 4, 5]"
- Confusing navigation

**Root Cause:**
Skipped a number when writing or editing.

**Solution:**
Renumber sections sequentially:
```markdown
## 1. What You'll Build
## 2. Concept Overview
## 3. Minimal Example
## 4. Guided Steps
## 5. Challenge
## 6. Troubleshooting
## 7. Summary
```

---

## Validation Failures

### Issue: Validation script exits with code 2 (errors)

**Symptoms:**
```
❌ VALIDATION FAILED
Error: Missing required section: [section name]
```

**Root Cause:**
Article missing required sections or incorrect format.

**Solution:**
1. **Read error message carefully**
2. **Check for required sections:**
   - H1 title
   - Audience metadata
   - Language metadata
   - Numbered sections (What You'll Build, Concept Overview, etc.)
3. **Verify section format:**
   ```markdown
   ✅ Correct: ## 1. What You'll Build
   ❌ Wrong: ## What You'll Build (missing number)
   ❌ Wrong: # 1. What You'll Build (H1 instead of H2)
   ```
4. **Re-run validation** after fixes

---

### Issue: JSON/YAML syntax errors

**Symptoms:**
```
Error: Invalid JSON: Unexpected token } at position 234
Error: Invalid YAML: mapping values are not allowed here
```

**Root Cause:**
Syntax error in chapters.json or seo.yaml.

**Solution:**

**For JSON (chapters.json):**
1. Check for:
   - Missing commas between array elements
   - Extra comma after last element
   - Unquoted strings
   - Mismatched brackets
2. Use JSON validator: https://jsonlint.com/

**For YAML (seo.yaml):**
1. Check for:
   - Incorrect indentation (use spaces, not tabs)
   - Missing colons after keys
   - Unquoted strings with special characters
2. Use YAML validator: https://www.yamllint.com/

**Prevention:**
- Use editor with JSON/YAML validation
- Copy from templates
- Test syntax before finalizing

---

## Language/Framework Specific

### Issue: Python code examples have syntax errors

**Common mistakes:**
- Missing colons after function definitions
- Incorrect indentation
- Using Python 2 syntax in Python 3 tutorial

**Solution:**
- Verify Python version compatibility
- Test code in Python REPL
- Use f-strings for Python 3.6+
- Follow PEP 8 style guide

**Example:**
```python
# ✅ Correct
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ❌ Wrong (Python 2 style)
def hello(name):
    return "Hello, %s!" % name
```

---

### Issue: JavaScript code uses outdated patterns

**Common mistakes:**
- Using `var` instead of `const`/`let`
- Not using arrow functions
- Missing async/await
- Using callbacks instead of Promises

**Solution:**
- Use modern ES6+ syntax
- Prefer `const` for immutable bindings
- Use arrow functions for callbacks
- Use async/await for async operations

**Example:**
```javascript
// ✅ Correct (Modern)
const fetchData = async (url) => {
  const response = await fetch(url);
  return await response.json();
};

// ❌ Wrong (Outdated)
var fetchData = function(url, callback) {
  fetch(url).then(function(response) {
    response.json().then(function(data) {
      callback(data);
    });
  });
};
```

---

### Issue: Java examples miss common patterns

**Common mistakes:**
- Not using Optional for nullable values
- Missing try-catch for checked exceptions
- Not using streams for collections
- Missing annotations (like @Override)

**Solution:**
- Use modern Java (11+) features
- Include proper exception handling
- Use streams API where appropriate
- Follow Java naming conventions

---

### Issue: Kotlin examples don't leverage language features

**Common mistakes:**
- Writing Java-style Kotlin
- Not using null safety
- Missing extension functions
- Not using data classes

**Solution:**
- Use Kotlin idiomatic patterns
- Leverage null safety (`?`, `!!`, `?.`)
- Use data classes for DTOs
- Use extension functions where appropriate

---

## Video Package Issues

### Issue: Video script lacks structure

**Symptoms:**
- No clear hook or CTA
- Missing timing estimates
- No stage directions

**Root Cause:**
Not following video_script_template.md structure.

**Solution:**
1. **Add required sections:**
   - [00:00-00:20] Hook
   - [00:20-00:45] Agenda
   - [Main sections with timing]
   - [End-45s] Recap
   - [End-30s] CTA
2. **Include stage directions:**
   - "Switch to terminal"
   - "Show diagram"
   - "Zoom in on code line 15"
3. **Add on-screen text cues:**
   - "Key concept: API endpoint"

---

### Issue: Chapter timestamps don't match video script

**Symptoms:**
- Chapter times don't align with script sections
- Non-sequential times
- First chapter doesn't start at 00:00

**Solution:**
1. **Extract timings from video script**
2. **Ensure sequential order**
3. **Start at 00:00**
4. **Match section breaks**

**Example alignment:**
```markdown
Script:
[00:00-00:20] Hook
[00:20-02:00] Setup
[02:00-05:00] Demo

Chapters:
{"time": "00:00", "title": "Hook"}
{"time": "00:20", "title": "Setup"}
{"time": "02:00", "title": "Demo"}
```

---

### Issue: Thumbnail brief is too vague

**Symptoms:**
- No specific visual concept
- Missing color palette
- No text overlay specified

**Root Cause:**
Not following thumbnail_brief_template.md.

**Solution:**
1. **Specify visual concept clearly:**
   ```
   ❌ Vague: "Something related to Kubernetes"
   ✅ Clear: "Split screen showing monolith architecture on left,
             microservices on right, with arrow between them"
   ```
2. **Define color palette:**
   - Primary color (hex code)
   - Secondary color
   - Text color
   - Contrast ratio verified
3. **Write exact text overlay:**
   ```
   Primary: "K8s Ingress" (max 5 words)
   Secondary: "Spring Boot" (optional)
   ```

---

## SEO & Metadata Issues

### Issue: Title too long

**Symptoms:**
- Validation warning: "Title is too long (72 chars)"
- Gets truncated in search results

**Root Cause:**
Title exceeds 60 character limit.

**Solution:**
1. **Shorten to under 60 characters**
2. **Keep keywords at the start**
3. **Remove filler words**

**Examples:**
```
❌ Too long (78 chars):
"A Comprehensive Guide to Building REST APIs with FastAPI for Python Developers"

✅ Just right (58 chars):
"Build REST APIs with FastAPI: Complete Python Guide"
```

---

### Issue: Description too short or too long

**Symptoms:**
- Validation warning about description length
- SEO impact: not compelling or gets cut off

**Root Cause:**
Description outside optimal 150-160 character range.

**Solution:**
1. **Target 150-160 characters**
2. **Include key benefit**
3. **Add call to action**

**Template:**
```
Learn to [benefit] with [technology]. [What's included]. Perfect for [audience].
```

**Example:**
```
Learn to build production-ready REST APIs with FastAPI. Includes validation,
docs, and deployment. Perfect for Python developers. (157 chars)
```

---

### Issue: Not enough keywords or tags

**Symptoms:**
- Validation warning: "Only 2 keywords. Recommended: 3-5."
- Poor discoverability

**Root Cause:**
Insufficient keyword research.

**Solution:**
1. **Identify 3-5 primary keywords:**
   - Tool/framework name + action (e.g., "fastapi tutorial")
   - Problem + solution (e.g., "kubernetes ingress setup")
   - Language + pattern (e.g., "python rest api")

2. **Add 8-12 tags:**
   - Language
   - Framework
   - Topic
   - Level (beginner/intermediate/advanced)
   - Type (tutorial, guide, demo)
   - Specific tools

**Example:**
```yaml
keywords:
  - "fastapi tutorial"
  - "python rest api"
  - "fastapi beginners"

tags:
  - "python"
  - "fastapi"
  - "rest-api"
  - "beginner"
  - "tutorial"
  - "web-development"
  - "backend"
  - "api-design"
```

---

### Issue: Slug not URL-friendly

**Symptoms:**
- Validation warning about non-URL-friendly characters
- Spaces, uppercase, or special characters in slug

**Root Cause:**
Not converting title properly to slug format.

**Solution:**
1. **Convert to lowercase**
2. **Replace spaces with hyphens**
3. **Remove special characters**
4. **Keep only alphanumeric and hyphens**

**Examples:**
```
Title: "Kubernetes Ingress for Spring Boot: Complete Guide"
✅ Correct slug: "kubernetes-ingress-spring-boot-complete-guide"
❌ Wrong: "Kubernetes_Ingress for Spring Boot!"
```

---

## General Troubleshooting Workflow

When you encounter any issue:

### 1. Identify the Issue
- What's the symptom?
- Which file is affected?
- What error message (if any)?

### 2. Check the Template
- Is the file following the correct template?
- Are all required sections present?
- Is the format correct?

### 3. Run Validation
```bash
python3 scripts/validate_tutorial.py article.md video_script.md chapters.json seo.yaml
```

### 4. Fix Errors
- Address critical errors first (exit code 2)
- Then warnings (exit code 1)
- Re-run validation after each fix

### 5. Review Examples
- Check EXAMPLES.md for reference
- Compare your output to examples
- Ensure similar quality and structure

### 6. Test Output
- Read article.md as if you're the learner
- Walk through code examples
- Verify links work
- Check video script flows naturally

---

## Getting Help

If issues persist after troubleshooting:

1. **Check WORKFLOW.md** - Ensure following correct process
2. **Review SKILL.md** - Verify understanding of skill requirements
3. **Consult EXAMPLES.md** - Compare with working examples
4. **Validation output** - Read error messages carefully
5. **Iterate** - Make incremental fixes and re-validate

---

## Prevention Checklist

Before finalizing any tutorial:

- [ ] Mode selection explicitly stated and justified
- [ ] All code examples are runnable (or marked as pseudo-code)
- [ ] Expected outputs shown after code blocks
- [ ] Challenges have collapsible solutions
- [ ] Troubleshooting section covers common issues
- [ ] Summary recap with checkmarks
- [ ] Next steps provide clear direction
- [ ] All files validated with script
- [ ] Links tested and working
- [ ] SEO metadata complete and optimized
- [ ] Video package (if applicable) has timing estimates
- [ ] Thumbnail brief specifies visual concept and colors

---

## Quick Reference: Error Codes

**Validation Script Exit Codes:**
- `0` - All checks passed ✅
- `1` - Warnings (non-critical) ⚠️
- `2` - Errors (critical issues) ❌

**Common Validation Errors:**
- "Missing required section" → Add section following template
- "Invalid JSON/YAML" → Check syntax with validator
- "Title too long" → Shorten to under 60 chars
- "Non-sequential chapter times" → Reorder timestamps

---

**Last Updated:** 2025
