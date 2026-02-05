# Kotlin LSP Integration for Claude Code

A step-by-step guide to set up JetBrains Kotlin Language Server integration in your project for use with Claude Code.

> **Note:** JetBrains Kotlin LSP is currently in **experimental/pre-alpha** phase. While functional for JVM Kotlin Gradle projects, expect rapid iteration and occasional breaking changes.

---

## Quick Start (Recommended)

If you just want Kotlin LSP support without custom configuration:

**1. Install the language server:**

```bash
brew install JetBrains/utils/kotlin-lsp
```

**2. Install the official plugin:**

```
/plugin install kotlin-lsp@claude-plugins-official
```

**Done!** Claude Code now has Kotlin code intelligence in all your projects.

> **Note:** The plugin only configures the connection to the language server—it does NOT include the binary. You must install `kotlin-lsp` separately.

---

## Overview

This guide shows you how to configure JetBrains Kotlin LSP integration directly in your project, enabling Claude Code to provide:

- **Code navigation** - Go to definition for Kotlin, Java, and builtins
- **Find references** - Locate all usages of symbols
- **Real-time diagnostics** - Errors and warnings as you type
- **Code completion** - IntelliJ-powered suggestions
- **Rename refactoring** - Safe symbol renaming across your project
- **Import organization** - Automatic import management
- **Document outline** - Navigate file structure

**Supported file extensions:** `.kt`, `.kts`

---

## Prerequisites

### Project Requirements

Kotlin LSP currently supports:

| Supported | Not Yet Supported |
|-----------|-------------------|
| JVM-only Kotlin projects | Kotlin Multiplatform (KMP) |
| Gradle build system | Maven |
| macOS and Linux | Windows (limited) |

### Java (Optional)

Recent versions of Kotlin LSP **bundle their own JDK**, so external Java installation is optional. However, if you need to use a specific JDK for symbol resolution, Java 17+ is required.

**Verify Java (if needed):**

```bash
java -version
```

---

## Install Kotlin LSP

Choose the installation method for your platform:

### Option A: Homebrew (macOS/Linux) — Recommended

```bash
brew install JetBrains/utils/kotlin-lsp
```

**Verify installation:**

```bash
which kotlin-lsp
kotlin-lsp --version
```

**If PATH not updated after installation:**

```bash
# Reload your shell configuration
exec $SHELL

# Or add to your shell config permanently (~/.zshrc or ~/.bashrc)
export PATH="/opt/homebrew/bin:$PATH"
```

### Option B: Manual Installation

1. **Download the latest release:**
   - Go to [Kotlin LSP Releases](https://github.com/Kotlin/kotlin-lsp/releases)
   - Download the standalone ZIP for your platform:
     - `kotlin-lsp-macos-arm64.zip` (Apple Silicon)
     - `kotlin-lsp-macos-x64.zip` (Intel Mac)
     - `kotlin-lsp-linux-x64.zip`
     - `kotlin-lsp-linux-arm64.zip`

2. **Extract to a permanent location:**

   ```bash
   mkdir -p ~/.local/share/kotlin-lsp
   unzip kotlin-lsp-*.zip -d ~/.local/share/kotlin-lsp
   ```

3. **Make executable and add to PATH:**

   ```bash
   chmod +x ~/.local/share/kotlin-lsp/kotlin-lsp.sh
   ln -s ~/.local/share/kotlin-lsp/kotlin-lsp.sh ~/.local/bin/kotlin-lsp
   ```

   Ensure `~/.local/bin` is in your PATH:

   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Verify installation:**

   ```bash
   kotlin-lsp --help
   ```

---

## Custom Project Configuration

Use this approach when you need project-specific LSP settings or want to share configuration with your team via version control.

### Option A: Separate LSP Config File

Use this approach when you want to keep LSP configuration in a separate file from the plugin metadata.

**Step 1:** Create the plugin directory structure:

```
your-project/
├── .claude-plugin/
│   └── plugin.json
└── .lsp.json          ← At project root, NOT inside .claude-plugin/
```

**Step 2:** Create `.lsp.json` at your project root (same level as `.claude-plugin/`):

```json
{
  "kotlin-lsp": {
    "command": "kotlin-lsp",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".kt": "kotlin",
      ".kts": "kotlin"
    },
    "startupTimeout": 120000
  }
}
```

**Step 3:** Create `.claude-plugin/plugin.json` that references the LSP config:

```json
{
  "name": "kotlin-lsp",
  "description": "Kotlin language server for this project",
  "version": "1.0.0",
  "lspServers": "./.lsp.json"
}
```

**Step 4:** Load the plugin:

```bash
claude --plugin-dir .
```

> **Important:** The `.lsp.json` file must be at the plugin root (same level as `.claude-plugin/`), not inside it. Claude Code does NOT auto-detect `.lsp.json` files—they must be part of a plugin with a `plugin.json` manifest.

### Option B: Inline LSP Config (All-in-One)

Create the directory structure:

```text
your-kotlin-project/
├── .claude-plugin/
│   └── plugin.json      ← Create this file
├── src/
├── build.gradle.kts     (or build.gradle)
└── ...
```

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "kotlin-lsp",
  "description": "Kotlin language server (JetBrains) for code intelligence",
  "version": "1.0.0",
  "strict": false,
  "lspServers": {
    "kotlin-lsp": {
      "command": "kotlin-lsp",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".kt": "kotlin",
        ".kts": "kotlin"
      },
      "startupTimeout": 120000
    }
  }
}
```

**Notes:**
- The `strict: false` field allows the plugin to merge with marketplace definitions
- The `startupTimeout` of 120000ms (2 minutes) allows time for project indexing
- Both `.kt` (source) and `.kts` (script) files are supported

### Load the Local Plugin

```bash
claude --plugin-dir .
```

### Loading Local Plugins

Local plugins are loaded with the `--plugin-dir` flag:

```bash
claude --plugin-dir .                # Load from current directory
claude --plugin-dir ./my-plugin      # Load from specific path
```

> **Note:** Local plugins must be loaded on each Claude Code startup. For persistent installation, publish to a marketplace and use `/plugin install`.

### For Team Sharing

To share LSP configuration with your team:

1. **Option A (Recommended):** Install from marketplace with project scope:
   ```bash
   /plugin install kotlin-lsp@claude-plugins-official --scope project
   ```
   This saves to `.claude/settings.json` which can be committed.

2. **Option B:** Commit the `.claude-plugin/` and `.lsp.json` files, then each team member runs:
   ```bash
   claude --plugin-dir .
   ```

---

## Verify Installation

1. **Check plugin status:**

   ```text
   /plugin
   ```

   You should see `kotlin-lsp` in the list of installed plugins.

2. **Test LSP features:**
   - Open any `.kt` file
   - Claude Code now has access to LSP-powered code intelligence
   - First startup may take 30-60 seconds for indexing

3. **Debug if needed:**

   ```bash
   claude --debug
   ```

   Look for LSP initialization messages.

---

## Configuration Reference

### All LSP Server Options

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `command` | string | Yes | — | Executable name (`kotlin-lsp`) |
| `args` | string[] | No | `[]` | Command-line arguments (`["--stdio"]`) |
| `extensionToLanguage` | object | Yes | — | Maps file extensions to language IDs |
| `transport` | string | No | `"stdio"` | Communication: `"stdio"` or `"socket"` |
| `env` | object | No | `{}` | Environment variables for the server |
| `initializationOptions` | object | No | `{}` | Options passed during LSP initialization |
| `settings` | object | No | `{}` | Workspace settings via `workspace/didChangeConfiguration` |
| `startupTimeout` | number | No | `30000` | Max startup wait time (ms) — use 120000+ for Kotlin |
| `shutdownTimeout` | number | No | `10000` | Graceful shutdown timeout (ms) |
| `restartOnCrash` | boolean | No | `true` | Auto-restart if server crashes |
| `maxRestarts` | number | No | `5` | Maximum restart attempts |

### Language Identifiers

| Extension | Language ID | Description |
|-----------|-------------|-------------|
| `.kt` | `kotlin` | Kotlin source files |
| `.kts` | `kotlin` | Kotlin script files (build scripts, etc.) |

---

## Project Structure

Kotlin LSP works with standard Gradle project structures:

### Gradle Kotlin DSL

```text
your-project/
├── .lsp.json (or .claude-plugin/plugin.json)
├── build.gradle.kts
├── settings.gradle.kts
└── src/
    ├── main/
    │   └── kotlin/
    │       └── com/example/
    │           └── Main.kt
    └── test/
        └── kotlin/
```

### Gradle Groovy DSL

```text
your-project/
├── .lsp.json (or .claude-plugin/plugin.json)
├── build.gradle
├── settings.gradle
└── src/
    ├── main/
    │   └── kotlin/
    └── test/
        └── kotlin/
```

---

## Team Setup

### Option A: Use Marketplace Plugin with Project Scope (Recommended)

Install the official plugin with project scope to share via version control:

```bash
/plugin install kotlin-lsp@claude-plugins-official --scope project
```

This saves to `.claude/settings.json`. Document in your README:

```markdown
## Claude Code Setup

This project uses Kotlin LSP. Ensure you have the language server installed:

```bash
brew install JetBrains/utils/kotlin-lsp
```

The LSP plugin is configured in `.claude/settings.json` and will load automatically.
```

### Option B: Commit Custom Plugin Files

If you need custom configuration, commit `.claude-plugin/` and `.lsp.json`:

1. Add the files to your repository
2. Document in your README:

```markdown
## Claude Code Setup

**Prerequisites:**
```bash
brew install JetBrains/utils/kotlin-lsp
```

**Load the plugin:**
```bash
claude --plugin-dir .
```
```

### Option C: Add to .gitignore

If you prefer personal configuration:

```gitignore
# Claude Code plugins (personal preference)
.claude-plugin/
.lsp.json
```

### Document in CLAUDE.md

For team projects, add LSP setup to your `CLAUDE.md`:

```markdown
## Kotlin LSP Setup

This project uses Kotlin LSP for enhanced code intelligence.

**Installation:**

```bash
brew install JetBrains/utils/kotlin-lsp
/plugin install kotlin-lsp@claude-plugins-official
```
```

---

## Troubleshooting

### kotlin-lsp command not found

1. **Homebrew installation:** Ensure Homebrew bin is in PATH:

   ```bash
   echo $PATH | grep -q "$(brew --prefix)/bin"
   ```

2. **Manual installation:** Verify the symlink exists:

   ```bash
   ls -la ~/.local/bin/kotlin-lsp
   ```

3. **Reload your shell:**

   ```bash
   exec $SHELL
   ```

### Project not recognized

Kotlin LSP requires a valid Gradle project:

1. Ensure `build.gradle.kts` or `build.gradle` exists in project root
2. Ensure `settings.gradle.kts` or `settings.gradle` exists
3. Run `./gradlew build` to verify project compiles

### Slow startup / timeout errors

Increase the startup timeout for large projects:

```json
{
  "kotlin-lsp": {
    "command": "kotlin-lsp",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".kt": "kotlin",
      ".kts": "kotlin"
    },
    "startupTimeout": 180000
  }
}
```

### JDK symbol resolution issues

If you need specific JDK symbols, ensure Java 17+ is available:

```bash
# Set JAVA_HOME if needed
export JAVA_HOME=$(/usr/libexec/java_home -v 17)  # macOS
```

### Features not working as expected

Remember that Kotlin LSP is in experimental phase. Some features may not work:

1. Check the [GitHub issues](https://github.com/Kotlin/kotlin-lsp/issues) for known problems
2. Try updating to the latest version: `brew upgrade kotlin-lsp`
3. Run debug mode to see what's happening:

   ```bash
   claude --debug
   ```

4. Clear the LSP cache and restart Claude Code

---

## Current Limitations

As an experimental project, Kotlin LSP has some limitations:

| Feature | Status |
|---------|--------|
| JVM Kotlin projects | ✅ Supported |
| Gradle build system | ✅ Supported |
| Code navigation | ✅ Supported |
| Diagnostics | ✅ Supported |
| Completion | ✅ Supported |
| Rename refactoring | ✅ Supported |
| Kotlin Multiplatform (KMP) | ❌ Not yet |
| Maven projects | ❌ Not yet |
| Amper projects | ❌ Not yet |
| Code formatting | ❌ Not yet |
| Move refactoring | ❌ Not yet |
| Windows | ⚠️ Limited support |

---

## Official LSP Plugins

Claude Code provides pre-built LSP plugins for common languages:

| Plugin | Language | Install Command |
|--------|----------|-----------------|
| `kotlin-lsp` | Kotlin | `/plugin install kotlin-lsp@claude-plugins-official` |
| `jdtls-lsp` | Java | `/plugin install jdtls-lsp@claude-plugins-official` |
| `typescript-lsp` | TypeScript/JavaScript | `/plugin install typescript-lsp@claude-plugins-official` |
| `pyright-lsp` | Python | `/plugin install pyright-lsp@claude-plugins-official` |

---

## Additional Resources

- [JetBrains Kotlin LSP GitHub](https://github.com/Kotlin/kotlin-lsp)
- [Kotlin LSP Releases](https://github.com/Kotlin/kotlin-lsp/releases)
- [Kotlin Blog](https://blog.jetbrains.com/kotlin/)
- [Claude Code Plugins Documentation](https://docs.claude.com/en/docs/agents-and-tools/plugins)
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)

---

## Summary

| Approach | When to Use |
|----------|-------------|
| **Quick Start** | Most users - `/plugin install kotlin-lsp@claude-plugins-official` |
| **Separate LSP Config** (Option A) | Keep config in `.lsp.json`, load with `claude --plugin-dir .` |
| **Inline LSP Config** (Option B) | Everything in `plugin.json`, load with `claude --plugin-dir .` |
| **Team Sharing** | Install from marketplace with `--scope project` |

| Step | Action |
|------|--------|
| 1 | Verify Gradle project structure |
| 2 | Install `kotlin-lsp` (Homebrew or manual) |
| 3 | Choose: marketplace plugin OR custom configuration |
| 4 | Marketplace: `/plugin install` • Custom: `claude --plugin-dir .` |
| 5 | Verify with `/plugin` command |
