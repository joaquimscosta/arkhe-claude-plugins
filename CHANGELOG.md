# Changelog

All notable changes to the Arkhe Claude Plugins project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Doc Plugin

- `managing-adrs` skill for Architecture Decision Records
  - Auto-numbering and template detection (minimal or MADR 4.0)
  - Python scripts using `uv` for `adr_create`, `adr_index`, `adr_supersede`
  - Supersession workflow for replacing existing ADRs
  - Auto-invokes on "ADR", "architecture decision" keywords

#### Google Stitch Plugin

- Design context discovery from `design-intent/memory/constitution.md`
  - Injects project type cues (Enterprise, Consumer, Internal, Marketing)
  - Injects design system names (Fluent UI, Material UI, Tailwind, etc.)
  - Falls back to `package.json` scanning if no design-intent
- Interactive `/prompt` command with 3-step preference gathering
  - Component selection (which UI components to include)
  - Style preferences (Enterprise, Consumer, Minimal, Playful, Custom)
  - Structure decisions (Combined, Split, Auto-detect)
  - "Quick generation" option to skip questions
  - Auto-skips questions for revision requests
- Structured input parsing for skill invocation
- 7 new examples (17-23) demonstrating design-aware and interactive flows

#### Plugin Dev Plugin

- `skill-validator` skill for validating skills against best practices
  - Frontmatter validation (name length, description quality, field values)
  - Structure validation (file organization, supporting docs)
  - Content standards (imperative form, time-sensitive info, progressive disclosure)
  - Reference integrity checks (broken links, anchor validation)
  - Security checks (shebang, file permissions, no third-party packages)
  - Confidence-based filtering with severity levels

### Changed

#### Project Structure

- **BREAKING**: Moved all 11 plugins from root to `plugins/` subdirectory
  - Follows `claude-plugins-official` structure pattern
  - Updated marketplace.json source paths from `./plugin-name` to `./plugins/plugin-name`
  - Updated all documentation references (CLAUDE.md, README.md, CONTRIBUTING.md, docs/README.md)
  - Git history preserved through renames

#### Design Intent Plugin

- Removed redundant `/design` command (skill auto-invokes on visual references)
- Enhanced `/implement` command with:
  - `argument-hint: [feature-name]` for better discoverability
  - Quality Review phase with 3 parallel `design-reviewer` agents
  - Proper skill reference pattern following Claude Code best practices
- Updated README with decision tree diagram for command selection
- Added "When to Use" column to commands table
- Fixed markdown lint warnings throughout documentation

## [1.3.0] - 2026-01-08

### Added

#### Spring Boot Plugin
- `spring-boot-upgrade-verifier` agent for verifying Spring Boot 4 upgrade readiness
  - Phase 1: Discovery - detect project version and relevant verifiers
  - Phase 2: Parallel verification - check dependencies, security, testing, observability
  - Phase 3: Migration report - unified checklist with severity levels
- `/verify-upgrade` command for Spring Boot project upgrade verification
- Parallel multi-skill review in `spring-boot-reviewer` agent
  - Phase 1: Discovery (haiku) - detect relevant skills from scope
  - Phase 2: Parallel review (sonnet) - launch skill-specific reviewers
  - Phase 3: Report & fix - consolidated findings with interactive fixes

#### Core Plugin
- Smart mode routing in `/workflow` command: auto-detect IMPLEMENT vs PLAN mode
- Plan persistence pipeline: explore → architect → save plan
- Quick validation (sonnet sanity check) always runs in workflow
- Deep validation (opus review) available with `--validate` flag
- Confidence-based issue filtering in `/double-check` command (≥75 threshold)
- Auto-scope detection via git commands before verification in `/double-check`
- `/feature` command replacing `/ultrathink` with 7-phase multi-agent workflow
- `code-explorer` agent for fast codebase exploration
- `code-architect` agent for architecture design
- `code-reviewer` agent for code quality reviews

#### SpecPrep Plugin
- Multi-file input support in `/specprep:plan`: accept spec, research files alongside plan drafts
- Dual operating modes in `/specprep:plan`: synthesis (generate from spec+research) and optimization (refine existing plan)
- Auto-detection of spec and plan draft files from directory
- Citation format for spec requirements and research sources
- Traceability matrix in strict mode

### Changed

#### Google Stitch Plugin
- Changed prompts storage from `.google-stitch/` to `design-intent/google-stitch/` for better discoverability
- Removed deprecated `stitch-session-manager` skill

#### Core Plugin
- Replaced `/ultrathink` command with `/feature` command
- Enhanced `/workflow` command to be spec-kit aware

#### Spring Boot Plugin
- Both reviewer agents now use TodoWrite for progress tracking
- 80+ confidence threshold for findings

### Fixed

#### Spring Boot Plugin
- Added missing `domain-driven-design` TROUBLESHOOTING.md (was referenced but didn't exist)
  - Common patterns: anemic domain model, god aggregate, cross-aggregate transactions
  - Entity vs value object confusion, missing bounded contexts
  - Repository responsibilities, domain layer infrastructure pollution

### Removed

#### SpecPrep Plugin
- `/specprep:plan` command (use `/speckit.plan` directly after creating specs)

### Breaking Changes

#### SpecPrep Plugin (2026-01-08)
**Commit**: 85ebcd6

The `/specprep:plan` command has been removed to simplify the plugin.

**Migration**:
```bash
# Old workflow (no longer supported)
/specprep:specify <feature>
/specprep:plan

# New workflow
/specprep:specify <feature>
/speckit.plan  # Use spec-kit directly
```

## [1.2.0] - 2025-12-22

### Added

#### Core Plugin
- `workflow-orchestration` skill for structured thinking and multi-agent parallel execution
  - Quick decision matrix for choosing between `/workflow`, `/think`, `/ultrathink`, and `deep-think-partner`
  - Keyword and context triggers for automatic orchestration detection
  - Model tier strategy (haiku for gating, sonnet for implementation, opus for deep analysis)
  - Supporting docs: WORKFLOW.md, EXAMPLES.md, TROUBLESHOOTING.md

#### Design Intent Plugin
- 3 specialized agents for UI/visual development:
  - `ui-explorer`: Fast codebase exploration for existing UI patterns, components, and design tokens
  - `ui-architect`: Design UI component architecture with props, styling, and responsive strategies
  - `design-reviewer`: Quality review for visual consistency, accessibility, and pattern adherence
- `/design-intent` command with 7-phase UI development workflow:
  1. Discovery - Understand UI requirements
  2. Exploration - Analyze existing patterns (optional with `--quick`)
  3. Clarifying Questions - Resolve visual ambiguities
  4. Architecture Design - Multi-approach planning (optional with `--quick`)
  5. Implementation - Build with design-intent-specialist skill
  6. Quality Review - Visual consistency and accessibility checks
  7. Patterns - Extract and document reusable design patterns

### Changed

#### Core Plugin
- Refactored `/workflow` command to use new `workflow-orchestration` skill (reduced from ~800+ lines to skill-based architecture)
- Updated `deep-think-partner` agent description

#### Design Intent Plugin
- Enhanced `design-intent-specialist` skill with improved visual reference handling
- Updated README with comprehensive plugin documentation

#### Documentation
- Updated core/README.md with new skill documentation
- Enhanced design-intent/README.md with full command and agent reference

## [1.1.0] - 2025-12-20

### Added

#### Spring Boot Plugin
- New plugin: Domain-Driven Design patterns with Spring Boot 4 implementation
- 7 specialized skills for DDD with Spring Boot:
  - `domain-driven-design`: Strategic and tactical DDD guidance (subdomains, bounded contexts, aggregates, domain services)
  - `spring-boot-data-ddd`: JPA/JDBC implementation patterns (strongly-typed IDs, value objects, repositories)
  - `spring-boot-web-api`: REST API patterns (validation, ProblemDetail RFC 9457, WebFlux)
  - `spring-boot-modulith`: Modular monolith with Spring Modulith 2.0 (module structure, event publishing)
  - `spring-boot-security`: Spring Security 7 Lambda DSL, JWT/OAuth2, method security
  - `spring-boot-observability`: Actuator, Micrometer, OpenTelemetry distributed tracing
  - `spring-boot-testing`: Slice tests, Testcontainers, @MockitoBean, Scenario API
- Tech stack: Spring Boot 4, Spring Framework 7, Java 21+, Jakarta EE 11, JSpecify
- Migration checklist for Spring Security 7 breaking changes
- Registered in marketplace.json as 11th plugin

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

### Fixed

- README.md banner image display issue

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
- Prompt versioning and storage in `design-intent/google-stitch/prompts/`
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

[Unreleased]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/joaquimscosta/arkhe-claude-plugins/releases/tag/v1.0.0
