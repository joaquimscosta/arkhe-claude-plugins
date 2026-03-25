# Spring Modulith Setup Workflow

Detailed step-by-step process for implementing bounded contexts as Spring Modulith modules.

---

## Step 1: Define Module Packages

Structure your application into package-based modules.

### 1a. Package Conventions

Each top-level package under the application root is a module:

```
com.example/
    Application.java              <- @SpringBootApplication (root)
    com.example.order/            <- Module: order
        OrderService.java         <- Public API (base package)
        OrderCreated.java         <- Public event (base package)
        internal/                 <- Encapsulated
            OrderRepository.java
            OrderEntity.java
    com.example.inventory/        <- Module: inventory
    com.example.shipping/         <- Module: shipping
```

**Rules**:
- Types in the base package (`com.example.order`) = **public API**
- Types in sub-packages (`com.example.order.internal`) = **internal, hidden from other modules**
- `@SpringBootApplication` must be in the root package

### 1b. Configure Module Metadata (Optional)

Add `package-info.java` for explicit configuration:

```java
@ApplicationModule(
    allowedDependencies = {"inventory", "shipping::api"}
)
package com.example.order;

import org.springframework.modulith.ApplicationModule;
```

### 1c. Named Interfaces

Expose specific internal packages as named interfaces:

```java
@NamedInterface("api")
package com.example.order.api;
```

Other modules can then depend on `order::api` without accessing all of `order`.

**Output**: Package structure with clear module boundaries.

---

## Step 2: Configure Module Dependencies

Control which modules can access which APIs.

### 2a. Declare Dependencies

In `package-info.java`:

```java
@ApplicationModule(
    allowedDependencies = {"inventory", "shipping::api"}
)
```

This means the order module can only depend on:
- `inventory` (full public API)
- `shipping::api` (only the named interface)

### 2b. Verify Dependencies

Add a verification test:

```java
@Test
void verifyModuleStructure() {
    ApplicationModules modules = ApplicationModules.of(Application.class);
    modules.verify();
}
```

This test fails if any module accesses another module's internal types or undeclared dependencies.

### 2c. Generate Documentation

```java
@Test
void generateModuleDocs() {
    ApplicationModules modules = ApplicationModules.of(Application.class);
    new Documenter(modules)
        .writeModulesAsPlantUml()
        .writeIndividualModulesAsPlantUml();
}
```

Generates PlantUML diagrams showing module dependencies — useful for CI and architecture reviews.

**Output**: Configured module dependencies with verification test.

---

## Step 3: Implement Event Communication

Use domain events for cross-module communication.

### 3a. Define Events as Records

```java
// In order module's base package (public)
public record OrderPlaced(Long orderId, Long customerId, BigDecimal total) {}
```

Events should be:
- **Immutable** (records)
- **In the base package** (so other modules can see them)
- **Self-contained** (include all data handlers need)

### 3b. Publish Events from Aggregates

```java
// In the aggregate root
public void place() {
    this.status = OrderStatus.PLACED;
    registerEvent(new OrderPlaced(this.id, this.customerId, this.total));
}
```

Events are dispatched after the transaction commits.

### 3c. Handle Events with @ApplicationModuleListener

```java
// In inventory module
@Service
class InventoryEventHandler {

    @ApplicationModuleListener
    void on(OrderPlaced event) {
        // Runs in its own transaction (REQUIRES_NEW)
        // After the publishing transaction commits (AFTER_COMMIT)
        // Asynchronously (@Async)
        reserveInventory(event.orderId());
    }
}
```

`@ApplicationModuleListener` combines:
- `@Async` — non-blocking
- `@Transactional(REQUIRES_NEW)` — isolated transaction
- `@TransactionalEventListener(AFTER_COMMIT)` — only after publisher commits

**Output**: Event-driven communication between modules.

---

## Step 4: Add Module Verification Test

Ensure module boundaries are enforced in CI.

### 4a. Structure Verification

```java
@SpringBootTest
class ModuleStructureTests {

    @Test
    void verifyModuleStructure() {
        ApplicationModules modules = ApplicationModules.of(Application.class);
        modules.verify();
    }
}
```

### 4b. Event Flow Verification with Scenario API

```java
@ApplicationModuleTest
class OrderModuleTests {

    @Test
    void orderPlacement_publishesEvent(Scenario scenario) {
        scenario.stimulate(() -> orderService.placeOrder(command))
            .andWaitForEventOfType(OrderPlaced.class)
            .matchingMappedValue(OrderPlaced::orderId, orderId)
            .toArrive();
    }
}
```

The Scenario API lets you:
- Trigger an action (`stimulate`)
- Wait for an event (`andWaitForEventOfType`)
- Assert event properties (`matchingMappedValue`)
- Verify event completion (`toArrive`)

### 4c. CI Integration

Add to your CI pipeline:

```yaml
# In GitHub Actions or similar
- name: Verify module structure
  run: ./gradlew test --tests '*ModuleStructureTests*'
```

**Output**: Automated module boundary enforcement in CI.

---

## Step 5: Event Externalization (Optional)

Externalize domain events to Kafka or AMQP for external consumers.

### 5a. Add Dependency

```xml
<!-- Kafka -->
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-events-kafka</artifactId>
</dependency>
```

### 5b. Mark Events for Externalization

```java
@Externalized("orders.events.placed::#{orderId()}")
public record OrderPlaced(Long orderId, Long customerId) {}
```

The `@Externalized` annotation:
- First part: Kafka topic / AMQP routing key
- After `::`: Key expression (for partitioning)

### 5c. Configure Event Publication

```yaml
spring:
  modulith:
    events:
      jdbc:
        enabled: true  # JDBC event log for at-least-once delivery
```

The JDBC event log stores events before sending to the broker, ensuring at-least-once delivery even if the broker is temporarily unavailable.

### 5d. Event Publication Lifecycle

```
Domain event registered
    -> Transaction commits
    -> Event stored in JDBC log
    -> Event sent to Kafka/AMQP
    -> Event marked as published in log
    -> Retry for failed publications
```

**Output**: Domain events flowing to external systems with guaranteed delivery.

---

## Verification Checklist

After implementing Modulith:

- [ ] Each module is a top-level package under the application root
- [ ] Internal types are in sub-packages (not the base package)
- [ ] `ApplicationModules.verify()` test passes
- [ ] Cross-module communication uses events, not direct bean injection
- [ ] Events are records in the publishing module's base package
- [ ] Event handlers use `@ApplicationModuleListener`
- [ ] PlantUML diagrams generated for documentation
