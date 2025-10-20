# Skola Plugin

Complete AI engineering and tutorial creation toolkit for Claude Code.

## Components

### Agents

- **tutorial-engineer**: Creates step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences with hands-on examples.

- **ai-engineer**: Build production-ready LLM applications, advanced RAG systems, and intelligent agents. Implements vector search, multimodal AI, agent orchestration, and enterprise AI integrations.

- **prompt-engineer**: Expert prompt engineer specializing in advanced prompting techniques, LLM optimization, and AI system design. Masters chain-of-thought, constitutional AI, and production prompt strategies.

- **context-manager**: Elite AI context engineering specialist mastering dynamic context management, vector databases, knowledge graphs, and intelligent memory systems.

- **mermaid-expert**: Create Mermaid diagrams for flowcharts, sequences, ERDs, and architectures. Masters syntax for all diagram types and styling.

### Commands

- **/doc-generate**: Automated documentation generation that extracts information from code, creates clear explanations, and maintains consistency across documentation types.

- **/code-explain**: Explains code in detail, breaking down complex logic into understandable concepts with examples and use cases.

- **/improve-agent**: Systematic improvement of existing agents through performance analysis, prompt engineering, and continuous iteration.

- **/multi-agent-optimize**: Optimizes multi-agent workflows for better collaboration, communication, and task coordination.

## Installation

```bash
# Add the marketplace
/plugin marketplace add ./arkhe-claude-plugins

# Install the skola plugin
/plugin install skola@arkhe-claude-plugins
```

## Usage

After installation, all agents and commands will be available:

```bash
# Use specialized agents
/agents
# Select from: tutorial-engineer, ai-engineer, prompt-engineer, context-manager, mermaid-expert

# Use tutorial and documentation commands
/doc-generate for the authentication module
/code-explain src/auth/middleware.ts
/improve-agent customer-support
/multi-agent-optimize
```

## Use Cases

- Creating educational content and tutorials
- Building production AI/LLM applications
- Optimizing prompts and agent workflows
- Generating technical documentation
- Creating architecture diagrams
- Managing context in complex AI systems

## Version

1.0.0
