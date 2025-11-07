# Tools & AI Workflows

Design tools and AI integration best practices for infographic creation.

## Design Tools

### Professional Tools
* **Figma**: Collaborative design, components, auto-layout
* **Draw.io (diagrams.net)**: Free, technical diagrams, export flexibility
* **Adobe Illustrator**: Vector graphics, precise control

### Quick Tools
* **Canva**: Templates, drag-and-drop, social media formats
* **Adobe Express**: Fast creation, brand kits
* **Google Slides**: Simple layouts, collaboration

### Code-Based Diagrams
* **Mermaid**: Flowcharts, sequence diagrams, class diagrams from markdown
* **PlantUML**: UML diagrams from text
* **D3.js**: Custom data visualizations

## AI Workflow Pattern

Follow this sequence when working with AI tools for infographic creation:

### 1. Brief
* Provide clear context: audience, goal, key message
* Specify constraints: dimensions, color palette, accessibility requirements
* Share content to visualize

### 2. Wireframe
* Request numbered wireframe showing regions only
* No styling at this stage—focus on structure
* Iterate on layout and information hierarchy

### 3. Content
* Fill wireframe regions with actual content
* Keep sections short (≤80 words per panel)
* Request multiple content variations if needed

### 4. Style Tokens
* Define type scale, colors, spacing
* Apply consistently across all elements
* Request design system documentation

### 5. Accessibility
* Run contrast checks
* Verify color-independent cues
* Add descriptive alt text
* Test with screen reader scenarios

### 6. Export
* Generate variants for different platforms
* Provide source files for future edits
* Include usage guidelines

## AI Prompting Best Practices

### Keep Sections Short
Break complex requests into sequential prompts rather than one large request.

**Good**:
> "Create a numbered wireframe for a process flow showing 5 steps of a CI/CD pipeline"

**Poor**:
> "Create a complete infographic with styling, colors, icons, and text explaining the entire CI/CD process including build, test, deploy, monitor, and rollback phases with examples"

### Ask for Variants
Request multiple options for comparison:
> "Show me 3 layout variations: one vertical ladder, one horizontal flow, and one circular process"

### Specify Format
Be explicit about deliverables:
> "Provide the wireframe as a numbered list with dimensions and region types, not as an image"

### Iterate Incrementally
Build complexity gradually rather than all at once:
1. Structure first
2. Content next
3. Visual polish last
4. Accessibility check final

## Collaboration Workflow

### With Designers
1. AI generates structure and content
2. Designer applies brand guidelines and polish
3. AI assists with accessibility validation

### With Subject Matter Experts
1. SME provides technical content
2. AI structures information pedagogically
3. SME validates accuracy
4. AI refines based on feedback

### With Developers
1. Developer provides code examples
2. AI creates visual representation
3. Developer verifies technical accuracy
4. AI generates documentation
