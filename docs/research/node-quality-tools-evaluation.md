---
title: "Node.js/TypeScript Quality Tools Evaluation"
version: "1.0.0"
status: Published
created: 2026-03-25
last_updated: 2026-03-25
---

# Node.js/TypeScript Quality Tools Evaluation

## A Practitioner's Guide for Modern Web Projects

> **Node.js baseline**: 18.18+ (LTS) | **Package manager**: pnpm (preferred), npm, yarn
>
> This guide evaluates 14 tools across seven categories for Node.js and TypeScript teams building
> production systems with React, Next.js, and server-side Node.js applications. Every tool listed
> is free or has a meaningful free tier. Configurations are shown using modern standards: ESM,
> `eslint.config.mjs` flat config, and TypeScript strict mode.

---

## Executive Summary

### Tool Landscape at a Glance

| Tool | Category | Version | TypeScript | React/Next.js | Setup Effort | Cost | Stars |
|------|----------|---------|------------|---------------|--------------|------|-------|
| **ESLint 9.x** | Static Analysis | 9.x (flat config) | Yes (typescript-eslint 8.x) | Yes | Medium | Free | 25.4k |
| **Biome 2.x** | Static Analysis + Formatting | 2.4.x | Built-in | Partial | Low | Free | 16.4k |
| **Prettier 3.x** | Formatting | 3.7.x | Yes | Yes | Low | Free | 49.7k |
| **TypeScript strict** | Type Checking | 5.8.x | Native | Yes | Low–Medium | Free | 103k |
| **noUncheckedIndexedAccess** | Type Checking | Built-in TS | Native | Yes | Trivial | Free | (TS) |
| **exactOptionalPropertyTypes** | Type Checking | Built-in TS | Native | Yes | Trivial | Free | (TS) |
| **Vitest 3.x** | Testing | 3.x | Built-in | Yes | Low | Free | 14.3k |
| **Jest 30.x** | Testing | 30.x | Yes (ts-jest / SWC) | Yes | Medium | Free | 44.5k |
| **Playwright Test 1.x** | Testing (E2E) | 1.58.x | Built-in | Yes (Next.js) | Medium | Free | 70.3k |
| **@testing-library/react** | Testing (component) | 16.x | Yes | Yes | Low | Free | 19.6k |
| **@vitest/coverage-v8** | Coverage | 3.x | Built-in | Yes | Low | Free | (Vitest) |
| **c8** | Coverage | 10.x | Yes | N/A | Low | Free | 3.0k |
| **istanbul/nyc** | Coverage (legacy) | 17.x | Partial | N/A | Medium | Free | 8.8k |
| **size-limit** | Bundle Analysis | 12.x | Yes | Yes | Low | Free | 6.9k |
| **@next/bundle-analyzer** | Bundle Analysis | 16.x | Yes | Next.js only | Low | Free | (Next.js) |
| **next lint** | Framework-Specific | 16.x | Yes | Next.js only | Trivial | Free | (Next.js) |

### Recommended Starting Sets

#### Small React/Next.js Team

| Layer | Tool | Why |
|-------|------|-----|
| Linting | ESLint 9.x + typescript-eslint | Industry standard, massive plugin ecosystem |
| Formatting | Prettier 3.x | Zero-config, widely supported, pre-commit auto-fix |
| Type safety | TypeScript `strict: true` + `noUncheckedIndexedAccess` | Catches indexed-access undefined crashes |
| Unit/component tests | Vitest 3.x + @testing-library/react | 3–10x faster than Jest for Vite/Next.js projects |
| E2E tests | Playwright Test 1.x | Multi-browser, auto-wait, Next.js native integration |
| Coverage | @vitest/coverage-v8 | Zero-config coverage with Vitest |
| Framework lint | `next lint` | Free Next.js rule set (Core Web Vitals) |
| Bundle check | @next/bundle-analyzer | Identifies bloated pages and dependencies |

#### Large TypeScript Monorepo Team

| Layer | Tool | Why |
|-------|------|-----|
| Linting | ESLint 9.x flat config with workspace overrides | Scope rules per package; type-aware rules where needed |
| Formatting | Prettier 3.x OR Biome 2.x | Biome is 10–25x faster for large codebases; Prettier has wider plugin ecosystem |
| Type safety | TypeScript strict + `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes` | Maximum compile-time safety |
| Unit tests | Vitest 3.x with workspace config | Native monorepo workspace support |
| Component tests | @testing-library/react | Standard React testing across all packages |
| E2E tests | Playwright Test 1.x | Shared test utilities, parallel sharding in CI |
| Coverage | @vitest/coverage-v8 with thresholds | Enforced per-package coverage gates |
| Bundle analysis | size-limit | PR comments with per-export size checks |
| Git hooks | Lefthook with staged-files mode | Fast pre-commit linting for large trees |

#### Library/Package Author

| Layer | Tool | Why |
|-------|------|-----|
| Linting | Biome 2.x | Single binary, zero peer deps, fast for library CI |
| Type safety | TypeScript strict + all strict extras | Strict public API guarantees for consumers |
| Unit tests | Vitest 3.x | ESM-native, no transform config for modern libraries |
| Coverage | @vitest/coverage-v8 with 90%+ threshold | Quality gate for published packages |
| Bundle analysis | size-limit | Enforce KB budget; CI comment on PRs |
| Type coverage | TypeScript project references | Isolate build per entrypoint |

---

## 1. Static Analysis

### 1.1 ESLint 9.x (Flat Config)

**What**: Pluggable JavaScript and TypeScript linter with 400+ built-in rules and a vast plugin ecosystem
**Site**: [eslint.org](https://eslint.org/) | **Version**: 9.x (flat config default since v9.0, April 2024) | **License**: MIT
**Compat**: TypeScript Yes (typescript-eslint 8.x), React/Next.js Yes (eslint-plugin-react, eslint-config-next), Node.js 18.18+

#### Why It Matters

ESLint is the industry standard for JavaScript and TypeScript linting with over 25,000 GitHub stars and 67M+ weekly npm downloads for `@typescript-eslint/eslint-plugin` alone. Version 9 introduced **flat config** as the default, replacing the legacy `.eslintrc.*` cascade with a single `eslint.config.mjs` file that uses standard ESM imports. This eliminates plugin resolution ambiguity, enables IDE autocomplete on the config itself, and drastically reduces the "which config wins?" debugging problem that plagued large monorepos.

The critical companion package, `typescript-eslint`, provides type-aware linting rules that flag patterns TypeScript's type checker cannot catch on its own, such as unsafe `any` usage, `no-floating-promises`, and return-type inconsistencies. ESLint v10 is in progress and will remove the legacy `.eslintrc` engine entirely; migrating now to flat config is the only forward-compatible path.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Strong** – typescript-eslint 8.x; 300+ TS-specific rules |
| React/Next.js Support | **Strong** – eslint-plugin-react, eslint-config-next, eslint-plugin-react-hooks |
| Setup Effort | **Medium** – flat config requires understanding ESM imports and config arrays |
| Performance | **Medium** – JS-based; type-aware rules require `parserServices`, slower on large files |
| Migration Path | **Clear** – Official migrator + `@eslint/eslintrc` compat package for legacy configs |
| Plugin Ecosystem | **Unmatched** – 10,000+ plugins on npm |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** – 25.4k stars, Google/Facebook/Airbnb configs widely used |

#### Quick Start

```bash
pnpm add -D eslint @eslint/js typescript-eslint eslint-plugin-react eslint-plugin-react-hooks
```

```js
// eslint.config.mjs
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";

export default tseslint.config(
  { ignores: ["dist/", ".next/", "coverage/", "node_modules/"] },

  // Base JS rules
  js.configs.recommended,

  // TypeScript rules (type-aware)
  ...tseslint.configs.recommendedTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // React rules
  {
    files: ["**/*.{tsx,jsx}"],
    plugins: {
      react: reactPlugin,
      "react-hooks": reactHooks,
    },
    settings: { react: { version: "detect" } },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      "react/react-in-jsx-scope": "off", // Not needed with React 17+
    },
  },

  // Disable type-checked rules on plain JS files
  {
    files: ["**/*.js", "**/*.mjs"],
    extends: [tseslint.configs.disableTypeChecked],
  }
);
```

```json
// package.json scripts
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix"
  }
}
```

#### Migrating from Legacy Config (.eslintrc.*)

```bash
# Step 1: Use the official migrator
npx @eslint/migrate-config .eslintrc.json

# Step 2: Install flat config compat shim for plugins not yet flat-config-native
pnpm add -D @eslint/eslintrc

# Step 3: Wrap legacy shareable configs
# eslint.config.mjs
import { FlatCompat } from "@eslint/eslintrc";
const compat = new FlatCompat();
export default [
  ...compat.extends("some-legacy-config"),
];
```

#### Key Configuration Options

| Option | Purpose | Recommended |
|--------|---------|-------------|
| `tseslint.configs.recommendedTypeChecked` | Type-aware TS rules (needs tsconfig) | Yes for TS projects |
| `tseslint.configs.strict` | Stricter TS rules (opinionated) | Large teams |
| `react/jsx-no-target-blank` | Security: prevent `target="_blank"` without `rel` | Always |
| `@typescript-eslint/no-floating-promises` | Catch unhandled promise rejections | Always |
| `@typescript-eslint/no-explicit-any` | Ban `any` usage | Recommended |
| `no-console` | Warn on console.log in production code | `"warn"` |

#### Known Limitations

- **Performance**: Type-aware rules require TypeScript program construction; adds 2–10x overhead vs. non-type-aware mode on large projects
- **Flat config learning curve**: Flat config replaces extends/overrides with config arrays; team education needed
- **Plugin ecosystem lag**: Some older plugins still lack flat config exports (use `@eslint/eslintrc` compat shim)
- **No formatting**: Deliberately does not format code — combine with Prettier or Biome for formatting
- **ESLint v10 deprecation**: Legacy `.eslintrc.*` support removed in v10 (planned 2026); migrate sooner rather than later

---

### 1.2 Biome 2.x

**What**: All-in-one Rust-based toolchain: linter + formatter + import organizer in a single binary
**Site**: [biomejs.dev](https://biomejs.dev/) | **Version**: 2.4.x (June 2025 — v2.0 "Biotype" released) | **License**: MIT
**Compat**: TypeScript Built-in, JSX/TSX Built-in, React Partial (plugins in v2+), Next.js Limited (no SSR-specific rules)

#### Why It Matters

Biome launched in 2022 as a community fork of Rome and has since become the fastest JavaScript/TypeScript linter and formatter available. Written in Rust, it processes 312 files in 1.3 seconds where ESLint+Prettier take 28 seconds — a 20x real-world improvement observed across multiple production codebases. Biome 2.0 ("Biotype"), released June 2025, added the ecosystem's most significant milestone: **type-aware linting without the TypeScript compiler**, using its own built-in type inference engine. Early results show ~75% detection parity with `typescript-eslint` for floating promise rules at a fraction of the performance cost.

Biome v2 also adds GritQL plugin support (custom lint rules), multi-file analysis, domain-based rule sets (React, testing frameworks auto-detected from `package.json`), and improved monorepo support. For teams starting fresh or willing to migrate, Biome eliminates the ESLint + Prettier dual-tool configuration problem.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Strong** – Built-in TS parser + v2 type inference (no `tsc` dependency) |
| React/Next.js Support | **Partial** – React domain rules in v2+; no Next.js-specific rules yet |
| Setup Effort | **Low** – Single binary, one `biome.json` config file |
| Performance | **Exceptional** – 10–25x faster than ESLint+Prettier on typical projects |
| Plugin Ecosystem | **Growing** – GritQL plugins in v2; much smaller than ESLint ecosystem |
| Migration from ESLint | **Good** – `biome migrate eslint --write` migrates configs automatically |
| Cost | **Free** |
| Ecosystem Maturity | **Emerging** – 16.4k stars; v2 released June 2025; rapid growth |

#### Quick Start

```bash
pnpm add -D --save-exact @biomejs/biome
npx @biomejs/biome init
```

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/2.4.0/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "files": {
    "ignoreUnknown": false,
    "ignore": ["dist", ".next", "coverage"]
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "domains": {
      "react": "all"
    },
    "rules": {
      "recommended": true,
      "correctness": {
        "noFloatingPromises": "error"
      }
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "semicolons": "always"
    }
  }
}
```

```json
// package.json scripts
{
  "scripts": {
    "lint": "biome lint --write .",
    "format": "biome format --write .",
    "check": "biome check --write ."
  }
}
```

#### Migrating from ESLint + Prettier

```bash
# Migrate ESLint config
npx @biomejs/biome migrate eslint --write

# Migrate Prettier config
npx @biomejs/biome migrate prettier --write

# Remove old packages
pnpm remove eslint prettier eslint-config-prettier eslint-plugin-prettier \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

#### Key Configuration Options

| Option | Purpose | Recommended |
|--------|---------|-------------|
| `linter.domains.react` | Enable all React-specific rules | `"all"` for React projects |
| `linter.domains.jest` | Enable jest/vitest matcher rules | `"all"` for test files |
| `formatter.lineWidth` | Max line length (default: 80) | `100` for most teams |
| `organizeImports.enabled` | Auto-sort imports | `true` |
| `vcs.useIgnoreFile` | Respect `.gitignore` | `true` |
| `javascript.formatter.quoteStyle` | Single or double quotes | Match team preference |

#### Known Limitations

- **No Next.js-specific rules**: Missing server component restrictions, `next/script` enforcement, Core Web Vitals rules — must pair with `next lint` for Next.js projects
- **Smaller plugin ecosystem**: Cannot replicate all ESLint plugins (e.g., security plugins, import order customizations)
- **Type inference parity**: v2 type inference covers ~75% of `typescript-eslint` type-aware rules; complex generics may be missed
- **CSS/HTML**: CSS formatting available in v2.4+; HTML formatting still experimental
- **Vue/Svelte/Astro**: Experimental support in v2.3+ (not production-recommended for frameworks)

---

## 2. Formatting

### 2.1 Prettier 3.x

**What**: Opinionated code formatter that enforces consistent style by re-printing entire source files
**Site**: [prettier.io](https://prettier.io/) | **Version**: 3.7.x (Nov 2025) | **License**: MIT
**Compat**: TypeScript Yes, JSX/TSX Yes, React Yes, Next.js Yes, JSON/CSS/Markdown/YAML Yes

#### Why It Matters

Prettier is the de facto standard code formatter for the JavaScript ecosystem with 49,700+ GitHub stars. Its core value proposition is eliminating code style debates entirely: it produces a single canonical output regardless of how the code was originally written. Prettier 3.x moved to ESM-only, improved performance, and added TypeScript configuration file support (prettier.config.ts in v3.5).

Prettier deliberately handles only formatting (whitespace, line breaks, quotes), leaving semantic correctness to ESLint. The two tools are complementary: use `eslint-config-prettier` to disable ESLint rules that conflict with Prettier's output. In pre-commit hooks, running `prettier --write` followed by staging the result gives automatic formatting on every commit via `stage_fixed: true` in Lefthook.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Strong** – Full TS/TSX support; prettier.config.ts supported in v3.5+ |
| React/Next.js Support | **Strong** – JSX, TSX, CSS modules, JSON all formatted consistently |
| Setup Effort | **Low** – `pnpm add -D prettier` + one config file |
| Performance | **Medium** – JS-based; slower than Biome for large codebases |
| Configurability | **Intentionally Limited** – Opinionated by design; limited options |
| Plugin Ecosystem | **Good** – Tailwind class sorting, SQL, GraphQL, Java plugins available |
| Cost | **Free** |
| Ecosystem Maturity | **Dominant** – 49.7k stars; universal IDE integration |

#### Quick Start

```bash
pnpm add -D prettier eslint-config-prettier
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": []
}
```

```json
// .prettierignore
node_modules/
.next/
dist/
build/
coverage/
*.min.js
```

```json
// package.json scripts
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

#### Integrating with ESLint (Flat Config)

```bash
pnpm add -D eslint-config-prettier
```

```js
// eslint.config.mjs — add as last entry to disable conflicting ESLint rules
import prettierConfig from "eslint-config-prettier";
export default [
  // ...other configs
  prettierConfig,
];
```

#### With Tailwind CSS (Automatic Class Sorting)

```bash
pnpm add -D prettier-plugin-tailwindcss
```

```json
// .prettierrc
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app/globals.css"  // Required for Tailwind v4
}
```

#### Key Configuration Options

| Option | Default | Notes |
|--------|---------|-------|
| `semi` | `true` | Semicolons at end of statements |
| `singleQuote` | `false` | Use single quotes for strings |
| `printWidth` | `80` | Recommended: 100–120 for modern screens |
| `trailingComma` | `"all"` (v3) | Trailing commas everywhere valid in ES5+ |
| `tabWidth` | `2` | Spaces per indentation level |
| `endOfLine` | `"lf"` | Use LF for cross-platform consistency |

#### Known Limitations

- **Intentionally opinionated**: Limited customization by design; some teams resist the output style
- **Performance at scale**: 28+ seconds for 312 files vs. Biome's 1.3 seconds — matters for pre-commit hooks
- **No linting**: Does not catch code quality issues; ESLint remains required for semantic checks
- **Tailwind v4**: `tailwindStylesheet` must be set or class sorting silently becomes a no-op

---

## 3. Type Checking

### 3.1 TypeScript Strict Mode

**What**: TypeScript's built-in strict mode umbrella flag enabling all strictness-related compiler checks
**Site**: [typescriptlang.org](https://typescriptlang.org/) | **Version**: 5.8.x (Mar 2026) | **License**: Apache 2.0
**Compat**: Native TypeScript, all frameworks

#### Why It Matters

TypeScript's `strict: true` is the single highest-leverage quality improvement available to any TypeScript project. It enables eight checks simultaneously: `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `strictPropertyInitialization`, and `useUnknownInCatchVariables`. Each of these catches a distinct class of runtime errors at compile time.

On a brownfield codebase, enabling strict mode typically reveals hundreds to thousands of latent type errors — each one a potential production bug. The discipline of maintaining strict mode prevents the `any` creep that eventually makes TypeScript lose its value.

#### Quick Start

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "esModuleInterop": true,
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src", "tests"],
  "exclude": ["node_modules", "dist", ".next"]
}
```

#### What `strict: true` Enables

| Flag | Protection |
|------|-----------|
| `strictNullChecks` | Prevents null/undefined access without guards |
| `noImplicitAny` | Bans untyped `any` inference |
| `strictFunctionTypes` | Catches function signature mismatches in callbacks |
| `strictPropertyInitialization` | Ensures class fields are initialized in constructor |
| `useUnknownInCatchVariables` | `catch (e)` is `unknown` not `any` (TS 4.4+) |
| `noImplicitThis` | Prevents untyped `this` in functions |

#### Known Limitations

- **Migration cost**: Enabling strict on an existing codebase causes many immediate type errors
- **Gradual adoption**: Use `// @ts-nocheck` on files being migrated; track via `strict: false` per-file
- **`skipLibCheck: true`**: Required for most projects due to incompatible declaration files in dependencies

---

### 3.2 noUncheckedIndexedAccess

**What**: TypeScript compiler flag that adds `| undefined` to all indexed access types
**Site**: TypeScript docs | **Version**: Available since TS 4.1 | **License**: Apache 2.0

#### Why It Matters

This is the most impactful TypeScript strictness flag **not** included in `strict: true`. By default, `arr[0]` and `obj[key]` are typed as their element type, hiding potential `undefined` crashes at runtime. With `noUncheckedIndexedAccess`, `arr[0]` becomes `string | undefined`, forcing the developer to check existence before use.

The reason this flag was not included in `strict` (see GitHub issue #49169, closed "not_planned") is that it breaks common loop patterns:
```ts
// Without the flag: fine. With it: requires guard.
for (let i = 0; i < arr.length; i++) {
  console.log(arr[i].toUpperCase()); // arr[i] is `string | undefined` with the flag
}
```

Despite this friction, most teams that enable it report zero real problems in practice; the "pain" is in patterns that are already unsafe. It is the single best additional flag after `strict: true`.

#### Quick Start

```json
// tsconfig.json (add alongside strict: true)
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```

#### Before/After Examples

```ts
// BEFORE (default TypeScript)
const config: Record<string, string> = {};
const val = config["key"]; // type: string — WRONG, could be undefined
console.log(val.toUpperCase()); // Silent crash if key missing

// AFTER (noUncheckedIndexedAccess enabled)
const val = config["key"]; // type: string | undefined — CORRECT
if (val !== undefined) {
  console.log(val.toUpperCase()); // Safe
}

// Pattern for arrays with confidence
const arr = [1, 2, 3];
const first = arr[0]; // string | undefined
const safeFirst = arr[0]!; // non-null assertion when you know it exists
```

#### Known Limitations

- **Not in `strict` by design**: The TypeScript team declined to add it to `strict` due to ergonomics (issue #49169)
- **Loop friction**: `for (let i = 0; i < arr.length; i++)` patterns require `arr[i]!` or `?? default`
- **Tuple types**: Tuple element access already typed correctly; minimal impact for tuples

---

### 3.3 exactOptionalPropertyTypes

**What**: TypeScript compiler flag that distinguishes between `{ prop?: string }` and `{ prop?: string | undefined }`
**Site**: TypeScript docs | **Version**: Available since TS 4.4 | **License**: Apache 2.0

#### Why It Matters

Without this flag, TypeScript treats `{ prop?: string }` as equivalent to `{ prop?: string | undefined }`, meaning you can explicitly set `prop: undefined` even on a field typed as `string | undefined`. This causes subtle bugs when merging objects or using APIs that distinguish between "key absent" and "key present with undefined value".

With `exactOptionalPropertyTypes`, assigning `undefined` to an optional property is a type error unless `| undefined` is explicit in the declaration.

#### Quick Start

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

#### Before/After Examples

```ts
// Interface
interface Config {
  timeout?: number; // means: number, or the key is absent
}

// BEFORE (default TypeScript)
const c: Config = { timeout: undefined }; // OK — but semantically wrong

// AFTER (exactOptionalPropertyTypes)
const c: Config = { timeout: undefined }; // ERROR: undefined not assignable to number
const c2: Config = {}; // OK — key is absent
const c3: Config = { timeout: 5000 }; // OK
```

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Value | **High** for APIs with `PUT` vs `PATCH` semantics, object merging |
| Breaking changes | **High** – Many codebases use `prop: undefined` to clear optional values |
| Recommended for | **Later** — Enable after `strict` + `noUncheckedIndexedAccess` are stable |

#### Known Limitations

- **High breakage on existing codebases**: Common pattern of `const update = { field: undefined }` breaks
- **Third-party library incompatibilities**: Many `@types/*` packages not designed for this flag; `skipLibCheck: true` required
- **Pragmatic workaround**: Declare `timeout?: number | undefined` explicitly where you need to assign undefined

---

## 4. Testing

### 4.1 Vitest 3.x

**What**: Next-generation Vite-native test runner with Jest-compatible API, instant HMR watch mode, and built-in TypeScript support
**Site**: [vitest.dev](https://vitest.dev/) | **Version**: 3.x (Jan 2025) | **License**: MIT
**Compat**: TypeScript Built-in, React Yes (@testing-library/react), Next.js Yes, Vite Yes, Node.js 18+

#### Why It Matters

Vitest emerged as the natural successor to Jest for Vite-based and modern Node.js projects. It went from 4.8M to 7.7M weekly npm downloads between Vitest 2 and 3, cementing its position as the dominant choice for new TypeScript projects. The performance advantage is not theoretical: a real-world React component library with 17 test files dropped from 18.7 seconds (Jest) to 1.8 seconds (Vitest), a 10x improvement, driven by Vite's transform pipeline replacing Babel/SWC transpilation.

Vitest 3.x (January 2025) rewrote the reporter system for stability, redesigned the public reporter API, improved the browser mode, and significantly enhanced the monorepo workspace support. Since v3.2.0, the v8 coverage provider uses AST-based remapping, giving identical coverage accuracy to Istanbul at v8 performance levels.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Exceptional** – Zero config; uses Vite's transform (esbuild by default) |
| React/Next.js Support | **Strong** – Works with @testing-library/react; jsdom/happy-dom environments |
| Performance | **Exceptional** – 3–10x faster than Jest on Vite projects; instant watch mode |
| Jest Compatibility | **Strong** – Same `describe/it/expect/vi.*` API; `vi` ≈ `jest` |
| Monorepo Support | **Strong** – Workspace config in v3.x; per-project coverage thresholds |
| ESM Support | **Native** – No `experimental-vm-modules` required |
| Cost | **Free** |
| Ecosystem Maturity | **Growing fast** – 14.3k stars, 7.7M weekly downloads, 550+ contributors |

#### Quick Start

```bash
pnpm add -D vitest @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom
```

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.stories.*", "src/test/**"],
    },
  },
});
```

```ts
// src/test/setup.ts
import "@testing-library/jest-dom";
```

```ts
// Example test: src/components/Button.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
  it("renders with label", () => {
    render(<Button label="Click me" />);
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
  });

  it("calls onClick when clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<Button label="Click me" onClick={handleClick} />);
    await user.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

#### Migrating from Jest

```bash
# 1. Install Vitest
pnpm add -D vitest @vitest/coverage-v8

# 2. Remove Jest packages
pnpm remove jest @types/jest ts-jest babel-jest jest-environment-jsdom

# 3. Replace jest.fn() with vi.fn(), jest.mock with vi.mock (usually find-and-replace)
# 4. Replace jest.config.ts with vitest.config.ts
# 5. Update tsconfig.json: replace @types/jest with vitest/globals (or use globals: true)
```

#### Key Configuration Options

| Option | Purpose | Recommended |
|--------|---------|-------------|
| `environment` | `jsdom`, `happy-dom`, or `node` | `jsdom` for DOM tests |
| `globals: true` | Inject `describe/it/expect` globally (Jest-like) | Yes for migration |
| `coverage.provider` | `v8` or `istanbul` | `v8` (recommended since 3.2.0) |
| `coverage.thresholds` | Fail if coverage drops below | 80%+ lines/functions |
| `workspace` | Define per-project configs in monorepo | Yes for monorepos |
| `pool` | `threads` (default) or `forks` for isolation | `forks` for snapshot tests |

#### Known Limitations

- **Non-Vite projects**: Jest may still be preferred for Express/NestJS projects without Vite
- **CommonJS modules**: ESM-first; CJS dependencies may need `transformIgnorePatterns` equivalent
- **Large test suites**: For 10,000+ tests, Jest's mature worker pool management may be more stable
- **Browser mode**: Vitest browser mode is powerful but adds complexity (Playwright dependency)

---

### 4.2 Jest 30.x

**What**: The original all-in-one JavaScript testing framework from Meta: test runner, assertion library, mock system, and coverage reporter
**Site**: [jestjs.io](https://jestjs.io/) | **Version**: 30.x (June 2025) | **License**: MIT
**Compat**: TypeScript Yes (ts-jest or `@swc/jest`), React Yes, Node.js 18+

#### Why It Matters

Jest remains the most widely deployed JavaScript testing framework with 44,500+ GitHub stars and the longest track record of any JS testing tool. Jest 30, released June 2025, is a major overhaul: it switched to the `unrs-resolver` for module resolution (faster, more standards-compliant), dropped Node 14/16/19/21 support, upgraded `jest-environment-jsdom` from jsdom 21 to 26, removed deprecated matcher aliases (e.g., `toBeCalled` → `toHaveBeenCalled`), and bundled each package into a single file for improved startup performance.

For teams with existing Jest suites — especially on NestJS, Express, or non-Vite frameworks — Jest 30 offers a substantial in-place upgrade. Teams building new Vite/Next.js projects should default to Vitest.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Strong** – via `ts-jest` (slower) or `@swc/jest` (faster) |
| React/Next.js Support | **Strong** – `jest-environment-jsdom` v26, @testing-library/react |
| Performance | **Medium** – Improved in v30; still slower than Vitest for Vite projects |
| ESM Support | **Partial** – Works but requires `--experimental-vm-modules` flag |
| Monorepo Support | **Strong** – `projects` config; per-package jest configs |
| Ecosystem Maturity | **Dominant** – 44.5k stars, 10+ years, extensive plugin ecosystem |
| Cost | **Free** |

#### Quick Start

```bash
pnpm add -D jest @types/jest @swc/jest @swc/core jest-environment-jsdom
```

```ts
// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  testEnvironment: "jsdom",
  transform: {
    "^.+\\.(t|j)sx?$": "@swc/jest",
  },
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  setupFilesAfterFramework: ["@testing-library/jest-dom"],
  coverageProvider: "v8",
  collectCoverageFrom: ["src/**/*.{ts,tsx}", "!src/**/*.stories.*"],
  coverageThreshold: {
    global: { lines: 80, functions: 80, branches: 75 },
  },
};

export default config;
```

#### Jest 30 Migration: Breaking Changes

```bash
# Alias matchers removed — use eslint-plugin-jest autofixer:
npx jscodeshift --transform=jest30-matcher-upgrade src/

# Old                          New
# expect(fn).toBeCalled()   →  expect(fn).toHaveBeenCalled()
# expect(fn).toBeCalledWith  →  expect(fn).toHaveBeenCalledWith()
# expect(() => {}).toThrowError  →  expect(() => {}).toThrow()

# Update snapshots (Google links changed)
npx jest --updateSnapshot
```

#### Key Configuration Options

| Option | Purpose | Recommended |
|--------|---------|-------------|
| `transform` | Set to `@swc/jest` for fast TypeScript transpilation | Always for TS |
| `testEnvironment` | `jsdom` for DOM tests, `node` for pure Node.js | Per project |
| `coverageProvider` | `v8` or `babel` | `v8` for speed |
| `moduleNameMapper` | Path alias resolution (matches tsconfig paths) | Required for aliases |
| `testPathPatterns` | Filter test files (renamed from `testPathPattern` in v30) | CI usage |

#### When to Choose Jest over Vitest

| Scenario | Choose Jest |
|----------|-------------|
| Existing Jest suite (100+ tests) | Migration cost exceeds benefit |
| NestJS / non-Vite project | Vitest's Vite dependency adds overhead |
| Heavy CommonJS dependencies | Jest's CJS handling is more mature |
| Custom reporters / CI integrations | Jest ecosystem is more mature |

#### Known Limitations

- **ESM**: Requires `--experimental-vm-modules` or `@swc/jest`; not as clean as Vitest's native ESM
- **Slower startup**: Jest's architecture is heavier than Vitest's Vite-based transform
- **Deprecated alias removals in v30**: Teams upgrading from v29 must update matcher names across entire codebase

---

### 4.3 Playwright Test 1.x

**What**: Microsoft's end-to-end testing framework supporting Chromium, Firefox, and WebKit with auto-wait, trace viewer, and rich assertions
**Site**: [playwright.dev](https://playwright.dev/) | **Version**: 1.58.x (Mar 2026) | **License**: Apache 2.0
**Compat**: TypeScript Built-in, Next.js Yes (webServer auto-start), React Yes, Node.js 18+

#### Why It Matters

Playwright has become the dominant E2E testing framework, surpassing Cypress in adoption for Next.js projects primarily due to superior multi-browser support (Chromium + Firefox + WebKit), true parallel execution across workers, and native TypeScript. With 70,300+ GitHub stars and Next.js's official test guide built around it, Playwright is the default choice for end-to-end testing in 2026.

Playwright's auto-wait eliminates flaky tests: actions like `page.click()` automatically wait for elements to be actionable (visible, stable, not obscured) without manual `waitFor` calls. The Trace Viewer records a full execution trace with screenshots, network calls, and DOM snapshots, making debugging CI failures dramatically easier. Playwright 1.57 added Chrome for Testing support; 1.58 added the Speedboard feature for identifying slow tests.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| TypeScript Support | **Exceptional** – First-class TS; `playwright.config.ts` native |
| React/Next.js Support | **Exceptional** – `webServer` auto-start; App Router and Pages Router tested |
| Multi-browser | **Exceptional** – Chromium, Firefox, WebKit in single suite |
| Auto-wait | **Exceptional** – Eliminates artificial timeouts |
| Debugging | **Strong** – Trace Viewer, UI Mode, codegen |
| Setup Effort | **Medium** – Browser binaries download (~300 MB) |
| Performance | **Strong** – Parallel workers; sharding for large suites |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** – 70.3k stars, Microsoft-backed, Next.js official integration |

#### Quick Start

```bash
pnpm create playwright@latest
# OR manually:
pnpm add -D @playwright/test
npx playwright install
```

```ts
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "html",

  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],

  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

```ts
// e2e/auth.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("user can log in", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("test@example.com");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL("/dashboard");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("bad@example.com");
    await page.getByLabel("Password").fill("wrong");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.getByRole("alert")).toContainText("Invalid credentials");
  });
});
```

#### Key Configuration Options

| Option | Purpose | Recommended |
|--------|---------|-------------|
| `retries` | Retry failed tests in CI | `2` in CI, `0` locally |
| `workers` | Parallel workers | `1` in CI for stability |
| `trace: "on-first-retry"` | Capture trace on test retry | Always in CI |
| `webServer` | Auto-start dev/preview server | Required for Next.js |
| `baseURL` | Avoid repeating full URL in tests | Always set |
| `devices` | Pre-configured viewport/UA combos | Use for mobile testing |

#### Known Limitations

- **Browser binary size**: ~300 MB download per platform; use `playwright install --with-deps chromium` in CI to download only needed browser
- **Setup time in CI**: Fresh installs slow; cache `~/.cache/ms-playwright` in GitHub Actions
- **Not for unit tests**: Playwright is E2E only; unit tests should use Vitest/Jest + @testing-library/react
- **`_react` selectors removed in v1.58**: Use `getByRole`/`getByLabel`/`getByText` locators instead

---

### 4.4 @testing-library/react

**What**: React DOM testing utilities that encourage testing from the user's perspective via accessible queries
**Site**: [testing-library.com](https://testing-library.com/) | **Version**: 16.x | **License**: MIT
**Compat**: TypeScript Yes, React 18/19 Yes, Vitest Yes, Jest Yes

#### Why It Matters

`@testing-library/react` is the standard React component testing library with 19,600+ GitHub stars. Its guiding principle — "The more your tests resemble the way your software is used, the more confidence they can give you" — drives developers toward accessibility-first selectors (`getByRole`, `getByLabelText`, `getByText`) rather than CSS classes or component internals. Tests written with Testing Library are resilient to refactoring because they don't test implementation details.

Testing Library replaced Enzyme as the React testing standard. It works with both Vitest and Jest, making it framework-agnostic. The `@testing-library/user-event` companion provides realistic user interaction simulation (focus, typing, click sequences) vs. the simpler `fireEvent`.

#### Quick Start

```bash
# With Vitest
pnpm add -D @testing-library/react @testing-library/user-event @testing-library/jest-dom

# With Jest
pnpm add -D @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

```tsx
// src/components/LoginForm.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { LoginForm } from "./LoginForm";

describe("LoginForm", () => {
  it("submits with correct values", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Email"), "user@example.com");
    await user.type(screen.getByLabelText("Password"), "secret");
    await user.click(screen.getByRole("button", { name: "Log in" }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: "user@example.com",
        password: "secret",
      });
    });
  });

  it("shows validation error for empty email", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Log in" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Email is required");
  });
});
```

#### Query Priority (Best Practice)

| Priority | Query | Use When |
|----------|-------|----------|
| 1 (best) | `getByRole` | Element has ARIA role + accessible name |
| 2 | `getByLabelText` | Form elements with `<label>` |
| 3 | `getByPlaceholderText` | Input with placeholder (fallback) |
| 4 | `getByText` | Non-interactive text content |
| 5 | `getByAltText` | Images with `alt` attribute |
| 6 | `getByTitle` | Title attributes |
| 7 (last) | `getByTestId` | When no semantic query works; use `data-testid` |

#### Key Configuration Options

| Option | Purpose |
|--------|---------|
| `render()` options `wrapper` | Wrap component in providers (Router, Context) |
| `screen.debug()` | Print current DOM for debugging |
| `within()` | Scope queries to a DOM subtree |
| `userEvent.setup()` | Recommended over direct `userEvent.*` calls for proper event sequencing |
| `@testing-library/jest-dom` | Adds matchers: `toBeInTheDocument`, `toHaveTextContent`, etc. |

#### Known Limitations

- **No shallow rendering**: Tests always render full DOM (intentional; encourages real integration tests)
- **Async complexity**: React 18 concurrent mode requires `act()` wrapping; async queries use `findBy*` variants
- **Hooks testing**: Use `renderHook` from `@testing-library/react` (built-in since v13)
- **React 19**: Full support in v16+; check for concurrent rendering async patterns

---

## 5. Coverage

### 5.1 @vitest/coverage-v8

**What**: Vitest's native V8-based code coverage provider using Node.js's built-in V8 coverage engine
**Site**: [vitest.dev/guide/coverage](https://vitest.dev/guide/coverage) | **Version**: Bundled with Vitest 3.x | **License**: MIT
**Compat**: TypeScript Yes, Vitest only, Node.js (V8 engine required)

#### Why It Matters

`@vitest/coverage-v8` is the recommended coverage provider for Vitest projects. It collects coverage using V8's built-in engine — no source transformation or instrumentation required. Since Vitest v3.2.0, V8 coverage uses AST-based remapping, achieving identical report accuracy to Istanbul while maintaining V8's performance advantage (lower memory, faster execution, no pre-transpile step).

#### Quick Start

```bash
pnpm add -D @vitest/coverage-v8
```

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.test.*",
        "src/**/*.stories.*",
        "src/test/**",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
});
```

```bash
# Run tests with coverage
pnpm vitest run --coverage

# Watch mode with coverage
pnpm vitest --coverage
```

#### Choosing Between v8 and Istanbul (Vitest)

| Consideration | v8 Provider | istanbul Provider |
|---------------|------------|-----------------|
| Performance | Faster (no pre-transpile) | Slower |
| Memory usage | Lower | Higher |
| Accuracy | Same as istanbul since v3.2.0 | Baseline reference |
| Non-V8 environments | Not supported | Works everywhere |
| Bun/Firefox | Not supported | Use istanbul |

---

### 5.2 c8

**What**: Standalone V8 coverage tool for any Node.js test runner or script
**Site**: [github.com/bcoe/c8](https://github.com/bcoe/c8) | **Version**: 10.x | **License**: ISC
**Compat**: TypeScript (via source maps), Node.js native test runner, any test framework

#### Why It Matters

c8 wraps Node.js's V8 coverage engine and works with any test runner, not just Vitest. It's ideal for pure Node.js scripts, the built-in `node:test` runner, or mixed test setups that don't use a full test framework. c8 is ~3–5x faster than nyc for large codebases because it requires no source instrumentation.

#### Quick Start

```bash
pnpm add -D c8
```

```json
// package.json
{
  "scripts": {
    "test:coverage": "c8 --reporter=html --reporter=text --branches=80 node --test tests/**/*.test.js"
  },
  "c8": {
    "include": ["src/**/*.{js,ts}"],
    "exclude": ["tests/**", "**/*.test.*"],
    "reporter": ["text", "html", "lcov"],
    "branches": 80,
    "functions": 80,
    "lines": 80
  }
}
```

#### Known Limitations

- **Vitest users**: Use `@vitest/coverage-v8` instead (better integration and accuracy)
- **Non-V8 environments**: Does not work with Bun or Firefox-based runtimes
- **Source maps required**: TypeScript coverage accuracy depends on source maps being correct

---

### 5.3 istanbul/nyc (Legacy)

**What**: The original JavaScript code coverage tool; nyc is the CLI for the istanbul instrumentation library
**Site**: [istanbul.js.org](https://istanbul.js.org/) | **Version**: nyc 17.x | **License**: ISC
**Stars**: 8.8k | **Status**: Maintenance mode — new features go to c8/@vitest/coverage-istanbul

#### Why It Matters (Legacy Context)

Istanbul/nyc was the industry standard for JavaScript coverage from 2012 through ~2020. It instruments source code by injecting coverage counters at transpile time, supporting all JavaScript environments regardless of the runtime engine. The instrumentation approach means it works everywhere (including environments without V8 coverage APIs like Firefox and Bun), but at the cost of slower execution and higher memory usage.

#### Current Status

Istanbul is in maintenance mode. For new projects:
- **Vitest projects**: Use `@vitest/coverage-v8` (or `@vitest/coverage-istanbul` if V8 is unavailable)
- **Jest projects**: Use Jest's built-in `coverageProvider: "v8"` option
- **Standalone Node.js scripts**: Use `c8`
- **Bun/Firefox environments**: Use `@vitest/coverage-istanbul`

If you have an existing nyc setup, it will continue to work but there is no reason to adopt it for new projects.

#### Quick Start (Existing Nyc Users)

```json
// package.json — existing nyc configuration
{
  "nyc": {
    "include": ["src/**/*.{js,ts}"],
    "exclude": ["**/*.test.*", "**/*.spec.*"],
    "reporter": ["text", "html", "lcov"],
    "branches": 80,
    "functions": 80,
    "lines": 80,
    "all": true
  }
}
```

---

## 6. Bundle Analysis

### 6.1 size-limit

**What**: Performance budget tool that calculates the real JavaScript cost (size + load time) for libraries and applications
**Site**: [github.com/ai/size-limit](https://github.com/ai/size-limit) | **Version**: 12.x (Mar 2026) | **License**: MIT
**Compat**: TypeScript Yes, ESM Yes, Rollup/Webpack/esbuild, Node.js 18+

#### Why It Matters

size-limit is the standard tool for enforcing JavaScript bundle budgets on npm packages and web applications. With 6,900+ GitHub stars and 538K weekly npm downloads, it's used by Material-UI, MobX, Ant Design, and PostCSS to prevent size regressions in published packages. It integrates with GitHub Actions to post bundle size changes as PR comments, making size regressions visible before merge.

Unlike `@next/bundle-analyzer` which provides a visual treemap, size-limit enforces a hard budget: CI fails if a bundle exceeds the configured limit. The `--why` flag shows which dependencies are contributing to the size using Statoscope analysis.

#### Quick Start

```bash
pnpm add -D size-limit @size-limit/preset-small-lib
```

```json
// package.json
{
  "scripts": {
    "size": "size-limit",
    "analyze": "size-limit --why"
  },
  "size-limit": [
    {
      "path": "dist/index.js",
      "limit": "10 kB",
      "import": "{ MyComponent }"
    },
    {
      "path": "dist/utils.js",
      "limit": "5 kB"
    }
  ]
}
```

```yaml
# .github/workflows/size.yml
name: Size Check
on: [pull_request]
jobs:
  size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

#### Preset Selection

| Preset | Use Case |
|--------|----------|
| `@size-limit/preset-small-lib` | Small npm libraries (esbuild bundler) |
| `@size-limit/preset-big-lib` | Large libraries needing tree-shaking verification |
| `@size-limit/preset-app` | Web applications with Webpack |

#### Key Configuration Options

| Option | Purpose | Example |
|--------|---------|---------|
| `path` | Entry point(s) to measure | `"dist/index.esm.js"` |
| `limit` | Maximum allowed size | `"10 kB"` |
| `import` | Named export to measure (tree-shaking aware) | `"{ useState }"` |
| `running: false` | Skip JS execution time estimate | Speed up CI |
| `gzip: true` | Measure gzip size (default) | Default |

#### Known Limitations

- **Library-focused**: Primary use case is npm packages; `@next/bundle-analyzer` is better for Next.js page-level analysis
- **Build output required**: Must build the library first before running size check
- **Not a treemap**: Use `--why` + Statoscope for visual breakdown; `@next/bundle-analyzer` for page-level treemaps

---

### 6.2 @next/bundle-analyzer

**What**: Webpack bundle analyzer integration for Next.js that generates interactive treemap visualizations of page bundles
**Site**: [npmjs.com/package/@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer) | **Version**: Matches Next.js (16.x) | **License**: MIT
**Compat**: Next.js only (Webpack bundler), TypeScript Yes, App Router and Pages Router

#### Why It Matters

`@next/bundle-analyzer` exposes the full bundle composition of every Next.js page and route, making it possible to identify why a specific page is large — whether due to a heavy dependency, duplicate code, or missing code splitting. It generates three HTML reports: one for the browser bundle, one for the Node.js server bundle, and one for the Edge runtime bundle.

Next.js 16.1+ also introduced an experimental Turbopack bundle analyzer (`npx next experimental-analyze`) with import chain tracing — a more powerful successor that works with Turbopack. Use `@next/bundle-analyzer` for stable Webpack-based analysis and the experimental command for Turbopack projects.

#### Quick Start

```bash
pnpm add -D @next/bundle-analyzer
```

```ts
// next.config.ts
import type { NextConfig } from "next";
import withBundleAnalyzer from "@next/bundle-analyzer";

const bundleAnalyzer = withBundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
  openAnalyzer: false,
});

const nextConfig: NextConfig = {
  // your Next.js config
};

export default bundleAnalyzer(nextConfig);
```

```json
// package.json
{
  "scripts": {
    "build:analyze": "ANALYZE=true pnpm build"
  }
}
```

```bash
# Run analysis — opens three HTML files in analyze/ directory
pnpm build:analyze
# Reports:
# analyze/client.html    — browser bundle
# analyze/nodejs.html    — server bundle
# analyze/edge.html      — edge runtime bundle
```

#### Turbopack Bundle Analyzer (Experimental, v16.1+)

```bash
# New experimental command for Turbopack-based Next.js projects
npx next experimental-analyze

# Save output for diffing/sharing
npx next experimental-analyze --output
```

#### Key Use Cases

| Scenario | Action |
|----------|--------|
| Page is too large | Open `client.html`, find the page, identify large modules |
| Dependency appears twice | Search for duplicate package names in treemap |
| Server-only code in browser | Check `client.html` for `node_modules` server packages |
| Edge runtime bloat | Open `edge.html`; edge bundles should be minimal |

#### Known Limitations

- **Webpack only**: Requires `next build` with Webpack; does not work with `--turbopack`
- **No budget enforcement**: Visualization only; use `size-limit` for CI budget gates
- **Per-build only**: Run manually as needed; not suitable for every PR check (slow build)
- **Next.js only**: Cannot be used with Vite, Remix, or other frameworks

---

## 7. Framework-Specific

### 7.1 next lint (eslint-config-next)

**What**: Next.js's built-in ESLint integration providing framework-specific rules, Core Web Vitals checks, and React/Hooks rule sets
**Site**: [nextjs.org/docs/app/api-reference/config/eslint](https://nextjs.org/docs/app/api-reference/config/eslint) | **Version**: Bundled with Next.js 16.x | **License**: MIT
**Compat**: TypeScript Yes, Next.js only, ESLint 9.x (flat config supported)

#### Why It Matters

`eslint-config-next` bundles three essential rule sets for Next.js projects in a single package: `@next/eslint-plugin-next` (framework-specific rules), `eslint-plugin-react` (React rules), and `eslint-plugin-react-hooks` (hooks rules). The `core-web-vitals` config upgrades rules that impact Core Web Vitals metrics from warnings to errors, making them CI-blocking.

The plugin enforces Next.js-specific patterns that generic ESLint + React configs cannot: preventing async Client Components, enforcing `next/image` over `<img>` tags, requiring inline scripts to have IDs, and warning against server component misuse patterns. These are checks that prevent silent performance degradations in production.

#### Quick Start

```bash
pnpm add -D eslint eslint-config-next
```

```js
// eslint.config.mjs (flat config — Next.js 15+)
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTypescript,
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);

export default eslintConfig;
```

```json
// package.json
{
  "scripts": {
    "lint": "next lint",
    "lint:fix": "next lint --fix"
  }
}
```

#### Included Rule Sets

| Config | Rules | When to Use |
|--------|-------|-------------|
| `eslint-config-next` | Base Next.js + React + React Hooks | Minimum baseline |
| `eslint-config-next/core-web-vitals` | Base + Core Web Vitals as errors | Recommended for all projects |
| `eslint-config-next/typescript` | TypeScript-specific rules (via typescript-eslint) | TypeScript projects |

#### Notable `@next/eslint-plugin-next` Rules

| Rule | Severity | What It Catches |
|------|----------|----------------|
| `@next/next/no-img-element` | Error | Unoptimized `<img>` instead of `next/image` |
| `@next/next/no-async-client-component` | Error | Async functions marked `"use client"` |
| `@next/next/no-head-element` | Error | `<head>` in App Router (use `metadata` instead) |
| `@next/next/google-font-preconnect` | Warning | Missing `preconnect` with Google Fonts |
| `@next/next/no-css-tags` | Error | Manual `<link rel="stylesheet">` instead of CSS modules |
| `@next/next/inline-script-id` | Error | Inline `<Script>` without `id` attribute |

#### Key Configuration Options

| Option | Notes |
|--------|-------|
| `next lint --dir .` | Lint all directories (default: `src`, `pages`, `app`, `components`) |
| `next lint --fix` | Auto-fix fixable issues |
| `next lint --file <path>` | Lint specific file (useful in git hooks) |
| `ignoreDuringBuilds: true` | Skip lint during `next build` (if running lint separately in CI) |

#### Known Limitations

- **Legacy config default**: Older Next.js versions create `.eslintrc.json` with legacy config; manually migrate to `eslint.config.mjs` for v9+
- **Flat config only in Next.js 15+**: Ensure you're on Next.js 15+ for native flat config support
- **TypeScript config separate**: Must explicitly extend `eslint-config-next/typescript` for TS rules

---

### 7.2 React Testing Patterns with @testing-library/react

#### Component Test Patterns

```tsx
// Pattern 1: Provider wrapping with custom render
// src/test/utils.tsx
import { render, type RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";

function AllProviders({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) {
  return render(ui, { wrapper: AllProviders, ...options });
}
```

```tsx
// Pattern 2: Testing async data fetching
it("displays user data after loading", async () => {
  server.use(
    http.get("/api/users/1", () => HttpResponse.json({ name: "Alice" }))
  );

  render(<UserProfile userId={1} />);

  // Wait for loading to resolve
  expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
  await waitForElementToBeRemoved(() => screen.queryByTestId("loading-spinner"));
  expect(screen.getByText("Alice")).toBeInTheDocument();
});
```

```tsx
// Pattern 3: Testing Server Actions (Next.js App Router)
import { renderHook } from "@testing-library/react";

it("server action updates state", async () => {
  const { result } = renderHook(() => useOptimistic([], serverAction));
  // Test optimistic updates
  act(() => result.current.addOptimistic({ id: "1", text: "New item" }));
  expect(result.current.optimisticItems).toHaveLength(1);
});
```

---

## 8. Dependency Management Integration

### Git Hook Configuration (Lefthook)

For Node.js-only projects, wire all tools into pre-commit hooks:

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    gitleaks:
      run: gitleaks protect --staged --verbose
      skip:
        - merge
        - rebase

    eslint:
      glob: "**/*.{ts,tsx,js,jsx}"
      run: npx eslint --fix {staged_files}
      stage_fixed: true

    prettier:
      glob: "**/*.{ts,tsx,js,jsx,json,css,md,yml}"
      run: npx prettier --write {staged_files}
      stage_fixed: true

    typecheck:
      glob: "**/*.{ts,tsx}"
      run: npx tsc --noEmit
```

### CI/CD Integration

```yaml
# .github/workflows/quality.yml
name: Quality Checks
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"

      - run: pnpm install --frozen-lockfile
      - run: pnpm run typecheck       # tsc --noEmit
      - run: pnpm run lint            # eslint .
      - run: pnpm run format:check    # prettier --check .
      - run: pnpm run test:coverage   # vitest run --coverage
      - run: pnpm run test:e2e        # playwright test (optional)

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps chromium
      - run: pnpm run test:e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 9. Migration Paths Summary

### ESLint Legacy → Flat Config

1. Run `npx @eslint/migrate-config .eslintrc.json` to auto-migrate
2. Delete `.eslintrc.*` and `.eslintignore` (move ignores into `eslint.config.mjs`)
3. Update plugins that export flat config (most major plugins updated by 2025)
4. For plugins without flat config support: use `@eslint/eslintrc` compat wrapper
5. Verify with `npx eslint --inspect-config`

### Jest → Vitest

1. `pnpm add -D vitest @vitest/coverage-v8`
2. `pnpm remove jest @types/jest ts-jest babel-jest jest-environment-jsdom`
3. Create `vitest.config.ts` mirroring `jest.config.ts` settings
4. Replace `jest.fn()` with `vi.fn()`, `jest.mock` with `vi.mock` (global find-replace)
5. Replace `@types/jest` with `vitest/globals` in tsconfig or enable `globals: true`
6. Update setup files: replace `jest.setup.ts` path in vitest config

### Biome Migration from ESLint + Prettier

1. `pnpm add -D --save-exact @biomejs/biome`
2. `npx @biomejs/biome migrate eslint --write` (migrates `.eslintrc.*`)
3. `npx @biomejs/biome migrate prettier --write` (migrates `.prettierrc`)
4. Review `biome.json` for rule gaps (complex ESLint plugins may not have Biome equivalents)
5. Remove old packages: `pnpm remove eslint prettier eslint-config-prettier ...`
6. Update pre-commit hooks to use `biome check --write`

---

## References

### Official Documentation

- **ESLint**: [eslint.org/docs/latest/use/configure/configuration-files](https://eslint.org/docs/latest/use/configure/configuration-files)
- **typescript-eslint**: [typescript-eslint.io/getting-started](https://typescript-eslint.io/getting-started) — Flat config setup guide
- **Biome**: [biomejs.dev](https://biomejs.dev/) — v2 documentation including GritQL plugins
- **Biome v2 announcement**: [biomejs.dev/blog/biome-v2](https://biomejs.dev/blog/biome-v2) — Type inference details
- **Prettier**: [prettier.io/docs](https://prettier.io/docs/) — Options reference
- **Vitest**: [vitest.dev/guide](https://vitest.dev/guide/) — Getting started
- **Vitest 3.0 announcement**: [main.vitest.dev/blog/vitest-3](https://main.vitest.dev/blog/vitest-3)
- **Jest 30 announcement**: [jestjs.io/blog/2025/06/04/jest-30](https://jestjs.io/blog/2025/06/04/jest-30)
- **Jest 30 migration guide**: [jestjs.io/docs/upgrading-to-jest30](https://jestjs.io/docs/upgrading-to-jest30)
- **Playwright**: [playwright.dev/docs/intro](https://playwright.dev/docs/intro)
- **Next.js + Playwright**: [nextjs.org/docs/pages/guides/testing/playwright](https://nextjs.org/docs/pages/guides/testing/playwright)
- **@testing-library/react**: [testing-library.com/docs/react-testing-library/intro](https://testing-library.com/docs/react-testing-library/intro)
- **Vitest coverage guide**: [vitest.dev/guide/coverage](https://vitest.dev/guide/coverage)
- **size-limit**: [github.com/ai/size-limit](https://github.com/ai/size-limit)
- **@next/bundle-analyzer**: [npmjs.com/package/@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)
- **Next.js ESLint config**: [nextjs.org/docs/app/api-reference/config/eslint](https://nextjs.org/docs/app/api-reference/config/eslint)
- **Next.js bundle analysis**: [nextjs.org/docs/app/guides/package-bundling](https://nextjs.org/docs/app/guides/package-bundling)

### TypeScript Strictness

- **TypeScript Handbook - Strict Mode**: [typescriptlang.org/tsconfig#strict](https://www.typescriptlang.org/tsconfig#strict)
- **noUncheckedIndexedAccess**: [typescriptlang.org/tsconfig#noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess)
- **exactOptionalPropertyTypes**: [typescriptlang.org/tsconfig#exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig#exactOptionalPropertyTypes)
- **@tsconfig/strictest**: [npmjs.com/package/@tsconfig/strictest](https://www.npmjs.com/package/@tsconfig/strictest) — Community strictest tsconfig base
- **GitHub issue #49169**: [github.com/microsoft/TypeScript/issues/49169](https://github.com/microsoft/TypeScript/issues/49169) — Why noUncheckedIndexedAccess is not in strict

### Benchmarks and Comparisons

- **Biome vs ESLint+Prettier (Better Stack, Oct 2025)**: [betterstack.com/community/guides/scaling-nodejs/biome-eslint](https://betterstack.com/community/guides/scaling-nodejs/biome-eslint)
- **Vitest vs Jest (2025 guide)**: [betterstack.com/community/guides/scaling-nodejs/vitest-vs-jest](https://betterstack.com/community/guides/scaling-nodejs/vitest-vs-jest)
- **c8 vs nyc vs Istanbul (2026)**: [pkgpulse.com/blog/c8-vs-nyc-vs-istanbul-javascript-code-coverage-2026](https://www.pkgpulse.com/blog/c8-vs-nyc-vs-istanbul-javascript-code-coverage-2026)
