---
description: Create an implementation plan after the feature spec is approved
---

# /plan

This command creates an implementation plan after the feature spec is approved.

## Process

1. **Check Current Feature**
   - Get current branch name
   - Verify feature spec exists at `/design-intent/specs/[branch-name]/feature-spec.md`
   - If no spec exists, stop and inform user

2. **Read Feature Spec**
   Extract from the spec:
   - Feature name and purpose
   - User stories and success criteria
   - What needs to be built (not how)

3. **Check for Visual References**
   If feature spec mentions design references/screenshots:
   - Add "Visual Reference Mapping" section to the plan
   - Map reference UI elements to feature requirements
   - Example:
     ```
     ## Visual Reference Mapping

     ### Reference: Loop Gallery → Our: Prototype Gallery
     - Loop shows workspaces → We show prototypes
     - Keep: 3-column grid, card hover effects, sidebar layout
     - Adapt: Workspace metadata → Prototype metadata (title, author, preview)
     ```

4. **Check Existing Design Intent**
   - Review existing `/design-intent/patterns/` for established patterns that should be reused
   - Note any custom patterns that should be followed for consistency

5. **Create Implementation Plan**
   Create `/design-intent/specs/[branch-name]/implementation-plan.md` with:
   - Technical approach (keeping it simple per constitution)
   - Visual reference mapping (if applicable)
   - Existing pattern references (for consistency)
   - Component structure
   - Time estimates (team vs AI-assisted)
   - Implementation phases

6. **Follow Constitution**
   Ensure the plan:
   - Starts simple (Article I)
   - Uses framework features first (Article II)
   - Includes responsive design approach (Article III)
   - Focuses on mock data and happy paths (Article IV)
   - Follows feature-first principle (Article V)
   - Uses existing patterns for consistency (Article VII)

7. **Confirm Creation**
   Report back:
   - Implementation plan created at: `/design-intent/specs/[branch-name]/implementation-plan.md`
   - Key technical decisions made
   - Ready to build when user approves

## Remember
- The spec defines WHAT and WHY
- The implementation plan defines HOW
- Keep it simple - this is for prototypes, not production
- Follow the constitution's principles
