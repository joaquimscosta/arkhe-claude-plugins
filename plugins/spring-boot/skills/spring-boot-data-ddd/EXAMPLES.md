# Spring Boot Data Layer Examples

Complete working examples for DDD patterns with Spring Data.

## Aggregate Root with Domain Events

JPA entity extending AbstractAggregateRoot for domain event publishing.

### Java

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

### Kotlin

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

**Key points:**
- Extend `AbstractAggregateRoot<T>` for domain event support
- Use `@Embedded` for value objects
- Register events with `registerEvent()` - published on save

---

## Repository with EntityGraph

Repository interface with N+1 prevention patterns.

```java
public interface OrderRepository extends JpaRepository<Order, Long> {

    @EntityGraph(attributePaths = {"lines", "lines.product"})
    Optional<Order> findWithLinesById(Long id);

    List<OrderSummary> findByStatus(OrderStatus status);  // Projection

    @Query("SELECT o FROM Order o WHERE o.customerId.value = :customerId")
    List<Order> findByCustomerId(@Param("customerId") String customerId);
}
```

**Key points:**
- Use `@EntityGraph` to eager fetch specific associations
- Return projections for read-only queries
- Query value objects by their internal field

---

## Transactional Service

Service with proper transaction boundaries.

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

**Key points:**
- Class-level `@Transactional` for default behavior
- Override with `readOnly = true` for queries (performance)
- Fetch with associations before modifying

---

## Value Object Implementation

Strongly-typed ID and Money patterns.

### Strongly-Typed ID

```java
@Embeddable
public record CustomerId(
    @Column(name = "customer_id")
    String value
) {
    public CustomerId {
        Objects.requireNonNull(value, "Customer ID required");
    }

    public static CustomerId generate() {
        return new CustomerId(UUID.randomUUID().toString());
    }
}
```

### Money Value Object

```java
@Embeddable
public record Money(
    @Column(name = "amount", precision = 19, scale = 4)
    BigDecimal amount,

    @Column(name = "currency", length = 3)
    String currency
) {
    public Money {
        Objects.requireNonNull(amount, "Amount required");
        Objects.requireNonNull(currency, "Currency required");
        if (amount.scale() > 4) {
            throw new IllegalArgumentException("Amount scale exceeds 4");
        }
    }

    public static Money of(BigDecimal amount, String currency) {
        return new Money(amount, currency);
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

**Key points:**
- Use `@Embeddable` for JPA mapping
- Records are immutable by default
- Validate in constructor (compact constructor for records)

---

## Projection for Read Operations

Interface-based projection for efficient queries.

```java
// Interface projection - only fetches needed columns
public interface OrderSummary {
    Long getId();
    String getStatus();
    Instant getCreatedAt();

    @Value("#{target.lines.size()}")
    int getLineCount();
}

// Record projection - explicit mapping
public record OrderDto(
    Long id,
    String status,
    BigDecimal totalAmount,
    List<OrderLineDto> lines,
    Instant createdAt
) {
    public static OrderDto from(Order order) {
        return new OrderDto(
            order.getId(),
            order.getStatus().name(),
            order.getTotal().amount(),
            order.getLines().stream().map(OrderLineDto::from).toList(),
            order.getCreatedAt()
        );
    }
}
```

**Key points:**
- Interface projections auto-generate SQL with only needed columns
- Use `@Value` for computed properties in interface projections
- Record DTOs for explicit conversion from entities

---

## Auditing Configuration

Automatic created/modified timestamps.

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {}

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class AuditableEntity {

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;
}

// Usage
@Entity
public class Order extends AuditableEntity {
    // ...
}
```

**Key points:**
- Enable with `@EnableJpaAuditing`
- Use `@MappedSuperclass` for common audit fields
- Implement `AuditorAware<String>` for `@CreatedBy`/`@LastModifiedBy`
