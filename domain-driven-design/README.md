# Domain-Driven Design Plugin

Domain-Driven Design guidance for architecting complex business systems.

## Components

### Skills

- **domain-driven-design**: Expert guidance for DDD architecture and implementation. Auto-invoked when users mention "DDD", "bounded context", "aggregate", "domain model", "ubiquitous language", "event storming", "context mapping", or "domain events".

## Use Cases

- Designing complex business systems with intricate domain logic
- Defining bounded contexts and linguistic boundaries
- Choosing between modular monolith vs microservices
- Implementing aggregates, entities, and value objects
- Strategic design with subdomains and context mapping
- Avoiding common DDD anti-patterns (anemic domain model, over-engineering)

## When to Apply DDD

**Good fit:**
- Domain has intricate business rules
- System is long-lived and high-value
- Domain experts are available
- Multiple teams/departments involved

**Overkill for:**
- Simple CRUD applications
- Tight deadlines with limited budgets
- Purely technical complexity (no business logic)

## Installation

### Add the Marketplace

```bash
/plugin marketplace add ./arkhe-claude-plugins
```

### Install the Plugin

```bash
/plugin install domain-driven-design@arkhe-claude-plugins
```

## Usage

The skill auto-invokes when you discuss DDD concepts:

```bash
# Triggers automatically
"How should I structure my bounded contexts for this e-commerce system?"
"I'm seeing an anemic domain model pattern - how do I fix it?"
"Should I use microservices or a modular monolith?"
```

## Coverage

The skill provides guidance across three DDD layers:

| Layer | Topics |
|-------|--------|
| **Strategic** | Subdomains, bounded contexts, context mapping, event storming |
| **Tactical** | Entities, value objects, aggregates, domain services, repositories |
| **Architecture** | Clean architecture, hexagonal, modular monolith, microservices |

## Version

1.0.0
