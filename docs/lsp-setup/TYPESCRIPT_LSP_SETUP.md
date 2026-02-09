# TypeScript LSP Integration for Claude Code

A step-by-step guide to set up TypeScript/JavaScript Language Server integration in your project for use with Claude Code.

---

## Quick Start (Recommended)

If you just want TypeScript/JavaScript LSP support without custom configuration:

**1. Install the language server:**
```bash
npm install -g typescript-language-server typescript
```

**2. Install the official plugin:**
```
/plugin install typescript-lsp@claude-plugins-official
```

**Done!** Claude Code now has TypeScript/JavaScript code intelligence in all your projects.

> **Note:** The plugin only configures the connection to the language server—it does NOT include the binary. You must install `typescript-language-server` separately.

---

## Overview

This guide shows you how to configure the TypeScript Language Server Protocol (LSP) integration directly in your project, enabling Claude Code to provide:

- **Go-to-definition** - Navigate to symbol definitions
- **Find references** - Locate all usages of symbols
- **Real-time error checking** - Diagnostics as you work
- **Code intelligence** - Type hints, hover information, autocomplete suggestions

**Supported file extensions:** `.ts`, `.tsx`, `.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs`

---

## Prerequisites

### Install TypeScript Language Server

> **Important:** The LSP plugin only configures how Claude Code connects to the language server. You must install the binary separately on your machine.

**Using npm (recommended):**
```bash
npm install -g typescript-language-server typescript
```

**Using yarn:**
```bash
yarn global add typescript-language-server typescript
```

**Verify installation:**
```bash
typescript-language-server --version
# Should output: 4.x.x

which typescript-language-server
# Should output: /usr/local/bin/typescript-language-server (or similar)
```

If `which` returns nothing, the binary is not in your PATH.

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
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescriptreact",
      ".js": "javascript",
      ".jsx": "javascriptreact",
      ".mts": "typescript",
      ".cts": "typescript",
      ".mjs": "javascript",
      ".cjs": "javascript"
    }
  }
}
```

**Step 3:** Create `.claude-plugin/plugin.json` that references the LSP config:

```json
{
  "name": "typescript-lsp",
  "description": "TypeScript/JavaScript language server for this project",
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
your-project/
├── .claude-plugin/
│   └── plugin.json      ← Create this file
├── src/
├── package.json
└── ...
```

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "typescript-lsp",
  "description": "TypeScript/JavaScript language server for enhanced code intelligence",
  "version": "1.0.0",
  "strict": false,
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".ts": "typescript",
        ".tsx": "typescriptreact",
        ".js": "javascript",
        ".jsx": "javascriptreact",
        ".mts": "typescript",
        ".cts": "typescript",
        ".mjs": "javascript",
        ".cjs": "javascript"
      }
    }
  }
}
```

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
   /plugin install typescript-lsp@claude-plugins-official --scope project
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
   You should see `typescript-lsp` in the list.

2. **Test LSP features:**
   - Open any `.ts` or `.js` file
   - Claude Code now has LSP-powered code intelligence

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
| `command` | string | Yes | — | Executable name (`typescript-language-server`) |
| `args` | string[] | No | `[]` | Command-line arguments (`["--stdio"]`) |
| `extensionToLanguage` | object | Yes | — | Maps file extensions to language IDs |
| `transport` | string | No | `"stdio"` | Communication: `"stdio"` or `"socket"` |
| `env` | object | No | `{}` | Environment variables for the server |
| `initializationOptions` | object | No | `{}` | Options passed during LSP initialization |
| `settings` | object | No | `{}` | Workspace settings via `workspace/didChangeConfiguration` |
| `startupTimeout` | number | No | `30000` | Max startup wait time (ms) |
| `shutdownTimeout` | number | No | `10000` | Graceful shutdown timeout (ms) |
| `restartOnCrash` | boolean | No | `true` | Auto-restart if server crashes |
| `maxRestarts` | number | No | `5` | Maximum restart attempts |

### Language Identifiers

| Extension | Language ID | Description |
|-----------|-------------|-------------|
| `.ts` | `typescript` | TypeScript files |
| `.tsx` | `typescriptreact` | TypeScript with JSX (React) |
| `.js` | `javascript` | JavaScript files |
| `.jsx` | `javascriptreact` | JavaScript with JSX (React) |
| `.mts` | `typescript` | TypeScript ES modules |
| `.cts` | `typescript` | TypeScript CommonJS modules |
| `.mjs` | `javascript` | JavaScript ES modules |
| `.cjs` | `javascript` | JavaScript CommonJS modules |

### Advanced Configuration Example

```json
{
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "transport": "stdio",
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescriptreact",
      ".js": "javascript",
      ".jsx": "javascriptreact"
    },
    "env": {
      "TSS_LOG": "-level verbose -file /tmp/tsserver.log"
    },
    "initializationOptions": {
      "preferences": {
        "includeInlayParameterNameHints": "all"
      }
    },
    "startupTimeout": 60000,
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
/plugin install typescript-lsp@claude-plugins-official --scope project
```

This saves to `.claude/settings.json`. Document in your README:

```markdown
## Claude Code Setup

This project uses TypeScript LSP. Ensure you have the language server installed:

```bash
npm install -g typescript-language-server typescript
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
npm install -g typescript-language-server typescript
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

---

## Troubleshooting

### "Executable not found in $PATH"

The language server binary is not installed or not in PATH:

```bash
# Check if installed
which typescript-language-server

# If not found, install it
npm install -g typescript-language-server typescript

# Verify PATH includes npm global bin
echo $PATH | grep -q "$(npm bin -g)" && echo "OK" || echo "Add npm bin to PATH"
```

### TypeScript Language Server not found on macOS ARM64

If you're on Apple Silicon and see binary issues:

```bash
# Ensure correct architecture
npm install -g typescript-language-server typescript

# Verify architecture
file $(which typescript-language-server)
# Should show: Mach-O 64-bit executable arm64
```

### Plugin not appearing after installation

1. Restart Claude Code
2. Verify directory structure:
   ```bash
   ls -la .claude-plugin/
   # or
   ls -la .lsp.json
   ```
3. Check for JSON syntax errors

### LSP features not working

1. **Verify binary is accessible:**
   ```bash
   which typescript-language-server
   ```

2. **Check project setup:**
   - TypeScript projects should have `tsconfig.json`
   - JavaScript projects benefit from `jsconfig.json`

3. **Run debug mode:**
   ```bash
   claude --debug
   ```
   Look for LSP server initialization messages.

### Slow startup

Increase the startup timeout:

```json
{
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "startupTimeout": 60000,
    "extensionToLanguage": { ... }
  }
}
```

---

## Official LSP Plugins

Claude Code provides pre-built LSP plugins for common languages. Check the marketplace before creating custom plugins:

| Plugin | Language | Install Command |
|--------|----------|-----------------|
| `typescript-lsp` | TypeScript/JavaScript | `/plugin install typescript-lsp@claude-plugins-official` |
| `pyright-lsp` | Python | `/plugin install pyright-lsp@claude-plugins-official` |
| `gopls-lsp` | Go | `/plugin install gopls-lsp@claude-plugins-official` |
| `rust-analyzer-lsp` | Rust | `/plugin install rust-analyzer-lsp@claude-plugins-official` |

---

## Additional Resources

- [typescript-language-server on npm](https://www.npmjs.com/package/typescript-language-server)
- [GitHub Repository](https://github.com/typescript-language-server/typescript-language-server)
- [Claude Code Plugins Documentation](https://docs.claude.com/en/docs/agents-and-tools/plugins)
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)

---

## Summary

| Approach | When to Use |
|----------|-------------|
| **Quick Start** | Most users - `/plugin install typescript-lsp@claude-plugins-official` |
| **Separate LSP Config** (Option A) | Keep config in `.lsp.json`, load with `claude --plugin-dir .` |
| **Inline LSP Config** (Option B) | Everything in `plugin.json`, load with `claude --plugin-dir .` |
| **Team Sharing** | Install from marketplace with `--scope project` |

| Step | Action |
|------|--------|
| 1 | Install `typescript-language-server` globally |
| 2 | Choose: marketplace plugin OR custom configuration |
| 3 | Marketplace: `/plugin install` • Custom: `claude --plugin-dir .` |
| 4 | Verify with `/plugin` command |
