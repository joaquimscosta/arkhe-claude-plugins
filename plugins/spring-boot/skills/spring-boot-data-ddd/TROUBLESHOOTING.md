# Spring Boot Data Layer Troubleshooting

Common issues and solutions for DDD with Spring Data.

## Common Issues

### Issue: Aggregate Root Not Persisting Child Entities

**Symptom:** Child entities (OrderLine) not saved when saving aggregate root

**Cause:** Missing cascade configuration or incorrect mapping

**Solution:**

```java
// Wrong - no cascade
@OneToMany
private Set<OrderLine> lines;

// Correct - cascade and orphan removal
@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
@JoinColumn(name = "order_id")  // Unidirectional from aggregate root
private Set<OrderLine> lines = new HashSet<>();
```

For bidirectional (if needed):
```java
// Parent side
@OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
private Set<OrderLine> lines = new HashSet<>();

// Child side
@ManyToOne
@JoinColumn(name = "order_id")
private Order order;

// Helper method in parent
public void addLine(OrderLine line) {
    lines.add(line);
    line.setOrder(this);
}
```

---

### Issue: N+1 Query Problems with Lazy Loading

**Symptom:** Multiple SELECT queries for each associated entity

**Cause:** Accessing lazy-loaded collections outside transaction or in loop

**Solution:**

1. Use `@EntityGraph` for known fetch patterns:
```java
@EntityGraph(attributePaths = {"lines", "lines.product"})
Optional<Order> findWithLinesById(Long id);
```

2. Or use JPQL JOIN FETCH:
```java
@Query("SELECT o FROM Order o JOIN FETCH o.lines WHERE o.id = :id")
Optional<Order> findWithLinesById(@Param("id") Long id);
```

3. Or use `@BatchSize` for bulk fetching:
```java
@OneToMany(cascade = CascadeType.ALL)
@BatchSize(size = 25)  // Fetch 25 at a time
private Set<OrderLine> lines;
```

---

### Issue: Value Object Mapping Issues

**Symptom:** `@Embedded` value object fields not mapped correctly

**Cause:** Column name conflicts or null handling

**Solution:**

1. Override column names if needed:
```java
@Embedded
@AttributeOverride(name = "value", column = @Column(name = "customer_id"))
private CustomerId customerId;
```

2. Handle null embedded objects:
```java
// By default, if all fields are null, embedded object is null
// Force instantiation with @Embeddable defaults:
@Embeddable
public record Address(
    @Column(name = "street") String street,
    @Column(name = "city") String city
) {
    public Address() {
        this("", "");  // Default constructor for JPA
    }
}
```

3. For multiple value objects of same type:
```java
@Embedded
@AttributeOverrides({
    @AttributeOverride(name = "amount", column = @Column(name = "subtotal_amount")),
    @AttributeOverride(name = "currency", column = @Column(name = "subtotal_currency"))
})
private Money subtotal;

@Embedded
@AttributeOverrides({
    @AttributeOverride(name = "amount", column = @Column(name = "total_amount")),
    @AttributeOverride(name = "currency", column = @Column(name = "total_currency"))
})
private Money total;
```

---

### Issue: Transaction Boundary Errors

**Symptom:** `LazyInitializationException` after method returns

**Cause:** Accessing lazy-loaded data outside transaction scope

**Solution:**

1. Fetch everything needed within transaction:
```java
@Transactional
public OrderDto findById(Long id) {
    Order order = orders.findWithLinesById(id).orElseThrow();
    // Convert to DTO while still in transaction
    return OrderDto.from(order);  // Access all lazy collections here
}
```

2. Use Open Session in View (not recommended for APIs):
```yaml
# Only for traditional web apps, NOT REST APIs
spring.jpa.open-in-view: true  # Default, causes N+1 issues
spring.jpa.open-in-view: false  # Recommended for APIs
```

3. Initialize lazy collections explicitly:
```java
@Transactional
public Order findById(Long id) {
    Order order = orders.findById(id).orElseThrow();
    Hibernate.initialize(order.getLines());  // Force loading
    return order;
}
```

---

### Issue: @Transactional on Private Methods Not Working

**Symptom:** Transaction not applied, no rollback on exception

**Cause:** Spring AOP proxy limitation

**Solution:**

```java
// Wrong - private method, proxy can't intercept
@Transactional
private void processOrder(Long id) { ... }  // Transaction NOT applied!

// Wrong - internal call bypasses proxy
@Service
public class OrderService {
    public void process(Long id) {
        // Direct call - no proxy!
        doProcess(id);
    }

    @Transactional
    public void doProcess(Long id) { ... }  // NOT transactional when called internally!
}

// Correct - public method, called through proxy
@Service
@Transactional
public class OrderService {
    public void process(Long id) { ... }  // Transactional
}

// Or inject self for internal calls
@Service
public class OrderService {
    @Autowired
    private OrderService self;  // Proxy-aware reference

    public void process(Long id) {
        self.doProcess(id);  // Goes through proxy
    }

    @Transactional
    public void doProcess(Long id) { ... }
}
```

---

### Issue: Domain Events Not Published

**Symptom:** `registerEvent()` called but event handlers not triggered

**Cause:** Entity not saved through repository, or events not flushed

**Solution:**

```java
@Service
@Transactional
public class OrderService {
    public void submit(Long orderId) {
        Order order = orders.findById(orderId).orElseThrow();
        order.submit();  // Calls registerEvent()

        // MUST save through repository to publish events
        orders.save(order);  // Events published here!
    }
}
```

Events are published when:
1. `save()` or `saveAndFlush()` is called
2. Transaction commits
3. `@TransactionalEventListener` phase matches (default: AFTER_COMMIT)

---

## Spring Boot 4 Migration Issues

### JSpecify Null-Safety

```java
// Boot 4 supports JSpecify annotations
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

@NullMarked  // All params/returns non-null by default
@Service
public class OrderService {

    public @Nullable Order findByIdOrNull(Long id) {
        return orders.findById(id).orElse(null);
    }
}
```

### Jakarta EE 11 Namespaces

```java
// Before (Boot 3.x / Jakarta EE 10)
import jakarta.persistence.*;
import jakarta.validation.*;

// Same in Boot 4.x / Jakarta EE 11 - no change needed
import jakarta.persistence.*;
import jakarta.validation.*;
```

### AOT Repository Compilation

Enabled by default in Boot 4. No configuration needed, but be aware:
- Query methods compile to source code at build time
- Faster startup, but changes require rebuild
- Some dynamic query features may behave differently
