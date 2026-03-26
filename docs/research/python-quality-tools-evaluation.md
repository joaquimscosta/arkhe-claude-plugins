---
title: "Python Quality Tools Evaluation"
version: "1.0.0"
status: Published
created: 2026-03-25
last_updated: 2026-03-25
---

# Python Quality Tools Evaluation

## A Practitioner's Guide for Modern Python Projects

> **Python baseline**: 3.12+ | **Package manager**: uv (recommended), pip, Poetry
>
> This guide evaluates 20 tools across eight categories for Python teams building
> production systems with Django, FastAPI, Flask, or data science workloads. Every tool
> listed is free or has a meaningful free tier. Configuration is shown in pyproject.toml
> format throughout, the modern standard for Python tooling.

---

## Executive Summary

### Tool Landscape at a Glance

| Tool | Category | Version | Python 3.12+ | Django | FastAPI | Flask | Cost | Stars |
|------|----------|---------|--------------|--------|---------|-------|------|-------|
| **Ruff (linter)** | Linting | 0.11.x | Yes | Yes | Yes | Yes | Free | 46k |
| **Flake8** | Linting | 7.3.0 | Yes | Yes | Yes | Yes | Free | 3.8k |
| **Pylint** | Linting | 4.0.5 | Yes | Plugin | Yes | Yes | Free | 5.7k |
| **Ruff (formatter)** | Formatting | 0.11.x | Yes | Yes | Yes | Yes | Free | 46k |
| **Black** | Formatting | 26.3.1 | Yes | Yes | Yes | Yes | Free | 41.4k |
| **isort** | Formatting | 8.0.1 | Yes | Yes | Yes | Yes | Free | 6.9k |
| **mypy** | Type Checking | 1.19.x | Yes | Plugin | Yes | Yes | Free | 20.3k |
| **Pyright** | Type Checking | 1.1.408 | Yes | Partial | Yes | Yes | Free | 15.3k |
| **pytest** | Testing | 9.0.2 | Yes | Plugin | Yes | Yes | Free | 13.7k |
| **Hypothesis** | Testing | 6.131.x | Yes | Yes | Yes | Yes | Free | 7.4k |
| **pytest-cov** | Coverage | 7.1.0 | Yes | Yes | Yes | Yes | Free | 1.7k |
| **coverage.py** | Coverage | 7.8.x | Yes | Yes | Yes | Yes | Free | 3.1k |
| **bandit** | Security | 1.7.9 | Yes | Yes | Yes | Yes | Free | 7.8k |
| **pip-audit** | Security | 2.9.x | Yes | Yes | Yes | Yes | Free | 1.2k |
| **safety** | Security | 3.x | Yes | Yes | Yes | Yes | Freemium | 1.7k |
| **Nox** | Task Runners | 2026.2.9 | Yes | Yes | Yes | Yes | Free | 1.5k |
| **tox** | Task Runners | 4.25.x | Yes | Yes | Yes | Yes | Free | 3.9k |
| **uv** | Dependency Mgmt | 0.6.10 | Yes | Yes | Yes | Yes | Free | 81.2k |
| **pip** | Dependency Mgmt | 25.x | Yes | Yes | Yes | Yes | Free | Built-in |
| **Poetry** | Dependency Mgmt | 2.1.x | Yes | Yes | Yes | Yes | Free | 33k |

### Recommended Starting Sets

#### Small FastAPI/Flask Team (1-5 developers)

| Layer | Tool | Why |
|-------|------|-----|
| Linting + Formatting | Ruff (both modes) | Single Rust binary replaces Flake8 + Black + isort; 10-100x faster |
| Type Checking | mypy (strict) | Catches `None` dereferences before async handlers fail at runtime |
| Testing | pytest + pytest-asyncio | Native async support, fixtures-first; ASGI TestClient via httpx |
| Coverage | pytest-cov | Single flag `--cov`; HTML report in one command |
| Security | bandit + pip-audit | SAST for code patterns + SCA for vulnerable dependencies |
| Dependency Mgmt | uv | 10-100x faster than pip; lockfile; Python version management built in |

#### Django Team (5-20 developers)

| Layer | Tool | Why |
|-------|------|-----|
| Linting + Formatting | Ruff | Understands Django ORM patterns; replaces multi-tool pre-commit chains |
| Type Checking | mypy + django-stubs | django-stubs provides typed ORM, views, forms |
| Testing | pytest + pytest-django | DB fixtures, `@pytest.mark.django_db`, transactional rollback |
| Coverage | pytest-cov (branch=True) | Branch coverage catches missing ORM edge cases |
| Security | bandit + pip-audit | Detects Django security misconfigurations (DEBUG=True, weak SECRET_KEY) |
| Property Testing | Hypothesis | Generate model instances to fuzz Django form validators |
| Task Runner | Nox | Matrix testing across Django LTS + latest versions |
| Dependency Mgmt | uv | Workspace support for monorepo (API + worker + admin) |

#### Data Science / ML Team

| Layer | Tool | Why |
|-------|------|-----|
| Linting | Ruff (selective rules) | Skip D-series docstring rules; enable PD (pandas-vet) rules |
| Formatting | Ruff formatter | Handles Jupyter notebooks natively since Ruff 0.6.0 |
| Type Checking | Pyright | Faster incremental checks; better numpy/pandas stub inference |
| Testing | pytest + Hypothesis | Property-based tests for numerical invariants (e.g., non-negative loss) |
| Coverage | pytest-cov | Exclude notebook cells, focus on library code |
| Security | pip-audit | Dependency CVE scanning; critical for supply-chain in ML infra |
| Dependency Mgmt | uv | Handles complex numpy/PyTorch version constraints; conda interop via pip |

#### Library / Package Author

| Layer | Tool | Why |
|-------|------|-----|
| Linting | Ruff (ALL rules minus noise) | Enforces public API hygiene; detects shadowed builtins |
| Formatting | Ruff formatter | Black-compatible output; no separate Black dependency |
| Type Checking | mypy + Pyright (both) | Validate stubs/py.typed; catch divergence between checkers |
| Testing | pytest | Plugin ecosystem; parametrize for multiple Python versions |
| Property Testing | Hypothesis | Fuzz public API with edge-case inputs |
| Coverage | pytest-cov (fail-under=90) | Gate releases on coverage threshold |
| Task Runner | Nox | Test matrix: Python 3.10 / 3.11 / 3.12 / 3.13; docs build; publish |
| Dependency Mgmt | uv + pip-tools for sdist | uv for development; pip-compatible sdist for users |
| Security | pip-audit | Pre-release dependency audit |

---

## 1. Linting

### 1.1 Ruff (Linter Mode)

**What**: Extremely fast Python linter written in Rust that implements 800+ rules from Flake8, isort, pyupgrade, pydocstyle, and others
**Site**: [astral.sh/ruff](https://astral.sh/ruff) | **Version**: 0.11.x (Mar 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes (quoted by FastAPI creator), Flask Yes

#### Why It Matters

Ruff has emerged as the fastest-growing Python linter in history, reaching 46k GitHub stars in roughly 2.5 years. Written in Rust by the Astral team (also creators of uv), it is 10-100x faster than Flake8 and Pylint on identical rule sets — linting the CPython codebase from scratch in milliseconds where Flake8 takes tens of seconds. Its design as a drop-in replacement for Flake8, isort, pyupgrade, and more means a pre-commit hook that previously took 18 seconds for a 50k-line codebase now completes in under 0.5 seconds.

In 2026, Ruff has achieved near-universal adoption: it is the default linter in FastAPI, SQLModel, Pydantic, Pandas, NumPy, SciPy, and hundreds of other major projects. The tool also supports both linting (`ruff check`) and formatting (`ruff format`), making it a single dependency that can replace an entire multi-tool linting pipeline.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support; Ruff targets Python 3.13+ syntax |
| Django Integration | **Strong** - Works on all Django code; DJ-specific rules via djlint community |
| FastAPI Integration | **Excellent** - FastAPI creator Sebastián Ramírez is a vocal advocate |
| Flask Integration | **Strong** - No framework-specific rules needed |
| Setup Effort | **Very Low** - `uv add --dev ruff` + 5-line pyproject.toml section |
| Performance | **Exceptional** - 10-100x faster than Flake8; entire CPython in milliseconds |
| Rule Coverage | **Excellent** - 800+ rules from 30+ source linters |
| Auto-fix | **Strong** - 68% of violations auto-fixable with `--fix` |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 46k stars; trusted by NumPy, Pandas, FastAPI, SQLModel |

#### Quick Start

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88
indent-width = 4
exclude = [".venv", "__pycache__", "migrations", "build", "dist"]

[tool.ruff.lint]
# Recommended base ruleset: pyflakes + pycodestyle errors + isort + bugbear
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes (unused imports, undefined names)
    "I",   # isort (import ordering)
    "B",   # flake8-bugbear (likely bugs, design problems)
    "UP",  # pyupgrade (use modern Python syntax)
    "S",   # bandit security rules (optional; overlap with bandit tool)
    "RUF", # Ruff-specific rules
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "B008",   # function call in argument defaults (common in FastAPI)
    "S101",   # use of assert (common in tests)
]
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.isort]
known-first-party = ["myapp"]
force-sort-within-sections = true

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "S105", "S106"]  # allow assert + hardcoded passwords in tests
"**/migrations/*.py" = ["E501", "RUF012"]   # Django migrations
```

```bash
# CLI usage
ruff check .                     # lint all files
ruff check --fix .               # auto-fix fixable violations
ruff check --diff .              # show what --fix would change
ruff check --select E,F .        # run specific rule categories
ruff rule E501                   # explain a specific rule
ruff linter                      # list all supported upstream linters
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `target-version` | Python version for syntax rules | `"py310"` |
| `line-length` | Maximum line length | `88` (Black-compatible) |
| `select` | Rules to enable | `["E4", "E7", "E9", "F"]` |
| `ignore` | Rules to disable | `[]` |
| `fixable = ["ALL"]` | Allow all auto-fixes | Limited set |
| `per-file-ignores` | Per-path rule overrides | `{}` |
| `extend-select = ["B"]` | Add rules without replacing defaults | N/A |
| `preview = true` | Enable preview rules | `false` |

#### Known Limitations

- Ruff is not a full replacement for Pylint's deep inference engine — Pylint tracks value flow across function calls in ways Ruff does not
- Security rules (S-prefix) overlap with Bandit but are less comprehensive; use both for security-critical code
- Some esoteric Flake8 plugins (e.g., flake8-rst-docstrings) have no Ruff equivalent yet
- The `--fix` flag is irreversible — always use `--diff` first in CI for review
- Configuration format changed significantly between v0.1.x and v0.4.x; check migration guide for upgrades

#### Migration from Flake8

```bash
# Step 1: Install Ruff
uv add --dev ruff

# Step 2: Use Ruff's migration helper
ruff check --select ALL . 2>&1 | head -50  # discover what rules match

# Step 3: Remove Flake8 and plugins
uv remove flake8 flake8-bugbear flake8-isort flake8-comprehensions

# Step 4: Map Flake8 config to Ruff (setup.cfg or .flake8)
# [flake8] max-line-length = 88  ->  [tool.ruff] line-length = 88
# [flake8] ignore = E501,W503    ->  [tool.ruff.lint] ignore = ["E501", "W503"]
```

---

### 1.2 Flake8

**What**: Lightweight Python linting wrapper combining PyFlakes, pycodestyle, and McCabe complexity
**Site**: [flake8.pycqa.org](https://flake8.pycqa.org/) | **Version**: 7.3.0 (Jun 2025) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Flake8 remains the most widely-deployed Python linter in existing codebases, particularly in projects started before 2023. Its extensive plugin ecosystem (600+ plugins) covers specialized rules that Ruff has not yet replicated. However, Flake8's Python-based implementation runs 18x slower than Ruff on identical rule sets. For teams on existing Flake8 setups, migration to Ruff is straightforward and strongly recommended. For greenfield projects, Ruff should be chosen directly.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Supports Python 3.14 since v7.3.0 |
| Django Integration | **Strong** - Extensive plugin ecosystem including flake8-django |
| FastAPI Integration | **Medium** - No async-specific rules; works generically |
| Setup Effort | **Low** - Single pip install; `.flake8` config file |
| Performance | **Slow** - 18x slower than Ruff; ~51 seconds for 187k LOC benchmark |
| Rule Coverage | **Medium** - ~100 built-in rules; plugins extend significantly |
| Auto-fix | **None** - No built-in auto-fix; requires autopep8 separately |
| Cost | **Free** |
| Ecosystem Maturity | **Stable** - 3.8k stars; actively maintained; large plugin ecosystem |

#### Quick Start

```toml
# pyproject.toml (Flake8 does NOT natively read pyproject.toml; use .flake8 file)
```

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    migrations
per-file-ignores =
    tests/*: S101
max-complexity = 10
```

```bash
# CLI usage
flake8 .                         # lint all files
flake8 --select E,F src/         # specific rules
flake8 --max-line-length 120 .   # override line length
flake8 --count .                 # show error count summary
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `max-line-length` | Maximum line length | `79` (PEP 8) |
| `extend-ignore` | Additional codes to ignore | `""` |
| `max-complexity` | McCabe complexity threshold | Off |
| `per-file-ignores` | Per-file rule overrides | `""` |
| `exclude` | Directories/files to skip | Standard set |

#### Known Limitations

- Does not read `pyproject.toml` natively (requires `Flake8-pyproject` plugin)
- No built-in auto-fix capability
- Single-threaded; noticeably slow on large codebases
- Plugin compatibility issues when combining incompatible plugins
- **Recommended action**: Migrate to Ruff for new and existing projects

---

### 1.3 Pylint

**What**: Deep static code analyser using AST inference to detect bugs, enforce coding standards, and identify code smells
**Site**: [pylint.readthedocs.io](https://pylint.readthedocs.io/) | **Version**: 4.0.5 (Feb 2026) | **License**: GPL-2.0
**Compat**: Python 3.12+ Yes (3.10+ required to run), Django via plugin, FastAPI Yes, Flask Yes

#### Why It Matters

Pylint's distinguishing capability is its inference engine: it tracks actual values across function calls, resolving imports and type flows that neither Flake8 nor Ruff attempt. This means `import logging as argparse; argparse.error(...)` is correctly identified as a logging call. This depth catches real bugs in complex codebases that other linters miss entirely, at the cost of significant runtime (120 seconds on a 1,000-file benchmark where Ruff takes 3.5 seconds).

In 2026, most Pylint users are migrating to Ruff for the 800+ overlap rules, keeping Pylint only for the subset of deep-inference checks that have no Ruff equivalent. The Pylint maintainers themselves recommend using Ruff alongside Pylint.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Requires Python 3.10+ to run |
| Django Integration | **Medium** - Requires pylint-django plugin |
| FastAPI Integration | **Medium** - No async-specific inference yet |
| Setup Effort | **Medium** - Config can be complex; `.pylintrc` or pyproject.toml |
| Performance | **Poor** - 120 seconds for 1,000 files; memory-intensive |
| Rule Coverage | **Deep** - 200+ checks with value inference; fewer surface rules |
| Auto-fix | **None** - No auto-fix |
| Cost | **Free** |
| Ecosystem Maturity | **Stable** - 5.7k stars; 15+ years; plugin ecosystem |

#### Quick Start

```toml
# pyproject.toml
[tool.pylint.main]
py-version = "3.12"
jobs = 4                    # parallel analysis
suggestion-mode = true

[tool.pylint.messages_control]
disable = [
    "C0111",  # missing-docstring (use D-rules in Ruff instead)
    "C0301",  # line-too-long (handled by Ruff/Black)
    "W0511",  # fixme
    "R0903",  # too-few-public-methods
]
enable = [
    "useless-suppression",
]

[tool.pylint.design]
max-args = 10
max-attributes = 10
max-bool-expr = 5
max-branches = 15
max-locals = 20
max-returns = 6
```

```bash
# CLI usage
pylint src/                      # analyse a package
pylint --errors-only src/        # only show errors (good for adoption)
pylint --disable=C,R src/        # disable conventions and refactoring
pylint --generate-toml-config    # generate pyproject.toml config section
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `jobs` | Parallel workers | `1` |
| `errors-only` | Only report errors | Off |
| `disable` | Message codes to suppress | Many |
| `max-line-length` | Line length limit | `100` |
| `py-version` | Target Python version | Auto |
| `load-plugins` | Plugin modules to load | None |

#### Known Limitations

- Extremely slow: 2 minutes for 1,000 files vs. 3.5 seconds for Ruff
- High false-positive rate without tuning (requires `.pylintrc` iteration)
- Django plugin (`pylint-django`) must be explicitly loaded and sometimes lags behind Django releases
- Does not produce auto-fixes
- GPL-2.0 license may affect corporate usage policies

---

## 2. Formatting

### 2.1 Ruff (Formatter Mode)

**What**: Black-compatible Python formatter built into the Ruff tool, written in Rust
**Site**: [astral.sh/ruff](https://astral.sh/ruff) | **Version**: 0.11.x (Mar 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

The Ruff formatter achieves >99.9% Black compatibility while running 30x faster than Black and 100x faster than YAPF. Teams already using Ruff for linting get formatting for free — no second tool to install, no second config section, no second pre-commit hook. Jupyter notebooks are formatted natively since Ruff 0.6.0.

The formatter's design explicitly targets Black-formatted projects as migration targets: running `ruff format` on a Black-formatted codebase should produce zero diffs in the vast majority of cases. The Ruff and Black teams coordinate on style changes to maintain this compatibility.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full Python 3.13 syntax support |
| Black Compatibility | **Excellent** - >99.9% compatible; coordinated style updates |
| Jupyter Notebook Support | **Strong** - Native since Ruff 0.6.0 |
| Setup Effort | **Zero** - Already included with Ruff installation |
| Performance | **Exceptional** - 30x faster than Black; 100x faster than YAPF |
| Configurability | **Low** - By design; matches Black's philosophy |
| Cost | **Free** |

#### Quick Start

```toml
# pyproject.toml — Ruff formatter configuration
[tool.ruff.format]
quote-style = "double"              # or "single"
indent-style = "space"              # or "tab"
skip-magic-trailing-comma = false   # preserve trailing commas
line-ending = "auto"                # or "lf", "cr-lf", "cr"
docstring-code-format = true        # format code in docstrings
docstring-code-line-length = "dynamic"  # or integer
```

```bash
# CLI usage
ruff format .                    # format all files in-place
ruff format --check .            # check without modifying (CI mode)
ruff format --diff .             # show what would change
ruff format src/ tests/          # specific directories

# Run both lint and format in CI
ruff check . && ruff format --check .
```

---

### 2.2 Black

**What**: The uncompromising Python code formatter — opinionated, deterministic, zero-config
**Site**: [black.readthedocs.io](https://black.readthedocs.io/) | **Version**: 26.3.1 (Mar 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes (requires Python 3.10+ to run), Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Black pioneered the "no-config formatter" philosophy for Python, ending style debates by making formatting non-negotiable. With 41k GitHub stars and adoption by CPython, Django, SQLAlchemy, Requests, and thousands of other projects, it is the de facto Python formatting standard. Black's stability guarantee (the "stable" style rarely changes) makes it safe for large codebases.

For teams not yet using Ruff, Black remains the gold standard. For teams already on Ruff, the formatter mode makes Black redundant — but Black's reputation and maturity justify keeping it as a comparison reference.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Supports all current Python versions |
| Opinionated Style | **Excellent** - Eliminates formatting debates entirely |
| Jupyter Support | **Strong** - `pip install "black[jupyter]"` |
| Setup Effort | **Very Low** - `uv add --dev black`; works with zero config |
| Performance | **Slow** - 30x slower than Ruff formatter on identical inputs |
| Configurability | **Very Low** - By design; only `line-length` and target version |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 41.4k stars; 450 contributors; PSF-backed |

#### Quick Start

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ["py312"]
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | .venv
)/
'''
```

```bash
# CLI usage
black .                          # format all Python files in-place
black --check .                  # CI mode: exit code 1 if any changes needed
black --diff .                   # show what would change
black --line-length 100 src/     # override line length
```

#### Known Limitations

- 30x slower than Ruff formatter (noticeable in CI on large codebases)
- Minimal configuration means no escape from its style choices
- Line length of 88 is a convention, not PEP 8 default (79)
- `# fmt: off` blocks allow bypassing but indicate design pressure
- **Recommended path**: Keep if already using; for new projects, prefer Ruff formatter

---

### 2.3 isort

**What**: Python utility that automatically sorts and organizes import statements by section and alphabetically
**Site**: [pycqa.github.io/isort](https://pycqa.github.io/isort/) | **Version**: 8.0.1 (Feb 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes (requires Python 3.10+), Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Consistent import ordering reduces diff noise in code review. isort has been the standard import sorter for a decade, with 6.9k GitHub stars and 100M+ monthly PyPI downloads. However, the `I` rule group in Ruff implements the same functionality via isort's own algorithm — teams using Ruff should enable `select = ["I"]` instead of installing isort separately.

isort v8.0.0 (Feb 2026) dropped Python 3.8/3.9 support and requires Python 3.10+ to run, aligning with modern baselines.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Black Compatibility | **Strong** - `profile = "black"` setting for zero conflicts |
| Setup Effort | **Low** - `uv add --dev isort` + profile config |
| Performance | **Adequate** - Python-based; slower than Ruff `I` rules |
| Standalone Value | **Low (if using Ruff)** - Ruff `I` rules provide identical functionality |
| Cost | **Free** |
| Ecosystem Maturity | **Mature** - 6.9k stars; 300 contributors; 100M+ monthly downloads |

#### Quick Start

```toml
# pyproject.toml
[tool.isort]
profile = "black"                # critical for Black/Ruff formatter compatibility
line_length = 88
known_first_party = ["myapp", "mylib"]
known_third_party = ["django", "fastapi", "flask"]
skip = [".venv", "migrations"]
```

```bash
# CLI usage
isort .                          # sort imports in-place
isort --check-only .             # CI mode
isort --diff .                   # preview changes

# If using Ruff, replace isort entirely:
# Add "I" to ruff.lint.select and remove isort from dependencies
```

#### Known Limitations

- Entirely superseded by Ruff's `I` rule group for teams using Ruff
- Black compatibility requires `profile = "black"` — easy to forget
- Slower than Ruff at the same import-sorting task
- **Recommended path**: Remove isort and enable `select = ["I"]` in Ruff

---

## 3. Type Checking

### 3.1 mypy (Strict Mode)

**What**: The original Python static type checker; the reference implementation of PEP 484 type annotations
**Site**: [mypy-lang.org](https://www.mypy-lang.org/) | **Version**: 1.19.0 (Nov 2025) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django via django-stubs, FastAPI Yes, Flask Yes

#### Why It Matters

mypy is the type checker that shaped Python's entire typing ecosystem, collaborating directly with Guido van Rossum and the core typing committee. It is used in CI by CPython itself, Django, SQLAlchemy, and nearly every major Python project. Strict mode (`--strict`) enables a full suite of checks that eliminate an entire class of `None` dereference, wrong-argument-type, and missing-return bugs.

In March 2026 benchmarks, mypy achieves 58.3% conformance with the Python typing specification's official test suite — lower than Pyright (97.8%) but this reflects mypy's conservative approach to edge cases rather than fundamental incompetence. For practical codebases, mypy strict mode remains the most common choice in CI pipelines.

mypy 1.19 introduced performance improvements to type alias processing and SCC (strongly-connected component) logic, and the new binary fixed-format cache system significantly accelerates incremental runs.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support for Python 3.12/3.13 typing features |
| Django Integration | **Excellent** - django-stubs provides typed ORM, views, forms, middleware |
| FastAPI Integration | **Strong** - FastAPI is typed throughout; no stubs required |
| Flask Integration | **Medium** - flask-stubs available; less comprehensive than django-stubs |
| Strict Mode | **Excellent** - `--strict` enables all checks including disallow-untyped |
| Performance | **Medium** - Slower than Pyright; incremental cache helps significantly |
| False Positive Rate | **Medium** - 231 false positives per 1K-file test in 2026 benchmark |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 20.3k stars; 420 contributors; Python community-led |

#### Quick Start

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true                       # enables all strict checks

# Strict mode is equivalent to enabling all of these:
# warn_unused_configs = true
# disallow_any_generics = true
# disallow_subclassing_any = true
# disallow_untyped_calls = true
# disallow_untyped_defs = true
# disallow_incomplete_defs = true
# check_untyped_defs = true
# disallow_untyped_decorators = true
# warn_redundant_casts = true
# warn_unused_ignores = true
# warn_return_any = true
# no_implicit_reexport = true
# strict_equality = true

# Practical overrides
ignore_missing_imports = true       # for third-party libraries without stubs
warn_return_any = false             # reduce noise when calling untyped APIs
exclude = ["migrations/", ".venv/"]

# Per-module overrides for legacy code
[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false       # allow untyped test helpers
```

```bash
# CLI usage
mypy src/                        # type-check a directory
mypy --strict src/               # strict mode (recommended)
mypy --show-error-codes src/     # show rule codes for suppression
mypy --ignore-missing-imports .  # suppress stub-not-found errors

# For Django projects
pip install django-stubs[compatible-mypy]
mypy --plugins mypy_django_plugin.main src/
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `strict = true` | Enable all strict checks | `false` |
| `python_version` | Target Python version | Current |
| `ignore_missing_imports` | Suppress stub-not-found errors | `false` |
| `plugins` | Load type checker plugins | `[]` |
| `exclude` | Patterns to exclude | `[]` |
| `follow_imports` | Control import following | `"normal"` |
| `cache_dir` | Where to store incremental cache | `.mypy_cache` |

#### Known Limitations

- 58.3% conformance with Python typing spec (vs. 97.8% for Pyright) — more false positives
- Significantly slower than Pyright for large codebases without cache warm-up
- Complex generics and Protocol subclassing can require `cast()` workarounds
- Django stubs sometimes lag behind Django releases
- PEP 747 TypeForm support is experimental in v1.19 (requires `--enable-incomplete-feature=TypeForm`)

---

### 3.2 Pyright

**What**: Microsoft's full-featured, standards-based Python type checker; powers the Pylance VS Code extension
**Site**: [github.com/microsoft/pyright](https://github.com/microsoft/pyright) | **Version**: 1.1.408 (Jan 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Partial (no official stubs), FastAPI Yes, Flask Yes

#### Why It Matters

Pyright leads all Python type checkers in conformance with the Python typing specification at 97.8% (March 2026 benchmark), with only 15 false positives across the entire official test suite. Its incremental analysis engine provides real-time type feedback in VS Code via Pylance, making it the preferred choice for IDE-first workflows. For data science teams, Pyright offers superior inference for NumPy, Pandas, and PyTorch generics through bundled stubs.

As of 2026, a growing number of teams run both mypy (for CI/CD compatibility and Django stubs) and Pyright (for IDE experience), using the two as complementary tools.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Excellent** - Defaults to Python 3.14 since v1.1.407 |
| Typing Spec Conformance | **Excellent** - 97.8% conformance; 15 false positives (2026 benchmark) |
| Django Integration | **Partial** - No official django-stubs; community stubs only |
| FastAPI Integration | **Excellent** - FastAPI typed natively; Pyright understands Pydantic |
| IDE Integration | **Excellent** - Powers Pylance/VS Code natively |
| Performance | **Excellent** - Incremental checks in milliseconds; 3x faster than mypy |
| Strict Mode | **Strong** - `typeCheckingMode = "strict"` for maximum coverage |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 15.3k stars; Microsoft-backed; 140 contributors |

#### Quick Start

```toml
# pyproject.toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"         # or "basic", "standard", "off"
venvPath = "."
venv = ".venv"
include = ["src"]
exclude = ["**/migrations/**", "**/.venv/**"]
reportMissingImports = true
reportMissingTypeStubs = false      # reduce noise for untyped libraries
```

```bash
# CLI usage (install via npm or pip)
pip install pyright
pyright src/                     # type-check
pyright --strict src/            # strict mode via CLI
pyright --outputjson src/        # JSON output for CI integration
pyright --createstub mymodule    # generate stubs for a library

# VS Code: install Pylance extension (includes Pyright)
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `typeCheckingMode` | `"off"`, `"basic"`, `"standard"`, `"strict"` | `"standard"` |
| `pythonVersion` | Target version | Detected |
| `reportMissingImports` | Error on missing imports | `true` |
| `reportMissingTypeStubs` | Error for unstubbed libraries | `false` |
| `reportGeneralTypeIssues` | Report general type errors | `true` |
| `useLibraryCodeForTypes` | Infer types from library source | `true` |
| `venvPath` | Root for virtual environment search | None |

#### Known Limitations

- No official Django stubs — less useful for Django teams vs. mypy+django-stubs
- Strict mode can produce a tsunami of errors on legacy codebases (15-25 per 1K LOC)
- CLI is Node.js-based (installed via npm or pip wrapper) — adds toolchain complexity
- Pyright strict and mypy strict are not 100% equivalent; running both can surface mypy-only issues
- Licensing notes: MIT license but bundled typeshed and Pylance (VS Code extension) have separate terms

---

## 4. Testing

### 4.1 pytest

**What**: The de facto Python test framework; extends `unittest` with a fixture system, plugin architecture, and expressive assertions
**Site**: [pytest.org](https://docs.pytest.org/) | **Version**: 9.0.2 (Dec 2025) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django via pytest-django, FastAPI via pytest-asyncio + httpx, Flask Yes

#### Why It Matters

pytest is the dominant Python test framework by an enormous margin, used in Django itself, CPython, NumPy, FastAPI, Flask, SQLAlchemy, and virtually every major Python project. Its fixture system with dependency injection, parametrize decorator for data-driven tests, and 1,000+ plugin ecosystem make it far more capable than the built-in `unittest` module. pytest 9.0 added a terminal progress feature (disabled by default in 9.0.2 due to terminal emulator compatibility) and resolves quadratic behaviour with `unittest` subtests.

For async frameworks (FastAPI, Starlette), `pytest-asyncio` with `asyncio_mode = "auto"` eliminates the boilerplate of event loop management. For Django, `pytest-django` provides `@pytest.mark.django_db`, `django_db_setup` fixtures, and transactional test isolation.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support; v9.1 targets Python 3.13 |
| Django Integration | **Excellent** - pytest-django v4.11.1; `@pytest.mark.django_db`, factories |
| FastAPI Integration | **Excellent** - pytest-asyncio + httpx TestClient; async fixtures |
| Flask Integration | **Excellent** - flask test_client as pytest fixture; no extra plugin needed |
| Fixture System | **Excellent** - Dependency injection, scoped (function/class/module/session) |
| Plugin Ecosystem | **Excellent** - 1,000+ plugins on PyPI |
| Parametrize | **Strong** - `@pytest.mark.parametrize` for data-driven tests |
| Setup Effort | **Very Low** - `uv add --dev pytest`; zero config for basic usage |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 13.7k stars; 3.1k forks; 15+ years |

#### Quick Start

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",                      # show summary of all non-passing tests
    "--strict-markers",         # error on unknown markers
    "--strict-config",          # error on config issues
    "-q",                       # quiet output (less verbose)
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
    "unit: marks unit tests",
]

# pytest-asyncio configuration (for FastAPI/async)
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# pytest-django configuration
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "myproject.settings.test"
```

```python
# conftest.py — shared fixtures
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def db_connection():
    """Session-scoped database connection."""
    conn = create_test_db()
    yield conn
    conn.close()
```

```bash
# CLI usage
pytest                           # run all tests
pytest -v                        # verbose output
pytest tests/unit/               # specific directory
pytest -k "test_auth"            # run tests matching pattern
pytest -m slow                   # run tests with marker
pytest --lf                      # run only last-failed tests
pytest -x                        # stop on first failure
pytest -n auto                   # parallel (pytest-xdist)
pytest --tb=short                # shorter tracebacks
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `addopts` | Default CLI flags | `""` |
| `testpaths` | Where to discover tests | Current dir |
| `asyncio_mode` | `"auto"` or `"strict"` for pytest-asyncio | `"strict"` |
| `--strict-markers` | Fail on unknown markers | Off |
| `-n auto` | Parallel workers (pytest-xdist) | Sequential |
| `--cov` | Enable coverage (pytest-cov) | Off |
| `--timeout` | Per-test timeout (pytest-timeout) | Off |

#### Known Limitations

- `asyncio_mode = "auto"` can cause interference with non-asyncio event loops (Trio, etc.)
- `scope="session"` fixtures shared across tests can introduce ordering dependencies
- pytest-xdist parallel execution requires tests to be stateless (no shared file system state)
- `--forked` (subprocess isolation) significantly slows test runs
- pytest 9.0.2 disabled terminal progress by default due to terminal emulator compatibility issues

---

### 4.2 Hypothesis

**What**: Property-based testing library that generates edge-case inputs automatically and shrinks failures to minimal examples
**Site**: [hypothesis.works](https://hypothesis.works/) | **Version**: 6.131.x (Mar 2026) | **License**: MPL-2.0
**Compat**: Python 3.12+ Yes (requires 3.9+), Django via extras, FastAPI Yes, Flask Yes

#### Why It Matters

Traditional unit tests verify specific known inputs. Hypothesis inverts this: you declare invariants ("for all valid users, login should not crash") and Hypothesis generates hundreds of random inputs — including integers at `sys.maxsize`, empty strings, `None`, Unicode edge cases — then shrinks any failing case to the simplest possible reproducer. With 31M+ monthly PyPI downloads and strategic adoption in data processing, financial, and API projects, Hypothesis is the go-to tool for finding bugs in domain logic that manual test-writing misses.

The library integrates with Django models (via `hypothesis-django`) and Pydantic models, allowing generation of valid model instances with property constraints. The `ghostwriter` feature can auto-generate a Hypothesis test file from your code's type annotations.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support; regularly updated for new Python features |
| Django Integration | **Strong** - `from hypothesis.extra.django import from_model` generates valid ORM instances |
| FastAPI Integration | **Strong** - Pair with `pytest-asyncio` to fuzz async endpoints |
| Flask Integration | **Strong** - Works with Flask test client in standard pytest fixture |
| Edge Case Discovery | **Excellent** - Finds zero-value, boundary, Unicode, empty-collection bugs |
| Failure Shrinking | **Excellent** - Reduces failing example to minimal reproducer automatically |
| Learning Curve | **Medium** - `@given` + `st.` strategies API requires practice |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 7.4k stars; 31M monthly downloads; used by major libraries |

#### Quick Start

```toml
# pyproject.toml
[tool.pytest.ini_options]
# Hypothesis settings via profile
```

```python
# tests/test_domain.py
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import from_model

from myapp.models import User
from myapp.services import calculate_discount

# Property: discount is always between 0 and 100%
@given(
    price=st.floats(min_value=0.01, max_value=1_000_000, allow_nan=False),
    quantity=st.integers(min_value=1, max_value=999),
)
def test_discount_is_valid(price: float, quantity: int) -> None:
    discount = calculate_discount(price, quantity)
    assert 0.0 <= discount <= 1.0

# Django model generation
@given(user=from_model(User, email=st.emails()))
def test_user_serialization(user: User) -> None:
    data = user.to_dict()
    assert data["email"] == user.email

# Test string operations
@given(st.text())
def test_reversed_twice_equals_original(s: str) -> None:
    assert s[::-1][::-1] == s

# Profile configuration in conftest.py
from hypothesis import settings as hypothesis_settings, HealthCheck
hypothesis_settings.register_profile("ci", max_examples=100, suppress_health_check=[HealthCheck.too_slow])
hypothesis_settings.register_profile("dev", max_examples=10)
hypothesis_settings.load_profile("ci")
```

```bash
# CLI usage (via pytest)
pytest --hypothesis-show-statistics  # show example counts
pytest --hypothesis-seed=42          # deterministic for debugging
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `max_examples` | Number of examples per test | `100` |
| `deadline` | Max milliseconds per test example | `200ms` |
| `suppress_health_check` | Disable specific health warnings | `[]` |
| `deriving_strategies` | Auto-derive strategies from types | Off |
| `database` | Persistent example database path | `.hypothesis/` |
| `phases` | `[Reuse, Generate, Target, Shrink, Explain]` | All |

#### Known Limitations

- Stateful tests (`RuleBasedStateMachine`) have a steep learning curve
- Database-touching tests require careful transaction management or `django_db` marker
- `deadline` health check fires on slow CI machines — tune or suppress per environment
- Complex composite strategies can become hard to read and maintain
- Hypothesis database can grow large on long-lived projects; clean periodically

---

## 5. Coverage

### 5.1 pytest-cov

**What**: pytest plugin that integrates coverage.py directly into the pytest workflow
**Site**: [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io/) | **Version**: 7.1.0 (Mar 2026) | **License**: MIT
**Compat**: Python 3.12+ Yes (requires 3.9+), Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

pytest-cov is the standard way Python teams measure test coverage, integrating coverage.py collection directly into the pytest run via a single `--cov` flag. Version 7.0.0 (Sep 2025) was a major release, and v7.1.0 (Mar 2026) added key improvements. It supports branch coverage, LCOV output for GitHub Actions coverage summaries, and fail-under thresholds for CI gates.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| pytest Integration | **Excellent** - Single plugin; no separate step in CI |
| Branch Coverage | **Strong** - `--cov-branch` or `branch = True` in config |
| Report Formats | **Strong** - term, term-missing, HTML, XML, JSON, LCOV, markdown |
| CI Gating | **Strong** - `--cov-fail-under=80` fails CI below threshold |
| Distributed Testing | **Strong** - Works with pytest-xdist parallel execution |
| Cost | **Free** |

#### Quick Start

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",                # measure coverage for src/ package
    "--cov-branch",             # enable branch coverage
    "--cov-report=term-missing",# show uncovered lines in terminal
    "--cov-report=html:htmlcov",# generate HTML report
    "--cov-report=xml",         # for SonarQube/Codecov
    "--cov-fail-under=80",      # fail CI below 80%
]

# .coveragerc (or [tool.coverage] in pyproject.toml)
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/conftest.py",
    "*/__init__.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[tool.coverage.html]
directory = "htmlcov"
```

```bash
# CLI usage
pytest --cov=src --cov-report=html     # run tests + generate HTML report
pytest --cov-fail-under=80             # CI gate
coverage report                         # show report from existing data
coverage html                           # generate HTML from existing data
open htmlcov/index.html                 # view in browser
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `--cov=SOURCE` | Package/path to measure | None |
| `--cov-branch` | Enable branch coverage | Off |
| `--cov-fail-under=N` | Fail if coverage below N% | Off |
| `--cov-report=TYPE` | Report formats to generate | `term` |
| `--no-cov` | Disable for debugging sessions | Off |
| `--cov-append` | Append to existing data (xdist) | Off |

#### Known Limitations

- Branch coverage can be surprising — a branch for an `else` clause you didn't write (implicit) will show as uncovered
- Coverage data from parallel pytest-xdist runs must be merged (handled automatically with `--cov-append`)
- Cannot measure coverage of code called in subprocesses without `coverage.subprocess_setup()`
- Pytest-cov overrides coverage's `parallel` option — don't set it in `.coveragerc` when using the plugin

---

### 5.2 coverage.py

**What**: The underlying code coverage tool for Python; measures which lines and branches are executed during tests
**Site**: [coverage.readthedocs.io](https://coverage.readthedocs.io/) | **Version**: 7.8.x (2025) | **License**: Apache 2.0
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

coverage.py is the foundation that pytest-cov is built on. Most teams interact with it through pytest-cov, but understanding coverage.py directly is important for advanced scenarios: measuring coverage in subprocess calls, combining coverage from distributed test runs, excluding specific lines with `pragma: no cover`, and integrating with SonarQube or Codecov via XML/LCOV output.

#### Quick Start

```bash
# Direct usage (when not using pytest-cov)
coverage run -m pytest tests/       # run tests and measure coverage
coverage combine                    # combine data from parallel runs
coverage report --show-missing      # terminal report
coverage html                       # HTML report in htmlcov/
coverage xml                        # XML for Codecov/SonarQube
coverage lcov                       # LCOV for GitHub Actions

# Configuration is shared with pytest-cov via [tool.coverage.*]
```

---

## 6. Security

### 6.1 bandit

**What**: AST-based SAST tool for Python that detects 47 security vulnerability patterns across 7 categories
**Site**: [bandit.readthedocs.io](https://bandit.readthedocs.io/) | **Version**: 1.7.9 (2025) | **License**: Apache 2.0
**Compat**: Python 3.12+ Yes (3.10-3.14 supported), Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

bandit is the standard Python SAST tool, maintained by the Python Code Quality Authority (PyCQA) with 7,800+ GitHub stars and 59,500+ dependent repositories on GitHub. Sponsored by Mercedes-Benz, Tidelift, and Stacklok, it analyzes Python source code via AST parsing — meaning it detects patterns regardless of variable naming or formatting. Its 47 built-in checks cover injection vulnerabilities, hardcoded credentials, weak cryptography, XML processing issues (XXE), Flask/Django-specific misconfigurations, and more.

The SARIF output format plugs directly into GitHub Code Scanning, making bandit results visible in pull request annotations with zero additional tooling.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Python 3.10-3.14 officially supported |
| Django Integration | **Strong** - Detects DEBUG=True, weak SECRET_KEY, open ALLOWED_HOSTS |
| FastAPI Integration | **Medium** - Generic Python patterns; no FastAPI-specific rules |
| Flask Integration | **Strong** - Detects `DEBUG=True`, CSRF, secret key issues |
| Security Check Depth | **Strong** - 47 checks across injection, crypto, XSS, misconfig categories |
| False Positive Rate | **Medium** - Confidence/severity thresholds help tune noise |
| GitHub Integration | **Strong** - SARIF output for GitHub Code Scanning annotations |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - 7.8k stars; 151 contributors; PyCQA-maintained |

#### Quick Start

```toml
# pyproject.toml
[tool.bandit]
exclude_dirs = ["tests", ".venv", "migrations"]
severity = "medium"              # minimum severity to report
confidence = "medium"            # minimum confidence to report
```

```bash
# CLI usage
bandit -r src/                   # recursive scan
bandit -r . -l -ii               # high severity + high confidence only
bandit -r . -f json -o bandit.json  # JSON output
bandit -r . -f sarif             # SARIF for GitHub Code Scanning
bandit -r . --skip B101,B601     # skip specific test IDs
bandit -t B201,B322 src/         # run only specific tests

# GitHub Actions integration
- name: Security scan
  run: bandit -r src/ -f sarif -o bandit.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: bandit.sarif
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `-l` / `--level` | Minimum severity (LOW/MEDIUM/HIGH) | LOW |
| `-i` / `--confidence` | Minimum confidence (LOW/MEDIUM/HIGH) | LOW |
| `--skip` | Test IDs to skip | None |
| `-t` / `--tests` | Run only these test IDs | All |
| `-f` / `--format` | Output format (json, sarif, xml, html, csv) | Screen |
| `exclude_dirs` | Directories to skip | None |

#### Security Check Categories

| ID Range | Category | Example |
|----------|----------|---------|
| B1xx | Miscellaneous | `assert_used`, `exec_used` |
| B2xx | Application/framework | `flask_debug_true`, `django_extra` |
| B3xx | Blacklist calls | `subprocess_without_shell_equals_true` |
| B4xx | Blacklist imports | `import_telnetlib`, `import_ftplib` |
| B5xx | Cryptography | `weak_md5`, `weak_sha1` |
| B6xx | Injection | `paramiko_calls`, `start_process_with_partial_path` |
| B7xx | XML | `xml_bad_cElementTree` (XXE) |

#### Known Limitations

- Limited to Python-specific patterns — not a replacement for general SAST platforms
- No inter-procedural analysis — cannot track tainted data across function calls
- High false-positive rate on test files (use `--skip B101` to allow `assert` in tests)
- Does not analyse templates (Django/Jinja2 template injection requires separate tools)
- Ruff's `S` rule group overlaps ~30 of bandit's 47 checks; for security-critical code, run both

---

### 6.2 pip-audit

**What**: Audits Python package dependencies for known vulnerabilities using the Python Packaging Advisory Database (PyPA) and OSV
**Site**: [github.com/pypa/pip-audit](https://github.com/pypa/pip-audit) | **Version**: 2.9.x (2025) | **License**: Apache 2.0
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

pip-audit performs Software Composition Analysis (SCA) — scanning your installed or declared dependencies against the PyPA Advisory Database and Open Source Vulnerability (OSV) database for known CVEs. Maintained by the Python Packaging Authority (PyPA), it is the official recommended tool for Python dependency vulnerability scanning. Unlike bandit (which scans source code), pip-audit scans packages — complementary, not overlapping.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Vulnerability Database | **Strong** - PyPA GHSA + OSV; regularly updated |
| SBOM Generation | **Strong** - Supports CycloneDX and SPDX output formats |
| CI Integration | **Excellent** - `--strict` exits non-zero on any vulnerability |
| False Positive Rate | **Low** - Based on official advisories, not heuristics |
| Cost | **Free** |
| Ecosystem Maturity | **Strong** - Official PyPA tool; 1.2k stars |

#### Quick Start

```bash
# CLI usage
pip-audit                              # audit current environment
pip-audit -r requirements.txt          # audit from requirements file
pip-audit --strict                     # fail CI on any vulnerability
pip-audit --progress-spinner off       # clean output for CI logs
pip-audit --output json -o audit.json  # JSON output
pip-audit --ignore-vuln GHSA-xxxx-xxxx # suppress specific advisory

# With uv
uv run pip-audit

# GitHub Actions
- name: Dependency audit
  run: pip-audit --strict --progress-spinner off
```

#### Known Limitations

- Requires packages to be installed or requirements file present — cannot scan `pyproject.toml` directly in all scenarios
- Does not detect vulnerabilities introduced via transitive dependencies from custom package indexes
- OSV database occasionally has false positives for version ranges that haven't been officially confirmed

---

### 6.3 safety

**What**: Commercial vulnerability scanner for Python dependencies with CLI and CI integration
**Site**: [safetycli.com](https://safetycli.com/) | **Version**: 3.x | **License**: MIT (CLI), Commercial (Safety 360)
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Safety was the original Python dependency vulnerability scanner and remains widely used in enterprise environments. The commercial tier (Safety 360) adds policy enforcement, Slack/Jira integration, and a managed vulnerability database with faster CVE coverage than pip-audit's public OSV database.

For teams choosing between safety and pip-audit: pip-audit is recommended for most open-source and startup projects (PyPA-official, free). Safety is preferred when enterprise-grade policy enforcement, SLA-backed database updates, or audit trail requirements exist.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Vulnerability Database | **Strong** - Commercial DB with faster updates than OSV |
| Policy Enforcement | **Excellent** (paid) - Block deploys based on policies |
| CI Integration | **Strong** - `safety check` exits non-zero on findings |
| Cost | **Freemium** - Free CLI; Safety 360 paid for advanced features |
| Ecosystem Maturity | **Strong** - 1.7k stars; long-standing commercial tool |

#### Quick Start

```bash
# CLI usage
safety check                     # audit current environment
safety check -r requirements.txt # audit from requirements file
safety check --json              # JSON output
safety check --full-report       # detailed advisory info
```

#### Known Limitations

- Free tier has rate limits and may lag behind commercial database
- Requires an account for full database access in newer versions
- pip-audit covers the same core use case without account requirements

---

## 7. Task Runners

### 7.1 Nox

**What**: Python-based task automation tool that runs sessions (test, lint, docs, etc.) in isolated virtual environments
**Site**: [nox.thea.codes](https://nox.thea.codes/) | **Version**: 2026.2.9 | **License**: Apache 2.0
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Nox is tox's modern successor, replacing INI-based configuration with a Python script (`noxfile.py`). This means sessions can use loops, conditionals, imports, and any Python logic — making test matrices across Python versions, Django versions, or dependency extras dramatically easier to express and maintain. It is used by pip, pipx, urllib3, Jupyter, Google Cloud Python libraries, and the CPython packaging working group.

The key differentiation from tox: everything is Python code. There are no INI syntax quirks, no obscure interpolation rules, no limitations on conditional logic. Google's `gapic-generator-python` and `google-cloud-python` use Nox extensively for their complex multi-environment CI matrices.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Configuration Language | **Excellent** - Python code; no INI learning curve |
| Flexibility | **Excellent** - Dynamic session generation with Python logic |
| Multi-version Testing | **Strong** - `@nox.session(python=["3.10", "3.11", "3.12", "3.13"])` |
| Dependency Isolation | **Strong** - Each session gets a fresh virtualenv |
| Performance | **Medium** - Slower startup than tox due to Python overhead |
| Adoption | **Medium** - 1.5k stars; smaller community than tox |
| Cost | **Free** |

#### Quick Start

```python
# noxfile.py
import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
DJANGO_VERSIONS = ["4.2", "5.0", "5.1"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".[dev]")
    session.run("pytest", "--cov=src", "--cov-report=xml", *session.posargs)


@nox.session(python=["3.12"])
def lint(session: nox.Session) -> None:
    """Run linting and formatting checks."""
    session.install("ruff", "mypy")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
    session.run("mypy", "src/")


@nox.session(python=["3.12"])
def security(session: nox.Session) -> None:
    """Run security scans."""
    session.install("bandit", "pip-audit")
    session.run("bandit", "-r", "src/", "-ll")
    session.run("pip-audit", "--strict")


@nox.session(python=["3.12"])
def docs(session: nox.Session) -> None:
    """Build documentation."""
    session.install(".[docs]")
    session.run("sphinx-build", "docs/", "docs/_build/html")


# Matrix: test against multiple Django versions
@nox.session(python="3.12")
@nox.parametrize("django", DJANGO_VERSIONS)
def test_django(session: nox.Session, django: str) -> None:
    session.install(f"django=={django}", "pytest", "pytest-django")
    session.run("pytest", "tests/")
```

```bash
# CLI usage
nox                              # run all sessions
nox -s tests                     # run only 'tests' session
nox -s tests-3.12                # run 'tests' on Python 3.12 specifically
nox -s lint security             # run multiple sessions
nox -l                           # list available sessions
nox -r                           # reuse existing virtualenvs (faster)
nox --no-venv                    # skip virtualenv creation (for speed)
nox -s tests -- -v -k "auth"     # pass args to pytest via --
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `@nox.session(python=...)` | Specify Python version(s) | System default |
| `@nox.session(reuse_venv=True)` | Reuse virtualenv between runs | `False` |
| `@nox.parametrize(...)` | Create session matrix | N/A |
| `session.install(...)` | Install packages in session venv | N/A |
| `session.run(...)` | Run commands in session | N/A |
| `session.posargs` | Forward CLI args after `--` | `[]` |

#### Known Limitations

- Slower session startup compared to tox (Python virtualenv creation overhead)
- Smaller ecosystem than tox; fewer documented examples for common patterns
- noxfile.py can grow complex for multi-matrix CI scenarios
- Not suitable for simple single-environment linting tasks (use Makefile or just CLI directly)

---

### 7.2 tox

**What**: The original Python multi-environment test automation tool; INI-based configuration, well-documented CI patterns
**Site**: [tox.wiki](https://tox.wiki/) | **Version**: 4.25.x (2025) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

tox is the de facto standard for Python multi-environment testing, used in Django, Flask, Requests, pytest itself, and thousands of open-source projects. Its INI-based `tox.ini` or `[tool.tox]` pyproject.toml section is well-documented and has a large body of examples. tox 4.x (major rewrite from tox 3.x) improved performance and configuration clarity.

For library authors who need to test against multiple Python versions and post results to CI services with known tox support (ReadTheDocs, Travis CI patterns), tox remains the conventional choice. For teams comfortable with Python code over INI, Nox is the modern alternative.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Configuration Language | **INI/TOML** - Familiar but less flexible than Nox's Python code |
| Documentation | **Excellent** - Extensive community examples and official docs |
| CI Integration | **Excellent** - Native support in ReadTheDocs, GitHub Actions, etc. |
| Adoption | **Strong** - 3.9k stars; default choice in most Python library projects |
| Performance | **Good** - Comparable to Nox after v4 rewrite |
| Cost | **Free** |

#### Quick Start

```toml
# pyproject.toml
[tool.tox]
requires = ["tox>=4"]
env_list = ["3.10", "3.11", "3.12", "3.13", "lint"]

[tool.tox.env_run_base]
description = "Run tests under {base_python}"
deps = ["pytest", "pytest-cov"]
commands = [["pytest", "--cov=src", "--cov-report=term-missing", {posargs}]]

[tool.tox.env.lint]
description = "Run linting"
skip_install = true
deps = ["ruff", "mypy"]
commands = [
    ["ruff", "check", "."],
    ["ruff", "format", "--check", "."],
    ["mypy", "src/"],
]
```

```bash
# CLI usage
tox                              # run all environments
tox -e 3.12                      # run specific Python version
tox -e lint                      # run lint environment
tox -e py312-django42            # parametrized environment
tox -l                           # list environments
tox -r                           # recreate virtualenvs
tox -- -v -k auth                # pass args to commands
```

#### Known Limitations

- INI configuration syntax is limiting for complex conditional logic (use Nox instead)
- `tox.ini` and `setup.cfg` have overlapping configuration that can cause confusion
- tox 4.x introduced breaking changes from tox 3.x; migration required for existing configs
- Factor-based environments (`[testenv:py{310,311,312}-django{42,50}]`) become unwieldy at scale

---

## 8. Dependency Management

### 8.1 uv

**What**: Extremely fast Python package and project manager written in Rust; single tool replacing pip, pip-tools, pyenv, virtualenv, and Poetry
**Site**: [docs.astral.sh/uv](https://docs.astral.sh/uv) | **Version**: 0.6.10 (Mar 2026) | **License**: Apache 2.0
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

uv has become the most-starred Python tooling project in history, reaching 81.2k GitHub stars since its February 2024 launch — a pace that outstrips even Ruff's record growth. Written in Rust by the Astral team, it is 10-100x faster than pip, replacing an entire Python toolchain (pip + pip-tools + virtualenv + pyenv) with a single binary.

Key differentiators: uv manages Python versions directly (`uv python install 3.13`), creating environments automatically. Its universal lockfile (`uv.lock`) works across platforms. The Cargo-style workspace model handles monorepos. PEP 621-compliant `pyproject.toml` configuration is the standard. CI install times drop from 45 seconds to 3 seconds for typical dependency sets.

uv 0.6.10 added `uv sync --check` (verify environment matches lockfile without modifying it), `.env` file support in `uv tool run`, and improved torch backend support.

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Excellent** - Manages Python versions; installs 3.8-3.13+ |
| Django Integration | **Excellent** - Standard `uv add django`, `uv run manage.py` |
| FastAPI Integration | **Excellent** - FastAPI team recommends uv in official docs |
| Flask Integration | **Excellent** - Works identically with pip semantics |
| Performance | **Exceptional** - 10-100x faster than pip; 15x faster than Poetry in CI |
| Lockfile | **Strong** - `uv.lock` cross-platform universal lockfile |
| Python Version Management | **Excellent** - Built-in; replaces pyenv |
| Workspace Support | **Strong** - Cargo-style monorepo workspaces |
| PEP Compliance | **Excellent** - PEP 517/518/621/660 compliant |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 81.2k stars; 470 contributors; Astral-backed |

#### Quick Start

```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# New project
uv init myproject
cd myproject

# Python version management
uv python install 3.12           # install a Python version
uv python pin 3.12               # pin project to Python 3.12

# Dependency management
uv add django fastapi             # add production dependencies
uv add --dev pytest ruff mypy    # add dev dependencies
uv add "django>=5.0,<6.0"       # version constraints
uv remove deprecated-package     # remove dependency
uv sync                          # install all dependencies from lockfile
uv sync --check                  # verify without modifying (v0.6+)
uv lock                          # regenerate lockfile

# Running commands
uv run python manage.py migrate  # run in project environment
uv run pytest                    # run tests
uvx ruff check .                 # run tool without installing globally

# Tool management (like pipx)
uv tool install ruff             # install global tool
uv tool run black .              # run without installing

# Pip-compatible interface (for legacy workflows)
uv pip install -r requirements.txt
uv pip compile requirements.in -o requirements.txt
```

```toml
# pyproject.toml (PEP 621 format)
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "django>=5.0",
    "fastapi>=0.115",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=7.0",
    "ruff>=0.11",
    "mypy>=1.19",
    "bandit>=1.7",
    "pip-audit>=2.9",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=7.0",
]
```

#### Key Configuration Options

| Setting | Purpose | Default |
|---------|---------|---------|
| `uv add --dev` | Add to dev dependencies | Production |
| `uv sync --frozen` | Use exact lockfile versions (CI) | Update if needed |
| `uv sync --check` | Verify without modifying (v0.6+) | Off |
| `UV_PYTHON` | Override Python version | From `.python-version` |
| `UV_CACHE_DIR` | Cache location | `~/.cache/uv` |
| `uv.lock` | Universal cross-platform lockfile | Auto-generated |

#### Migration from pip/pip-tools

```bash
# From requirements.txt
uv init
uv add $(cat requirements.txt | grep -v '#' | tr '\n' ' ')

# From Poetry
# Poetry's pyproject.toml is largely compatible
uv sync  # uv reads [project.dependencies] directly

# From Pipenv
uv init
# Copy dependencies from Pipfile to pyproject.toml [project.dependencies]
uv sync
```

#### Known Limitations

- `uv.lock` format is different from `poetry.lock` and `pip-tools` lock files — cannot directly exchange
- Publishing to PyPI via `uv publish` is still marked beta in v0.6
- Conda environments are not managed by uv; scientific teams using conda must maintain both toolchains
- Some advanced Poetry features (plugins, dependency groups beyond dev) require re-mapping to uv equivalents
- Windows support works but has edge cases with long paths on older Windows versions

---

### 8.2 pip

**What**: The built-in Python package installer; no lockfile, no virtual environment management, no version management
**Site**: [pip.pypa.io](https://pip.pypa.io/) | **Version**: 25.x | **License**: MIT
**Compat**: Python 3.12+ Yes (bundled), Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

pip is the foundation of the Python packaging ecosystem and is bundled with every Python installation. For simple scripts, one-off installs, and legacy environments, it remains the default. However, pip's lack of a built-in lockfile mechanism and Python version management makes it insufficient for production project management.

For new projects, use uv. For legacy projects with `requirements.txt`, migrate to uv's pip-compatible interface (`uv pip`) which provides identical semantics with 10-100x the speed.

#### Quick Start

```bash
# Basic usage
pip install package                  # install
pip install -r requirements.txt      # install from requirements file
pip install --upgrade package        # upgrade
pip freeze > requirements.txt        # generate requirements file
pip uninstall package                # uninstall

# uv pip-compatible interface (recommended migration path)
uv pip install package               # same API, 10-100x faster
uv pip compile requirements.in       # pip-tools-compatible
```

---

### 8.3 Poetry

**What**: Python project management tool combining dependency management, virtual environments, and package building/publishing
**Site**: [python-poetry.org](https://python-poetry.org/) | **Version**: 2.1.x (2025) | **License**: MIT
**Compat**: Python 3.12+ Yes, Django Yes, FastAPI Yes, Flask Yes

#### Why It Matters

Poetry has been the most mature alternative to pip for project management since 2018, with 33k GitHub stars and wide adoption in library projects that publish to PyPI. Its `poetry.lock` format is reliable, its dependency resolver handles complex constraints, and `poetry publish` is the most polished PyPI publishing workflow available.

In 2026, uv has emerged as the faster, PEP-compliant alternative. The primary reasons to choose Poetry over uv:
- **Library publishing**: `poetry publish` with its project scaffolding and publishing workflow is more mature than `uv publish` (still beta)
- **Existing poetry.lock files**: Teams with established Poetry workflows should not migrate without a specific reason
- **Plugin ecosystem**: Poetry's plugin system (poetry-dynamic-versioning, poetry-plugin-export) has no uv equivalent

#### Evaluation Summary

| Criterion | Rating |
|-----------|--------|
| Python 3.12+ Compatibility | **Strong** - Full support |
| Performance | **Medium** - 15x slower than uv in CI; ~45 seconds for typical installs |
| Lockfile | **Strong** - `poetry.lock` reliable; platform-specific by design |
| Package Publishing | **Excellent** - Most mature PyPI publishing workflow |
| Python Version Management | **Poor** - Requires pyenv separately |
| PEP Compliance | **Partial** - Uses custom `pyproject.toml` sections, not pure PEP 621 |
| Cost | **Free** |
| Ecosystem Maturity | **Excellent** - 33k stars; mature plugin ecosystem |

#### Quick Start

```bash
# Installation
curl -sSL https://install.python-poetry.org | python3 -

# New project
poetry new myproject
cd myproject

# Dependency management
poetry add django fastapi        # add dependencies
poetry add --group dev pytest ruff  # dev dependencies
poetry install                   # install from poetry.lock
poetry update                    # update within constraints
poetry publish --build           # build and publish to PyPI

# Running commands
poetry run python manage.py migrate
poetry run pytest
```

#### Known Limitations

- 15x slower than uv for dependency installation in CI
- `poetry.lock` is larger and slower to regenerate than `uv.lock`
- Does not manage Python versions (requires pyenv or similar)
- Poetry's `pyproject.toml` format differs from PEP 621 for dependency specifications
- **Recommended path**: Keep if publishing libraries; consider uv for application projects

---

## References

### Official Documentation

- **Ruff**: [docs.astral.sh/ruff](https://docs.astral.sh/ruff) — Configuration reference, rule catalog, migration guides
- **uv**: [docs.astral.sh/uv](https://docs.astral.sh/uv) — Full uv documentation and feature guides
- **pytest**: [docs.pytest.org](https://docs.pytest.org/) — Test framework documentation (Release 9.0/9.1)
- **mypy**: [mypy.readthedocs.io](https://mypy.readthedocs.io/) — Type checker documentation, strict mode guide
- **Pyright**: [github.com/microsoft/pyright](https://github.com/microsoft/pyright) — Configuration and type checking mode docs
- **Black**: [black.readthedocs.io](https://black.readthedocs.io/) — Black formatter documentation
- **Hypothesis**: [hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/) — Strategy reference, Django integration
- **Nox**: [nox.thea.codes](https://nox.thea.codes/) — Session configuration and CLI usage
- **bandit**: [bandit.readthedocs.io](https://bandit.readthedocs.io/) — Security check reference, plugin API
- **pytest-cov**: [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io/) — Coverage configuration options

### Benchmark Sources

- Ruff performance benchmarks: [astral.sh/blog/the-ruff-formatter](https://astral.sh/blog/the-ruff-formatter) — 30x vs Black, 100x vs YAPF
- Linter accuracy benchmark (1,000 files): [tildalice.io/ruff-vs-black-vs-flake8-linting-accuracy-benchmark](https://tildalice.io/ruff-vs-black-vs-flake8-linting-accuracy-benchmark/) — Ruff 847 issues vs Flake8 634 in 18x less time
- uv performance: [docs.bswen.com/blog/2026-02-12-uv-vs-poetry](https://docs.bswen.com/blog/2026-02-12-uv-vs-poetry/) — 10-100x vs pip, 15x faster CI than Poetry
- Type checker conformance (Mar 2026): [docs.bswen.com/blog/2026-03-17-python-type-checker-conformance-comparison](https://docs.bswen.com/blog/2026-03-17-python-type-checker-conformance-comparison) — Pyright 97.8%, mypy 58.3%
- Pylint vs Ruff performance: [docs.bswen.com/blog/2026-02-16-pyrefly-vs-linters](https://docs.bswen.com/blog/2026-02-16-pyrefly-vs-linters/) — Ruff 3.5s vs Pylint 120s on 1,000 files

### Community Articles

- [Real Python — Managing Python Projects with uv](https://realpython.com/python-uv/) — Comprehensive uv guide
- [Real Python — Ruff: Modern Python Linter](https://realpython.com/ruff-python/) — Ruff getting started guide
- [ArjanCodes — Property Testing with Hypothesis](https://arjancodes.com/blog/how-to-use-property-based-testing-in-python-with-hypothesis/) — Hypothesis patterns
- [DZone — Tox and Nox for Multi-Version Testing](https://dzone.com/articles/automating-python-testing-across-versions-with-tox-and-nox) — Comparison and setup

### GitHub Repositories

- [astral-sh/ruff](https://github.com/astral-sh/ruff) — 46k stars
- [astral-sh/uv](https://github.com/astral-sh/uv) — 81.2k stars
- [psf/black](https://github.com/psf/black) — 41.4k stars
- [python/mypy](https://github.com/python/mypy) — 20.3k stars
- [microsoft/pyright](https://github.com/microsoft/pyright) — 15.3k stars
- [pytest-dev/pytest](https://github.com/pytest-dev/pytest) — 13.7k stars
- [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis) — 7.4k stars
- [PyCQA/bandit](https://github.com/PyCQA/bandit) — 7.8k stars
- [PyCQA/isort](https://github.com/PyCQA/isort) — 6.9k stars
- [pylint-dev/pylint](https://github.com/pylint-dev/pylint) — 5.7k stars
