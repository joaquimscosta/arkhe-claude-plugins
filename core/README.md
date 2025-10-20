# Core Plugin

Essential documentation and quality control utilities for Claude Code.

## Components

### Agents

- **docs-architect**: Creates comprehensive technical documentation from existing codebases. Analyzes architecture, design patterns, and implementation details to produce long-form technical manuals and ebooks.

### Commands

- **/discuss**: Facilitates thorough technical discussions about code, architecture, and implementation decisions. Helps you think through problems by asking focused questions.

- **/double-check**: Quality validation command that verifies your work from multiple angles. Ensures completeness and correctness before finalizing.

- **/ultrathink**: Deep thinking command for complex problem-solving. Takes time to analyze problems thoroughly from different perspectives.

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
```

## Version

1.0.0
