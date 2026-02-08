# Architecture Alignment with DDD

DDD aligns with several architectural styles. Choose based on team size, domain complexity, and operational maturity.

## Table of Contents

- [Clean Architecture](#clean-architecture)
  - [Layers (Inner to Outer)](#layers-inner-to-outer)
  - [The Dependency Rule](#the-dependency-rule)
  - [DDD Mapping](#ddd-mapping)
- [Hexagonal Architecture](#hexagonal-architecture)
  - [Core Concepts](#core-concepts)
  - [Port Types](#port-types)
  - [DDD Mapping](#ddd-mapping-1)
  - [Benefits for DDD](#benefits-for-ddd)
- [Onion Architecture](#onion-architecture)
  - [Layers (Core to Edge)](#layers-core-to-edge)
  - [Core Rule](#core-rule)
  - [DDD Mapping](#ddd-mapping-2)
- [Modular Monolith](#modular-monolith)
  - [Structure](#structure)
  - [Module Communication Rules](#module-communication-rules)
  - [Advantages](#advantages)
  - [When to Choose Modular Monolith](#when-to-choose-modular-monolith)
  - [Migration Path to Microservices](#migration-path-to-microservices)
- [Microservices](#microservices)
  - [DDD Alignment Principle](#ddd-alignment-principle)
  - [One-to-One Mapping Isn't Mandatory](#one-to-one-mapping-isnt-mandatory)
  - [Communication Patterns](#communication-patterns)
  - [Anticorruption Layer in Microservices](#anticorruption-layer-in-microservices)
  - [When Microservices Work Well](#when-microservices-work-well)
  - [When Microservices Fail](#when-microservices-fail)
- [Architecture Decision Framework](#architecture-decision-framework)
  - [Decision Tree](#decision-tree)
  - [Architecture Comparison](#architecture-comparison)
- [Implementation Patterns](#implementation-patterns)
  - [Package Structure (Java/Spring)](#package-structure-javaspring)
  - [Persistence Strategies](#persistence-strategies)
  - [CQRS Integration](#cqrs-integration)
  - [Event Sourcing Integration](#event-sourcing-integration)

---

## Clean Architecture

Robert Martin's layered approach with domain at center.

### Layers (Inner to Outer)
1. **Entities**: Enterprise business rules, domain objects
2. **Use Cases**: Application-specific business rules (application services)
3. **Interface Adapters**: Controllers, presenters, gateways
4. **Frameworks & Drivers**: Web frameworks, databases, external services

### The Dependency Rule
Source code dependencies only point inward. Inner layers know nothing about outer layers.

### DDD Mapping
- Entities layer = DDD entities, value objects, aggregates
- Use Cases layer = Application services, commands, queries
- Interface Adapters = Repository implementations, controllers
- Frameworks = Spring, JPA, HTTP libraries

---

## Hexagonal Architecture

Alistair Cockburn's ports and adapters approach.

### Core Concepts
- **Hexagon**: Domain model at center
- **Ports**: Technology-agnostic interfaces (how domain talks to outside)
- **Adapters**: Translate between external systems and ports

### Port Types
- **Driving/Primary Ports**: How outside world uses domain (API, CLI, UI)
- **Driven/Secondary Ports**: How domain uses infrastructure (DB, messaging)

### DDD Mapping
- Hexagon core = Domain layer (entities, value objects, domain services)
- Driving ports = Application service interfaces
- Driven ports = Repository interfaces (defined in domain)
- Adapters = Controllers, JPA repositories, message handlers

### Benefits for DDD
- Domain isolated from infrastructure
- Easy to swap implementations (MySQL → MongoDB)
- Natural test boundaries
- Persistence ignorance enforced

---

## Onion Architecture

Jeffrey Palermo's concentric layer approach.

### Layers (Core to Edge)
1. **Domain Model**: Entities, value objects
2. **Domain Services**: Business logic across aggregates
3. **Application Services**: Use case orchestration
4. **Infrastructure**: Persistence, messaging, external services

### Core Rule
Outer layers depend on inner layers. Inner layers have no knowledge of outer layers.

### DDD Mapping
Directly maps to DDD tactical patterns with explicit layer separation.

---

## Modular Monolith

Single deployable application with internal bounded context modules.

### Structure
```
application/
├── shared-kernel/              # Shared code (minimal)
├── order-context/              # Bounded Context
│   ├── domain/
│   │   ├── model/              # Aggregates, entities, value objects
│   │   ├── service/            # Domain services
│   │   └── repository/         # Repository interfaces
│   ├── application/
│   │   ├── service/            # Application services
│   │   ├── command/            # Commands
│   │   └── query/              # Queries
│   └── infrastructure/
│       ├── persistence/        # Repository implementations
│       └── messaging/          # Event handlers
├── inventory-context/          # Another Bounded Context
└── customer-context/           # Another Bounded Context
```

### Module Communication Rules
1. No direct method calls between modules
2. Communication via events (preferred) or internal APIs
3. Each module owns its database schema (logical separation)
4. Shared kernel kept minimal

### Advantages
- Single deployment simplicity
- No network latency for in-process calls
- Simpler transaction handling
- Lower infrastructure costs
- Easier debugging
- Prepared for future decomposition

### When to Choose Modular Monolith
- Team under 20 developers
- Domain boundaries unclear
- Time-to-market critical
- Strong consistency requirements
- Limited infrastructure budget
- Early product development

### Migration Path to Microservices
1. Establish strict module boundaries
2. Replace in-memory events with message broker
3. Extract high-load modules using Strangler Fig
4. Add ACLs during transition

---

## Microservices

Distributed bounded contexts as independent deployable services.

### DDD Alignment Principle
**Each microservice should be no smaller than an aggregate and no larger than a bounded context.**

### One-to-One Mapping Isn't Mandatory
- Single bounded context may split for scaling (read vs write services)
- Multiple related contexts may consolidate to reduce operational overhead
- Let organizational and scaling needs drive decisions

### Communication Patterns

**Synchronous (REST/gRPC)**
- Published contracts
- Versioned APIs
- Use for queries requiring immediate response

**Asynchronous (Events)**
- Preferred for decoupling
- Domain events for eventual consistency
- Saga pattern for distributed transactions

### Anticorruption Layer in Microservices
Essential when integrating with:
- Legacy systems
- External services
- Systems with different domain models
- During monolith migration

### When Microservices Work Well
- Bounded contexts have distinct languages
- Teams can own full contexts
- Independent scaling required
- DevOps maturity exists
- Organization structure aligns (Conway's Law)

### When Microservices Fail
- Context boundaries unclear
- High coupling between contexts
- Small teams manage many services
- Consistency requirements span contexts
- Simple CRUD dominates

---

## Architecture Decision Framework

### Decision Tree
```
How complex is the domain?
├── Simple CRUD → Skip DDD, use simple layered architecture
└── Complex rules → Apply DDD
    │
    How large is the team?
    ├── < 20 developers → Modular Monolith
    └── > 20 developers → Consider split
        │
        Are bounded context boundaries clear?
        ├── No → Modular Monolith (discover boundaries first)
        └── Yes → Team autonomy needed?
            ├── No → Modular Monolith
            └── Yes → Independent scaling needed?
                ├── No → Modular Monolith
                └── Yes → Microservices
```

### Architecture Comparison

| Factor | Modular Monolith | Microservices |
|--------|-----------------|---------------|
| Deployment | Single unit | Per service |
| Consistency | Strong (transactions) | Eventual |
| Latency | In-process | Network |
| Complexity | Application | Infrastructure |
| Team size | Small-medium | Large |
| Debugging | Simpler | Distributed tracing |
| Cost | Lower | Higher |

---

## Implementation Patterns

### Package Structure (Java/Spring)

**Package by Layer (avoid)**
```
com.company.app/
├── controller/
├── service/
├── repository/
└── model/
```

**Package by Feature/Bounded Context (preferred)**
```
com.company.app/
├── order/
│   ├── domain/
│   │   ├── Order.java
│   │   ├── OrderId.java
│   │   └── OrderRepository.java (interface)
│   ├── application/
│   │   ├── PlaceOrderService.java
│   │   └── PlaceOrderCommand.java
│   └── infrastructure/
│       ├── JpaOrderRepository.java
│       └── OrderController.java
├── customer/
└── inventory/
```

### Persistence Strategies

**JPA/Hibernate Challenges**
- No-args constructors break value object immutability
- Setters violate encapsulation
- Lazy loading violates aggregate boundaries
- `@ManyToOne` creates coupling between aggregates

**JPA Workarounds**
- Package-private constructors
- Reference by ID (not entity) using value object wrappers
- Custom Hibernate types for strongly-typed IDs
- `@Converter` for complex value types

**Spring Data JDBC (DDD-friendly)**
- Enforces aggregate boundaries naturally
- No lazy loading
- Automatic child deletion
- Reference-by-ID is default
- Simpler mapping

**Document Databases**
- Natural fit: store aggregate as document
- Aggregate = document boundary
- No ORM mapping complexity

### CQRS Integration

**Separate Read/Write Models**
- Write side: Rich domain model with aggregates
- Read side: Denormalized projections for queries

**Implementation**
1. Commands mutate aggregates
2. Aggregates emit domain events
3. Event handlers update read models
4. Queries read from projections

**When to Apply CQRS**
- Read/write patterns differ significantly
- Query optimization needed
- Event sourcing in use
- Complex reporting requirements

**Apply per bounded context, not system-wide.**

### Event Sourcing Integration

**Store Events, Not State**
- Aggregate state rebuilt by replaying events
- Complete audit trail
- Time-travel debugging
- Multiple projections possible

**When to Use**
- Audit/compliance requirements
- Domain naturally thinks in events
- Historical state reconstruction needed
- Event-driven architecture exists

**When to Avoid**
- Simple CRUD
- Team unfamiliar with pattern
- Immediate consistency required for all reads
- Very long event histories

**Module-level decision, not system-wide.**
