# PM Skill — Troubleshooting

Common issues and fixes for the Product Manager skill.

## No Project Context Found

**Symptom:** Skill produces generic analysis without project-specific insights.

**Cause:** No `.arkhe.yaml`, `.arkhe/roadmap/`, `CLAUDE.md`, or `README.md` found.

**Fix:**
1. Ensure the project has at least a `README.md` or `CLAUDE.md`
2. For richer context, create `.arkhe/roadmap/project.md` with project overview, personas, and constraints
3. Or create `.arkhe.yaml` with a `roadmap:` section pointing to existing docs

## Personas Not Matching Project Domain

**Symptom:** User stories reference generic personas instead of project-specific ones.

**Cause:** No persona definitions found in context files.

**Fix:** Define personas in `.arkhe/roadmap/project.md`:

```markdown
## Personas

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| Merchant | Shop owner using POS daily | Reliability, offline, simplicity |
| Admin | System administrator | User management, reports |
```

## Stories Too Generic

**Symptom:** Acceptance criteria are vague ("it should work").

**Cause:** Insufficient domain context for the feature area.

**Fix:**
1. Provide more specific feature context in the argument: `stories authentication with OAuth2 and MFA`
2. Add domain constraints to `.arkhe/roadmap/project.md`
3. Point the skill to existing specs: mention the spec path in your prompt

## File Save Fails

**Symptom:** "Permission denied" or directory not found when saving.

**Cause:** Output directory doesn't exist or path is misconfigured.

**Fix:**
1. Check `.arkhe.yaml` `roadmap.output_dir` value
2. Create the directory: `mkdir -p arkhe/roadmap/requirements`
3. If no config, default is `arkhe/roadmap/requirements/`

## Scope Assessment Missing Dependencies

**Symptom:** Scope assessment doesn't mention known blockers.

**Cause:** Blocker information is in docs that weren't discovered.

**Fix:**
1. Create `.arkhe/roadmap/documents.md` listing key docs and their roles
2. Or mention the specific blocking issue in your prompt

## Prioritization Ignores Existing Specs

**Symptom:** Prioritize mode doesn't account for already-planned work.

**Cause:** Spec directory not found during discovery.

**Fix:**
1. Ensure specs are in a standard location: `arkhe/specs/`, `specs/`, or `docs/specs/`
2. Or set `roadmap.context_dir` in `.arkhe.yaml` to point to your planning directory

## Compare Mode Produces One-Sided Analysis

**Symptom:** Comparison clearly favors one option without fair assessment.

**Cause:** One option has more codebase evidence than the other.

**Fix:** Provide additional context for the less-documented option in your prompt:
```
/roadmap:pm compare Redis (in-memory, fast, needs server) vs SQLite (embedded, no server, slower queries)
```
