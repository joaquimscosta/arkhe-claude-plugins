# DDD Anti-Patterns and Pitfalls

Common mistakes that undermine DDD benefits. Recognize and avoid these patterns.

## Table of Contents

- [Anemic Domain Model](#anemic-domain-model)
  - [Symptoms](#symptoms)
  - [Why It's Harmful](#why-its-harmful)
  - [The Fix: Rich Domain Model](#the-fix-rich-domain-model)
  - [Greg Young's "Making Bubbles" Approach](#greg-youngs-making-bubbles-approach)
- [Over-Engineering](#over-engineering)
  - [Symptoms](#symptoms-1)
  - [Decision Criteria: When DDD is Overkill](#decision-criteria-when-ddd-is-overkill)
  - [Microsoft's Guidance](#microsofts-guidance)
  - [The Fix](#the-fix)
- [Aggregate Design Mistakes](#aggregate-design-mistakes)
  - [Mistake 1: Aggregates Too Large](#mistake-1-aggregates-too-large)
  - [Mistake 2: Wrong Aggregate Root](#mistake-2-wrong-aggregate-root)
  - [Mistake 3: Cross-Aggregate Transactions](#mistake-3-cross-aggregate-transactions)
  - [Mistake 4: Direct Object References](#mistake-4-direct-object-references)
- [Leaky Abstractions](#leaky-abstractions)
  - [Symptoms](#symptoms-2)
  - [Why It's Harmful](#why-its-harmful-1)
  - [The Fix: Persistence Ignorance](#the-fix-persistence-ignorance)
- [Misaligned Bounded Contexts](#misaligned-bounded-contexts)
  - [Symptoms](#symptoms-3)
  - [Causes](#causes)
  - [The Fix](#the-fix-1)
- [Technical vs Business Domain Confusion](#technical-vs-business-domain-confusion)
  - [Symptoms](#symptoms-4)
  - [Examples](#examples)
  - [The Fix](#the-fix-2)
- [Tactical Without Strategic](#tactical-without-strategic)
  - [Symptoms](#symptoms-5)
  - [Why It Fails](#why-it-fails)
  - [The Correct Order](#the-correct-order)
  - [Signs of Correct Order](#signs-of-correct-order)
- [Quick Anti-Pattern Checklist](#quick-anti-pattern-checklist)

---

## Anemic Domain Model

**The most common DDD anti-pattern.** Domain objects become data bags with getters/setters; all logic lives in services.

### Symptoms
- Domain classes are pure data containers
- All business logic in Service/Manager classes
- Domain objects can exist in invalid states
- Setters change state without business rules
- Code like `order.setStatus(Status.SHIPPED)` instead of `order.ship()`

### Why It's Harmful
- Loses DDD's core benefit: encapsulated business logic
- Business rules scattered across services
- Hard to maintain invariants
- Code doesn't express domain concepts

### The Fix: Rich Domain Model

**Before (Anemic)**
```
class Order {
    Status status;
    void setStatus(Status s) { this.status = s; }
}

class OrderService {
    void shipOrder(Order order) {
        if (order.getStatus() != Status.PAID) {
            throw new IllegalStateException();
        }
        order.setStatus(Status.SHIPPED);
        // notify, update inventory, etc.
    }
}
```

**After (Rich)**
```
class Order {
    private Status status;
    
    void ship() {
        if (status != Status.PAID) {
            throw new OrderNotPaidException();
        }
        status = Status.SHIPPED;
        registerEvent(new OrderShipped(this.id));
    }
}
```

### Greg Young's "Making Bubbles" Approach
Every time new requirements arrive, put the logic inside the domain model, not in service classes.

---

## Over-Engineering

Applying DDD patterns where simple CRUD suffices.

### Symptoms
- Separate classes for every conceivable concept
- Aggregate hierarchies for straightforward data
- Bounded contexts where natural boundaries don't exist
- Repository abstraction over 3 database tables
- Domain events for simple state changes

### Decision Criteria: When DDD is Overkill
- Simple data entry with no complex rules
- No domain expert to consult
- Read-heavy application with simple writes
- Prototype or throwaway code
- CRUD-dominant functionality

### Microsoft's Guidance
> "DDD approaches should be applied only if implementing complex microservices with significant business rules. Simpler responsibilities, like a CRUD service, can be managed with simpler approaches."

### The Fix
- Start simple, add patterns when pain emerges
- Apply tactical DDD only in core domains
- Use transaction scripts for simple use cases
- Reserve aggregates for complex invariants

---

## Aggregate Design Mistakes

### Mistake 1: Aggregates Too Large
**Symptom**: Aggregate contains many entities, causes contention and performance issues.

**Cause**: Modeling relationships instead of invariants.

**Example**: Order aggregate containing full Customer and full Product objects.

**Fix**: Keep aggregates small. ~70% should be root + value objects only. Reference other aggregates by ID.

### Mistake 2: Wrong Aggregate Root
**Symptom**: Commands need to go through awkward paths to reach data.

**Cause**: Choosing root based on data relationships, not business invariants.

**Fix**: Root should be the object responsible for enforcing aggregate invariants.

### Mistake 3: Cross-Aggregate Transactions
**Symptom**: Business logic tries to update multiple aggregates atomically.

**Cause**: Not accepting eventual consistency between aggregates.

**Fix**: One transaction = one aggregate. Use domain events for cross-aggregate coordination.

### Mistake 4: Direct Object References
**Symptom**: Aggregate holds reference to another aggregate's entity.

```
class Order {
    Customer customer;  // Direct reference - bad
}
```

**Fix**: Reference by ID only.
```
class Order {
    CustomerId customerId;  // ID reference - good
}
```

---

## Leaky Abstractions

Infrastructure concerns appearing in domain layer.

### Symptoms
- Database annotations (`@Entity`, `@Column`) on domain classes
- Repository implementations exposing ORM details
- Transaction management in domain services
- Framework exceptions in domain layer
- Domain objects implement persistence interfaces

### Why It's Harmful
- Domain depends on infrastructure
- Hard to test domain in isolation
- Framework changes ripple through domain
- Domain concepts polluted with technical concerns

### The Fix: Persistence Ignorance

**Domain Layer Contains Only**
- Plain objects (entities, value objects)
- Repository interfaces (not implementations)
- Domain services with no infrastructure dependencies
- Domain events

**Infrastructure Layer Contains**
- Repository implementations
- ORM mappings
- Database configurations
- External service integrations

**Mapping Strategy**
If ORM requires annotations, consider:
- Separate persistence models mapped to domain objects
- XML/external mapping configuration
- Spring Data JDBC (requires fewer annotations)

---

## Misaligned Bounded Contexts

Context boundaries drawn incorrectly or not at all.

### Symptoms
- Same term has different meanings across system
- Multiple teams work in same codebase, creating conflicts
- Boundaries drawn on technical lines (frontend/backend) not linguistic
- Big Ball of Mud: all concepts in one context
- Frequent merge conflicts between teams

### Causes
- Technical decomposition instead of business decomposition
- Ignoring linguistic boundaries
- Premature decomposition before understanding domain
- Following database schema, not business capabilities

### The Fix

**Draw boundaries where language changes.** When domain experts from different areas use different vocabulary for same concept, that's a boundary.

**Accept duplication for autonomy.** Same-named concepts in different contexts should have separate representations.

**Synchronize through events, not shared objects.** Contexts communicate through published events, not shared database tables or objects.

---

## Technical vs Business Domain Confusion

Confusing technical concerns with business domain.

### Symptoms
- "User" aggregate that's really authentication concern
- "Notification" bounded context that's infrastructure
- Technical services named as domain services
- Database schema driving domain model
- API structure dictating bounded contexts

### Examples

**Wrong**: "Let's create a Logging bounded context"
- Logging is infrastructure, not business domain

**Wrong**: "Let's create a User aggregate"
- User management is often generic subdomain (auth)
- Conflating identity with business concepts (Customer, Employee)

**Wrong**: "Our bounded contexts are Frontend, Backend, Database"
- These are technical layers, not business capabilities

### The Fix
- Ask: "Do domain experts talk about this concept?"
- Separate business domains from technical concerns
- Technical concerns go in infrastructure layer
- Business capabilities define bounded contexts

---

## Tactical Without Strategic

Jumping to aggregates and repositories without strategic design.

### Symptoms
- Team debates aggregate boundaries without knowing domain boundaries
- Repository interfaces before understanding context boundaries
- Domain events without context mapping
- Technical debates before business understanding

### Why It Fails
- Aggregate boundaries wrong without bounded context boundaries
- Tactical patterns applied in generic subdomains (waste)
- No ubiquitous language because no strategic analysis
- Refactoring required when strategic understanding emerges

### The Correct Order
1. **Strategic first**: Identify subdomains, classify (core/supporting/generic)
2. **Context boundaries**: Draw bounded contexts, create context map
3. **Ubiquitous language**: Establish shared vocabulary with domain experts
4. **Tactical selectively**: Apply patterns only in core domains

### Signs of Correct Order
- Team can explain subdomain types and why
- Context map exists and is referenced
- Domain experts recognize code terminology
- Simple approaches used in generic subdomains

---

## Quick Anti-Pattern Checklist

Before implementing, verify:

- [ ] **Not anemic**: Business logic lives in domain objects, not just services
- [ ] **Not over-engineered**: Complexity is justified by business rules
- [ ] **Aggregates small**: Most are root + value objects only
- [ ] **ID references**: No direct object references between aggregates
- [ ] **Single transaction per aggregate**: Eventual consistency outside
- [ ] **Domain layer clean**: No infrastructure dependencies
- [ ] **Strategic foundation**: Bounded contexts and subdomains identified
- [ ] **Language aligned**: Code uses terms domain experts recognize
