---
name: spring-boot-modulith
description: Spring Modulith 2.0 implementation for bounded contexts in Spring Boot 4. Use when structuring application modules, implementing @ApplicationModuleListener for event-driven communication, testing with Scenario API, enforcing module boundaries, or externalizing events to Kafka/AMQP. For modular monolith architecture decisions, see the domain-driven-design skill.
---

# Spring Modulith for Bounded Contexts

Implements DDD bounded contexts as application modules with enforced boundaries and event-driven communication.

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Application Module** | Package-based boundary = bounded context |
| **Module API** | Types in base package (public) |
| **Internal** | Types in sub-packages (encapsulated) |
| **Events** | Cross-module communication mechanism |

## Module Structure

```
src/main/java/
├── com.example/
│   └── Application.java              ← @SpringBootApplication
├── com.example.order/                ← Module: order
│   ├── OrderService.java             ← Public API
│   ├── OrderCreated.java             ← Public event
│   ├── package-info.java             ← @ApplicationModule config
│   └── internal/                     ← Encapsulated
│       ├── OrderRepository.java
│       └── OrderEntity.java
├── com.example.inventory/            ← Module: inventory
│   ├── InventoryService.java
│   └── internal/
└── com.example.shipping/             ← Module: shipping
```

Types in `com.example.order` = public API
Types in `com.example.order.internal` = hidden from other modules

## Quick Implementation

### Module Configuration

```java
// package-info.java in com.example.order
@ApplicationModule(
    allowedDependencies = {"inventory :: api", "customer"},
    type = Type.OPEN  // or CLOSED for strict encapsulation
)
package com.example.order;

import org.springframework.modulith.ApplicationModule;
```

### Event Publishing

```java
// Domain event (in module's public API)
public record OrderSubmitted(
    Long orderId,
    CustomerId customerId,
    List<OrderLine> lines,
    Instant occurredAt
) {
    public OrderSubmitted(Long orderId, CustomerId customerId, List<OrderLine> lines) {
        this(orderId, customerId, lines, Instant.now());
    }
}

// Service that publishes
@Service
@Transactional
public class OrderService {
    private final OrderRepository repository;
    private final ApplicationEventPublisher events;
    
    public Order submit(Long orderId) {
        Order order = repository.findById(orderId).orElseThrow();
        order.submit();
        Order saved = repository.save(order);
        
        events.publishEvent(new OrderSubmitted(
            saved.getId(),
            saved.getCustomerId(),
            saved.getLines()
        ));
        
        return saved;
    }
}
```

### Event Handling (Different Module)

```java
// In inventory module
@Component
public class InventoryEventHandler {
    private final StockRepository stocks;
    
    @ApplicationModuleListener
    void on(OrderSubmitted event) {
        // Runs async, in new transaction, after original commits
        event.lines().forEach(line ->
            stocks.decrementStock(line.productId(), line.quantity())
        );
    }
}
```

```kotlin
@Component
class InventoryEventHandler(private val stocks: StockRepository) {
    
    @ApplicationModuleListener
    fun on(event: OrderSubmitted) {
        event.lines.forEach { line ->
            stocks.decrementStock(line.productId, line.quantity)
        }
    }
}
```

### Module Verification Test

```java
class ModularityTests {
    
    ApplicationModules modules = ApplicationModules.of(Application.class);
    
    @Test
    void verifyModuleStructure() {
        modules.verify();  // Fails if boundaries violated
    }
    
    @Test
    void generateDocumentation() {
        new Documenter(modules)
            .writeModulesAsPlantUml()
            .writeIndividualModulesAsPlantUml();
    }
}
```

## Spring Boot 4 / Modulith 2.0 Specifics

### Dependency

```xml
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-starter-core</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

### @ApplicationModuleListener Behavior

Combines three annotations:
- `@Async` — Non-blocking execution
- `@Transactional(propagation = REQUIRES_NEW)` — Independent transaction
- `@TransactionalEventListener(phase = AFTER_COMMIT)` — After publisher commits

### Event Externalization

```java
// Mark event for external publication
@Externalized("orders::#{#this.customerId}")
public record OrderSubmitted(Long orderId, String customerId, ...) {}
```

```properties
# application.properties
spring.modulith.events.externalization.enabled=true
spring.modulith.events.jdbc.enabled=true  # Event publication log
```

## Detailed References

- **Module Structure**: See [references/module-structure.md](references/module-structure.md) for package conventions, named interfaces, dependency rules
- **Event Patterns**: See [references/events.md](references/events.md) for publishing, handling, externalization, testing with Scenario API

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| Direct bean injection across modules | Use events or expose API |
| Synchronous cross-module calls | Use `@ApplicationModuleListener` |
| Module dependencies not declared | Add `allowedDependencies` in `@ApplicationModule` |
| Missing verification test | Add `ApplicationModules.verify()` test |
| Internal types in public API | Move to `.internal` sub-package |
| Events without data | Include all data handlers need |

## Critical Reminders

1. **One module = one bounded context** — Mirror DDD boundaries
2. **Events are the integration mechanism** — Not direct method calls
3. **Verify in CI** — `ApplicationModules.verify()` catches boundary violations
4. **Reference by ID** — Never direct object references across modules
5. **Transaction per module** — `@ApplicationModuleListener` ensures isolation
