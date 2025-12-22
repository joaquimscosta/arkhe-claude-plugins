# Spring Modulith Examples

Complete working examples for Spring Modulith 2.0 patterns.

## Module Configuration

Package-info.java for declaring module boundaries and dependencies.

```java
// package-info.java in com.example.order
@ApplicationModule(
    allowedDependencies = {"inventory :: api", "customer"},
    type = Type.OPEN  // or CLOSED for strict encapsulation
)
package com.example.order;

import org.springframework.modulith.ApplicationModule;
```

**Key points:**
- Place in module's base package (e.g., `com.example.order`)
- Use `:: api` suffix to depend only on another module's public API
- `Type.OPEN` exposes all types, `Type.CLOSED` only base package types

---

## Event Publishing

Domain event with publishing service.

### Domain Event (Module's Public API)

```java
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
```

### Publishing Service

```java
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

**Key points:**
- Events are records for immutability
- Include all data handlers need (avoid lazy loading)
- Publish after save to ensure consistency

---

## Event Handling (Cross-Module)

Async event handler in a different module.

### Java

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

### Kotlin

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

**Key points:**
- `@ApplicationModuleListener` combines:
  - `@Async` - non-blocking execution
  - `@Transactional(propagation = REQUIRES_NEW)` - independent transaction
  - `@TransactionalEventListener(phase = AFTER_COMMIT)` - runs after publisher commits

---

## Module Verification Test

CI-friendly test to enforce module boundaries.

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

**Key points:**
- Run `verify()` in CI to catch boundary violations early
- Generate PlantUML diagrams for architecture documentation
- No Spring context needed - fast execution

---

## Event Externalization

Publish events to external systems (Kafka, AMQP).

### Event Annotation

```java
@Externalized("orders::#{#this.customerId}")
public record OrderSubmitted(Long orderId, String customerId, ...) {}
```

### Configuration

```properties
# application.properties
spring.modulith.events.externalization.enabled=true
spring.modulith.events.jdbc.enabled=true  # Event publication log for reliability
```

**Key points:**
- `@Externalized` marks events for external publication
- Routing key expression (`#{#this.customerId}`) determines topic/queue
- JDBC publication log ensures at-least-once delivery

---

## Module Structure Example

Complete package layout for order module.

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

**Rules:**
- Types in `com.example.order` = public API (other modules can use)
- Types in `com.example.order.internal` = hidden from other modules
- One module = one bounded context in DDD terms
