# Code Explanation Troubleshooting

Common issues when using the code-explanation skill.

---

## Explanation Too Long or Verbose

**Symptoms**: Output exceeds what the user needs, overwhelming detail for simple code.

**Cause**: Complexity assessment defaulted to advanced when user needed a quick overview.

**Fix**: Specify the audience level or ask for a brief explanation. The skill adapts depth based on the audience indicator (beginner/intermediate/advanced).

---

## Mermaid Diagrams Not Rendering

**Symptoms**: Raw Mermaid syntax appears instead of a visual diagram.

**Cause**: The viewing environment does not support Mermaid rendering (e.g., plain terminal output).

**Fix**: Copy the Mermaid code block into a compatible viewer:
- GitHub markdown files render Mermaid natively
- Use [mermaid.live](https://mermaid.live) for browser-based rendering
- VS Code with the Mermaid extension

---

## Missing Context for Explanation

**Symptoms**: Explanation references unknown types, functions, or modules without explaining them.

**Cause**: The code depends on project-specific abstractions not visible in the snippet provided.

**Fix**: Provide surrounding context — either the full file or references to the imported modules. The skill works best when it can read related files.

---

## Explanation Doesn't Match Code Version

**Symptoms**: Explanation references patterns or APIs that don't match the actual code.

**Cause**: The skill may infer common patterns from the language/framework rather than reading the exact code.

**Fix**: Ensure the skill reads the actual file using the `Read` tool before explaining. If explaining a snippet, paste the exact code rather than paraphrasing.
