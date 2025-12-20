---
name: spring-boot-data-ddd
description: Spring Boot 4 data layer implementation for Domain-Driven Design. Use when implementing JPA or JDBC aggregates, Spring Data repositories, transactional services, projections, or entity auditing. Covers aggregate roots with AbstractAggregateRoot, value object mapping, EntityGraph for N+1 prevention, and Spring Boot 4 specifics (JSpecify null-safety, AOT repositories). For DDD concepts and design decisions, see the domain-driven-design skill.
---

# Spring Boot Data Layer for DDD

Implements DDD tactical patterns with Spring Data JPA and Spring Data JDBC in Spring Boot 4.

## Technology Selection

| Choose | When |
|--------|------|
| **Spring Data JPA** | Complex queries, existing Hibernate expertise, need lazy loading |
| **Spring Data JDBC** | DDD-first design, simpler mapping, aggregate-per-table, no lazy loading |

Spring Data JDBC enforces aggregate boundaries naturally—recommended for new DDD projects.

## Core Workflow

1. **Define aggregate root** → Extend `AbstractAggregateRoot<T>` for domain events
2. **Map value objects** → Use `@Embedded` or `@Converter` for immutability
3. **Create repository interface** → One per aggregate root, extend appropriate base
4. **Implement service layer** → `@Transactional` on public methods, one aggregate per transaction
5. **Add projections** → Interface or record-based for read operations

## Quick Implementation Patterns

### Aggregate Root with Domain Events

```java
@Entity
public class Order extends AbstractAggregateRoot<Order> {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Embedded
    private CustomerId customerId;  // Value object
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.DRAFT;
    
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private Set<OrderLine> lines = new HashSet<>();
    
    public void submit() {
        if (lines.isEmpty()) throw new IllegalStateException("Empty order");
        this.status = OrderStatus.SUBMITTED;
        registerEvent(new OrderSubmitted(this.id));
    }
}
```

```kotlin
@Entity
class Order : AbstractAggregateRoot<Order>() {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null
        private set
    
    @Embedded
    lateinit var customerId: CustomerId
        private set
    
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private val _lines: MutableSet<OrderLine> = mutableSetOf()
    val lines: Set<OrderLine> get() = _lines.toSet()
    
    fun submit(): Order {
        check(_lines.isNotEmpty()) { "Empty order" }
        status = OrderStatus.SUBMITTED
        registerEvent(OrderSubmitted(id!!))
        return this
    }
}
```

### Repository with EntityGraph

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    @EntityGraph(attributePaths = {"lines", "lines.product"})
    Optional<Order> findWithLinesById(Long id);
    
    List<OrderSummary> findByStatus(OrderStatus status);  // Projection
    
    @Query("SELECT o FROM Order o WHERE o.customerId.value = :customerId")
    List<Order> findByCustomerId(@Param("customerId") String customerId);
}
```

### Transactional Service

```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orders;
    
    @Transactional(readOnly = true)
    public OrderDto findById(Long id) {
        return orders.findById(id)
            .map(OrderDto::from)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }
    
    public OrderDto submit(Long orderId) {
        Order order = orders.findWithLinesById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        order.submit();
        return OrderDto.from(orders.save(order));
    }
}
```

## Spring Boot 4 Specifics

### JSpecify Null-Safety
```java
@NullMarked  // All params/returns non-null by default
@Service
public class OrderService {
    public @Nullable Order findByIdOrNull(Long id) {
        return orders.findById(id).orElse(null);
    }
}
```

### AOT Repository Compilation
Enabled by default—query methods compile to source code for faster startup. No configuration needed.

### Jakarta EE 11 Namespaces
All imports use `jakarta.*`:
- `jakarta.persistence.*` (JPA)
- `jakarta.validation.*` (Bean Validation)
- `jakarta.transaction.Transactional` (or Spring's)

## Detailed References

- **Aggregates & Entities**: See [references/aggregates.md](references/aggregates.md) for complete patterns with value objects, typed IDs, auditing
- **Repositories & Queries**: See [references/repositories.md](references/repositories.md) for custom queries, projections, specifications
- **Transactions**: See [references/transactions.md](references/transactions.md) for propagation, isolation, cross-aggregate consistency

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| `FetchType.EAGER` on associations | Use `LAZY` + `@EntityGraph` when needed |
| Returning entities from controllers | Convert to DTOs in service layer |
| `@Transactional` on private methods | Use public methods (proxy limitation) |
| Missing `readOnly = true` on queries | Add for read operations (performance) |
| Direct aggregate-to-aggregate references | Reference by ID only |
| Multiple aggregates in one transaction | Use domain events for eventual consistency |

## Critical Reminders

1. **One aggregate per transaction** — Cross-aggregate changes via domain events
2. **Repository per aggregate root** — Never for child entities
3. **Value objects are immutable** — No setters, return new instances
4. **Flush before events** — Call `repository.save()` before events dispatch
5. **Test with `@DataJpaTest`** — Use `TestEntityManager` for setup
