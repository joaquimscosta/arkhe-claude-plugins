# UI Plugin

> UI/UX design and design system toolkit for interface design, accessibility, and user experience optimization

## Overview

The UI plugin provides comprehensive UI/UX design expertise including design systems, accessibility compliance, user research methodologies, and modern design workflows. Specializes in creating accessible, user-centered interfaces with design token architecture and component library design.

## Components

### Agents (1)

#### ui-ux-designer
Complete UI/UX design expert specializing in accessibility-first design, design systems, and user research methodologies.

**Capabilities**:
- Design system architecture and token management
- Accessibility compliance (WCAG 2.1/2.2 AA)
- User research and usability testing
- Responsive and cross-platform design
- Component library design with Figma/Storybook integration
- Design-to-development handoff optimization
- Atomic design methodology
- Multi-brand design system scaling

**Design Tools Expertise**:
- Figma advanced features (Auto Layout, Variants, Components, Variables)
- Design token systems (Style Dictionary, Figma Variables)
- Prototyping with advanced interactions and micro-animations
- Collaborative design workflows and version control
- Design system governance and maintenance

**User Research Methods**:
- Contextual inquiry and ethnographic research
- Usability testing and A/B testing methodologies
- User journey mapping and persona development
- Accessibility testing (screen readers, keyboard navigation)
- Design critique facilitation

**Use via**: `/agents` interface

### Commands

Currently no commands available. All UI/UX capabilities are accessible through the `ui-ux-designer` agent.

---

## Installation

### Add the Marketplace

```bash
/plugin marketplace add /path/to/arkhe-claude-plugins
```

### Install the Plugin

```bash
/plugin install ui@arkhe-claude-plugins
```

After installation, restart Claude Code.

## Usage

### Accessing the UI/UX Designer Agent

Browse and select the agent through the `/agents` interface:

```bash
/agents
```

Select **ui-ux-designer** to access comprehensive UI/UX design capabilities.

### Example Use Cases

#### Design System Creation
```bash
/agents
# Select: ui-ux-designer
"Help me create a design token system for our multi-brand product"
"Build a component library architecture using atomic design principles"
```

#### Accessibility Optimization
```bash
/agents
# Select: ui-ux-designer
"Review our interface for WCAG 2.1 AA compliance"
"Help me implement keyboard navigation patterns"
"Design accessible form validation with proper error messaging"
```

#### User Research & Testing
```bash
/agents
# Select: ui-ux-designer
"Create a usability testing plan for our checkout flow"
"Help me design user personas based on research data"
"Build a user journey map for our onboarding experience"
```

#### Responsive Design
```bash
/agents
# Select: ui-ux-designer
"Design a responsive navigation system for mobile-first"
"Create a layout system that scales from mobile to desktop"
"Optimize touch targets for mobile accessibility"
```

#### Design-to-Development Handoff
```bash
/agents
# Select: ui-ux-designer
"Create a design system documentation structure for developers"
"Build a Figma-to-Storybook integration workflow"
"Design a component specification template"
```

## Use Cases

✅ Design system architecture and token management
✅ Accessibility compliance and inclusive design
✅ User research and usability testing
✅ Responsive and cross-platform design
✅ Component library design and documentation
✅ Design-to-development workflow optimization

## Applies To

- Design system creation and scaling
- UI component library design
- Accessibility audits and improvements
- User research and testing initiatives
- Design workflow optimization
- Multi-platform design coordination

## Related Plugins

- **review**: For design reviews using Playwright MCP (`design-review` agent, `/design` command)
- **doc**: For design system documentation generation
- **core**: For workflow orchestration and quality control

## Troubleshooting

### Agent Not Found

If the agent isn't recognized after installation:
1. Restart Claude Code
2. Verify plugin is enabled: `/plugin`
3. Check marketplace is added: `/plugin marketplace list`

### Command Conflicts

If another plugin provides a conflicting command name:
- Use namespaced invocation: `/ui:command-name`

## Contributing

Issues and pull requests welcome at the arkhe-claude-plugins repository.

## License

See individual plugin directories for licensing information.

## Version

1.0.0
