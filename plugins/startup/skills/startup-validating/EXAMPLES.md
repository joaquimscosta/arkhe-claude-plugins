# Startup Validation — Examples

## Basic Usage

### Validate a simple idea

```bash
/startup-validate "A mobile app that helps freelancers track expenses and send invoices"
```

Runs all 6 stages with human-in-the-loop decision gates. No presets — uses general knowledge.

### Validate from a research brief

```bash
/startup-validate @research-brief.md
```

Reads the idea description and any research context from the file. The orchestrator extracts the idea and asks you to confirm mode and presets interactively.

### Validate with file and flags

```bash
/startup-validate @idea.md --preset fintech --preset cape-verde --deep
```

Combines file-based idea input with explicit CLI flags. Since flags are provided, the orchestrator skips interactive confirmation for mode and presets.

### Validate with domain presets

```bash
/startup-validate "NôsPay — a remittance app for the US-Cape Verde diaspora" --preset fintech --preset cape-verde
```

Injects fintech regulatory context and Cape Verde market data into relevant stages.

## Advanced Usage

### Fast mode (autonomous)

```bash
/startup-validate "AI-powered code review tool for small teams" --preset saas --fast
```

Runs all 6 stages without pausing. Produces full scorecard at the end.

### Deep mode (parallel specialists)

```bash
/startup-validate "NôsPay" --preset fintech --preset cape-verde --deep
```

Each stage spawns 3 parallel specialist sub-agents. A validation critic synthesizes findings with Confession Pattern and confidence scoring.

### Resume from a specific stage

```bash
/startup-validate "NôsPay" --from 3 --name nospay
```

Reads Stage 1-2 reports from `startup-validation/nospay/` and continues from Stage 3.

### Run a single stage

```bash
/startup-validate "NôsPay" --stage 4 --name nospay
```

Runs only Stage 4 (Business Model). Useful for revisiting specific areas after pivoting.

### Named run

```bash
/startup-validate "POS system for Cape Verde SMEs" --name pos-system
```

Saves output to `startup-validation/pos-system/` instead of auto-generated slug.

## Typical Workflow

1. **First pass** (interactive): `/startup-validate "idea" --preset fintech`
2. **Review Stage 1**: If market looks weak, PIVOT or refine the idea
3. **Continue**: PROCEED through remaining stages
4. **Pause for later**: At any decision gate, choose PAUSE to save progress
5. **Resume later**: `/startup-validate --from 3 --name my-idea` (auto-loads saved state from `pipeline-state.json`)
6. **Deep dive on weak areas**: `/startup-validate "idea" --stage 2 --deep --name my-idea`
7. **Final scorecard**: Check `startup-validation/my-idea/summary.md`
