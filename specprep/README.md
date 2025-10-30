# SpecPrep Plugin

**SpecPrep** is an AI meta-prompt framework that optimizes text and files for use with the [Spec Kit](https://github.com/github/spec-kit) workflow.  
It preprocesses inputs to ensure clarity, compliance, and structure before they are passed into the main `/speckit` commands.

---

## 🧭 Overview

SpecPrep provides a set of namespaced slash commands that prepare your content for Spec Kit’s three key stages of Spec-Driven Development (SDD):

| Command | Purpose | Target Command |
|----------|----------|----------------|
| `/specprep:specify` | Cleans and structures raw feature ideas into well-formed specifications | `/speckit:specify` |
| `/specprep:plan` | Validates and refines implementation plans for architectural compliance | `/speckit:plan` |
| `/specprep:tasks` | Extracts and organizes executable tasks from plans and research | `/speckit:tasks` |

Each command acts as a **meta-prompt optimizer**, enforcing SDD best practices such as:

- Clear "WHAT and WHY" separation from "HOW"
- Proper abstraction levels
- `[NEEDS CLARIFICATION]` tagging for ambiguity
- Compliance with the project constitution (Articles VII–IX)

---

## ⚙️ Usage Examples

```bash
/specprep:specify @notes/feature-idea.txt
/specprep:plan @specs/002-feature/plan.md
/specprep:tasks @specs/002-feature/plan.md @specs/002-feature/research.md
```

Each command outputs optimized text ready for immediate use:

```bash
/speckit:specify [optimized text]
/speckit:plan [optimized text]
/speckit:tasks [optimized text]
```

---

## 💡 Workflow Integration

Typical Spec Kit + SpecPrep pipeline:

```bash
/specprep:specify @drafts/feature.txt
→ /speckit:specify

/specprep:plan @specs/002-feature/spec.md
→ /speckit:plan

/specprep:tasks @specs/002-feature/plan.md
→ /speckit:tasks
```

This architecture ensures that every phase of Spec-Driven Development begins with clean, validated input — turning raw ideas into executable specifications with maximum quality and minimal noise.

---

## 📚 Reference Documentation

For detailed information about Spec-Driven Development and the Spec Kit workflow:

- **[Quick Start Guide](docs/quickstart.md)** - 4-step SDD workflow with complete examples
- **[Spec-Driven Development](docs/spec-driven.md)** - Methodology, philosophy, and constitutional framework
- **[Documentation Index](docs/README.md)** - Overview of all reference materials

These documents from [GitHub's Spec Kit](https://github.com/github/spec-kit) provide the context and principles that SpecPrep enforces through its meta-prompt optimization.

---

## 📦 Installation

```bash
# Add the Arkhe marketplace (if not already added)
/plugin marketplace add ./arkhe-claude-plugins

# Install the SpecPrep plugin
/plugin install specprep@arkhe-claude-plugins

# Verify installation
/help  # Commands will appear as /specprep:*
```

---

## 🧩 Notes

- These commands are plugin-scoped and will appear as `/specprep:*` in `/help`.
- They are designed for **text optimization**, not code generation.
- Outputs are formatted for **direct use** with Spec Kit commands.
- **Dependency**: Designed to work with the Spec Kit plugin. While SpecPrep can be used standalone for text optimization, its primary value is in preparing inputs for Spec Kit commands.
