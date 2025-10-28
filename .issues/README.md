# Issues Archive

This directory contains detailed analyses and solutions for significant issues encountered during plugin development. These documents provide historical context and reference material for future development decisions.

## Purpose

- **Document complex issues** that required significant research or discussion
- **Preserve solutions** and the rationale behind implementation choices
- **Provide reference** for similar issues in the future
- **Track decisions** made during development

## Structure

Each issue is organized in its own directory:

```
.issues/
├── README.md                    # This file
└── YYYY-MM-DD-brief-name/       # Issue-specific directory
    ├── ANALYSIS.md              # Problem analysis and investigation
    ├── SOLUTION.md              # Implemented solution and results
    └── [additional files]       # Any supporting documents
```

## Naming Convention

Directory format: `YYYY-MM-DD-brief-description/`

- **Date prefix**: When the issue was addressed (YYYY-MM-DD)
- **Brief description**: Short kebab-case summary of the issue
- Examples: `2025-10-28-dependency-uv/`, `2025-11-15-auth-cookies/`

## Index of Issues

| Date | Issue | Status | Summary |
|------|-------|--------|---------|
| 2025-10-28 | [dependency-uv](2025-10-28-dependency-uv/) | ✅ Resolved | Dependency installation failure with Python 2.7 default; solved with UV inline script metadata (PEP 723) |
| 2025-10-28 | [youtube-api-compatibility](2025-10-28-youtube-api-compatibility/) | ✅ Resolved | Transcript extraction failing due to youtube-transcript-api v1.0+ breaking changes; updated to instance-based API |

## Adding New Issues

When documenting a new issue:

1. **Create directory**: `.issues/YYYY-MM-DD-brief-name/`
2. **Add analysis**: Document the problem in `ANALYSIS.md`
3. **Add solution**: Document the resolution in `SOLUTION.md`
4. **Update index**: Add entry to the table above
5. **Keep focused**: These are for significant architectural/technical decisions, not routine bug fixes

## Note

These documents are **not linked from main documentation**. They serve as internal reference material for developers and maintainers. Users should not need to consult these files.
