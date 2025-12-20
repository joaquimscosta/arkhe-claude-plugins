# Aggregates, Entities & Value Objects

Complete implementation patterns for DDD building blocks in Spring Data.

## Strongly-Typed IDs

Wrap primitive IDs to prevent parameter mixups and add domain meaning.

### Java

```java
@Embeddable
public record CustomerId(String value) {
    public CustomerId {
        Objects.requireNonNull(value, "CustomerId cannot be null");
        if (value.isBlank()) throw new IllegalArgumentException("CustomerId cannot be blank");
    }
    
    public static CustomerId generate() {
        return new CustomerId(UUID.randomUUID().toString());
    }
}
```

### Kotlin

```kotlin
@Embeddable
data class CustomerId(val value: String) {
    init {
        require(value.isNotBlank()) { "CustomerId cannot be blank" }
    }
    
    companion object {
        fun generate() = CustomerId(UUID.randomUUID().toString())
    }
}
```

## Value Objects

Immutable, equality by attributes, encapsulate validation.

### Java - Money Value Object

```java
@Embeddable
public record Money(
    @Column(name = "amount") BigDecimal amount,
    @Column(name = "currency") String currency
) {
    public static final Money ZERO = new Money(BigDecimal.ZERO, "USD");
    
    public Money {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.scale() > 2) {
            amount = amount.setScale(2, RoundingMode.HALF_UP);
        }
    }
    
    public Money add(Money other) {
        requireSameCurrency(other);
        return new Money(this.amount.add(other.amount), this.currency);
    }
    
    public Money multiply(int quantity) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(quantity)), this.currency);
    }
    
    private void requireSameCurrency(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch");
        }
    }
}
```

### Kotlin - Money Value Object

```kotlin
@Embeddable
data class Money(
    @Column(name = "amount") val amount: BigDecimal,
    @Column(name = "currency") val currency: String = "USD"
) {
    init {
        require(amount.scale() <= 2) { "Amount scale must be <= 2" }
    }
    
    operator fun plus(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch" }
        return Money(amount + other.amount, currency)
    }
    
    operator fun times(quantity: Int) = Money(amount * quantity.toBigDecimal(), currency)
    
    companion object {
        val ZERO = Money(BigDecimal.ZERO)
    }
}
```

## Complex Value Object with Converter

For value objects that don't map cleanly to columns.

### Java

```java
// Value object
public record Address(String street, String city, String postalCode, String country) {
    public Address {
        Objects.requireNonNull(street);
        Objects.requireNonNull(city);
        Objects.requireNonNull(postalCode);
        Objects.requireNonNull(country);
    }
    
    public String formatted() {
        return String.join(", ", street, city, postalCode, country);
    }
}

// JPA Converter
@Converter
public class AddressConverter implements AttributeConverter<Address, String> {
    private static final String DELIMITER = "|||";
    
    @Override
    public String convertToDatabaseColumn(Address address) {
        if (address == null) return null;
        return String.join(DELIMITER, 
            address.street(), address.city(), 
            address.postalCode(), address.country());
    }
    
    @Override
    public Address convertToEntityAttribute(String dbData) {
        if (dbData == null) return null;
        String[] parts = dbData.split("\\|\\|\\|");
        return new Address(parts[0], parts[1], parts[2], parts[3]);
    }
}

// Usage in entity
@Entity
public class Customer {
    @Convert(converter = AddressConverter.class)
    @Column(name = "shipping_address")
    private Address shippingAddress;
}
```

## Complete Aggregate Root

Full pattern with auditing, versioning, and domain events.

### Java

```java
@Entity
@Table(name = "orders")
@EntityListeners(AuditingEntityListener.class)
public class Order extends AbstractAggregateRoot<Order> {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Embedded
    @AttributeOverride(name = "value", column = @Column(name = "customer_id"))
    private CustomerId customerId;
    
    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "amount", column = @Column(name = "total_amount")),
        @AttributeOverride(name = "currency", column = @Column(name = "total_currency"))
    })
    private Money total = Money.ZERO;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status = OrderStatus.DRAFT;
    
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Set<OrderLine> lines = new HashSet<>();
    
    @Version
    private Long version;
    
    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;
    
    @LastModifiedDate
    private Instant updatedAt;
    
    protected Order() {} // JPA
    
    public Order(CustomerId customerId) {
        this.customerId = Objects.requireNonNull(customerId);
    }
    
    // Domain behavior
    public void addLine(ProductId productId, int quantity, Money unitPrice) {
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot modify non-draft order");
        }
        lines.add(new OrderLine(productId, quantity, unitPrice));
        recalculateTotal();
    }
    
    public void submit() {
        if (lines.isEmpty()) {
            throw new IllegalStateException("Cannot submit empty order");
        }
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Order already submitted");
        }
        this.status = OrderStatus.SUBMITTED;
        registerEvent(new OrderSubmitted(this.id, this.customerId, this.total));
    }
    
    private void recalculateTotal() {
        this.total = lines.stream()
            .map(OrderLine::lineTotal)
            .reduce(Money.ZERO, Money::add);
    }
    
    // Getters only - no setters
    public Long getId() { return id; }
    public CustomerId getCustomerId() { return customerId; }
    public Money getTotal() { return total; }
    public OrderStatus getStatus() { return status; }
    public Set<OrderLine> getLines() { return Collections.unmodifiableSet(lines); }
}
```

### Kotlin

```kotlin
@Entity
@Table(name = "orders")
@EntityListeners(AuditingEntityListener::class)
class Order private constructor() : AbstractAggregateRoot<Order>() {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null
        private set
    
    @Embedded
    @AttributeOverride(name = "value", column = Column(name = "customer_id"))
    lateinit var customerId: CustomerId
        private set
    
    @Embedded
    @AttributeOverrides(
        AttributeOverride(name = "amount", column = Column(name = "total_amount")),
        AttributeOverride(name = "currency", column = Column(name = "total_currency"))
    )
    var total: Money = Money.ZERO
        private set
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus = OrderStatus.DRAFT
        private set
    
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true, fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private val _lines: MutableSet<OrderLine> = mutableSetOf()
    val lines: Set<OrderLine> get() = _lines.toSet()
    
    @Version
    var version: Long? = null
        private set
    
    @CreatedDate
    @Column(updatable = false)
    var createdAt: Instant? = null
        private set
    
    @LastModifiedDate
    var updatedAt: Instant? = null
        private set
    
    constructor(customerId: CustomerId) : this() {
        this.customerId = customerId
    }
    
    fun addLine(productId: ProductId, quantity: Int, unitPrice: Money) {
        check(status == OrderStatus.DRAFT) { "Cannot modify non-draft order" }
        _lines.add(OrderLine(productId, quantity, unitPrice))
        recalculateTotal()
    }
    
    fun submit(): Order {
        check(_lines.isNotEmpty()) { "Cannot submit empty order" }
        check(status == OrderStatus.DRAFT) { "Order already submitted" }
        status = OrderStatus.SUBMITTED
        registerEvent(OrderSubmitted(id!!, customerId, total))
        return this
    }
    
    private fun recalculateTotal() {
        total = _lines.map { it.lineTotal() }.fold(Money.ZERO) { acc, m -> acc + m }
    }
}
```

## Child Entity (within aggregate)

```java
@Entity
@Table(name = "order_lines")
public class OrderLine {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Embedded
    @AttributeOverride(name = "value", column = @Column(name = "product_id"))
    private ProductId productId;
    
    private int quantity;
    
    @Embedded
    private Money unitPrice;
    
    protected OrderLine() {}
    
    OrderLine(ProductId productId, int quantity, Money unitPrice) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
        this.productId = Objects.requireNonNull(productId);
        this.quantity = quantity;
        this.unitPrice = Objects.requireNonNull(unitPrice);
    }
    
    public Money lineTotal() {
        return unitPrice.multiply(quantity);
    }
}
```

## Domain Events

```java
// Immutable event record
public record OrderSubmitted(
    Long orderId,
    CustomerId customerId,
    Money totalAmount,
    Instant occurredAt
) {
    public OrderSubmitted(Long orderId, CustomerId customerId, Money totalAmount) {
        this(orderId, customerId, totalAmount, Instant.now());
    }
}
```

## Enable Auditing

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {
    
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName);
    }
}
```

## Spring Data JDBC Alternative

For simpler, DDD-native mapping without JPA overhead:

```java
// No @Entity - just a class
public class Order {
    @Id
    private Long id;
    
    private CustomerId customerId;
    private Money total;
    private OrderStatus status;
    
    // Child entities automatically managed as aggregate members
    private Set<OrderLine> lines = new HashSet<>();
    
    // Same domain behavior methods...
}

// Repository
public interface OrderRepository extends CrudRepository<Order, Long> {
    List<Order> findByStatus(OrderStatus status);
}
```

Spring Data JDBC benefits:
- No lazy loading surprises
- Automatic cascade delete of children
- Simpler SQL generation
- Natural aggregate boundaries
