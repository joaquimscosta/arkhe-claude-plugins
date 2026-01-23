# Lyra Troubleshooting Guide

Common issues and solutions when using the Lyra prompt optimizer.

---

## Common Issues

### 1. Optimized Prompt Is Too Long

**Symptoms:**
- Optimized prompt exceeds AI's context limits
- Prompt feels bloated with unnecessary detail
- Users complain about verbosity

**Causes:**
- DETAIL mode used for simple requests
- Too many optional sections included
- Over-specification of obvious constraints

**Solutions:**

1. **Use BASIC mode for simple prompts**
   ```
   /lyra BASIC Summarize this article
   ```

2. **Remove optional sections**
   - Cut "nice to have" context
   - Remove redundant constraints
   - Eliminate examples if pattern is clear

3. **Compress multi-line to single-line where possible**
   ```
   Before:
   Output Format:
   - Use markdown
   - Include headers
   - Add bullet points

   After:
   Output: Markdown with headers and bullet points
   ```

4. **Ask user about essential vs optional elements**
   - What must be in the output?
   - What can be left to AI's judgment?

---

### 2. Platform Mismatch

**Symptoms:**
- Optimized prompt uses techniques not supported by target AI
- Claude-optimized prompt used in ChatGPT gives poor results
- XML tags confuse non-Claude models

**Causes:**
- Platform not specified in command
- User copied prompt to different platform
- Generic optimization applied

**Solutions:**

1. **Always specify platform**
   ```
   /lyra BASIC for Claude Write documentation
   /lyra DETAIL for ChatGPT Analyze this data
   ```

2. **Platform-specific adjustments**

   | If Using | Avoid | Prefer |
   |----------|-------|--------|
   | ChatGPT | XML tags | Markdown headers, numbered lists |
   | Claude | Numbered-only structure | XML tags, detailed context |
   | Gemini | Rigid structure | Exploratory framing |

3. **Universal fallback pattern**
   ```
   Role: [Who the AI should be]
   Context: [Background information]
   Task: [What to do]
   Output: [Expected format]
   ```

---

### 3. Optimization Doesn't Help

**Symptoms:**
- AI response quality unchanged after optimization
- User says "it's basically the same"
- Optimization feels superficial

**Causes:**
- Original prompt was already well-structured
- Wrong optimization techniques applied
- Missing critical context that no prompt can replace

**Solutions:**

1. **Check if optimization is needed**
   - Well-formed prompts may need minor tweaks only
   - Acknowledge when original is good enough

2. **Focus on the actual weakness**
   ```
   Original: "Write a Python function to sort a list"

   Issue: Not vague, just missing edge cases

   Better optimization focus:
   - Specify sorting algorithm preferences
   - Define handling for empty lists, duplicates
   - Specify return type and error handling
   ```

3. **Ask clarifying questions even in BASIC mode if stuck**
   - What's actually wrong with current AI responses?
   - What specific improvement are they looking for?

4. **Sometimes the problem isn't the prompt**
   - User needs better input data
   - Task is fundamentally ambiguous
   - Wrong AI model for the task

---

### 4. Missing Critical Context

**Symptoms:**
- Optimized prompt makes assumptions that don't apply
- User says "but my situation is different"
- Generic advice when specific needed

**Causes:**
- Skipped DETAIL mode when it was needed
- Didn't gather domain-specific requirements
- User withheld relevant information

**Solutions:**

1. **Switch to DETAIL mode**
   ```
   /lyra DETAIL for Claude [prompt]
   ```
   Then ask targeted questions about context.

2. **Probe for hidden constraints**
   - Technical constraints (language, framework, version)
   - Business constraints (compliance, branding, audience)
   - Personal constraints (expertise level, time available)

3. **Include context placeholders**
   ```
   [Note: Customize based on your specific:
   - Industry/domain
   - Target audience
   - Existing systems
   - Compliance requirements]
   ```

---

### 5. Wrong Mode Selected

**Symptoms:**
- BASIC mode for complex request = shallow optimization
- DETAIL mode for simple request = wasted time
- User frustrated with too many/few questions

**Causes:**
- User defaulted to one mode
- Complexity misjudged

**Solutions:**

1. **Mode selection guidance**

   | Prompt Type | Best Mode |
   |-------------|-----------|
   | Clear, simple task | BASIC |
   | Multi-step process | DETAIL |
   | Domain-specific | DETAIL |
   | Quick polish | BASIC |
   | First time on topic | DETAIL |

2. **Suggest mode switch if mismatch detected**
   ```
   "This looks like a complex request. Would you prefer
   DETAIL mode for more thorough optimization?"
   ```

3. **Allow mode override mid-process**
   - If BASIC feels insufficient, offer to restart with DETAIL
   - If DETAIL seems overkill, offer to skip remaining questions

---

## Platform-Specific Issues

### Claude Issues

| Issue | Solution |
|-------|----------|
| XML tags being treated as text | Ensure proper tag syntax: `<tag>content</tag>` |
| Context too long | Use XML sections to organize, Claude handles long context |
| Responses too formal | Add tone guidance in prompt |

### ChatGPT Issues

| Issue | Solution |
|-------|----------|
| Ignores complex structure | Simplify to numbered steps |
| Adds unsolicited content | Add explicit constraints: "Only include X, Y, Z" |
| System message not working | Format as: "ROLE: ... TASK: ..." |

### Gemini Issues

| Issue | Solution |
|-------|----------|
| Too creative/divergent | Add constraints and specific requirements |
| Misses details | Use explicit checklists |
| Inconsistent formatting | Provide format example |

---

## Tips for Better Results

### Before Using Lyra

1. **Know your goal**: What specifically should improve?
2. **Gather context**: What details matter for this task?
3. **Choose platform**: Where will this prompt be used?
4. **Select mode**: How thorough should optimization be?

### During Optimization

1. **Provide examples**: Show what good output looks like
2. **Be specific about failures**: What went wrong before?
3. **Share constraints**: Budget, time, technical limits
4. **Indicate preferences**: Tone, style, format

### After Optimization

1. **Test the prompt**: Run it and evaluate results
2. **Iterate if needed**: Good prompts often need 2-3 rounds
3. **Save successful prompts**: Build a personal library
4. **Note what worked**: Learn patterns for future use

---

## When to Skip Optimization

Not every prompt needs Lyra:

- **Already specific**: "Translate 'hello' to Spanish"
- **Trivial tasks**: "What's 2+2?"
- **One-word answers**: "Capital of France?"
- **Well-formed requests**: Clear role, context, output already specified

Focus optimization effort where it matters: complex, ambiguous, or high-stakes prompts.

---

## Getting Help

If issues persist:

1. **Check examples**: Review [EXAMPLES.md](EXAMPLES.md) for similar cases
2. **Review methodology**: Ensure all 4 phases in [WORKFLOW.md](WORKFLOW.md) were applied
3. **Try different mode**: Switch between BASIC and DETAIL
4. **Use --research flag**: Get current best practices via web search
5. **Simplify**: Sometimes starting fresh works better than fixing
