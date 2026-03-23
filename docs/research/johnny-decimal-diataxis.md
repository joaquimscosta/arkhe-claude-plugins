---
title: "Synthesizing Johnny.Decimal and the Diataxis Documentation Framework"
version: "1.0.0"
status: Published
created: 2026-03-23
last_updated: 2026-03-23
---

# Synthesizing Johnny.Decimal and the Diataxis Documentation Framework

## Executive Summary

Two systems have emerged for managing information in modern software projects: **Johnny.Decimal** addresses the structural "where" through numeric constraints and hierarchical rigor, while **Diataxis** addresses the cognitive "what" by categorizing documentation based on user needs. Used in isolation, Johnny.Decimal produces a "well-organized library of bad books" and Diataxis produces "great books scattered randomly on the floor." Combined — with Johnny.Decimal as the container and Diataxis as the classifier — they form a complete information architecture where every document has both a unique numeric ID and a clear functional purpose. This integration reduces the time developers spend seeking information, improves onboarding, and creates bidirectional links between code and documentation that survive refactoring.

---

## The Johnny.Decimal System

The Johnny.Decimal system replaces subjective folder naming with a deterministic numeric hierarchy. It imposes a "no more than ten" rule at the top two levels, forcing consolidation over redundant silos.

### Structure

The system uses `AC.ID` notation (Area-Category.ID) across three nested levels:

| Level | Range | Analog | Description |
| :--- | :--- | :--- | :--- |
| **Area** | 10-99 | The Shelf | Broadest grouping, organized into blocks of ten |
| **Category** | 11-19, 21-29, etc. | The Box | Similar work types within an Area |
| **ID** | 11.01-11.99 | The Folder | Specific documents or files |

No file is ever more than two levels deep from its category, preventing infinite nesting. Areas (10-19, 20-29, etc.) represent fundamental divisions like "Engineering" or "Legal." Categories subdivide Areas (e.g., within Engineering 40-49: category 41 = Backend, 42 = Frontend). IDs are two-digit counters (.01-.99) for specific artifacts.

### Cognitive Principles

By limiting choices to ten at each junction, the system reduces the cognitive load of filing and retrieval decisions. Creating a new category consumes a limited slot, encouraging consolidation. The numeric identifiers provide stable, "speakable" reference points — "Project 42.11" is more precise than `Docs/Eng/Archive/2023/Project_Alpha_Final_v2`.

## The Diataxis Documentation Framework

Diataxis combats the "tendency to collapse" — where documentation becomes an unusable mixture of history, instructions, and facts — by classifying content based on its relationship to human action and cognition.

### The Four Quadrants

Documentation is organized along two axes: Action vs. Cognition, and Study vs. Work.

| Quadrant | Orientation | User State | Goal |
| :--- | :--- | :--- | :--- |
| **Tutorials** | Learning-oriented | Study (Action) | Building confidence through guided practice |
| **How-to Guides** | Problem-oriented | Work (Action) | Solving a specific real-world problem |
| **Reference** | Information-oriented | Work (Cognition) | Providing complete, accurate facts about the system |
| **Explanation** | Understanding-oriented | Study (Cognition) | Clarifying concepts and the "why" behind decisions |

Tutorials are lessons for beginners in controlled scenarios. How-to guides are recipes for competent users. Reference is the dictionary — exhaustive detail without distraction. Explanations provide the bigger picture and conceptual background.

### Quadrant Purity

A key insight: documentation "quality" is a function of alignment with these quadrants, not prose quality. Including architectural explanations inside a tutorial creates cognitive friction. Separating the four types allows the correct "voice" for each — authoritative for reference, encouraging for tutorials.

## Comparative Analysis

Johnny.Decimal and Diataxis operate at different levels of the information stack. Johnny.Decimal is a system of **location**; Diataxis is a system of **intent**.

| Feature | Johnny.Decimal | Diataxis |
| :--- | :--- | :--- |
| **Primary Domain** | File systems, email, physical storage | Documentation sites, wikis, manuals |
| **Structural Logic** | Numeric hierarchy (10x10x100) | Functional quadrant based on cognitive axes |
| **Key Constraint** | Limited slots (10 per level) | Strict separation of four content modes |
| **Strength** | Fast retrieval and stable path referencing | Improved usability and clearer authoring |
| **Limitation** | Rigid; renumbering is difficult | Does not provide a file-storage strategy |
| **Typical Use Case** | Corporate shared drives, personal knowledge bases | Open-source project documentation |

## Integrated Strategy

The integration strategy dedicates specific Johnny.Decimal Categories (within a Documentation Area) to the four Diataxis quadrants.

### Category-to-Quadrant Mapping

| JD Category | Diataxis Quadrant | Guideline |
| :--- | :--- | :--- |
| **41 Tutorials** | Tutorials | Sequential lessons; no abstract theory |
| **42 Recipes** | How-to Guides | Problem-titled files (e.g., "How to solve X") |
| **43 Specifications** | Reference | Tabular data, API endpoints, schema facts |
| **44 Concepts** | Explanation | Narrative prose on architecture and "the why" |

### Governance

Two mechanisms maintain the system: the **JDex** (a master index listing every ID, its title, and its Diataxis quadrant) and the **Librarian** role (a team member who approves new IDs and prevents "quadrant bleed").

### Case Study: AuraStream API Platform

An illustrative implementation for a SaaS data streaming platform:

**Area Map:**
- 10-19: Project Management & Governance
- 20-29: Legal & Financial
- 30-39: Core Infrastructure (Terraform, CI/CD)
- **40-49: Technical Documentation (Diataxis Area)**
- 50-59: Product Development (Source Code)

**Documentation Tree (Area 40-49):**

```
40-49 Technical Documentation
├── 41 Tutorials (Learning-Oriented)
│   ├── 41.01 Getting Started: Your First Stream in 5 Minutes
│   ├── 41.02 Skill-Building: Mastering Filter Expressions
│   └── 41.03 Collaborative Streaming: Team Workflows
├── 42 How-to Guides (Problem-Oriented)
│   ├── 42.01 How to Authenticate using JWT and OAuth2
│   ├── 42.02 How to Handle Backpressure in High-Volume Streams
│   ├── 42.03 How to Migrate from Version 1.2 to 2.0
│   └── 42.04 How to Configure Custom Webhook Endpoints
├── 43 Technical Reference (Information-Oriented)
│   ├── 43.01 REST API Endpoints: Complete Schema
│   ├── 43.02 Error Code Dictionary and Mitigation Steps
│   ├── 43.03 CLI Command Reference: aura-tools v3
│   └── 43.04 Environment Variables and Config Parameters
└── 44 Explanations (Understanding-Oriented)
    ├── 44.01 Why AuraStream uses Eventual Consistency
    ├── 44.02 The Architecture of Our Edge Computing Layer
    └── 44.03 Design Principles: Security and Zero-Trust
```

A new developer follows a deterministic path: **41.01** for onboarding, **42.02** for solving backpressure in production, **43.01** for a timestamp field format, **44.01** for understanding consistency trade-offs. Numeric prefixes can be used in code comments (e.g., `// Refer to docs ID 42.01 for JWT renewal logic`), creating bidirectional links that survive refactoring.

## Best Practices

| Practice | Rationale |
| :--- | :--- |
| **Strict Category Limits** | Ten categories per area keeps top-level navigation within human short-term memory |
| **Quadrant Discipline** | Never mix reference facts into a tutorial; use hyperlinks to bridge quadrants |
| **One Source of Truth** | Each document exists at exactly one ID — no duplication across IDs |
| **Predictable File Naming** | Use IDs as prefixes (e.g., `43.01_API_Endpoints.md`) for natural sort order |
| **Maintenance Cycle** | Regularly review the JDex for orphaned IDs or categories exceeding their ten-slot limit |

As projects grow, "number exhaustion" is managed through **Area Expansion** (promoting a category to its own area) or **SYS.AC.ID notation**. For documentation, Diataxis recommends layered hierarchies where a guide serves as a landing page for more specific sub-guides.

## Common Pitfalls

### Structural Failures

**The Shallow System**: IDs created without meaningful categories, producing a flat list of 100 items. Mitigate with a mandatory sorting session once a category reaches twenty IDs.

**Subjective Numbering**: Different team members assign numbers based on personal importance. The JDex must be a shared, collaborative document.

### Content Failures

**The Collapsed Document**: A single README containing the installation guide, API table, and project history. Mitigate with standard templates per quadrant that force authors to separate non-conforming content.

### Integration Failures

**Desynchronization**: Numeric IDs in the file system no longer match titles on the documentation site. Solve by using the JD ID as the permanent URL slug or unique identifier in documentation metadata (e.g., Markdown front matter).

## References

1. A system to organise your life - Johnny.Decimal, accessed March 22, 2026, <https://johnnydecimal.com/>
2. Start here - Diataxis in five minutes - Diataxis, accessed March 22, 2026, <https://diataxis.fr/start-here/>
3. Diataxis framework, accessed March 22, 2026, <https://diataxis.fr/>
4. 11.04 Philosophy - Johnny.Decimal, accessed March 22, 2026, <https://johnnydecimal.com/10-19-concepts/11-core/11.04-philosophy/>
5. What's the appeal of Johnny Decimal? : r/ObsidianMD - Reddit, accessed March 22, 2026, <https://www.reddit.com/r/ObsidianMD/comments/1fmbkbe/whats_the_appeal_of_johnny_decimal/>
6. TIL: Johnny Decimal Organization System - Stonecharioteer on Tech, accessed March 22, 2026, <https://tech.stonecharioteer.com/posts/2021/til-johnny-decimal-organization-system/>
7. 10-19 Concepts - Johnny.Decimal, accessed March 22, 2026, <https://johnnydecimal.com/10-19-concepts/>
8. 11.02 Areas and categories - Johnny.Decimal, accessed March 22, 2026, <https://johnnydecimal.com/10-19-concepts/11-core/11.02-areas-and-categories/>
9. How to Organize Confluence: Johnny Decimal and Maps of Content, accessed March 22, 2026, <https://www.guildmasterconsulting.com/post/how-to-organize-confluence-johnny-decimal-and-maps-of-content>
10. The Johnny Decimal System | Chris Johns, accessed March 22, 2026, <https://chrisjohns.me/posts/the-johnny-decimal-system/>
11. Add an example for Johnny.Decimal - Issue #10 - roboyoshi/datacurator-filetree - GitHub, accessed March 22, 2026, <https://github.com/roboyoshi/datacurator-filetree/issues/10>
12. Documentation Quadrants - The Grand Unified Theory of ..., accessed March 22, 2026, <https://dunnhq.com/posts/2023/documentation-quadrants/>
13. Diataxis: A Systematic Approach to Technical Documentation Authoring, accessed March 22, 2026, <https://bssw.io/items/diataxis-a-systematic-approach-to-technical-documentation-authoring>
14. What is Diataxis and should you be using it with your documentation ..., accessed March 22, 2026, <https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework>
15. How I mixed Johnny Decimal and Second Brain to organize my documents | Luca Franceschini, accessed March 22, 2026, <https://lucaf.eu/2023/02/23/luca-decimal.html>
16. Information architecture and docs structure : r/technicalwriting - Reddit, accessed March 22, 2026, <https://www.reddit.com/r/technicalwriting/comments/127eugy/information_architecture_and_docs_structure/>
17. Ask HN: How do you manage your companies knowledge base? - Hacker News, accessed March 22, 2026, <https://news.ycombinator.com/item?id=30371723>
18. Help creating a Johnny.Decimal example filetree : r/datacurator - Reddit, accessed March 22, 2026, <https://www.reddit.com/r/datacurator/comments/aglbq6/help_creating_a_johnnydecimal_example_filetree/>
19. File Naming Conventions - Harvard Biomedical Data Management, accessed March 22, 2026, <https://datamanagement.hms.harvard.edu/plan-design/file-naming-conventions>
20. Is Johnny Decimal a good way to go? : r/datacurator - Reddit, accessed March 22, 2026, <https://www.reddit.com/r/datacurator/comments/16qz77p/is_johnny_decimal_a_good_way_to_go/>
21. Folder Structure Standards, accessed March 22, 2026, <https://www.lcc.edu/its/records-management/documents/lcc-folder-structure-standards-112321.docx>
22. Areas and categories advice needed - 14 Build and learn - Johnny.Decimal forum, accessed March 22, 2026, <https://forum.johnnydecimal.com/t/areas-and-categories-advice-needed/2178>
23. Diataxis in complex hierarchies - Diataxis, accessed March 22, 2026, <https://diataxis.fr/complex-hierarchies/>
24. Tech Habits: How I Moved Into My Johnny Decimal (and Obsidian Bases) System for Organizing Notes | by Geet Duggal | Medium, accessed March 22, 2026, <https://medium.com/@geetduggal/tech-habits-how-i-moved-into-my-johnny-decimal-and-obsidian-bases-system-for-organizing-notes-6bc7a00747e7>
