# Core Plugin

Quality control and workflow orchestration utilities for Claude Code.

## Components

### Agents

- **deep-think-partner**: Elite reasoning partner for complex logical problems, multi-step reasoning challenges, and strategic decisions. Use when you need collaborative deep thinking for architectural decisions, complex data transformations, or validating reasoning chains. Engages as a peer thinking partner rather than a subordinate.

### Commands

- **/discuss**: Facilitates thorough technical discussions about code, architecture, and implementation decisions. Helps you think through problems by asking focused questions.

- **/double-check**: Quality validation command that verifies your work from multiple angles. Ensures completeness and correctness before finalizing.

- **/ultrathink**: Deep thinking command for complex problem-solving. Takes time to analyze problems thoroughly from different perspectives.

- **/workflow**: Product Manager-led orchestration agent that coordinates specialist agents across any domain. Supports enhanced thinking modes (--seq, --ultrathink, --thinkhard), MCP server integration (--exa, --c7), spec kit workflows, and natural language requests. Tracks work via AGENT_TODOS.md.

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
/ultrathink how to optimize the database queries

# Use workflow orchestration
/workflow implement OAuth2 authentication --seq --c7
/workflow refactor-payment-system --thinkhard

# Use debugging
/debug why is my API returning 500 errors
/debug TypeError: Cannot read property 'map' of undefined

# Use deep thinking
/think how should I structure the authentication module
/think  # Analyzes current context
```

## Version

1.0.0
