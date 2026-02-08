# Strategic DDD Patterns

Strategic DDD focuses on the problem space—understanding the domain before writing code.

## Table of Contents

- [Subdomains](#subdomains)
  - [Core Domain](#core-domain)
  - [Supporting Domain](#supporting-domain)
  - [Generic Domain](#generic-domain)
  - [Subdomain Identification Questions](#subdomain-identification-questions)
- [Bounded Contexts](#bounded-contexts)
  - [Key Principles](#key-principles)
  - [Problem Space vs Solution Space](#problem-space-vs-solution-space)
  - [Identifying Bounded Context Boundaries](#identifying-bounded-context-boundaries)
  - [Bounded Context Design Checklist](#bounded-context-design-checklist)
- [Context Mapping Patterns](#context-mapping-patterns)
  - [Partnership](#partnership)
  - [Shared Kernel](#shared-kernel)
  - [Customer-Supplier](#customer-supplier)
  - [Conformist](#conformist)
  - [Anticorruption Layer (ACL)](#anticorruption-layer-acl)
  - [Open Host Service](#open-host-service)
  - [Published Language](#published-language)
  - [Separate Ways](#separate-ways)
  - [Context Map Decision Framework](#context-map-decision-framework)
- [Event Storming](#event-storming)
  - [Color Coding](#color-coding)
  - [Three Zoom Levels](#three-zoom-levels)
  - [Facilitation Tips](#facilitation-tips)
  - [Event Storming Outcomes](#event-storming-outcomes)

---

## Subdomains

Subdomains classify business capabilities by strategic importance.

### Core Domain
- **What**: Competitive advantage—what makes the organization unique
- **Investment**: Maximum effort, best developers, custom from scratch
- **Examples**: Spotify's recommendation engine, trading platform's execution logic, ad platform's optimization
- **Decision**: If competitors could buy this off-the-shelf, it's not core

### Supporting Domain
- **What**: Necessary for core to function but doesn't differentiate
- **Investment**: Custom development, quality tradeoffs acceptable
- **Examples**: E-commerce inventory management, streaming playlist management
- **Decision**: Required but no market advantage

### Generic Domain
- **What**: Commodity functionality, all companies operate identically
- **Investment**: Buy off-the-shelf, open-source, or outsource
- **Examples**: Authentication, email notifications, accounting (regulated)
- **Note**: Same capability can be different types for different companies (identity is generic for e-commerce but core for Okta)

### Subdomain Identification Questions
1. What makes us different from competitors?
2. What would we never outsource?
3. Where do domain experts spend their time?
4. What capabilities could we buy instead of build?

---

## Bounded Contexts

A bounded context is where a domain model and ubiquitous language remain consistent.

### Key Principles
- **Same term, different meaning**: "Order" means different things in Sales, Shipping, Accounting
- **Each context owns its model**: Duplicating concepts across contexts is acceptable
- **Linguistic boundary**: When language changes, you've crossed a boundary

### Problem Space vs Solution Space
- **Subdomain** = Problem space (what problems exist)
- **Bounded Context** = Solution space (how we solve them)
- Not necessarily 1:1—a subdomain can have multiple bounded contexts

### Identifying Bounded Context Boundaries

**Language signals:**
- Terms have different meanings to different teams
- Domain experts from different areas use different vocabulary
- Confusion when teams discuss the same concept

**Organizational signals:**
- Different teams own different parts
- Different business processes
- Different rates of change

**Technical signals:**
- Different data models for same concept
- Multiple motivations for change in one area
- Teams stepping on each other's code

### Bounded Context Design Checklist
- [ ] Single ubiquitous language within context
- [ ] Clear owner (team or individual)
- [ ] Explicit public interface for external communication
- [ ] Internal model hidden from other contexts
- [ ] Context map documents relationships

---

## Context Mapping Patterns

Context maps document relationships between bounded contexts, from tight to loose coupling.

### Partnership
- **When**: Two teams must succeed or fail together
- **How**: Coordinated planning, joint meetings
- **Tradeoff**: High coordination cost, tight coupling
- **Use when**: Contexts evolve together frequently

### Shared Kernel
- **When**: Small, explicit subset of model shared between teams
- **How**: Shared code/schema, changes require consultation
- **Tradeoff**: Coupling through shared code, coordination overhead
- **Keep it minimal**: Large shared kernels become Big Ball of Mud

### Customer-Supplier
- **When**: Upstream team accommodates downstream needs
- **How**: Downstream specifies requirements, upstream prioritizes
- **Tradeoff**: Upstream team must balance multiple customers
- **Formalize**: Explicit contracts, regular communication

### Conformist
- **When**: Downstream adopts upstream model wholesale
- **How**: No translation layer, direct use of upstream model
- **Tradeoff**: Tight coupling, no protection from upstream changes
- **Use when**: Upstream model is good enough, translation cost too high

### Anticorruption Layer (ACL)
- **When**: Upstream model would corrupt downstream model integrity
- **How**: Translation layer isolates downstream from foreign concepts
- **Tradeoff**: Development overhead, maintenance of translation
- **Essential for**: Legacy integration, external services, model mismatch

### Open Host Service
- **When**: Many consumers need the same upstream functionality
- **How**: Well-defined API protocol, versioned contracts
- **Tradeoff**: API stability requirements, versioning complexity
- **Use when**: Multiple downstream contexts need same data

### Published Language
- **When**: Standard format for exchange between contexts
- **How**: Documented schema (JSON, Protobuf, industry standard)
- **Combine with**: Open Host Service for complete solution

### Separate Ways
- **When**: No integration at all
- **How**: Contexts evolve independently
- **Use when**: Integration cost exceeds benefit, truly separate domains

### Context Map Decision Framework

```
Do models share concepts?
├── No → Separate Ways
└── Yes → Do we control both sides?
    ├── No → Must we adapt?
    │   ├── Yes, model is good → Conformist
    │   └── No, protect our model → ACL
    └── Yes → How tightly coupled?
        ├── Very tight → Partnership or Shared Kernel
        └── Upstream/downstream → Customer-Supplier + Open Host
```

---

## Event Storming

Alberto Brandolini's technique for rapid domain discovery.

### Color Coding
- **Orange**: Domain events (past tense: "Order Placed")
- **Blue**: Commands (what triggers events)
- **Yellow**: Actors (who/what issues commands)
- **Pink**: Hot spots (problems, questions, risks)
- **Purple**: Policies (reactions: "When X happens, do Y")
- **Green**: Read models (data needed for decisions)
- **Pale yellow**: Aggregates (clusters of events)

### Three Zoom Levels

**Big Picture** (1-2 days)
- 25-30 participants across business
- Explore entire business lines
- Identify opportunities and boundaries
- Output: Subdomain candidates, bounded context hints

**Process Modeling** (half day)
- Focused on specific business process
- More rigorous grammar
- Output: Detailed process flow, policies identified

**Software Design** (hours)
- Add aggregates and commands
- Bridge business and technical concerns
- Output: Aggregate candidates, bounded context boundaries

### Facilitation Tips
1. Start with domain events (what happened?)
2. Use reverse narrative—work backward to find hidden events
3. Mark hot spots, don't solve them immediately
4. Look for pivotal events that change business state
5. Identify where language changes (bounded context hints)

### Event Storming Outcomes
- Shared understanding across business and tech
- Discovered subdomain boundaries
- Aggregate identification
- Foundation for ubiquitous language
- Hot spots for further investigation
