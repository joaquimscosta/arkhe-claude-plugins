# Java LSP Integration for Claude Code

A step-by-step guide to set up Eclipse JDT.LS (Java Language Server) integration in your project for use with Claude Code.

---

## Quick Start (Recommended)

If you just want Java LSP support without custom configuration:

**1. Install Java JDK (11 or later, 21+ recommended):**
```bash
# macOS
brew install openjdk@21

# Verify
java -version
```

**2. Install the language server:**
```bash
brew install jdtls
```

**3. Install the official plugin:**
```
/plugin install jdtls-lsp@claude-plugins-official
```

**Done!** Claude Code now has Java code intelligence in all your projects.

> **Note:** The plugin only configures the connection to the language server—it does NOT include the binary. You must install `jdtls` separately.

---

## Overview

This guide shows you how to configure Eclipse JDT.LS integration directly in your project, enabling Claude Code to provide:

- **Go-to-definition** - Navigate to class, method, and field definitions
- **Find references** - Locate all usages of symbols across your codebase
- **Real-time error checking** - Compilation diagnostics as you work
- **Code intelligence** - Type information, hover documentation, autocomplete
- **Refactoring support** - Rename symbols, extract methods, and more

**Supported file extensions:** `.java`

---

## Prerequisites

### 1. Java Development Kit (JDK)

Eclipse JDT.LS requires **Java 11 or later** (JDK, not just JRE). **Java 21+ is recommended** for best compatibility with the latest features.

**Verify your Java version:**
```bash
java -version
```

You should see output like:
```
openjdk version "21.0.x" ...
```

**Install Java if needed:**

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install openjdk@21` |
| Ubuntu/Debian | `sudo apt install openjdk-21-jdk` |
| Fedora | `sudo dnf install java-21-openjdk-devel` |
| Windows | Download from [Adoptium](https://adoptium.net/) |

### 2. Set JAVA_HOME (if not already set)

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export JAVA_HOME=$(/usr/libexec/java_home -v 21)  # macOS
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk     # Linux (path may vary)
```

---

## Install Eclipse JDT.LS

Choose the installation method for your platform:

### Option A: Homebrew (macOS) — Recommended

```bash
brew install jdtls
```

**Verify installation:**
```bash
which jdtls
jdtls --version
```

### Option B: AUR (Arch Linux)

```bash
yay -S jdtls
```

Or with paru:
```bash
paru -S jdtls
```

### Option C: Manual Installation (All Platforms)

1. **Download the latest release:**
   - Milestone releases: http://download.eclipse.org/jdtls/milestones/
   - Snapshot builds: http://download.eclipse.org/jdtls/snapshots/

2. **Extract to a permanent location:**
   ```bash
   mkdir -p ~/.local/share/jdtls
   tar -xzf jdt-language-server-*.tar.gz -C ~/.local/share/jdtls
   ```

3. **Create a wrapper script:**

   Create `~/.local/bin/jdtls` (ensure `~/.local/bin` is in your PATH):

   ```bash
   #!/bin/bash

   JDTLS_HOME="$HOME/.local/share/jdtls"

   # Detect platform
   case "$(uname -s)" in
       Linux*)  CONFIG_DIR="config_linux";;
       Darwin*) CONFIG_DIR="config_mac";;
       *)       CONFIG_DIR="config_linux";;
   esac

   exec java \
       -Declipse.application=org.eclipse.jdt.ls.core.id1 \
       -Dosgi.bundles.defaultStartLevel=4 \
       -Declipse.product=org.eclipse.jdt.ls.core.product \
       -Dlog.level=ALL \
       -noverify \
       -Xmx1G \
       --add-modules=ALL-SYSTEM \
       --add-opens java.base/java.util=ALL-UNNAMED \
       --add-opens java.base/java.lang=ALL-UNNAMED \
       -jar "$JDTLS_HOME/plugins/org.eclipse.equinox.launcher_"*.jar \
       -configuration "$JDTLS_HOME/$CONFIG_DIR" \
       -data "${1:-$HOME/.cache/jdtls-workspace}" \
       "$@"
   ```

4. **Make it executable:**
   ```bash
   chmod +x ~/.local/bin/jdtls
   ```

5. **Verify installation:**
   ```bash
   which jdtls
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
  "jdtls": {
    "command": "jdtls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".java": "java"
    },
    "startupTimeout": 120000
  }
}
```

**Step 3:** Create `.claude-plugin/plugin.json` that references the LSP config:

```json
{
  "name": "java-lsp",
  "description": "Java language server for this project",
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
```
your-java-project/
├── .claude-plugin/
│   └── plugin.json      ← Create this file
├── src/
├── pom.xml              (Maven) or build.gradle (Gradle)
└── ...
```

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "java-lsp",
  "description": "Java language server (Eclipse JDT.LS) for code intelligence",
  "version": "1.0.0",
  "strict": false,
  "lspServers": {
    "jdtls": {
      "command": "jdtls",
      "args": ["serve"],
      "extensionToLanguage": {
        ".java": "java"
      },
      "startupTimeout": 120000
    }
  }
}
```

**Note:** The `startupTimeout` of 120000ms (2 minutes) is important because Eclipse JDT.LS takes longer to initialize than other language servers, especially on first run when it needs to index your project.

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
   /plugin install jdtls-lsp@claude-plugins-official --scope project
   ```
   This saves to `.claude/settings.json` which can be committed.

2. **Option B:** Commit the `.claude-plugin/` and `.lsp.json` files, then each team member runs:
   ```bash
   claude --plugin-dir .
   ```

---

## Verify Installation

1. **Check plugin status:**
   ```
   /plugin
   ```
   You should see `java-lsp` in the list of installed plugins.

2. **Test LSP features:**
   - Open any `.java` file
   - Claude Code now has access to LSP-powered code intelligence
   - Note: First startup may take 30-60 seconds while JDT.LS indexes your project

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
| `command` | string | Yes | — | Executable name (`jdtls`) |
| `args` | string[] | No | `[]` | Command-line arguments (`["serve"]` for jdtls) |
| `extensionToLanguage` | object | Yes | — | Maps file extensions to language IDs |
| `transport` | string | No | `"stdio"` | Communication: `"stdio"` or `"socket"` |
| `env` | object | No | `{}` | Environment variables for the server |
| `initializationOptions` | object | No | `{}` | Options passed during LSP initialization |
| `settings` | object | No | `{}` | Workspace settings via `workspace/didChangeConfiguration` |
| `startupTimeout` | number | No | `30000` | Max startup wait time (ms) — use 120000+ for Java |
| `shutdownTimeout` | number | No | `10000` | Graceful shutdown timeout (ms) |
| `restartOnCrash` | boolean | No | `true` | Auto-restart if server crashes |
| `maxRestarts` | number | No | `5` | Maximum restart attempts |

### Language Identifiers

| Extension | Language ID | Description |
|-----------|-------------|-------------|
| `.java` | `java` | Java source files |

### Advanced Configuration Example

```json
{
  "jdtls": {
    "command": "jdtls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".java": "java"
    },
    "env": {
      "JAVA_OPTS": "-Xmx2G"
    },
    "initializationOptions": {
      "extendedClientCapabilities": {
        "resolveCodeActionSupport": true
      }
    },
    "startupTimeout": 180000,
    "restartOnCrash": true,
    "maxRestarts": 3
  }
}
```

---

## Team Setup

### Option A: Use Marketplace Plugin with Project Scope (Recommended)

Install the official plugin with project scope to share via version control:

```bash
/plugin install jdtls-lsp@claude-plugins-official --scope project
```

This saves to `.claude/settings.json`. Document in your README:

```markdown
## Claude Code Setup

This project uses Java LSP. Ensure you have the prerequisites:

- Java 11+ JDK installed (21+ recommended)
- Eclipse JDT.LS (`jdtls`) installed:
  - macOS: `brew install jdtls`
  - Arch Linux: `yay -S jdtls`

The LSP plugin is configured in `.claude/settings.json` and will load automatically.
```

### Option B: Commit Custom Plugin Files

If you need custom configuration, commit `.claude-plugin/` and `.lsp.json`:

1. Add the files to your repository
2. Document in your README:

```markdown
## Claude Code Setup

**Prerequisites:**
- Java 11+ JDK installed (21+ recommended)
- Eclipse JDT.LS: `brew install jdtls`

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

---

## Troubleshooting

### jdtls command not found

1. Verify installation:
   ```bash
   which jdtls
   ```

2. If using manual installation, ensure `~/.local/bin` is in your PATH:
   ```bash
   echo $PATH | grep -q "$HOME/.local/bin" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   ```

### JAVA_HOME not set or incorrect

1. Check current value:
   ```bash
   echo $JAVA_HOME
   java -version
   ```

2. Set it correctly in your shell profile:
   ```bash
   # macOS
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)

   # Linux (adjust path as needed)
   export JAVA_HOME=/usr/lib/jvm/java-21-openjdk
   ```

### Wrong Java version

Eclipse JDT.LS requires Java 11+. If you have multiple Java versions:

```bash
# macOS - list installed versions
/usr/libexec/java_home -V

# Use a specific version
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```

### Slow startup / timeout errors

Java LSP takes longer to start than other language servers. Increase the timeout:

```json
{
  "jdtls": {
    "command": "jdtls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".java": "java"
    },
    "startupTimeout": 180000
  }
}
```

For very large projects, you may need up to 180000ms (3 minutes).

### LSP features not working

1. **Check for a build file**: JDT.LS works best with Maven (`pom.xml`) or Gradle (`build.gradle`) projects
2. **Check project structure**: Ensure your source files are in the standard `src/main/java` layout
3. **Clear the workspace cache**:
   ```bash
   rm -rf ~/.cache/jdtls-workspace
   ```
4. **Run debug mode:**
   ```bash
   claude --debug
   ```
   Look for LSP server initialization messages.

### Out of memory errors

Increase heap size via env configuration or JAVA_OPTS:
```bash
export JAVA_OPTS="-Xmx2G"
```

Or in your LSP configuration:
```json
{
  "jdtls": {
    "command": "jdtls",
    "env": {
      "JAVA_OPTS": "-Xmx2G"
    },
    ...
  }
}
```

### Conflicts with IDE Java extensions

If your editor has a built-in Java extension:
- **VS Code**: Disable "Extension Pack for Java" if using Claude Code's JDT.LS
- **IntelliJ**: Claude Code's LSP runs alongside IntelliJ's LSP (no conflict)
- **Eclipse**: Not applicable (JDT.LS is native to Eclipse)

---

## Project Structure Tips

Eclipse JDT.LS works best with standard project structures:

### Maven Project
```
your-project/
├── .lsp.json (or .claude-plugin/plugin.json)
├── pom.xml
└── src/
    ├── main/
    │   └── java/
    │       └── com/example/
    │           └── App.java
    └── test/
        └── java/
```

### Gradle Project
```
your-project/
├── .lsp.json (or .claude-plugin/plugin.json)
├── build.gradle
└── src/
    ├── main/
    │   └── java/
    └── test/
        └── java/
```

---

## Official LSP Plugins

Claude Code provides pre-built LSP plugins for common languages:

| Plugin | Language | Install Command |
|--------|----------|-----------------|
| `jdtls-lsp` | Java | `/plugin install jdtls-lsp@claude-plugins-official` |
| `kotlin-lsp` | Kotlin | `/plugin install kotlin-lsp@claude-plugins-official` |
| `typescript-lsp` | TypeScript/JavaScript | `/plugin install typescript-lsp@claude-plugins-official` |
| `pyright-lsp` | Python | `/plugin install pyright-lsp@claude-plugins-official` |

---

## Additional Resources

- [Eclipse JDT.LS GitHub](https://github.com/eclipse-jdtls/eclipse.jdt.ls)
- [Eclipse JDT.LS Downloads](http://download.eclipse.org/jdtls/milestones/)
- [jdtls Homebrew Formula](https://formulae.brew.sh/formula/jdtls)
- [VSCode Java Extension](https://github.com/redhat-developer/vscode-java) (uses JDT.LS internally)
- [Claude Code Plugins Documentation](https://docs.claude.com/en/docs/agents-and-tools/plugins)
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)

---

## Summary

| Approach | When to Use |
|----------|-------------|
| **Quick Start** | Most users - `/plugin install jdtls-lsp@claude-plugins-official` |
| **Separate LSP Config** (Option A) | Keep config in `.lsp.json`, load with `claude --plugin-dir .` |
| **Inline LSP Config** (Option B) | Everything in `plugin.json`, load with `claude --plugin-dir .` |
| **Team Sharing** | Install from marketplace with `--scope project` |

| Step | Action |
|------|--------|
| 1 | Install Java 11+ JDK (21+ recommended) and set JAVA_HOME |
| 2 | Install `jdtls` (Homebrew, AUR, or manual) |
| 3 | Choose: marketplace plugin OR custom configuration |
| 4 | Marketplace: `/plugin install` • Custom: `claude --plugin-dir .` |
| 5 | Verify with `/plugin` command |
