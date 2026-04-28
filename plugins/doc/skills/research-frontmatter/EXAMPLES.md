# Research Frontmatter Examples

## Example 1: Validate Research Docs (No JD Config)

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --format text
============================================================
  Research Document Validation
============================================================

[WARNING] RD016: Stale: last_updated=2025-12-18 but git shows 2026-01-15 (>7 day threshold)  (spring-boot-ecosystem-research.md)
  -> Update last_updated to 2026-01-15

Summary: 1 warning
```

## Example 2: Resolve Path with JD Config

Given `.jd-config.json`:
```json
{
  "version": 1,
  "root": "docs",
  "areas": {
    "00": "getting-started",
    "10": "product",
    "20": "architecture",
    "30": "research",
    "90": "archive"
  }
}
```

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/resolve_research_path.py --format json
{
  "path": "docs/30-research",
  "jd_aware": true,
  "prefix": "30",
  "area_name": "research",
  "root": "docs"
}
```

## Example 3: Resolve Path Without JD Config

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/resolve_research_path.py --format json
{
  "path": "docs/research",
  "jd_aware": false,
  "prefix": null,
  "area_name": null,
  "root": "docs"
}
```

## Example 4: Staleness-Only Check

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --staleness-only --format text
============================================================
  Research Document Staleness
============================================================

  All checks passed!
```

## Example 5: JSON Output

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py --format json
{
  "title": "Research Document Validation",
  "total_issues": 1,
  "issues": [
    {
      "rule_id": "RD013",
      "severity": "ERROR",
      "message": "Not listed in README.md index",
      "location": "new-research.md"
    }
  ],
  "summary": {
    "ERROR": 1
  }
}
```

## Example 6: Override Research Directory

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/validate_research_docs.py \
    --research-dir docs/30-research --format text
```

## Example 7: Custom JD Area Name

Given `.jd-config.json` with custom area:
```json
{
  "areas": {
    "50": "spikes-and-research"
  }
}
```

```bash
$ uv run ${CLAUDE_SKILL_DIR}/scripts/resolve_research_path.py --format text
docs/50-spikes-and-research  (JD area 50-spikes-and-research)
```

The resolver matches any area name containing "research".

## Example 8: Research Document Template

```yaml
---
title: "Your Research Topic"
version: "1.0.0"
status: Draft
created: 2026-04-11
last_updated: 2026-04-11
---

## Executive Summary

Brief overview of the research topic and key findings.

## 1. Introduction

...

## References

- [Source 1](url)
```
