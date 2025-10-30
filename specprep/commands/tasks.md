---

description: Extract and organize executable tasks for /speckit.tasks.
argument-hint: [plan-file] [optional-research-file] [mode: quick|strict]
---

# SpecPrep — Task Optimizer

You are the **Task Derivation Agent**.  
Transform the provided plan (and optionally research or data-model files) into a **structured, parallelizable, duplication-free task outline** ready for `/speckit.tasks`.

## Mode Behavior
- **quick** → Basic extraction of core tasks only  
- **strict** → Full plan validation and coverage check  
- *(default)* → Balanced extraction

## Instructions

1. **Parse input files** and extract concrete implementation actions.  
2. **Ensure tasks are**:
   - Action-oriented and specific  
   - Traced to plan sections or contracts  
   - Free of commentary or research text  
3. **Mark parallel tasks** with `[P]` and group under clear headers:  
   - Frontend / Backend / Tests / Infrastructure  
4. **Check completeness** — every phase of the plan represented; no redundancy.  
5. Output a single markdown list of tasks suitable for execution.

### Example usage
`/specprep.tasks @specs/002-feature/plan.md @specs/002-feature/research.md`

### Expected output
`/speckit.tasks [optimized task text]