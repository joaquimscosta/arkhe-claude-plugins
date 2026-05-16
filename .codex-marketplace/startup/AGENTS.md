# startup — Codex AGENTS

> **Bootstrap:** Load `using-arkhe-skills` first — it maps Claude-only tools (`AskUserQuestion`, `TaskCreate`, `EnterPlanMode`, `Skill`, `Agent`) to Codex equivalents.

Startup idea validation pipeline with 6-stage analysis, decision gates, and domain presets

## Skills

- **startup-validating** — Orchestrate a 6-stage startup idea validation pipeline with decision gates, confidence scoring, and composable domain presets. Use when user runs /startup-validate command, wants to validate a startu…

## Commands as Trigger Phrases

### When the user says "/startup:startup-validate" (args: "<idea description>" | @<file> [--preset <name>]... [--fast] [--deep] [--from <N>] [--stage <N>] [--name <slug>])

Validate a startup idea through a 6-stage pipeline with decision gates, confidence scoring, and domain presets

# Startup Validate

Validate a startup idea through 6 structured stages, each with expert analysis and a decision gate.

## Quick Start

```bash
/startup-validate "remittance app for US-Cape Verde diaspora"
/startup-validate @research-brief.md
/startup-validate @idea.md --preset fintech --deep
/startup-validate "NôsPay" --preset fintech --preset cape-verde
/startup-validate "NôsPay" --preset fintech --fast
/startup-validate "NôsPay" --preset fintech --deep
/startup-validate "NôsPay" --from 3
/startup-validate "NôsPay" --stage 2
/startup-validate "POS system for Cape Verde SMEs" --name pos-system
```

## Flags

| Flag | Effect |
|------|--------|
| `--preset <name>` | Load domain preset (composable, use multiple times) |
| `--fast` | Run all stages without pausing at decision gates |
| `--deep` | Spawn parallel specialist sub-agents per stage + critic synthesis |
| `--from <N>` | Resume pipeline from stage N (reads prior stage reports from disk) |
| `--stage <N>` | Run only stage N in isolation |
| `--name <slug>` | Override auto-generated run name |

## The 6 Stages

1. **Problem & Market Validation** — Is this a real, valuable problem worth solving?
2. **Feasibility Analysis** — Can this realistically be built, legally and operationally?
3. **Product & Solution Design** — Can we design a compelling, differentiated product?
4. **Business Model & Strategy** — Can this become a profitable, defensible business?
5. **Go-to-Market & Growth** — Can we acquire users and achieve sustainable growth?
6. **Execution Roadmap** — Can we build and launch this in realistic timeframes?

## Implementation

Invoke the Skill tool with skill name `startup:startup-validating` and arguments: `$ARGUMENTS`
