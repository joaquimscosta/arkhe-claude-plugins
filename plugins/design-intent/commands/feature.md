---
description: Create a new feature specification following the SDD workflow
---

# /feature

This command guides AI assistants through creating a new feature following the SDD workflow.

## Required Information

Before creating a feature, ensure you have:
- **Problem Statement**: What problem are we solving?
- **User Personas**: Who will use this feature?
- **Success Metrics**: How will we measure if it works?
- **Assumptions**: What do we believe about user needs?
- **Scope**: Clear boundaries of what's included/excluded

If any information is missing, ask for it before proceeding.

## Process

### 1. Create Feature Branch

```bash
# Find repository root
git rev-parse --show-toplevel

# Check existing features
ls design-intent/specs/

# Generate next number (e.g., 001, 002, 003)
# Create branch name: ###-feature-name (2-3 words, lowercase, hyphenated)
git checkout -b ###-feature-name
```

### 2. Create Feature Structure

```bash
# Create feature directory
mkdir -p design-intent/specs/###-feature-name

# Copy templates
cp design-intent/specs/000-template/feature-spec.md design-intent/specs/###-feature-name/
cp design-intent/specs/000-template/implementation-plan.md design-intent/specs/###-feature-name/
```

### 3. Fill Feature Spec

Update the feature spec with:
- Current date
- Author name
- Feature branch name
- Problem statement focusing on user impact
- User stories with clear happy paths
- Success criteria tied to metrics

### 4. Create Initial Assumption

Before jumping to solutions, document in the spec:
- What assumption are we making about user behavior?
- What hypotheses could validate this assumption?
- What metrics would prove we're right?

### 5. Confirm Creation

Report back:
- Branch name created
- Files created at paths
- Next step: Review feature spec and create implementation plan

## Example Output

"I've created feature branch `003-game-preloading` with:
- `/design-intent/specs/003-game-preloading/feature-spec.md`
- `/design-intent/specs/003-game-preloading/implementation-plan.md`

The spec captures your assumption that slow game loads cause user drop-off. Next, we should review the spec and plan implementation approaches."
