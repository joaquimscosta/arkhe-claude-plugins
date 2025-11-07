# Examples & Styles

Successful infographic patterns for technical content.

## Example 1: Backpropagation in 4 Panels

**Template**: Process Flow

**Structure**:
1. **Forward Pass**: Input → Hidden → Output (blue arrows)
2. **Loss Calculation**: Compare prediction vs actual (red box)
3. **Gradient Computation**: Chain rule backwards (orange arrows)
4. **Weight Update**: Apply gradients to weights (green arrows)

**Why it works**:
* Unidirectional arrows per panel reduce confusion
* Color coding separates phases
* Sequential numbering provides clear flow
* Mathematical notation in monospace font
* 60-80 words per panel keeps focus

**Audience**: ML students, engineers learning neural networks

## Example 2: Time Complexity Comparison + Decision Tree

**Template**: Hybrid (Comparison Matrix + Process Flow)

**Structure**:
* **Top half**: Matrix comparing O(n), O(n log n), O(n²)
  - Rows: Algorithm names (Bubble Sort, Quick Sort, Merge Sort)
  - Columns: Best case, Average case, Worst case
  - Visual: Graph showing growth curves
* **Bottom half**: Decision tree for "Which sort to use?"
  - Factors: Data size, memory constraints, stability requirements
  - Outcomes: Specific algorithm recommendations

**Why it works**:
* "What" vs "what to choose" pairing
* Matrix provides comparison data
* Decision tree provides actionable guidance
* Two related but distinct information types
* Reduces need for multiple separate infographics

**Audience**: Computer science students, interview prep

## Example 3: Kubernetes Resource Map with Concentric Scope

**Template**: Architecture Snapshot (modified)

**Structure**:
* **Outer ring**: Cluster resources (Nodes, Namespaces)
* **Middle ring**: Workload resources (Deployments, Pods, Services)
* **Inner ring**: Configuration (ConfigMaps, Secrets)
* **Center**: Application (your app)
* Arrows show containment and relationships

**Why it works**:
* Concentric circles reduce line crossings
* Clear visual hierarchy by scope/abstraction level
* Containment relationships obvious from position
* Legend explains resource types
* Easier to understand than traditional box-and-line diagrams

**Audience**: DevOps engineers, Kubernetes learners

## Example 4: REST API Design Pattern

**Template**: How-To Ladder

**Structure**:
1. **Define Resource**: Noun-based endpoints (`/users`, `/posts`)
2. **Map HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (remove)
3. **Design URL Structure**: Collection vs individual (`/users` vs `/users/123`)
4. **Add Query Parameters**: Filtering, sorting, pagination
5. **Version Your API**: `/v1/users` vs `/v2/users`
6. **Common Errors Strip**: 404 Not Found, 401 Unauthorized, 400 Bad Request

**Why it works**:
* Progressive complexity building
* Each step has clear input/output
* Code examples in monospace
* Error prevention at bottom
* Vertical ladder format easy to follow

**Audience**: Backend developers, API designers

## Example 5: Git Branching Strategy

**Template**: Concept Map

**Structure**:
* **Central node**: Main branch (production)
* **Connected nodes**:
  - Develop branch (integration)
  - Feature branches (active work)
  - Release branches (staging)
  - Hotfix branches (emergency fixes)
* **Labeled edges**:
  - "merge into" (solid arrow)
  - "branch from" (dashed arrow)
  - "tag as" (dotted line to version numbers)
* **Example panel**: Timeline showing actual branch lifecycle

**Why it works**:
* Abstract concept made concrete
* Relationship types clearly differentiated
* Real-world example grounds theory
* Color coding by branch type
* Legend explains line types

**Audience**: Development teams, Git beginners

## Style Variations

### Minimalist Technical
* Monochrome + 1 accent color
* Sans serif only (no display font)
* Maximum white space
* Focus on clarity over decoration
* **Best for**: API documentation, system diagrams

### Educational Vibrant
* 2-3 accent colors (semantic)
* Display font for titles
* Icons for visual interest
* Callout boxes for tips
* **Best for**: Tutorials, student materials

### Professional Consulting
* Corporate brand colors
* Clean grid layout
* Data visualizations prominent
* Minimal decorative elements
* **Best for**: Client presentations, reports

### Developer Dark Mode
* Dark background (#1e1e1e)
* Syntax highlighting colors
* High contrast text (#e0e0e0)
* Monospace heavy
* **Best for**: Technical blogs, code-focused content
