# These instructions are like this project's "Constitution"

This constitution establishes the core principles that govern the development of React front-end prototypes. These principles are designed to ensure simplicity, effectiveness, and realistic user experiences for static front-end prototypes that simulate realistic apps.

## Project Configuration

<!-- AUTO-FILL: This section is customized by /setup based on project detection -->

**Project Type:** <!-- AUTO-FILL: Enterprise/Consumer/Internal/Marketing -->
**Framework:** <!-- AUTO-FILL: React/Next.js/Vue/Angular -->
**Design System:** <!-- AUTO-FILL: Fluent UI/Material UI/Chakra/Tailwind -->
**MCP Capabilities:** <!-- AUTO-FILL: List of available MCPs -->

---

## Feature Types & Application

This constitution governs prototype development:
- **Static Front-end Prototypes**: Realistic app simulations focused on user experience and interaction patterns
- **Focus on Creation**: Prioritize building and demonstrating concepts over code quality and process overhead

---

## Article I: The Simplicity Imperative

### Section 1.1: Start Simple, Evolve Gradually

All implementations **MUST** begin with the simplest viable architecture. Add complexity only when:

* User feedback drives it
* The demo story requires it

### Section 1.2: YAGNI (You Aren't Gonna Need It)

No feature may be added based on hypothetical needs. Architectural decisions **MUST** be justified by real, current requirements.

### Section 1.3: Minimal Project Structure

Start with the fewest number of projects:

* Single React app preferred for prototypes
* Additional projects require documented justification
* Prefer consolidation over separation

### Section 1.4: Pattern Justification

Complex UI patterns (deeply nested state, custom rendering engines) **PROHIBITED** unless:

* Simpler component composition doesn't work
* Pattern gives measurable visual/UX benefits

### Section 1.5: No-Change Without Cause

Unnecessary modifications are discouraged. Implementation code, refactoring, or restructuring **MUST NOT** be introduced without clear justification. Changes must serve a concrete purpose such as:

* Improving clarity or maintainability
* Fixing a verified issue
* Enabling measurable benefits
* **Exception**: Changes that improve demo storytelling are always justified

Cosmetic or speculative changes are considered non-compliant unless tied to an approved implementation plan.

### Section 1.6: Browser Simulation Constraints

For browser-based prototypes:
* Simulate only visual browser chrome (no real browser APIs)
* Mock all external data sources
* Use React state for all data persistence (no localStorage)
* Fake real-time updates with intervals/timeouts

---

## Article II: The Anti-Abstraction Principle

### Section 2.1: Framework Trust

Use framework features directly unless:

* Required functionality is missing
* Multiple implementations must be supported
* Proven portability needs exist

### Section 2.2: Framework-First Development

**MANDATORY**: Always research framework capabilities before custom implementation:

* Research using available tools (MCP, documentation, web search) before coding
* Read component documentation thoroughly before implementation
* Use built-in component props over custom implementations
* Leverage framework responsive utilities before custom CSS
* Verify accessibility features are properly configured
* Follow framework naming conventions and patterns
* **MANDATORY for Fluent UI**: Query MCP Fluent server before implementing any component
* Check Fluent UI v9 docs for existing patterns before custom solutions
* Use Fluent tokens for all spacing, colors, and typography

### Section 2.3: Single Model Principle

Data **MUST** be represented with minimum number of models:

* Use framework models directly
* Add transfer objects only for serialization needs
* Avoid parallel model hierarchies unless justified

### Section 2.4: Direct Dependencies

Prefer concrete implementations over interfaces unless:

* Multiple implementations exist
* Abstraction has clear, documented benefits

---

## Article III: The Responsive Design Mandate

### Section 3.1: Universal Responsive Requirements

All UI components **MUST** be responsive across device breakpoints:

* **Desktop behavior**: Optimized for 640px+ screens
* **Mobile behavior**: Optimized for <768px screens
* **Minimum margins**: 16px spacing on small screens
* **Framework breakpoints**: Use framework-provided breakpoints, not custom ones

### Section 3.2: Mobile-First Approach

Design and implementation **MUST** consider mobile experience:

* Test on mobile breakpoints during development
* Ensure touch-friendly interaction areas
* Maintain readability and usability on small screens
* Prevent content from being flush against screen edges

### Section 3.3: Responsive Design Validation

Every UI component implementation **MUST**:

* Define responsive behavior in specification
* Test across target breakpoints
* Document responsive patterns used
* Verify accessibility across device sizes

---

## Article IV: The Prototype Principles

### Section 4.1: Mock Data Excellence

All data **MUST** be:
* Realistic enough to tell the story
* Consistent across the demo flow
* Pre-seeded with compelling examples
* Reproducible (use fixed seeds for randomness)

### Section 4.2: Happy Path Priority

Focus on the demo flow:
* Implement complete happy paths first
* Edge cases only if they enhance the story
* Error states can show static messages
* Performance optimization is unnecessary

### Section 4.3: Visual Impact Over Implementation

Prioritize what users see:
* Animations and transitions matter more than code structure
* Mock complex operations with simple timeouts
* Pre-build variants rather than generating them
* Use static data that shows the concept clearly

---

## Article V: Feature-First Development

### Section 5.1: Feature-First, Style-Second Principle

**ABSOLUTE RULE**: Features define WHAT, references define HOW it looks.

When implementing prototypes:
* **Features are sacred**: Never sacrifice feature requirements for visual accuracy
* **References are style guides**: Adapt their patterns to your features
* **Content drives design**: Your data shapes how reference styles apply
* **Function over form**: A working prototype with adapted styling beats a pixel-perfect clone of the wrong thing

### Section 5.2: Visual Reference Mapping

When visual references are provided:
* **Map, don't copy**: Understand what reference UI represents
* **Adapt to your needs**: Reference shows workspaces? Build prototypes in that style
* **Keep the essence**: Maintain visual language while changing content
* **Document mappings**: Record what reference elements become in your feature
* **Don't force references**: If a reference doesn't fit your feature, acknowledge it and adapt or find alternatives

Common adaptations required:
* Reference shows generic content → Replace with feature-specific content
* Reference has different navigation → Keep your feature's navigation, style it like reference
* Reference lacks needed elements → Add them using reference's design language
* Reference has extra elements → Remove them, keep the visual style
* Reference doesn't match feature needs → Extract design language, apply to appropriate components

---

## Article VI: UI Quality Standards

### Section 6.1: Quality Indicators

High-quality UI implementation includes:
* **Microinteractions**: Smooth transitions (0.2s ease), consistent hover states
* **Visual Hierarchy**: Clear primary, secondary, tertiary actions
* **Consistent Spacing**: Follow established spacing system
* **Polish Details**: Proper focus states, loading states, empty states
* **Content Quality**: Realistic data, proper images, no "lorem ipsum" in final

### Section 6.2: Quality Without Feature Sacrifice

Improve UI quality by:
* **Better placeholders**: Use realistic, high-quality images
* **Refined animations**: Match reference timing and easing
* **Complete states**: Error, loading, empty, success states
* **Accessibility**: Proper ARIA, keyboard navigation, focus indicators
* **Performance**: Optimize images, lazy load, smooth scrolling

Never improve quality by:
* Adding features not in spec
* Removing features for cleaner look
* Changing navigation for aesthetics
* Prioritizing beauty over function

---

## Article VII: Design Intent Documentation

### Section 7.1: Living Design Memory

The `/design-intent/` folder is the persistent memory of successful design decisions:
* **Documents proven success**: Only captures patterns that work, after verification
* **Design dialect focus**: Records custom decisions, not design system artifacts
* **Single source of truth**: Future features consult for consistency

### Section 7.2: Implementation-First Documentation Workflow

**During Implementation Planning**:
* Check existing design intent for established patterns
* Extract from references purely to implement accurately
* NO upfront documentation - focus on visual accuracy

**During Implementation**:
* Prioritize visual accuracy through iteration
* Support "vibe coding" until user satisfaction
* NO documentation during iteration - focus on getting it right

**During Documentation Phase** (triggered by user command):
* `/document-intent` - Document all design dialect patterns
* `/document-intent [pattern]` - Document specific pattern only
* Capture only successful, proven decisions

### Section 7.3: What to Document (Design Dialect Only)

Document in `/design-intent/` only custom decisions that won't come from design system:
* **Custom Layout Patterns**: App-specific compositions and arrangements
* **Contextual Spacing**: Spacing decisions that deviate from standard tokens
* **Content Hierarchies**: Information architecture patterns specific to the app
* **Custom Compositions**: How standard components are combined uniquely

### Section 7.4: What NOT to Document (Design System Artifacts)

Do NOT document standard design system elements:
* Colors that are just framework tokens
* Typography using standard scales
* Component props that are library defaults
* Standard responsive breakpoints
* Default spacing values

### Section 7.5: Documentation Triggers

Documentation happens on explicit user command:
* **Manual trigger**: User says `/document-intent` when satisfied with results
* **Never automatic**: No documentation during implementation or iteration
* **Success-based**: Only document patterns that achieved user satisfaction

---

## Appendix: Project-Type Specific Guidance

<!-- AUTO-FILL: This section is customized by /setup based on detected project type -->

### For Enterprise Dashboards

<!-- Include if project type is Enterprise -->

**Priority Adjustments:**
- **Data Density**: Optimize for information display; users need to compare and analyze
- **Keyboard Navigation**: Critical for power users; ensure all actions are keyboard accessible
- **Consistent Patterns**: Prioritize predictability over novelty; users work faster with familiar patterns
- **Table-First**: Default to tables for data display; cards only when comparison isn't needed

**Quality Indicators:**
- Sorting and filtering work smoothly
- Bulk actions are discoverable
- Export functionality is accessible
- Loading states show progress for large datasets

### For Consumer Applications

<!-- Include if project type is Consumer -->

**Priority Adjustments:**
- **Visual Appeal**: Emphasize breathing room and visual delight
- **Progressive Disclosure**: Hide complexity; reveal on demand
- **Microinteractions**: Invest in smooth transitions and feedback
- **Card-First**: Default to cards and carousels; tables only for comparison views

**Quality Indicators:**
- Delightful hover states and animations
- Clear visual hierarchy guides the eye
- Empty states are helpful and encouraging
- Onboarding flows are smooth and skippable

### For Internal Tools

<!-- Include if project type is Internal -->

**Priority Adjustments:**
- **Efficiency**: Optimize for speed; users perform tasks repeatedly
- **Keyboard Shortcuts**: Power users expect them
- **Dense Information**: More data per screen is acceptable
- **Functional Over Beautiful**: Polish is nice but function is critical

### For Marketing Sites

<!-- Include if project type is Marketing -->

**Priority Adjustments:**
- **Visual Impact**: First impressions matter most
- **Performance**: Speed affects conversion
- **Mobile-First**: Mobile traffic often dominates
- **CTA Clarity**: Calls to action must be unmistakable

---

## Appendix: Framework-Specific Guidance

<!-- AUTO-FILL: This section is customized by /setup based on detected framework -->

### For React + TypeScript

<!-- Include if framework is React + TypeScript -->

**Component Patterns:**
- Use functional components with hooks
- Prefer composition over prop drilling
- Type all props and state explicitly
- Use discriminated unions for complex state

**State Management:**
- Start with useState/useReducer
- Add context only when prop drilling is painful
- External state (Zustand, Redux) only if context isn't enough

### For Next.js

<!-- Include if framework is Next.js -->

**Component Decisions:**
- Default to Server Components
- Use 'use client' only when needed (interactivity, browser APIs)
- Colocate data fetching with components

**Route Organization:**
- Group by feature, not by type
- Use route groups for shared layouts
- Prefer parallel routes for complex UIs

### For Design System: Fluent UI

<!-- Include if design system is Fluent UI -->

**Mandatory Practices:**
- Query Fluent Pilot MCP before implementing any component
- Use Fluent tokens for ALL spacing, colors, typography
- Check v9 docs for existing patterns before custom solutions
- Follow Fluent naming conventions

### For Design System: Material UI

<!-- Include if design system is Material UI -->

**Mandatory Practices:**
- Use MUI's sx prop for styling
- Follow Material Design guidelines for spacing
- Use theme tokens, not hardcoded values
- Check MUI component API before custom solutions

### For Design System: Tailwind CSS

<!-- Include if design system is Tailwind -->

**Mandatory Practices:**
- Use design system classes, not arbitrary values
- Extract repeated patterns to components
- Follow responsive prefix conventions (sm:, md:, lg:)
- Use @apply sparingly
