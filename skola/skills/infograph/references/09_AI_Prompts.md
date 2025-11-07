# AI Prompts

Ready-to-use prompt templates for wireframes, content, and accessibility checks.

## Wireframe Generation

Use this prompt to get structured layout without styling decisions.

### Basic Wireframe Prompt
```
Create a numbered wireframe for a [TEMPLATE TYPE] infographic about [TOPIC].

Requirements:
- Show only numbered regions with dimensions
- Specify region type for each (title, content, code, diagram, callout)
- No colors, fonts, or styling details
- Include approximate size ratios
- Target dimensions: [WIDTH]×[HEIGHT]px

Return as a numbered list with region descriptions.
```

### Example Usage
```
Create a numbered wireframe for a Process Flow infographic about CI/CD pipeline.

Requirements:
- Show only numbered regions with dimensions
- Specify region type for each (title, content, code, diagram, callout)
- No colors, fonts, or styling details
- Include approximate size ratios
- Target dimensions: 1200×800px

Return as a numbered list with region descriptions.
```

### Expected Output Format
```
1. Title Bar (1200×100px) - type: title
2. Step 1: Build (280×150px) - type: content
3. Arrow 1 (40×150px) - type: connector
4. Step 2: Test (280×150px) - type: content
5. Arrow 2 (40×150px) - type: connector
...
```

## Content Placement

Use this prompt to fill wireframe regions with actual content.

### Content Placement Prompt
```
Place the following content into the wireframe regions:

**Wireframe:**
[PASTE WIREFRAME HERE]

**Content to place:**
[PASTE YOUR FACTS, CONCEPTS, CODE HERE]

Requirements:
- ≤80 words per content region
- Label all edges with verb+noun (e.g., "sends request")
- Use monospace indicators for code (wrap in backticks)
- Add alt text describing structure and key takeaway
- Identify any missing content needed

Return filled regions with content mapped to region numbers.
```

### Example Usage
```
Place the following content into the wireframe regions:

**Wireframe:**
1. Title Bar (1200×100px) - type: title
2. Step 1 (280×150px) - type: content
3. Step 2 (280×150px) - type: content

**Content to place:**
- Git commit triggers webhook
- Jenkins pulls code and runs tests
- Docker builds container image
- Kubernetes deploys to cluster

Requirements:
- ≤80 words per content region
- Label all edges with verb+noun
- Add alt text

Return filled regions with content mapped to region numbers.
```

## Accessibility Audit

Use this prompt to validate accessibility compliance.

### Accessibility Audit Prompt
```
Audit the following infographic design for accessibility:

**Design description:**
[DESCRIBE LAYOUT, COLORS, TEXT SIZES, VISUAL ELEMENTS]

Check for:
1. Contrast ratios (WCAG AA: 4.5:1 normal text, 3:1 large text)
2. Color-independence (information conveyed without relying on color alone)
3. Text sizes (minimum 14px body, 12px annotations)
4. Alt text presence and quality (structure + takeaway)
5. Reading order for screen readers

Return:
- List of issues found with severity (Critical, High, Medium, Low)
- Specific fixes for each issue
- Pass/Fail status for WCAG AA compliance
```

### Example Usage
```
Audit the following infographic design for accessibility:

**Design description:**
- Title: 32px bold, dark gray (#333) on white background
- Body text: 14px regular, medium gray (#666) on white background
- Accent color: Blue (#3498db) used for arrows and highlights
- Error states shown only in red (#e74c3c)
- Code blocks: 12px monospace on light gray (#f5f5f5)

Check for WCAG AA compliance and list all issues with fixes.
```

## Style Token Definition

Use this prompt to establish consistent design system.

### Style Tokens Prompt
```
Define style tokens for a [STYLE VARIATION] infographic about [TOPIC].

Provide:
1. **Type scale**: Font sizes for title/heading/body/annotation/code
2. **Color palette**:
   - Primary/accent colors (hex codes)
   - Semantic colors (success, error, info, neutral)
   - Background and text colors
3. **Spacing scale**: Grid increments (e.g., 4px, 8px, 16px, 24px)
4. **Stroke weights**: Line thicknesses for borders, connectors, dividers
5. **Corner radius**: Rounding for boxes/cards (if applicable)

Target audience: [AUDIENCE]
Accessibility: WCAG AA compliant

Return as structured token list ready for design tool implementation.
```

### Example Usage
```
Define style tokens for a Minimalist Technical infographic about API architecture.

Provide type scale, color palette, spacing scale, stroke weights, and corner radius.

Target audience: Backend developers
Accessibility: WCAG AA compliant

Return as structured token list ready for Figma implementation.
```

## Iteration & Refinement

Use this prompt to improve existing designs.

### Refinement Prompt
```
Review this infographic design and suggest improvements:

**Current design:**
[DESCRIBE OR PASTE DESIGN]

**Feedback received:**
[USER COMMENTS OR TEST RESULTS]

Analyze against Core Principles (clarity, hierarchy, flow, cognitive load, accessibility) and suggest:
1. Specific changes to improve clarity
2. Adjustments to visual hierarchy
3. Flow optimization ideas
4. Ways to reduce cognitive load
5. Accessibility enhancements

Prioritize changes by impact (High/Medium/Low).
```

## Template Selection

Use this prompt to choose the right template.

### Template Selection Prompt
```
Recommend the best infographic template for the following:

**Topic:** [TOPIC]
**Audience:** [AUDIENCE]
**Goal:** [LEARNING OBJECTIVE]
**Content type:** [Data/Process/Conceptual/Hybrid]
**Key information:** [BULLET POINTS OF MAIN CONTENT]

Available templates:
- Concept Map
- Process Flow
- Algorithm Breakdown
- Comparison Matrix
- Architecture Snapshot
- How-To Ladder

Return:
- Recommended template with justification
- Alternative template if primary doesn't fit
- Suggested modifications to template structure
```

## Export Specification

Use this prompt to define export requirements.

### Export Specification Prompt
```
Generate export specifications for this infographic:

**Usage contexts:** [Social media / Blog / Presentation / Print / Documentation]
**Brand requirements:** [Colors, fonts, logo placement]

Provide:
1. Required dimensions for each platform
2. File formats needed (PNG/SVG/PDF)
3. Resolution recommendations (72dpi web, 300dpi print)
4. Color profile (RGB/CMYK)
5. Alt text template
6. Usage guidelines (when/where to use)

Return as checklist with export settings.
```
