# Changelog

All notable changes to the Arkhe Claude Plugins project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Design Intent Plugin
- New plugin: Design Intent for Spec-Driven Development
- 7 commands: `/setup`, `/design`, `/feature`, `/plan`, `/implement`, `/document-design-intent`, `/diary`
- `design-intent-specialist` skill with auto-invocation for Figma URLs, screenshots, and UI implementation requests
- Templates: constitution (7 articles), team-roles, project-vision, feature-spec, implementation-plan, design-intent-template, session-template
- README with installation guide and optional MCP setup (Figma, Fluent UI)
- Registered in marketplace.json

### Changed

#### Documentation
- Added GitHub shorthand installation method as recommended option (`/plugin marketplace add joaquimscosta/arkhe-claude-plugins`)
- Updated README.md Quick Start with dual installation options (GitHub direct vs local clone)
- Updated INSTALLATION.md with streamlined prerequisites and installation options
- Fixed README.md markdown formatting issues (code blocks, escaped HTML, broken links)
- Added thematic emojis to plugin table for better visual identification
- Removed component emojis from Key Components column for cleaner presentation
- Fixed placeholder GitHub URLs (replaced `yourusername` with actual repository owner)
- Fixed broken documentation links that pointed to Google search URLs

#### Google Stitch Plugin
- Refactored `authoring-stitch-prompts` skill to single-file format with `---` separators (replacing directory-based multi-file structure)
- Implemented layout prompt generation with foundation/wireframe approach for multi-component pages
- Added 6-prompt Stitch limit enforcement with automatic file splitting into part files
- Introduced HTML comment labels (`<!-- Layout: -->` and `<!-- Component: -->`) for file navigation
- Updated WORKFLOW.md with detection logic (Section 1.7) and generation steps (Section 3.5)
- Rewrote SKILL.md File Output section for single-file composition and versioning
- Updated REFERENCE.md Section 4 with single-file format documentation
- Enhanced EXAMPLES.md with Examples 14-16 demonstrating new format (including split file scenario)
- Created layout-prompt-template.md with structure guidelines and validation checklist
- Updated evaluation.json test cases to verify single-file generation behavior

## [1.0.0] - 2025-11-12

Initial release of the Arkhe Claude Plugins marketplace with 10 specialized plugins providing agents, commands, and skills for documentation, AI engineering, code review, UI/UX design, git workflows, Google Stitch prompting, Spec-Driven Development, and language-specific programming.

### Added

#### Core Plugin
- `/workflow` command for product manager orchestration with spec-kit integration
- `/discuss` command for technical discussions with focused clarifying questions
- `/double-check` command for comprehensive verification from multiple angles
- `/ultrathink` command for multi-agent orchestration with extended thinking

#### Git Plugin
- `/commit` command with context-aware commit generation and smart pre-commit checks
- `/create-branch` command with optimized short naming and auto-incrementing
- `/create-pr` command with intelligent PR descriptions and existing PR detection
- `/changelog` command with semantic versioning and conventional commit support
- `creating-commit` skill for standardized commit workflow
- `creating-branch` skill for feature branch management
- `generating-changelog` skill with auto-invoke on CHANGELOG.md edits
- `creating-pr` skill for GitHub pull request automation

#### AI Plugin
- `/improve-agent` command for systematic agent improvement through performance analysis
- `/multi-agent-optimize` command for AI-powered multi-agent coordination
- `/lyra` command for transforming vague inputs into optimized AI prompts
- `ai-engineer` agent for building production-ready LLM applications
- `prompt-engineer` agent for advanced prompting techniques and optimization
- `context-manager` agent for dynamic context management and intelligent memory systems

#### Doc Plugin
- `/doc-generate` command for comprehensive technical documentation from codebases
- `/code-explain` command for explaining complex code through narratives and diagrams
- `/diagram` command for creating and editing Mermaid diagrams
- `docs-architect` agent for architecture guides and technical deep-dives
- `mermaid` skill with auto-invoke for flowcharts, sequence diagrams, ERDs, state machines (#4)

#### Review Plugin
- `/code` command for pragmatic code reviews balancing excellence and velocity
- `/security` command for comprehensive security reviews
- `/design` command for front-end design reviews with accessibility compliance
- `/codebase` command for comprehensive codebase analysis and documentation
- `pragmatic-code-review` agent for substantive code quality reviews
- `design-review` agent for UI/UX design validation and testing

#### UI Plugin
- `ui-ux-designer` agent for interface designs, wireframes, and design systems
- Design tokens, component libraries, and inclusive design specialization

#### SpecPrep Plugin
- `/specify` command for refining and validating feature specifications (#7)
- `/plan` command for creating and validating implementation plans (#7)
- Mode system (quick/strict) for configurable validation levels
- Draft mode for iterative specification refinement
- Automatic command chaining (specify→plan workflow)

#### Google Stitch Plugin
- `/prompt` command for generating Stitch-ready prompts from briefs or spec files
- `authoring-stitch-prompts` skill for converting descriptions into optimized Stitch prompts
- `stitch-session-manager` skill for tracking multi-screen design sessions with style continuity
- Prompt versioning and storage in `.google-stitch/prompts/`
- Session logging with metadata and style guide preservation

#### Documentation
- Automated Claude Code documentation sync system with update script
- Comprehensive skill development best practices guide (SKILL_DEVELOPMENT_BEST_PRACTICES.md)
- Progressive disclosure architecture documentation (SKILL.md → WORKFLOW.md → EXAMPLES.md → TROUBLESHOOTING.md)
- Anthropic skills repository references and official examples
- Plugin marketplace structure with `.claude-plugin/` metadata
- Installation guide (INSTALLATION.md) with local and published marketplace setup

### Changed

#### Git Plugin
- Migrated shell scripts to skills-based architecture for better maintainability
- Enhanced skill trigger words for improved discoverability
- Enforced no-footer policy removing AI attribution from commit messages
- Removed "Generated with Claude Code" footers from commits and PRs
- Updated changelog skill to Nos Ilha coding style with cleaner formatting

#### SpecPrep Plugin
- Implemented automatic command chaining replacing manual `/tasks` invocation
- Enhanced draft mode with semantic feature name generation
- Improved mode validation with quick and strict options

#### Google Stitch Plugin
- Renamed `stitch-prompt` skill to `authoring-stitch-prompts` following gerund form best practice
- Updated YAML frontmatter and main heading for consistency
- Renamed template file to `authoring-stitch-prompts-template.md`
- Updated 30+ cross-references across skill files, commands, and documentation

#### Documentation
- Updated all skill references to gerund-based naming convention (#4)
- Simplified command documentation with clearer examples
- Enhanced README with structured plugin overview and learning paths
- Consolidated developer tools documentation into main guides
- Fixed markdown code block rendering in skill documentation
- Removed temporary skill review files from repository

#### Plugin Architecture
- Consolidated agents and commands for better organization
- Split UI/UX capabilities into separate dedicated plugin
- Reorganized commands with namespace prefixes for clarity
- Implemented comprehensive marketplace catalog structure

### Removed

#### SpecPrep Plugin
- `/tasks` command (replaced by automatic command chaining in two-command architecture)

#### Documentation
- DEVELOPER_TOOLS.md (content consolidated into PLUGINS.md, COMMANDS.md, and other guides)
- Temporary skill review markdown files from evaluation phase

### Fixed

#### Documentation
- Markdown code block rendering issues in skill documentation files
- Broken cross-references after plugin reorganization

### Security

No security vulnerabilities addressed in this release. All skills use standard library only with no external dependencies beyond Python 3.8+ runtime.

### Breaking Changes

#### 1. SpecPrep Tasks Command Removal (2025-10-31)

**Commit**: d57034d

The `/specprep:tasks` command has been removed in favor of automatic command chaining.

**Migration**:
```bash
# Old workflow (no longer supported)
/specprep:specify <feature>
/specprep:tasks

# New workflow (automatic chaining)
/specprep:specify <feature>
# Tasks are now automatically generated after specification
```

## Development Statistics

- **Development Period**: October 20 - November 12, 2025 (23 days)
- **Total Commits**: 34 commits
- **Pull Requests**: 12 merged PRs
- **Plugins**: 8 specialized plugins
- **Skills**: 10+ auto-invoked and command-driven skills
- **Commands**: 15+ slash commands
- **Agents**: 8 specialized AI subagents

## Project Links

- **Repository**: https://github.com/joaquimscosta/arkhe-claude-plugins
- **Documentation**: See README.md and docs/ directory
- **Installation**: See INSTALLATION.md

[Unreleased]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/releases/tag/v1.0.0
