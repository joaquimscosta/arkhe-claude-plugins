# lang Plugin

Language-specific programming skills for production-grade code development across multiple programming languages.

## Overview

The `lang` plugin provides expert-level programming skills for different languages, focusing on production-ready patterns, defensive programming, testing, and best practices.

## Available Skills

### Bash Scripting (`scripting-bash`)

Master defensive Bash scripting for production automation, CI/CD pipelines, and system utilities.

**Use when**:
- Writing shell scripts for automation
- Creating CI/CD pipeline scripts
- Building system utilities
- Need production-grade Bash code
- Implementing defensive programming patterns

**Key capabilities**:
- ✅ POSIX compliance and portability
- ✅ Modern Bash 5.x features with fallbacks
- ✅ Comprehensive error handling
- ✅ Testing frameworks (bats-core, shellspec)
- ✅ CI/CD integration patterns
- ✅ Security scanning and hardening
- ✅ ShellCheck compliance

**Triggers**: "bash", "shell script", "automation", "defensive programming", "CI/CD script"

## Installation

### Via Claude Code Plugin Marketplace (Recommended)

```bash
# Install from marketplace
claude-code plugins install lang
```

### Manual Installation

1. Clone the arkhe-claude-plugins repository:
```bash
git clone https://github.com/your-org/arkhe-claude-plugins.git
cd arkhe-claude-plugins/lang
```

2. Link the plugin to your Claude Code plugins directory:
```bash
# macOS/Linux
ln -s $(pwd) ~/.claude/plugins/lang

# Or copy the directory
cp -r lang ~/.claude/plugins/
```

## Usage

The skills in this plugin are automatically invoked when Claude Code detects relevant trigger keywords in your prompts.

### Example: Bash Scripting

```
User: "Create a production-ready Bash script for database backups with error handling"

Claude Code will automatically use the scripting-bash skill to:
- Apply defensive programming patterns
- Add comprehensive error handling
- Ensure POSIX compliance
- Include testing setup
- Add CI/CD integration examples
```

### Manual Skill Invocation

You can also explicitly invoke a skill using the Skill tool:

```
Use the lang:scripting-bash skill to create a deployment script
```

## Skill Structure

Each language skill follows a progressive disclosure pattern:

```
skills/language-name/
├── SKILL.md              # Core patterns and guidance (~150 lines)
├── EXAMPLES.md           # Code examples and usage patterns
├── TROUBLESHOOTING.md    # Common pitfalls and solutions
└── references/           # Deep-dive documentation (loaded on-demand)
    ├── MODERN_FEATURES.md
    ├── TESTING.md
    ├── CICD.md
    └── SECURITY.md
```

This structure ensures:
- **Low context usage**: Only core patterns loaded initially
- **Progressive disclosure**: Reference docs loaded when needed
- **Fast invocation**: Quick access to essential patterns
- **Comprehensive coverage**: Deep resources available on-demand

## Future Skills

The lang plugin is designed to grow with additional language-specific skills:

- 🚧 **Python** (`developing-python`) - Coming soon
- 🚧 **Rust** (`developing-rust`) - Planned
- 🚧 **TypeScript** (`developing-typescript`) - Planned
- 🚧 **Go** (`developing-go`) - Planned

## Contributing

Contributions are welcome! When adding a new language skill:

1. Follow the established skill structure
2. Keep SKILL.md under 200 lines
3. Use progressive disclosure for detailed content
4. Include comprehensive examples
5. Add troubleshooting guides
6. Test trigger keywords
7. Update this README

## Architecture

For technical details about the plugin architecture and skill patterns, see [ARCHITECTURE.md](ARCHITECTURE.md).

## License

[Your license here]

## Support

For issues, questions, or contributions:
- GitHub Issues: [Repository issues](https://github.com/your-org/arkhe-claude-plugins/issues)
- Documentation: [Plugin docs](https://github.com/your-org/arkhe-claude-plugins/tree/main/lang)
