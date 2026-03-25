# Spring Boot Data Layer Workflow

Detailed step-by-step process for implementing DDD patterns with Spring Data.

---

## Step 1: Define Aggregate Root

Design and implement the aggregate root entity.

### 1a. Choose Technology

| Choose | When |
|--------|------|
| **Spring Data JPA** | Complex queries, existing Hibernate expertise, lazy loading needed |
| **Spring Data JDBC** | DDD-first design, simpler mapping, no lazy loading surprises |

Spring Data JDBC enforces aggregate boundaries naturally — recommended for new DDD projects.

### 1b. Create the Aggregate Root

Extend `AbstractAggregateRoot<T>` for domain event support:

```java
@Entity
public class Order extends AbstractAggregateRoot<Order> {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Embedded
    private CustomerId customerId;  // Value object reference by ID

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderLine> lines = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    // Domain method that registers an event
    public void place() {
        if (this.lines.isEmpty()) {
            throw new IllegalStateException("Cannot place empty order");
        }
        this.status = OrderStatus.PLACED;
        registerEvent(new OrderPlaced(this.id));
    }
}
```

### 1c. Apply Aggregate Design Rules

- [ ] Root entity controls all access to child entities
- [ ] External references use IDs only (not object references)
- [ ] Invariants are enforced within the aggregate
- [ ] Keep aggregates small (~70% should be root + value objects)

**Output**: Aggregate root entity with domain methods and event registration.

---

## Step 2: Map Value Objects

Implement immutable value objects for domain concepts.

### 2a. Simple Value Objects with @Embedded

```java
@Embeddable
public record Money(
    @Column(name = "amount") BigDecimal amount,
    @Column(name = "currency") String currency
) {
    public Money {
        Objects.requireNonNull(amount, "Amount cannot be null");
        Objects.requireNonNull(currency, "Currency cannot be null");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

### 2b. Complex Value Objects with @Converter

For value objects that need custom serialization:

```java
@Converter(autoApply = true)
public class EmailConverter implements AttributeConverter<Email, String> {
    @Override
    public String convertToDatabaseColumn(Email email) {
        return email == null ? null : email.value();
    }

    @Override
    public Email convertToEntityAttribute(String value) {
        return value == null ? null : new Email(value);
    }
}
```

### 2c. Strongly-Typed IDs

Prevent primitive obsession:

```java
@Embeddable
public record OrderId(@Column(name = "id") Long value) {
    public OrderId {
        Objects.requireNonNull(value, "OrderId cannot be null");
    }
}
```

**Output**: Immutable value objects mapped to database columns.

---

## Step 3: Create Repository Interface

Define one repository per aggregate root.

### 3a. Choose Base Interface

| Interface | Returns | Use When |
|-----------|---------|----------|
| `ListCrudRepository<T, ID>` | `List<T>` | Standard CRUD (recommended for Boot 4) |
| `ListPagingAndSortingRepository<T, ID>` | `List<T>` | Need pagination and sorting |
| `JpaRepository<T, ID>` | `List<T>` | Need JPA-specific features (flush, batch) |

### 3b. Define Repository

```java
public interface OrderRepository extends ListCrudRepository<Order, Long> {

    @EntityGraph(attributePaths = {"lines", "lines.product"})
    Optional<Order> findById(Long id);

    List<Order> findByCustomerIdAndStatus(CustomerId customerId, OrderStatus status);
}
```

### 3c. AOT Compilation Notes (Spring Boot 4)

- Repository proxies are generated at build time by default
- Custom query methods work with AOT
- `@Query` annotations are fully supported

**Output**: Repository interface with optimized queries.

---

## Step 4: Implement Service Layer

Create application services with proper transactional boundaries.

### 4a. Define Service

```java
@Service
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public Order placeOrder(PlaceOrderCommand command) {
        Order order = new Order(command.customerId());
        command.items().forEach(item ->
            order.addLine(item.productId(), item.quantity(), item.price())
        );
        order.place();  // Registers domain event
        return orderRepository.save(order);  // Saves and dispatches events
    }

    @Transactional(readOnly = true)
    public Optional<Order> findOrder(Long id) {
        return orderRepository.findById(id);
    }
}
```

### 4b. Transaction Rules

| Rule | Implementation |
|------|---------------|
| One aggregate per transaction | Each service method modifies ONE aggregate root |
| Read-only for queries | `@Transactional(readOnly = true)` on read methods |
| Events after commit | Domain events dispatch after transaction commits |
| Cross-aggregate via events | Use `@ApplicationModuleListener` for cross-aggregate work |

### 4c. Domain Event Flow

```
Service.save(aggregate)
    -> Repository.save()
    -> JPA flush
    -> Transaction commits
    -> Domain events dispatched
    -> @ApplicationModuleListener handlers execute
```

**Output**: Application service with transactional boundaries and event dispatch.

---

## Step 5: Add Projections

Create read-optimized views for query operations.

### 5a. Interface-Based Projections

```java
public interface OrderSummary {
    Long getId();
    OrderStatus getStatus();
    @Value("#{target.lines.size()}")
    int getLineCount();
}

// In repository
List<OrderSummary> findByStatus(OrderStatus status);
```

### 5b. Record-Based DTOs

```java
public record OrderDto(Long id, String status, List<OrderLineDto> lines) {
    public static OrderDto from(Order order) {
        return new OrderDto(
            order.getId(),
            order.getStatus().name(),
            order.getLines().stream().map(OrderLineDto::from).toList()
        );
    }
}
```

### 5c. EntityGraph for N+1 Prevention

```java
@EntityGraph(attributePaths = {"lines", "lines.product"})
List<Order> findByCustomerId(Long customerId);
```

Use `@EntityGraph` instead of `FetchType.EAGER` — it is explicit and query-specific.

**Output**: Read-optimized projections for different use cases.

---

## Verification Checklist

After implementing the data layer:

- [ ] One repository per aggregate root (never for child entities)
- [ ] Value objects are immutable (records or final fields)
- [ ] `@Transactional` on public service methods
- [ ] `readOnly = true` on query methods
- [ ] `@EntityGraph` used instead of `FetchType.EAGER`
- [ ] Domain events registered in aggregate methods
- [ ] Tests with `@DataJpaTest` cover repository queries
