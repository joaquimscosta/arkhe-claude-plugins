# Refresh Skill — Troubleshooting

## "No git history found"

**Symptom**: Script outputs `"git_available": false` or all staleness values are missing.

**Cause**: The project is not a git repository, or git is not installed.

**Fix**: Initialize git (`git init && git add . && git commit -m "initial"`) or run in a git-managed project. Without git, the refresh skill can still scaffold files but cannot detect drift.

## "Context files not detected" / Wrong path

**Symptom**: Script reports files don't exist, but you created them at a different path.

**Cause**: The context directory defaults to `.arkhe/roadmap/`. If your files are elsewhere, the script won't find them.

**Fix**: Set the custom path in `.arkhe.yaml`:
```yaml
roadmap:
  context_dir: path/to/your/context
```

## "Generated content is too generic"

**Symptom**: Context files have placeholder text instead of real project details.

**Cause**: The project lacks a README.md or CLAUDE.md with project information.

**Fix**: Create a README.md with project purpose, tech stack, and target audience before running `/roadmap:refresh init`. The more information in README.md and CLAUDE.md, the richer the generated context.

## "No modules discovered"

**Symptom**: Module inventory is empty in architecture.md.

**Cause**: The project doesn't use standard directory patterns (`apps/*`, `src/*`, `packages/*`, etc.).

**Fix**: The skill will still generate architecture.md from build files and other sources. For non-standard layouts, manually add module information to the generated architecture.md after scaffolding.

## "New modules listed but they're not real modules"

**Symptom**: Drift check reports "new modules" that are utility directories, not actual modules.

**Cause**: The detection script uses directory globs that may match non-module directories.

**Fix**: After refreshing architecture.md, review and remove irrelevant entries. The hybrid format is designed to be edited — the header notes "Edit freely."

## "Permission denied running script"

**Symptom**: `bash: permission denied` when running the detection script.

**Fix**: Make scripts executable:
```bash
chmod +x plugins/roadmap/skills/refresh/scripts/*.py
```
