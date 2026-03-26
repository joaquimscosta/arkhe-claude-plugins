# Startup Plugin

Startup idea validation pipeline with 6-stage analysis, decision gates, confidence scoring, and composable domain presets.

## Overview

Validates startup ideas through a structured 6-stage pipeline inspired by how top founders and investors evaluate opportunities. Each stage assigns an expert AI agent, produces a confidence-scored report, and presents a decision gate (proceed / iterate / pivot / stop).

## The 6 Stages

| # | Stage | Expert Role | Decision Gate |
|---|-------|-------------|--------------|
| 1 | Problem & Market Validation | Market Research Analyst | Is this a real problem worth solving? |
| 2 | Feasibility Analysis | Feasibility Expert | Can this be built legally and operationally? |
| 3 | Product & Solution Design | Product Manager + Architect | Can we design a differentiated product? |
| 4 | Business Model & Strategy | Business Strategist | Can this become profitable and defensible? |
| 5 | Go-to-Market & Growth | Growth Strategist | Can we acquire users sustainably? |
| 6 | Execution Roadmap | Execution Coach | Can we build and launch realistically? |

## Quick Start

```bash
# Basic validation
/startup-validate "A mobile POS system for Cape Verde retailers"

# With domain presets
/startup-validate "NôsPay remittance app" --preset fintech --preset cape-verde

# Autonomous mode
/startup-validate "NôsPay" --fast

# Deep mode (parallel specialists per stage)
/startup-validate "NôsPay" --deep

# Resume from stage 3
/startup-validate "NôsPay" --from 3 --name nospay

# Single stage
/startup-validate "NôsPay" --stage 2
```

## Components

### Command
- `/startup-validate` — Main entry point for the validation pipeline

### Skill
- `startup-validating` — Orchestrates the 6-stage pipeline with decision gates

### Agents (7)
- `market-validator` — Stage 1: Problem & Market Validation
- `feasibility-analyst` — Stage 2: Feasibility Analysis
- `product-designer` — Stage 3: Product & Solution Design
- `business-strategist` — Stage 4: Business Model & Strategy
- `growth-strategist` — Stage 5: Go-to-Market & Growth
- `execution-planner` — Stage 6: Execution Roadmap
- `validation-critic` — Deep mode: synthesizes parallel analyses

### Presets (4)
- `fintech` — Regulatory, compliance, payment rails
- `cape-verde` — Cape Verde market, diaspora, SISP/Vinti4
- `saas` — SaaS metrics, pricing models, growth benchmarks
- `marketplace` — Two-sided markets, take rates, liquidity

## Output

Reports are saved to `startup-validation/{slug}/` in the current project:

```
startup-validation/nospay/
├── idea.md
├── stage-1-market-validation.md
├── stage-2-feasibility.md
├── stage-3-product-design.md
├── stage-4-business-model.md
├── stage-5-go-to-market.md
├── stage-6-execution-roadmap.md
└── summary.md
```

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| Interactive (default) | _(none)_ | Pauses at each stage for user decision |
| Fast | `--fast` | Runs all stages without pausing |
| Deep | `--deep` | Spawns 3 parallel specialists per stage + critic |

## Multi-Agent Patterns Used

Pipeline, Specialized Roles, Human-in-the-Loop, Confidence-Gated Completion, Critic-Actor, Confession Pattern, Supervisor-Worker, Parallel Execution, Fresh Context per Iteration.
