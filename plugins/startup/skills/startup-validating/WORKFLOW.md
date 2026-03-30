# Startup Validation — Workflow

Complete orchestration protocol for the 6-stage startup validation pipeline.

## Phase 1: Initialization

### 1.1 Parse Arguments

Determine the input shape of `$ARGUMENTS` before parsing:

**Shape A — Well-formed CLI**: Contains a quoted idea string and/or recognized flags (`--preset`, `--fast`, `--deep`, `--from`, `--stage`, `--name`). Parse directly:
- **idea**: The quoted idea description
- **presets**: All `--preset <name>` values → list of preset names
- **fast**: Boolean, true if `--fast` present
- **deep**: Boolean, true if `--deep` present
- **from_stage**: Integer N from `--from <N>` (default: 1)
- **single_stage**: Integer N from `--stage <N>` (default: null)
- **name**: String from `--name <slug>` (default: null)

If all required fields are present (at minimum: idea or `--from`), skip 1.1b and proceed to 1.2.

**Shape B — File content / unstructured text**: `$ARGUMENTS` contains multi-line content (from `@file` references), no recognized flags, or a block of text without quotes. Treat the content as the idea description or a research brief. Extract any embedded flags if present, then fall through to 1.1b.

**Shape C — Empty or ambiguous**: `$ARGUMENTS` is empty, contains only flags without an idea, or does not clearly convey an idea description. Fall through to 1.1b.

### 1.1b Interactive Confirmation

**Only triggered for Shape B or Shape C inputs.** Use `AskUserQuestion` for a 3-step confirmation:

1. **Confirm idea**: Present the extracted idea description (for Shape B) or ask for one (Shape C). Example: "I extracted the following idea: '{text}'. Is this correct, or would you like to refine it?"
2. **Choose mode**: Standard (default, with decision gates), Deep (parallel specialists + critic), or Fast (autonomous, no gates).
3. **Choose presets**: List available presets by reading `${CLAUDE_SKILL_DIR}/../../presets/*.md` filenames (without `.md` extension). Allow the user to select zero or more.

If `$ARGUMENTS` contained Shape B content with research documents (not just an idea description), store the research content for injection in Phase 2 (see section 2.1, item 4).

### 1.2 Generate Slug

If `--name` provided, use it directly. Otherwise, auto-generate from idea text:
1. Convert to lowercase
2. Strip diacritics (e.g., ô → o, ã → a)
3. Replace spaces and special characters with hyphens
4. Remove consecutive hyphens
5. Truncate to 40 characters
6. Remove trailing hyphens

Examples: "NôsPay Remittance App" → `nospay-remittance-app`, "POS System for Cape Verde SMEs" → `pos-system-for-cape-verde-smes`

### 1.3 Set Up Output Directory

```
output_dir = startup-validation/{slug}/
```

Create the directory if it doesn't exist. If it already exists (resume scenario), preserve existing files.

**Resume from pipeline state**: If `--from` is used and `{output_dir}/pipeline-state.json` exists, read the state file and auto-populate: idea, mode, presets, completed stages, and prior scores. Log: "Resuming from pipeline state. Completed stages: {list}. Next: Stage {N}." Delete `pipeline-state.json` after successful load (it has been consumed).

### 1.4 Write idea.md

Write `{output_dir}/idea.md`:

```markdown
# Startup Idea

**Idea:** {idea description}
**Presets:** {comma-separated preset names, or "none"}
**Created:** {YYYY-MM-DD}
**Run name:** {slug}
```

### 1.5 Load Presets

For each preset name in `--preset` flags:
1. Read `${CLAUDE_SKILL_DIR}/../../presets/{name}.md`
2. Parse YAML frontmatter for `applies-to-stages` field
3. Store content + stage filter for injection during stage execution

If a preset file doesn't exist, warn the user and continue without it.

### 1.6 Determine Stages to Run

- Default: stages 1 through 6
- If `--from N`: stages N through 6
- If `--stage N`: only stage N
- `--stage` takes precedence over `--from` if both specified

## Phase 2: Stage Execution

For each stage to run, execute the following protocol.

### 2.1 Build Stage Context

Assemble the context payload for the stage agent:

1. **Idea description** from idea.md
2. **Preset content**: Concatenate all preset bodies whose `applies-to-stages` includes this stage number (or all presets if `applies-to-stages` is not set). Note: Presets provide domain context, not constraints. Agents should use relevant sections and ignore irrelevant ones (e.g., if a fintech preset includes remittance corridor data but the idea is about developer tools, the agent should focus on regulatory sections and disregard remittance-specific data).
3. **Previous stage reports**: For stages 2+, read any existing `stage-{N}-*.md` files from the output directory. If `--from` was used and prior reports don't exist, warn: "Note: No prior stage reports found on disk. Agent will work without prior context." and proceed.
4. **User-provided research**: If the user referenced files via `@file` or provided research documents during initialization (see 1.1b), include a "Research Context" section in the agent prompt. Summarize each document as a bullet-point list of key claims and data points (do not include full document content). Add the instruction: "Consider this prior research as context but stress-test its assumptions — do not accept claims at face value."

### 2.2 Standard Mode (no --deep)

Spawn the stage's dedicated agent using the Agent tool:

```
Agent(
  subagent_type: "startup:{agent-name}",
  description: "Stage {N}: {stage name}",
  prompt: "
    You are validating a startup idea. Here is your context:

    ## Idea
    {idea description}

    ## Domain Context (from presets)
    {concatenated preset content for this stage}

    ## Previous Stage Analysis
    {previous stage reports, or 'This is the first stage.' if stage 1}

    ## Research Context (user-provided)
    {bullet-point summaries of research docs, or omit this section if none}

    ## Instructions
    Analyze this idea from your expert perspective. Use the deep-research skill
    to search for real market data, competitors, regulations, and trends via EXA.

    Produce a structured report following the Stage Report Format.
    Include a confidence score (0-100) and a verdict (STRONG / MODERATE / WEAK).
    End with a recommendation: PROCEED / PROCEED WITH CAVEATS / ITERATE / STOP.
    Include a Confession section and a Sources section (see Stage Report Format).

    Write your report to: {output_dir}/stage-{N}-{stage-slug}.md
  "
)
```

**Stage agent mapping:**

| Stage | Agent | Slug |
|-------|-------|------|
| 1 | `market-validator` | `market-validation` |
| 2 | `feasibility-analyst` | `feasibility` |
| 3 | `product-designer` | `product-design` |
| 4 | `business-strategist` | `business-model` |
| 5 | `growth-strategist` | `go-to-market` |
| 6 | `execution-planner` | `execution-roadmap` |

### 2.2b Orchestrator Verification (Standard Mode)

After the agent writes its report, verify report quality before proceeding to the decision gate:

1. **File check**: Confirm the report file exists at the expected path.
2. **Section check**: Read the report and verify these required sections are present: Confidence score and Verdict in the header, Analysis, Key Findings, Risks & Concerns, Confession, Sources, Decision Gate.
3. **Sources check**: If the Sources section says "No external sources consulted" or is empty, log a warning: "Warning: Stage {N} report contains no external sources. Analysis may rely on stale training data."
4. **Substance check**: If the report contains fewer than 3 specific data points (numbers, dates, named entities), log a warning: "Warning: Stage {N} report appears to lack specific data. Consider re-running with --deep."

If any check fails, log the warning but still proceed to the decision gate. Never block the pipeline on verification warnings.

### 2.3 Deep Mode (--deep)

For each stage, spawn 3 parallel sub-agents using the Agent tool, then a critic to synthesize.

**Step A: Spawn 3 parallel sub-agents**

Launch all three in a single message (parallel execution):

```
Agent(
  subagent_type: "general-purpose",
  description: "Stage {N} - {sub-role-name}",
  prompt: "
    You are a {sub-role-persona} analyzing a startup idea.

    ## Idea
    {idea description}

    ## Domain Context
    {preset content}

    ## Previous Analysis
    {previous stage reports}

    ## Research Context (user-provided)
    {bullet-point summaries of research docs, or omit this section if none}

    ## Your Focus
    {sub-role-specific focus areas}

    Use the deep-research skill to search for real data via EXA.
    Produce a focused analysis document covering your area of expertise.
    Be critical, realistic, and evidence-based.
    List all URLs consulted in a Sources section at the end.
  "
)
```

**Sub-agent roles per stage:**

| Stage | Sub-Agent 1 | Sub-Agent 2 | Sub-Agent 3 |
|-------|-------------|-------------|-------------|
| 1 | Market Size Analyst: TAM/SAM/SOM, market growth, trends | Competitor Analyst: Existing players, market share, pricing, gaps | Demand Signal Analyst: User behavior, search trends, pain points, proxies |
| 2 | Regulatory Analyst: Licenses, compliance, legal barriers, jurisdiction | Technical Analyst: Architecture feasibility, complexity, infrastructure | Cost Analyst: Startup costs, operational costs, funding requirements |
| 3 | UX Designer: User journey, onboarding, key interactions, trust | Systems Architect: Technical architecture, integrations, scalability | Differentiation Analyst: Competitive positioning, unique value, moats |
| 4 | Revenue Modeler: Pricing models, revenue streams, projections | Unit Economics Analyst: CAC, LTV, margins, payback period | Moat Analyst: Defensibility, network effects, switching costs, brand |
| 5 | Channel Analyst: Acquisition channels, cost per channel, scalability | Partnership Analyst: Strategic partnerships, distribution deals | Viral/Growth Analyst: Growth loops, referral mechanics, organic growth |
| 6 | Roadmap Planner: MVP scope, timeline, milestones, phasing | Resource Analyst: Team requirements, tools, infrastructure needs | Risk Analyst: Execution risks, dependencies, contingency plans |

**Step B: Spawn validation-critic to synthesize**

After all 3 sub-agents complete, spawn the `validation-critic` agent:

```
Agent(
  subagent_type: "startup:validation-critic",
  description: "Stage {N}: Critic synthesis",
  prompt: "
    Synthesize the following parallel analyses for Stage {N} ({stage name})
    of the startup idea: {idea description}

    ## Sub-Agent 1 Analysis ({sub-role-1-name})
    {sub-agent-1-output}

    ## Sub-Agent 2 Analysis ({sub-role-2-name})
    {sub-agent-2-output}

    ## Sub-Agent 3 Analysis ({sub-role-3-name})
    {sub-agent-3-output}

    Produce a unified stage report following the Stage Report Format.
    Include the Confession section. Score confidence 0-100.
    Write to: {output_dir}/stage-{N}-{stage-slug}.md
  "
)
```

### 2.3b Orchestrator Verification (Deep Mode)

After the validation-critic writes the synthesized report, run the same verification as 2.2b: file check, section check, sources check, and substance check. Log warnings but never block the pipeline.

### 2.4 Decision Gate

After the stage report is written (standard or deep mode):

1. Read the stage report from disk
2. Extract the confidence score and recommendation

**If `--fast` mode**: Log the score and continue to next stage without pausing.

**If interactive mode**: Present findings and ask the user:

```
AskUserQuestion(
  questions: [{
    question: "Stage {N} ({stage name}) complete. Confidence: {score}/100 — {verdict}. How do you want to proceed?",
    header: "Stage {N}",
    options: [
      { label: "PROCEED", description: "Move to Stage {N+1}" },
      { label: "ITERATE", description: "Re-run Stage {N} with the same idea" },
      { label: "PIVOT", description: "Refine the idea and re-run from this stage" },
      { label: "PAUSE", description: "Save progress and resume later" },
      { label: "STOP", description: "End the pipeline and generate a partial summary" }
    ]
  }]
)
```

If approximate stage duration is available, include it in the presentation: "Stage completed in approximately N minutes."

**Handle response:**
- **PROCEED**: Continue to next stage
- **ITERATE**: Re-run the current stage (go back to 2.1)
- **PIVOT**: Ask the user for a refined idea description, update idea.md, re-run from this stage
- **PAUSE**: Write `{output_dir}/pipeline-state.json` (see schema below), then jump to Phase 3 with `partial: true`. Display resume command: `/startup-validate --from {next_stage} --name {slug}`
- **STOP**: Jump to Phase 3 (summary generation)

**pipeline-state.json schema** (written on PAUSE):

```json
{
  "slug": "{slug}",
  "idea": "{idea description}",
  "completed_stages": [1, 2],
  "next_stage": 3,
  "mode": "standard|deep|fast",
  "presets": ["fintech", "cape-verde"],
  "paused_at": "YYYY-MM-DD",
  "scores": {
    "1": { "confidence": 62, "verdict": "MODERATE" },
    "2": { "confidence": 75, "verdict": "STRONG" }
  }
}
```

## Phase 3: Summary Generation

After all stages complete, STOP is chosen, or PAUSE is chosen:

### 3.1 Generate summary.md

Read all existing stage reports from `{output_dir}/`. For each, extract the confidence score and verdict.

Write `{output_dir}/summary.md`:

```markdown
# Startup Validation Summary: {Idea Name}

**Idea:** {description}
**Date:** {YYYY-MM-DD}
**Mode:** {standard|deep} | **Presets:** {preset names}

## Scorecard

| Stage | Confidence | Verdict |
|-------|-----------|---------|
| 1. Market Validation | {score}/100 | {verdict} |
| 2. Feasibility | {score}/100 | {verdict} |
| 3. Product Design | {score}/100 | {verdict} |
| 4. Business Model | {score}/100 | {verdict} |
| 5. Go-to-Market | {score}/100 | {verdict} |
| 6. Execution | {score}/100 | {verdict} |

**Overall: {average}/100 — {overall verdict}**
**Stages completed:** {N of 6} | **Mode:** {standard|deep|fast}

## Critical Risks
1. {Highest risk from across all stage reports}
2. {Second highest risk}
3. {Third highest risk}

## Strongest Signals
1. {Strongest positive signal}
2. {Second strongest}

## Recommended Next Steps
- {Actionable next step 1}
- {Actionable next step 2}
- {Actionable next step 3}
```

**Overall verdict thresholds:**
- 80+: STRONG — PROCEED
- 60-79: MODERATE — PROCEED WITH CAUTION
- 40-59: WEAK — SIGNIFICANT CONCERNS
- Below 40: POOR — CONSIDER PIVOTING

Only include rows for stages that were actually run. For early exits:
- If paused: "Pipeline paused after Stage {N}. Resume with: `/startup-validate --from {next_stage} --name {slug}`"
- If stopped: "Pipeline stopped after Stage {N}. Remaining stages not evaluated."

### 3.2 Update Index

Read or create `startup-validation/README.md`. Add/update an entry for this run:

```markdown
# Startup Validation Runs

| Run | Idea | Date | Stages | Overall | Status | Link |
|-----|------|------|--------|---------|--------|------|
| {slug} | {idea short} | {date} | {1-N} | {score}/100 | {Complete/In Progress/Stopped} | [View](./{slug}/summary.md) |
```

### 3.3 Present Results

Display the summary scorecard to the user. If any stage scored below 60, highlight it as needing attention.

## Stage Report Format

All stage agents must produce reports following this structure:

```markdown
# Stage {N}: {Stage Name}

**Idea:** {idea description}
**Presets:** {preset names}
**Date:** {YYYY-MM-DD}
**Confidence:** {0-100}/100
**Verdict:** {STRONG|MODERATE|WEAK} OPPORTUNITY

## Analysis

{Stage-specific structured analysis with subsections matching the agent's focus areas}

## Key Findings

- {Finding 1 with evidence}
- {Finding 2 with evidence}
- {Finding 3 with evidence}

## Risks & Concerns

- {Risk 1 with severity assessment}
- {Risk 2 with severity assessment}

## Confession

- **Assumptions:** {what was assumed without verification}
- **Uncertainties:** {areas where confidence is low}
- **Missing Data:** {what couldn't be found via research}

In standard mode, keep the Confession section concise (3-5 bullet points total). In deep mode, be comprehensive.

## Sources

- {URL 1} — {brief description of what was found}
- {URL 2} — {brief description}

_List all URLs consulted via deep-research. If no external sources were consulted, state: "No external sources consulted — analysis based on training data."_

## Decision Gate

- **Recommendation:** {PROCEED|PROCEED WITH CAVEATS|ITERATE|STOP}
- **Caveats:** {what to watch for in subsequent stages}

---
*Generated by startup-validate | Mode: {standard|deep} | Presets: {list}*
```
