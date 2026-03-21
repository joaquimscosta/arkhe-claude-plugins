# Claude Setup Workflow

Detailed per-category setup flows. Each category follows the pattern: detect existing state, ask user preferences via `AskUserQuestion`, show confirmation, then execute.

---

## Category 1: Global CLAUDE.md

**Detect**: Check `detection.global.claude_md.exists`

**If exists**: Read the file, summarize contents, then `AskUserQuestion`:
- Merge new rules into existing file
- Replace entirely with recommended template
- Skip this category

**If missing**: `AskUserQuestion` (multiSelect: true) — which security rules to include:
- NEVER publish sensitive data (passwords, API keys, tokens to git/npm/docker)
- NEVER commit .env files (always verify .env in .gitignore)
- NEVER read or expose secrets (.env, credentials, SSH keys, service account keys)

Then ask account configuration (use "Other" for text input):
- GitHub username
- Git protocol: HTTPS (recommended) or SSH
- Git identity: name and email
- Docker Hub username (optional)

**Execute**: Write `~/.claude/CLAUDE.md` with selected rules and account config. Follow the template from Guide Section 1.

---

## Category 2: Project Scaffolding

**Detect**: Check `detection.project.*` fields

**AskUserQuestion** (multiSelect: true) — which items to create (skip items that already exist, show them as "already configured"):
- `.env.example` — template with placeholder values
- `.gitignore` — with .env, node_modules/, dist/, .env.local, .env.production
- `CLAUDE.md` — project overview template
- `.claude/skills/` directory
- `.claude/agents/` directory
- `.claude/commands/` directory
- `src/` directory
- `tests/` directory
- `docs/` directory
- `scripts/` directory

**Execute**: Create selected directories with `mkdir -p` via Bash. Create selected files with Write tool using appropriate templates.

### Templates

**.env.example**:
```
# Application Configuration
# Copy to .env and fill in real values
# NEVER commit .env to git

# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# API_KEY=your-api-key-here
# SECRET_KEY=your-secret-key-here
```

**.gitignore** (append to existing or create):
```
# Environment
.env
.env.local
.env.production
.env.*

# Dependencies
node_modules/
vendor/

# Build
dist/
build/
target/
*.pyc
__pycache__/

# IDE
.idea/
.vscode/
*.swp
```

**CLAUDE.md** (project template):
```markdown
# CLAUDE.md

## Project Overview

[Brief description of the project]

## Development Commands

```bash
# Install dependencies
# Run tests
# Build
# Lint
```

## Architecture

[Key architecture decisions and patterns]

## Conventions

[Coding conventions and style guidelines]
```

---

## Category 3: MCP Servers

**Detect**: Run `claude mcp list` via Bash to get currently installed servers.

**Cross-reference** against the guide's recommended servers (Section 3). Group by category:

**AskUserQuestion** — MCP server scope:
- Global (available in all projects, `-s user`)
- Project-only (this project only, `-s project`)

**AskUserQuestion** (multiSelect: true) per server group — skip servers already installed:

**Core Development**:
- Context7 — Live docs for any library
- Filesystem — Advanced file operations
- Sequential Thinking — Structured problem-solving

**Databases** (ask only if relevant to project):
- MongoDB — Atlas/Community
- PostgreSQL — Query Postgres naturally
- DBHub — Universal (MySQL, SQLite, etc.)

**Documents & RAG**:
- Docling — PDF/DOCX parsing
- Qdrant — Vector search
- Chroma — Embeddings, vector DB

**Browser & Testing**:
- Browser MCP — Use your logged-in Chrome

**Cloud & DevOps**:
- AWS — S3, Lambda, CloudWatch
- Docker — Container management
- Kubernetes — Cluster operations

**Execute**: For each selected server, run the corresponding `claude mcp add` command from the guide with the chosen scope flag.

---

## Category 4: Hooks

**Detect**: Check `detection.global.settings_json.has_hooks` and `detection.global.hooks_dir`

**AskUserQuestion** (multiSelect: true) — which hooks to configure:
- **Block secrets hook** — PreToolUse hook that blocks Read/Edit/Write access to .env, secrets.json, id_rsa, and similar files
- **Setup hook** — Runs `npm install && npm run prepare` on session init
- **Custom hook** — Describe your hook (text input)

### Block Secrets Hook Setup

1. Create `~/.claude/hooks/` directory if missing
2. Write `~/.claude/hooks/block-secrets.py` with the block-secrets script from Guide Section 7
3. Read existing `~/.claude/settings.json` (or start with `{}`)
4. Deep-merge the PreToolUse hook configuration:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Read|Edit|Write",
           "hooks": [{
             "type": "command",
             "command": "python3 ~/.claude/hooks/block-secrets.py"
           }]
         }
       ]
     }
   }
   ```
5. Write merged settings back

### Setup Hook

Merge into settings.json:
```json
{
  "hooks": {
    "Setup": [{
      "type": "command",
      "command": "npm install && npm run prepare"
    }]
  }
}
```

---

## Category 5: Custom Agents

**Detect**: Check `detection.global.agents_dir` and list existing agent files.

**AskUserQuestion** (multiSelect: true) — create starter agents:
- **Code reviewer** — Read-only agent (Read, Grep, Glob) using Sonnet for code review
- **Security auditor** — Read-only agent (Read, Grep, Glob) using Opus for security analysis
- **Documentation writer** — Read-write agent (Read, Write, Grep, Glob) using Sonnet for docs

**AskUserQuestion** — agent scope:
- Personal (`~/.claude/agents/`) — available in all projects
- Project (`.claude/agents/`) — this project only

**Execute**: Create agent `.md` files with appropriate frontmatter and system prompts.

### Agent Templates

**code-reviewer.md**:
```markdown
---
name: code-reviewer
description: Reviews code for security, performance, and best practices. Use for code review tasks.
tools: Read, Grep, Glob
model: sonnet
---

You are a senior code reviewer. When reviewing code:
1. Check for security vulnerabilities (OWASP Top 10)
2. Look for performance issues (N+1 queries, memory leaks)
3. Verify error handling (edge cases, null checks)
4. Assess code maintainability and naming
5. Provide specific line references and concrete fixes

Be critical but constructive. Explain WHY something is a problem.
```

**security-auditor.md**:
```markdown
---
name: security-auditor
description: Audits code for security vulnerabilities, secrets exposure, and compliance issues.
tools: Read, Grep, Glob
model: opus
---

You are a security auditor. When auditing code:
1. Scan for hardcoded secrets, API keys, and credentials
2. Check for injection vulnerabilities (SQL, XSS, command injection)
3. Verify authentication and authorization patterns
4. Review dependency versions for known CVEs
5. Check file permissions and access controls

Report findings with severity ratings (Critical/High/Medium/Low).
```

**documentation-writer.md**:
```markdown
---
name: documentation-writer
description: Writes and updates project documentation, READMEs, and code comments.
tools: Read, Write, Grep, Glob
model: sonnet
---

You are a technical documentation writer. When writing docs:
1. Start with a clear overview of what the component does
2. Include usage examples with realistic code
3. Document parameters, return values, and error cases
4. Add architecture notes for complex components
5. Keep language concise and scannable

Match the existing documentation style in the project.
```

---

## Category 6: Keybindings

**Detect**: Check `detection.global.keybindings_json.exists`

**If exists**: Read the file, show current bindings, offer to add more.

**AskUserQuestion** (multiSelect: true) — recommended keybindings from the guide:
- `ctrl+shift+r` -> `/review` (code review)
- `ctrl+shift+d` -> `/deploy` (deploy)
- `ctrl+shift+t` -> `/test` (run tests)
- `ctrl+shift+c` -> `/commit` (create commit)

**Execute**: Create or merge `~/.claude/keybindings.json`.

---

## Category 7: Settings

**Detect**: Check `detection.global.settings_json`

**AskUserQuestion** — language preference:
- English (default)
- Other (text input for language code, e.g., "ja", "es", "pt")

**AskUserQuestion** — background tasks:
- Enable (recommended)
- Disable

**Execute**: Read existing `~/.claude/settings.json`, merge new settings, write back.

---

## Confirmation Summary

Before executing any changes, show a summary table:

```
## Proposed Changes

| Action | Target | Description |
|--------|--------|-------------|
| CREATE | ~/.claude/CLAUDE.md | Global security rules + account config |
| CREATE | .claude/agents/ | Project agent directory |
| INSTALL | Context7 MCP | claude mcp add context7 (global) |
| SKIP | .gitignore | Already exists |
| ... | ... | ... |

Total: X files to create, Y servers to install, Z settings to update.
```

Use `AskUserQuestion`:
- Proceed with all changes
- Modify selections (go back to category selection)
- Cancel

---

## Post-Setup Summary

After execution, show:

```
## Setup Complete

| Status | Item |
|--------|------|
| [done] | Global CLAUDE.md with 3 security rules |
| [done] | Project scaffolding (5 directories, 3 files) |
| [done] | 3 MCP servers installed (Context7, Filesystem, Sequential Thinking) |
| [done] | Block-secrets hook configured |
| [skip] | Custom agents (skipped by user) |
| [done] | 4 keybindings configured |
| [done] | Language set to English |

## Next Steps
- Run `/context` to check your token usage
- Try `ctrl+shift+r` to trigger code review
- Run `/devtools:code-env-setup` again anytime to add more configuration
```
