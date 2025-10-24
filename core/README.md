# Core Plugin

Essential documentation, quality control, and workflow orchestration utilities for Claude Code.

## Components

### Agents

- **docs-architect**: Creates comprehensive technical documentation from existing codebases. Analyzes architecture, design patterns, and implementation details to produce long-form technical manuals and ebooks.

### Commands

- **/discuss**: Facilitates thorough technical discussions about code, architecture, and implementation decisions. Helps you think through problems by asking focused questions.

- **/double-check**: Quality validation command that verifies your work from multiple angles. Ensures completeness and correctness before finalizing.

- **/ultrathink**: Deep thinking command for complex problem-solving. Takes time to analyze problems thoroughly from different perspectives.

- **/workflow**: Product Manager-led orchestration agent that coordinates specialist agents across any domain. Supports enhanced thinking modes (--seq, --ultrathink, --thinkhard), MCP server integration (--exa, --c7), spec kit workflows, and natural language requests. Tracks work via AGENT_TODOS.md.

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the core plugin
/plugin install core@arkhe-claude-plugins
```

## Usage

After installation, the agent and commands will be available:

```bash
# Use the docs-architect agent
/agents
# Select "docs-architect" from the list

# Use quality control commands
/discuss implementing a new authentication system
/double-check
/ultrathink how to optimize the database queries

# Use workflow orchestration
/workflow implement OAuth2 authentication --seq --c7
/workflow refactor-payment-system --thinkhard
```

## Version

1.0.0
