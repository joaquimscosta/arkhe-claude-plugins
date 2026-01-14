# Core Plugin

Quality control and workflow orchestration utilities for Claude Code.

## Components

### Skills

- **sdlc-develop** (command-invoke): 6-phase SDLC pipeline for feature development with progressive disclosure. Orchestrates Discovery, Requirements, Architecture, Workstreams, Implementation, and Summary phases. Supports plan persistence to `arkhe/specs/`, resume mode, and autonomous execution. Invoked via `/develop` command.

- **workflow-orchestration** (auto-invoke): Coordinates structured thinking and multi-agent parallel execution for complex tasks. Auto-triggered when tackling multi-step projects, planning parallel work, breaking down complex problems, or when user mentions "workflow", "orchestration", "multi-step", "coordinate", "parallel execution", "structured thinking". Recommends appropriate tools (`/develop`, `/think`) based on context.

- **deep-research** (auto-invoke + command-invoke): Deep technical research using EXA tools with intelligent two-tier caching. Auto-triggered when user asks to research a topic, investigate best practices, look up information, find patterns, or explore architectures. Also invoked via `/research` command. Features cross-project cache reuse and promotion to version-controlled project docs.

### Agents

- **deep-think-partner**: Elite reasoning partner for complex logical problems, multi-step reasoning challenges, and strategic decisions. Triggers on "should I", "what are the tradeoffs", "help me decide", or "think through". Provides structured output with problem restatement, multi-perspective analysis, and ranked recommendations. Uses Opus model with sequential-thinking MCP for maximum reasoning depth.

- **deep-researcher**: Deep research specialist using EXA tools for comprehensive topic investigation. Manages a two-tier cache system (user-level for cross-project reuse, project-level for version-controlled team knowledge). Conducts research on patterns, architectures, technologies, and best practices.

- **code-explorer**: Specialized agent for exploring and understanding codebases. Traces through implementations, maps architecture, identifies patterns, and returns lists of key files to read.

- **code-architect**: Software architecture agent for designing implementation approaches. Evaluates trade-offs between minimal changes, clean architecture, and pragmatic balance.

- **code-reviewer**: Expert code reviewer for bugs, logic errors, security vulnerabilities, and project convention adherence. Uses confidence-based filtering to report only high-priority issues.

### Commands

- **/discuss**: Facilitates thorough technical discussions about code, architecture, and implementation decisions. Helps you think through problems by asking focused questions.

- **/double-check**: Quality validation command that verifies your work from multiple angles. Ensures completeness and correctness before finalizing.

- **/develop**: Unified SDLC command with 6-phase pipeline (Discovery, Requirements, Architecture, Workstreams, Implementation, Summary). Supports plan persistence, resume mode (`@path/to/plan.md`), and configurable interaction (`--auto` for autonomous). Includes mandatory Phase 0 existing system analysis. Flags: `--plan-only`, `--validate`, `--phase=N`, `--auto`.

- **/debug**: Systematic debugging assistant that walks through structured troubleshooting steps. Analyzes issues with a framework covering problem definition, environment assessment, error investigation, hypothesis formation, and testing strategy.

- **/think**: Invokes the deep-think-partner agent for collaborative reasoning on complex problems. Can be called with a specific problem or to analyze the current conversation context.

- **/research**: Deep technical research with intelligent caching. Supports: `/research <topic>` (research), `/research promote <slug>` (promote to project docs), `/research refresh <slug>` (force refresh), `/research list` (show inventory). Uses EXA tools for web search and code context retrieval.

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the core plugin
/plugin install core@arkhe-claude-plugins
```

## Usage

After installation, the agents and commands will be available:

```bash
# Use quality control commands
/discuss implementing a new authentication system
/double-check

# Use the unified develop command
/develop add user authentication              # Full 6-phase pipeline
/develop add logout button --auto             # Autonomous mode
/develop create plan for dashboard --plan-only # Plan only, don't implement
/develop @arkhe/specs/01-auth/                # Resume existing spec
/develop refactor payment service --validate  # With deep validation

# Use debugging
/debug why is my API returning 500 errors
/debug TypeError: Cannot read property 'map' of undefined

# Use deep thinking
/think how should I structure the authentication module
/think  # Analyzes current context

# Use deep research
/research domain-driven design            # Research a topic
/research promote domain-driven-design    # Promote to project docs
/research refresh domain-driven-design    # Force refresh
/research list                            # Show all cached research
```

## Version

2.0.0
