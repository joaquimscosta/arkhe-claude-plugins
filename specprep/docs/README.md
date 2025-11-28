# SpecPrep Reference Documentation

This directory contains reference documentation from GitHub's **Spec Kit** project, which defines the Specification-Driven Development (SDD) methodology that SpecPrep is designed to support.

## Contents

### [quickstart.md](quickstart.md)
A practical guide to the 4-step Spec-Driven Development workflow:
1. **Install Specify** - Project initialization
2. **Create the Spec** - Define WHAT and WHY (via `/speckit:specify`)
3. **Create Technical Plan** - Specify HOW (via `/speckit:plan`)
4. **Break Down and Implement** - Generate tasks (via `/speckit:tasks`)

Includes a detailed example of building "Taskify", a team productivity platform, with complete workflow demonstration.

### [spec-driven.md](spec-driven.md)
Comprehensive philosophy and methodology document covering:
- **The Power Inversion** - Why specifications should drive code, not vice versa
- **SDD Workflow in Practice** - How specifications become executable artifacts
- **Core Principles** - Executable specifications, continuous refinement, research-driven context
- **The Constitutional Framework** - Nine articles of development (library-first, CLI interfaces, test-first, etc.)
- **Template-Driven Quality** - How structure constrains LLMs for better outcomes
- **Implementation Approaches** - Practical guidance for practicing SDD

## How SpecPrep Fits In

**SpecPrep** serves as a meta-prompt optimization layer that prepares your inputs to be compliant with Spec Kit's standards:

- `/specprep:specify` - Cleans and structures raw feature ideas for `/speckit:specify`
- `/specprep:plan` - Validates architectural compliance for `/speckit:plan`
- `/specprep:tasks` - Organizes and parallelizes tasks for `/speckit:tasks`

Think of SpecPrep as quality control that ensures your inputs meet SDD principles before they enter the Spec Kit workflow.

## Source

These documents are sourced from the official [github/spec-kit](https://github.com/github/spec-kit) repository:

- **quickstart.md**: https://github.com/github/spec-kit/blob/main/docs/quickstart.md
- **spec-driven.md**: https://github.com/github/spec-kit/blob/main/spec-driven.md

**Last synced**: October 29, 2025

For the latest versions and updates, visit the [upstream repository](https://github.com/github/spec-kit).

## Key Concepts Reference

### Specification-Driven Development (SDD)
A methodology where specifications become the primary artifact and code becomes their expression. Instead of specs serving code, code serves specifications.

### The Three Commands
1. **`/speckit:specify`** - Transforms feature descriptions into structured specifications
2. **`/speckit:plan`** - Generates implementation plans with constitutional compliance
3. **`/speckit:tasks`** - Derives executable task lists from plans

### Constitutional Framework
Nine articles that govern development:
- **Article I**: Library-First Principle
- **Article II**: CLI Interface Mandate
- **Article III**: Test-First Imperative
- **Article VII**: Simplicity (≤3 projects)
- **Article VIII**: Anti-Abstraction (use frameworks directly)
- **Article IX**: Integration-First Testing

### `[NEEDS CLARIFICATION]` Markers
Explicit uncertainty markers used throughout specifications to highlight ambiguities rather than making assumptions.

## License & Attribution

All content in this directory is sourced from [github/spec-kit](https://github.com/github/spec-kit). Please refer to the upstream repository for licensing information.

**SpecPrep** is an independent plugin that complements Spec Kit by providing input optimization capabilities.
