# Spring Modulith Troubleshooting

Common issues and solutions for Spring Modulith 2.0.

## Common Issues

### Issue: Module Verification Failures

**Symptom:** `ApplicationModules.verify()` throws exception about illegal dependencies

**Cause:** Module accessing internal types of another module

**Solution:**

1. Check the error message for specific violation:
```
Module 'order' depends on non-exposed type
com.example.inventory.internal.StockEntity of module 'inventory'
```

2. Options to fix:
   - Move type to module's public API (base package)
   - Expose via `allowedDependencies` in `@ApplicationModule`
   - Use events instead of direct references

```java
// Option A: Expose the type
// Move StockEntity from internal/ to com.example.inventory/

// Option B: Allow dependency
@ApplicationModule(
    allowedDependencies = {"inventory"}  // Full access
    // or
    allowedDependencies = {"inventory :: api"}  // API only
)
package com.example.order;

// Option C: Use events (recommended)
// Publish InventoryReserved event instead of direct call
```

---

### Issue: Events Not Being Published

**Symptom:** `@ApplicationModuleListener` never triggered

**Cause:** Event not published or transaction not committed

**Solution:**

1. Ensure event is published within transaction:
```java
@Service
@Transactional  // Must be present
public class OrderService {
    public Order submit(Long orderId) {
        Order order = repository.findById(orderId).orElseThrow();
        order.submit();
        Order saved = repository.save(order);

        // Publish AFTER save
        events.publishEvent(new OrderSubmitted(saved.getId()));

        return saved;
    }
}
```

2. Check listener annotation:
```java
// Wrong - @EventListener runs synchronously, before commit
@EventListener
void on(OrderSubmitted event) { ... }

// Correct - @ApplicationModuleListener runs after commit
@ApplicationModuleListener
void on(OrderSubmitted event) { ... }
```

3. Verify event class is accessible:
```java
// Event must be in publishing module's public API
// (base package, not internal/)
package com.example.order;  // Correct
public record OrderSubmitted(...) {}

// NOT in
package com.example.order.internal;  // Can't be seen by other modules
```

---

### Issue: @ApplicationModuleListener Not Triggered

**Symptom:** Handler method exists but never executes

**Cause:** Async processing disabled or transaction rollback

**Solution:**

1. Enable async processing:
```java
@Configuration
@EnableAsync  // Required for @ApplicationModuleListener
public class AsyncConfig {}
```

2. Check for transaction rollback:
```java
// If publishing transaction rolls back, events are discarded
@Transactional
public void submit(Long orderId) {
    events.publishEvent(new OrderSubmitted(orderId));
    throw new RuntimeException();  // Rollback = no event!
}
```

3. Verify event publication log (if using JDBC):
```sql
SELECT * FROM event_publication WHERE completed = false;
```

---

### Issue: Circular Module Dependencies

**Symptom:** Verification error about cyclic dependency

**Cause:** Module A depends on Module B and Module B depends on Module A

**Solution:**

Use events to break the cycle:

```java
// Instead of direct call from Order to Inventory AND Inventory to Order:

// Order module publishes event
events.publishEvent(new OrderSubmitted(orderId));

// Inventory module listens
@ApplicationModuleListener
void on(OrderSubmitted event) {
    // Reserve stock, then publish
    events.publishEvent(new StockReserved(event.orderId()));
}

// Order module listens (if needed)
@ApplicationModuleListener
void on(StockReserved event) {
    // Continue order processing
}
```

---

### Issue: Event Data Missing After Async Handler

**Symptom:** `LazyInitializationException` in event handler

**Cause:** Event contains entity reference instead of data

**Solution:**

Include all needed data in event:

```java
// Wrong - entity reference causes lazy loading issues
public record OrderSubmitted(Order order) {}  // Don't do this!

// Correct - include data directly
public record OrderSubmitted(
    Long orderId,
    String customerId,
    List<OrderLineData> lines,  // Data, not entities
    Instant occurredAt
) {}

public record OrderLineData(
    String productId,
    int quantity,
    BigDecimal price
) {
    public static OrderLineData from(OrderLine line) {
        return new OrderLineData(
            line.getProductId(),
            line.getQuantity(),
            line.getPrice()
        );
    }
}
```

---

## Spring Boot 4 / Modulith 2.0 Migration Issues

### Dependency Changes

```xml
<!-- Modulith 2.0 for Boot 4 -->
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-starter-core</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<!-- Optional: JDBC event publication log -->
<dependency>
    <groupId>org.springframework.modulith</groupId>
    <artifactId>spring-modulith-starter-jdbc</artifactId>
</dependency>
```

### Event Externalization Configuration

```yaml
# Modulith 2.0 configuration
spring:
  modulith:
    events:
      externalization:
        enabled: true
      jdbc:
        enabled: true
        schema-initialization:
          enabled: true  # Auto-create event_publication table
```

### @ApplicationModuleListener Semantics

In Modulith 2.0, `@ApplicationModuleListener` explicitly combines:
- `@Async` - always async
- `@Transactional(propagation = REQUIRES_NEW)` - new transaction
- `@TransactionalEventListener(phase = AFTER_COMMIT)` - after publisher commits

This is the same as Modulith 1.x but more clearly documented.
