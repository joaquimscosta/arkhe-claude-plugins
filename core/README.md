# Core Plugin

Quality control and workflow orchestration utilities for Claude Code.

## Components

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

After installation, the commands will be available:

```bash
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
