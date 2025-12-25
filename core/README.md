# Core Plugin

Quality control and workflow orchestration utilities for Claude Code.

## Components

### Skills

- **workflow-orchestration** (auto-invoke): Coordinates structured thinking and multi-agent parallel execution for complex tasks. Auto-triggered when tackling multi-step projects, planning parallel work, breaking down complex problems, or when user mentions "workflow", "orchestration", "multi-step", "coordinate", "parallel execution", "structured thinking". Recommends appropriate tools (`/workflow`, `/feature`, `/think`) based on context.

### Agents

- **deep-think-partner**: Elite reasoning partner for complex logical problems, multi-step reasoning challenges, and strategic decisions. Use when you need collaborative deep thinking for architectural decisions, complex data transformations, or validating reasoning chains. Engages as a peer thinking partner rather than a subordinate.

- **code-explorer**: Specialized agent for exploring and understanding codebases. Traces through implementations, maps architecture, identifies patterns, and returns lists of key files to read.

- **code-architect**: Software architecture agent for designing implementation approaches. Evaluates trade-offs between minimal changes, clean architecture, and pragmatic balance.

- **code-reviewer**: Expert code reviewer for bugs, logic errors, security vulnerabilities, and project convention adherence. Uses confidence-based filtering to report only high-priority issues.

### Commands

- **/discuss**: Facilitates thorough technical discussions about code, architecture, and implementation decisions. Helps you think through problems by asking focused questions.

- **/double-check**: Quality validation command that verifies your work from multiple angles. Ensures completeness and correctness before finalizing.

- **/feature**: Guided feature development with codebase exploration, architecture design, and quality review. Uses code-explorer, code-architect, and code-reviewer agents through a 7-phase workflow with user checkpoints.

- **/workflow**: Multi-agent orchestration with parallel execution and spec-kit awareness. Detects spec-kit artifacts, uses existing plans when available, and coordinates specialist agents. Supports `--validate` flag for constitution compliance verification.

- **/debug**: Systematic debugging assistant that walks through structured troubleshooting steps. Analyzes issues with a framework covering problem definition, environment assessment, error investigation, hypothesis formation, and testing strategy.

- **/think**: Invokes the deep-think-partner agent for collaborative reasoning on complex problems. Can be called with a specific problem or to analyze the current conversation context.

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
/feature add user authentication

# Use workflow orchestration
/workflow implement OAuth2 authentication
/workflow implement Phase 1 from @specs/auth/ --validate

# Use debugging
/debug why is my API returning 500 errors
/debug TypeError: Cannot read property 'map' of undefined

# Use deep thinking
/think how should I structure the authentication module
/think  # Analyzes current context
```

## Version

1.0.0
