# Architect Skill — Troubleshooting

Common issues and fixes for the System Architect skill.

## Module Not Found

**Symptom:** "Could not find module 'payments'" or empty analysis.

**Cause:** Module name doesn't match directory structure.

**Fix:**
1. Check actual directory names: the skill searches for `**/name/**/*`
2. Use the exact directory name, not a label: `module payment` not `module payment-processing`
3. If modules are nested, use the full path: `module services/payment`

## Wrong Tech Stack Detected

**Symptom:** Skill analyzes Java patterns but project is TypeScript.

**Cause:** Multiple build files present (e.g., `package.json` for tooling alongside `build.gradle.kts`).

**Fix:**
1. Create `.arkhe/roadmap/architecture.md` specifying the primary tech stack:
   ```markdown
   ## Tech Stack
   - Primary: TypeScript (Node.js)
   - Framework: Next.js 14 (App Router)
   - Database: PostgreSQL with Prisma
   ```

## Boundary Analysis Too Shallow

**Symptom:** Only finds direct imports, misses indirect coupling.

**Cause:** The skill checks import statements but not runtime coupling.

**Fix:**
1. Ask for specific coupling types: `boundaries` checks imports; for event-based coupling, ask explicitly
2. For database-level coupling (shared tables), use `data-model` mode instead
3. Describe known coupling in `.arkhe/roadmap/architecture.md`

## Pattern Check Returns No Violations

**Symptom:** Says "all patterns conform" but you know there are violations.

**Cause:** Skill only checks patterns it can detect from file structure and imports.

**Fix:**
1. Describe expected patterns in `.arkhe/roadmap/architecture.md`:
   ```markdown
   ## Patterns
   - All entities must extend BaseEntity
   - Services must not import from controllers
   - DTOs must live in dto/ subdirectory
   ```
2. The skill will check these explicit rules in addition to auto-detected patterns

## ADRs Not Found for Decision Tracing

**Symptom:** Decision mode says "No ADRs found."

**Cause:** ADRs are in a non-standard location.

**Fix:**
1. Standard locations: `docs/adr/`, `docs/decisions/`, `plan/decisions/`
2. Or specify in `.arkhe/roadmap/documents.md`:
   ```markdown
   ## Architecture Decisions
   - `design-docs/decisions/*.md` — All ADRs
   ```

## Frontend Analysis Doesn't Match Framework

**Symptom:** Skill suggests React patterns for a Vue project.

**Cause:** Framework not correctly detected or multiple frameworks present.

**Fix:**
1. Ensure the framework config file is at the project root (`nuxt.config.ts`, `svelte.config.js`, etc.)
2. Specify framework in `.arkhe/roadmap/architecture.md`

## Review Mode Takes Too Long

**Symptom:** `review <module>` seems to read excessive files.

**Cause:** Module has many files and the skill reads all of them.

**Fix:**
1. Use `module <name>` for a lighter analysis (skips quality checks)
2. For focused reviews, ask about specific aspects: `api payments` or `boundaries`
