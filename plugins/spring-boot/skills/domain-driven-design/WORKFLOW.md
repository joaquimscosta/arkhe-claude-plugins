# Domain-Driven Design Workflow

Detailed step-by-step process for applying DDD to a software system.

---

## Step 1: Domain Discovery

Identify subdomains and their strategic importance.

### 1a. Engage Domain Experts

- Schedule domain expert interviews or Event Storming sessions
- Focus on understanding business processes, not technical implementation
- Document domain terminology — this becomes your **ubiquitous language**

### 1b. Identify Subdomains

Classify each area of the business:

| Subdomain Type | Investment Level | Strategy |
|---------------|-----------------|----------|
| **Core** | Maximum — competitive advantage | Custom development with DDD tactical patterns |
| **Supporting** | Moderate — needed but not differentiating | Simpler patterns, quality tradeoffs OK |
| **Generic** | Minimal — commodity | Buy/outsource (auth, email, payments) |

### 1c. Event Storming (Optional but Recommended)

1. Gather domain experts and developers
2. Identify **domain events** (past tense: "Order Placed", "Payment Received")
3. Group events by business process
4. Identify **commands** that trigger events
5. Identify **aggregates** that handle commands
6. Draw boundaries where language or process changes

**Output**: Subdomain map with strategic classification and initial event flow.

---

## Step 2: Bounded Context Definition

Draw boundaries where the ubiquitous language changes.

### 2a. Identify Language Boundaries

Signs you need a boundary:
- Same word means different things to different teams (e.g., "Account" in billing vs. authentication)
- Different teams own different parts of the process
- Data models diverge significantly
- Deployment or scaling requirements differ

### 2b. Define Context Boundaries

For each bounded context:
- Name it using the ubiquitous language of that context
- List the aggregates, entities, and value objects it owns
- Define its public API (what it exposes to other contexts)
- Identify its internal model (hidden from other contexts)

### 2c. Create Context Map Diagram

Visualize relationships between contexts:

```
+---------------+     +---------------+
|    Orders     |---->|   Inventory   |
|    (Core)     |     |  (Supporting) |
+---------------+     +---------------+
       |
       v
+---------------+
|   Payments    |
|   (Generic)   |
+---------------+
```

**Output**: Context map showing boundaries and relationships.

---

## Step 3: Context Mapping

Define integration patterns between bounded contexts.

### 3a. Choose Integration Pattern

| Pattern | When to Use | Direction |
|---------|-------------|-----------|
| **Shared Kernel** | Two teams co-own a small model | Bidirectional |
| **Customer-Supplier** | Upstream provides, downstream consumes | Upstream to Downstream |
| **Conformist** | Downstream adopts upstream's model as-is | Upstream to Downstream |
| **Anti-Corruption Layer (ACL)** | Protect your model from external changes | Downstream defense |
| **Published Language** | Standardized format (e.g., JSON schema) | Between contexts |
| **Open Host Service** | Expose a well-defined protocol | Upstream provides |
| **Separate Ways** | No integration needed | Independent |

### 3b. Document Integration Contracts

For each integration:
1. Which contexts are involved?
2. What data flows between them?
3. What pattern is used?
4. Who owns the contract?
5. How are changes negotiated?

### 3c. Implement Integration

- **Events** (preferred): Domain events for loose coupling — see `spring-boot-modulith` skill
- **API calls**: REST/gRPC for synchronous needs — see `spring-boot-web-api` skill
- **ACL**: Translation layer at context boundary

**Output**: Integration pattern decisions for each context relationship.

---

## Step 4: Architecture Selection

Choose the right architecture for your bounded contexts.

### 4a. Evaluate Constraints

| Factor | Modular Monolith | Microservices |
|--------|------------------|---------------|
| Team size | < 20 developers | 20+ developers |
| Domain clarity | Boundaries still evolving | Well-understood boundaries |
| Time-to-market | Critical — ship fast | Can invest in infrastructure |
| Consistency | Strong consistency needed | Eventual consistency acceptable |
| DevOps maturity | Low — shared deployment | High — CI/CD per service |
| Scaling needs | Uniform scaling OK | Independent scaling required |

### 4b. Make the Decision

**Start with modular monolith** (recommended for most projects):
- Use Spring Modulith for enforced boundaries — see `spring-boot-modulith` skill
- Evolve to microservices later if needed (contexts are already separated)
- Lower operational complexity, faster development

**Choose microservices when**:
- Teams can independently own, deploy, and scale their context
- Bounded contexts have clearly distinct data stores
- Independent scaling is a hard requirement

### 4c. Apply Architecture Pattern

Within each bounded context, choose internal architecture:

| Pattern | Best For |
|---------|----------|
| **Hexagonal (Ports & Adapters)** | Core domains with complex business logic |
| **Clean Architecture** | Similar to hexagonal, explicit use-case layer |
| **Transaction Script** | Supporting/generic domains with simple CRUD |

**Output**: Architecture decision for each bounded context.

---

## Step 5: Tactical Implementation

Apply DDD patterns within core domains.

### 5a. Design Aggregates

Apply Vaughn Vernon's 4 rules:
1. Model true invariants in consistency boundaries
2. Design small aggregates (~70% should be root + value objects only)
3. Reference other aggregates by ID only
4. Use eventual consistency outside the boundary

### 5b. Implement Core Building Blocks

| Building Block | When to Use | Spring Boot Implementation |
|---------------|-------------|---------------------------|
| **Entity** | Identity matters, tracked over time | JPA `@Entity` — see `spring-boot-data-ddd` |
| **Value Object** | Defined by attributes, immutable | `@Embedded` or records — see `spring-boot-data-ddd` |
| **Aggregate Root** | Consistency boundary entry point | `AbstractAggregateRoot<T>` — see `spring-boot-data-ddd` |
| **Domain Service** | Logic spanning multiple aggregates | `@Service` in domain package |
| **Domain Event** | Cross-aggregate/cross-context communication | Java record + `@ApplicationModuleListener` — see `spring-boot-modulith` |
| **Repository** | Aggregate persistence | `ListCrudRepository` — see `spring-boot-data-ddd` |

### 5c. Validate Implementation

- [ ] Each aggregate enforces its own invariants
- [ ] Value objects are immutable (no setters)
- [ ] Aggregates reference each other by ID only
- [ ] One aggregate per transaction
- [ ] Domain layer has no infrastructure dependencies
- [ ] Repository exists only for aggregate roots
- [ ] Domain events handle cross-aggregate side effects

**Output**: Working implementation of DDD patterns in core domains.

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Starting with tactical patterns | Do strategic design (Steps 1-4) first |
| Applying DDD everywhere | Only use in core domains; CRUD is fine elsewhere |
| Anemic domain model | Put behavior IN entities, not just in services |
| Big aggregates | Keep small; reference by ID |
| Ignoring ubiquitous language | Code should read like business language |
| Premature microservices | Start monolith, extract later |

See [references/ANTI-PATTERNS.md](references/ANTI-PATTERNS.md) for detailed anti-pattern analysis.
