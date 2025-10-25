# Skola Plugin

Tutorial and educational content toolkit for Claude Code.

## Components

### Agents

- **tutorial-engineer**: Creates step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences with hands-on examples.

### Commands

- **/teach-code**: Educational code explanation that breaks down complex logic into understandable concepts with examples, visual diagrams, and step-by-step narratives for learners at all levels.

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the skola plugin
/plugin install skola@arkhe-claude-plugins
```

## Usage

After installation, the agent and command will be available:

```bash
# Use the tutorial-engineer agent
/agents
# Select: tutorial-engineer

# Use educational code explanation
/teach-code src/auth/middleware.ts
/teach-code the authentication flow in this codebase
```

## Use Cases

- Creating step-by-step tutorials from existing code
- Building progressive learning experiences
- Explaining complex algorithms and patterns
- Generating hands-on coding exercises
- Creating educational content for onboarding
- Teaching programming concepts with real examples

## Recommended Companion Plugins

For comprehensive educational content creation, consider installing:
- **doc** plugin - For generating documentation and diagrams (`docs-architect`, `mermaid-expert`)
- **ai** plugin - For AI engineering tutorials (`ai-engineer`, `prompt-engineer`, `context-manager`)

## Version

1.0.0
