# Review Plugin

> Code quality review and workflow orchestration tools for development teams

## Overview

The Review plugin provides comprehensive code quality tools including code review, security assessment, design review, codebase documentation, and workflow orchestration. All commands support customizable output paths for flexible integration into any project workflow.

## Components

### Agents (2)

#### 1. pragmatic-code-review
Principal Engineer code reviewer implementing the "Pragmatic Quality" framework - balancing rigorous engineering standards with development velocity.

**Capabilities**:
- Architectural design evaluation
- Functionality and correctness analysis
- Security vulnerability assessment
- Maintainability and readability review
- Testing strategy evaluation
- Performance and scalability analysis

**Use via**: `/agents` interface

#### 2. ui-ux-designer
Complete UI/UX design expert specializing in accessibility-first design, design systems, and user research methodologies.

**Capabilities**:
- Design system architecture
- Accessibility compliance (WCAG 2.1/2.2 AA)
- User research and usability testing
- Responsive and cross-platform design
- Component library design
- Design token management

**Use via**: `/agents` interface

### Commands (5)

#### 1. /code
Comprehensive code review analyzing git changes with the Pragmatic Quality framework.

**Features**:
- Analyzes complete git diff
- Hierarchical review framework (Architecture → Security → Maintainability)
- Actionable feedback with engineering principles
- Triage matrix (Critical/Improvement/Nit)
- Generates markdown report

**Usage**:
```bash
/code                    # Saves to .claude/reports/
/code reviews/           # Saves to custom path
/review:code             # Namespaced invocation
```

**Output**: `{path}/{YYYY-MM-DD}_{HH-MM-SS}_code-review.md`

---

#### 2. /security
Security-focused code review identifying high-confidence exploitable vulnerabilities.

**Features**:
- Focuses on HIGH and MEDIUM severity issues
- Minimizes false positives (>80% confidence threshold)
- Comprehensive vulnerability categories
- Exploit scenario documentation
- Fix recommendations

**Vulnerability Categories**:
- Input validation (SQL injection, XSS, command injection)
- Authentication & authorization bypasses
- Cryptographic vulnerabilities
- Data exposure and PII handling
- Injection and code execution

**Usage**:
```bash
/security                # Saves to .claude/reports/
/security audits/        # Saves to custom path
```

**Output**: `{path}/{YYYY-MM-DD}_{HH-MM-SS}_security-review.md`

---

#### 3. /design
Frontend design review with Playwright automation for interactive testing.

**Features**:
- Live environment testing (requires preview URL)
- Responsive design validation (desktop/tablet/mobile)
- Accessibility compliance testing (WCAG 2.1 AA)
- Interactive state verification (hover, active, disabled)
- Visual consistency analysis
- Browser console error checking

**Review Phases**:
1. Interaction and user flow testing
2. Responsiveness across viewports
3. Visual polish and consistency
4. Accessibility (keyboard navigation, focus states, contrast)
5. Robustness testing (edge cases, error states)
6. Code health review

**Requirements**: Playwright MCP server (see [MCP Setup](#mcp-requirements))

**Usage**:
```bash
/design                  # Interactive review with screenshots
```

**Output**: Inline markdown report with screenshots

---

#### 4. /codebase
Complete codebase documentation generator analyzing project structure, architecture, and key files.

**Features**:
- Directory structure analysis
- File categorization and documentation
- API endpoint discovery
- Architecture deep dive
- Technology stack breakdown
- Visual architecture diagrams
- Key insights and recommendations

**Usage**:
```bash
/codebase                       # Generates codebase_analysis.md in root
```

**Output**: `codebase_analysis.md` (root directory)

---

#### 5. /workflow
Product Manager-led orchestration agent with enhanced thinking modes and MCP server integration.

**Features**:
- Multi-agent orchestration
- Task tracking with AGENT_TODOS.md
- Parallel execution waves
- Enhanced thinking modes (--seq, --ultrathink, --thinkhard)
- MCP server integration (--exa, --c7)
- Spec kit support
- Natural language request handling

**Flags**:
- `--seq`: Sequential thinking for deep analytical reasoning
- `--exa`: Web research and competitive analysis
- `--c7`: Best practices research from documentation
- `--ultrathink`: Ultra-deep thinking mode
- `--thinkhard`: Intensive thinking mode
- `--thinkharder`: Maximum thinking mode

**Usage**:
```bash
/workflow implement auth --seq           # With sequential thinking
/workflow oauth-integration --exa --c7   # Spec kit with research
/workflow refactor payment --thinkhard   # Natural language with deep analysis
```

**Workflow Directory**: `.claude/workflow/` (customizable via arguments)

**Output**:
- `.claude/workflow/AGENT_TODOS.md` (natural language requests)
- `.claude/workflow/specs/{spec-name}/AGENT_TODOS.md` (spec kits)
- `.claude/workflow/archive/` (archived task tracking)

---

## Installation

### Add the Marketplace

```bash
/plugin marketplace add /path/to/arkhe-claude-plugins
```

### Install the Plugin

```bash
/plugin install review@arkhe-claude-plugins
```

After installation, restart Claude Code.

## Usage

### Direct Invocation

When no command conflicts exist:

```bash
/code
/security
/design
/codebase
/workflow implement feature --seq
```

### Namespaced Invocation

When command name conflicts exist with other plugins:

```bash
/review:code
/review:security
/review:design
/review:codebase
/review:workflow feature --seq
```

### Custom Output Paths

Commands support optional custom output paths:

```bash
# Code review
/code                    # Default: .claude/reports/
/code reviews/code       # Custom: reviews/code/
/code ../shared-reviews  # Relative paths supported

# Security review
/security                # Default: .claude/reports/
/security audits/sec     # Custom: audits/sec/

# Workflow
/workflow feature               # Default: .claude/workflow/
/workflow feature custom/wf     # Custom: custom/wf/
```

### Accessing Agents

Browse and select agents through the `/agents` interface:

```bash
/agents
```

This will show both:
- **pragmatic-code-review** - Principal Engineer code reviewer
- **ui-ux-designer** - UI/UX design expert

## MCP Requirements

### Playwright MCP (design-review command)

The `/design` command requires the Playwright MCP server for automated browser testing.

**Setup**:
1. Install Playwright MCP server
2. Configure in your project's `.mcp.json`
3. Ensure MCP server is running

**Playwright Tools Used**:
- `browser_navigate` - Navigate to preview URLs
- `browser_click/type/select_option` - Interactive testing
- `browser_take_screenshot` - Visual evidence capture
- `browser_resize` - Viewport testing
- `browser_snapshot` - DOM analysis
- `browser_console_messages` - Error detection

For detailed Playwright MCP setup, see Playwright MCP documentation.

## Configuration

### Default Paths

The plugin uses the following default paths:

| Command | Default Path | Customizable |
|---------|--------------|--------------|
| code | `.claude/reports/` | ✅ Yes (via `$ARGUMENTS`) |
| security | `.claude/reports/` | ✅ Yes (via `$ARGUMENTS`) |
| design | N/A (inline output) | ❌ No |
| codebase | `./` (root) | ❌ No (fixed filename) |
| workflow | `.claude/workflow/` | ✅ Yes (via `$ARGUMENTS`) |

### Project Integration

The plugin automatically creates output directories if they don't exist:

```bash
# These directories are created automatically:
.claude/
├── reports/           # Code and security reviews
└── workflow/          # Workflow orchestration
    ├── specs/         # Spec kit directories
    └── archive/       # Archived task tracking
```

## Examples

### Code Review Workflow

```bash
# 1. Review current changes
/code

# 2. Address critical issues
# ... make fixes ...

# 3. Run security review
/security

# 4. Review UI changes (if applicable)
/design
```

### Workflow Orchestration

```bash
# Start new feature with spec kit
/workflow oauth-integration --seq --c7

# Or natural language request
/workflow implement user authentication with JWT --thinkhard

# Check task progress
# (View .claude/workflow/AGENT_TODOS.md)
```

### Codebase Documentation

```bash
# Generate comprehensive docs
/codebase

# Review the generated codebase_analysis.md
```

## Troubleshooting

### Command Not Found

If commands aren't recognized after installation:
1. Restart Claude Code
2. Verify plugin is enabled: `/plugin`
3. Check marketplace is added: `/plugin marketplace list`

### Command Conflicts

If another plugin provides the same command name:
- Use namespaced invocation: `/review:command-name`

### Playwright MCP Issues

If `/design` fails:
1. Verify Playwright MCP server is running
2. Check `.mcp.json` configuration
3. Ensure preview environment is accessible
4. Review MCP server logs

### Output Path Issues

If reports aren't saving:
1. Check directory permissions
2. Verify path is valid (absolute or relative)
3. Ensure parent directories exist (plugin creates them automatically)

## Contributing

Issues and pull requests welcome at the arkhe-claude-plugins repository.

## License

See individual plugin directories for licensing information.

## Version

1.0.0
