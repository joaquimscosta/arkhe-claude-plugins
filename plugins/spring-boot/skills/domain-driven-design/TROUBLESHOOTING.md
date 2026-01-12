# Domain-Driven Design Troubleshooting

Common issues and solutions for DDD implementation.

## Common Issues

### Issue: Anemic Domain Model

**Symptom:** Entities are just data holders with getters/setters, all logic in services

**Cause:** Treating domain objects as data structures rather than behavior-rich objects

**Solution:**

```java
// Before - Anemic domain model (ANTI-PATTERN)
public class Order {
    private OrderStatus status;
    private List<OrderItem> items;

    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }
}

public class OrderService {
    public void cancelOrder(Order order) {
        if (order.getStatus() == SHIPPED) {
            throw new IllegalStateException("Cannot cancel shipped order");
        }
        order.setStatus(CANCELLED);
        // refund logic...
    }
}

// After - Rich domain model
public class Order {
    private OrderStatus status;
    private List<OrderItem> items;

    public void cancel() {
        if (this.status == SHIPPED) {
            throw new OrderCannotBeCancelledException("Order already shipped");
        }
        this.status = CANCELLED;
        // Domain event could be raised here
    }
}
```

---

### Issue: God Aggregate (Too Large)

**Symptom:** One aggregate contains too many entities, transactions are slow, contention issues

**Cause:** Modeling entire domain in a single aggregate instead of identifying true invariants

**Solution:**

```java
// Before - God aggregate (ANTI-PATTERN)
public class Customer {
    private List<Order> orders;           // Could be millions
    private List<Address> addresses;
    private List<PaymentMethod> payments;
    private ShoppingCart cart;
    private WishList wishList;
    private LoyaltyAccount loyalty;
}

// After - Small, focused aggregates with ID references
public class Customer {
    private CustomerId id;
    private CustomerProfile profile;
    private List<AddressId> addressIds;    // Reference by ID
    private DefaultPaymentMethodId defaultPayment;
}

public class Order {
    private OrderId id;
    private CustomerId customerId;          // Reference by ID
    private List<OrderLine> lines;          // True invariant: order totals
}

public class ShoppingCart {
    private CustomerId customerId;          // Separate aggregate
    private List<CartItem> items;
}
```

**Rule of thumb:** ~70% of aggregates should be just root + value objects.

---

### Issue: Cross-Aggregate Transactions

**Symptom:** Business operation requires updating multiple aggregates atomically

**Cause:** Wrong aggregate boundaries or misunderstanding eventual consistency

**Solution:**

```java
// Before - Cross-aggregate transaction (ANTI-PATTERN)
@Transactional
public void placeOrder(Order order, Inventory inventory, Customer customer) {
    orderRepository.save(order);
    inventory.decrementStock(order.getItems());  // Different aggregate!
    customer.addLoyaltyPoints(order.getTotal()); // Different aggregate!
}

// After - Domain events with eventual consistency
public class Order extends AbstractAggregateRoot<Order> {
    public void place() {
        // ... order logic
        registerEvent(new OrderPlacedEvent(this.id, this.items, this.total));
    }
}

@Component
public class InventoryEventHandler {
    @EventListener
    public void on(OrderPlacedEvent event) {
        // Handle in separate transaction
        inventory.decrementStock(event.items());
    }
}

@Component
public class LoyaltyEventHandler {
    @EventListener
    public void on(OrderPlacedEvent event) {
        customer.addLoyaltyPoints(event.total());
    }
}
```

---

### Issue: Entity Used Where Value Object Needed

**Symptom:** Objects with generated IDs that don't need identity tracking

**Cause:** Defaulting to entities, not asking "does identity matter?"

**Solution:**

```java
// Before - Entity when value object is appropriate (ANTI-PATTERN)
@Entity
public class Money {
    @Id @GeneratedValue
    private Long id;           // Why does money need an ID?
    private BigDecimal amount;
    private String currency;
}

// After - Value object (immutable, no identity)
@Embeddable
public record Money(BigDecimal amount, Currency currency) {
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new CurrencyMismatchException();
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

**Ask:** "If two objects have the same attributes, are they the same thing?"
- Yes → Value Object
- No → Entity

---

### Issue: Bounded Contexts Not Defined

**Symptom:** Single model tries to represent everything, terms have multiple meanings

**Cause:** Skipping strategic design, jumping to tactical patterns

**Solution:**

```
// Before - One model for everything (ANTI-PATTERN)
Customer
├── name, email              (Identity context)
├── shippingAddresses        (Shipping context)
├── creditScore, paymentTerms (Billing context)
├── purchaseHistory          (Sales context)
└── supportTickets           (Support context)

// After - Different models per bounded context
Identity Context:        Customer { id, email, profile }
Shipping Context:        Recipient { customerId, addresses }
Billing Context:         Account { customerId, creditLimit, paymentTerms }
Sales Context:           Buyer { customerId, preferences, history }
Support Context:         Contact { customerId, tickets, satisfaction }
```

Each context has its own `Customer` representation with only relevant attributes.

---

### Issue: Repository Does Too Much

**Symptom:** Repository has business logic, complex queries, or returns DTOs

**Cause:** Misunderstanding repository's role as collection abstraction

**Solution:**

```java
// Before - Repository with business logic (ANTI-PATTERN)
public interface OrderRepository {
    List<OrderDTO> findPendingOrdersForDashboard();  // Returns DTO
    void cancelExpiredOrders();                       // Business logic!
    BigDecimal calculateRevenueByMonth(Month month);  // Reporting query
}

// After - Repository as pure collection abstraction
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order);
    List<Order> findByStatus(OrderStatus status);
}

// Business logic in domain service or aggregate
public class OrderExpirationService {
    public void cancelExpiredOrders() {
        List<Order> pending = orderRepository.findByStatus(PENDING);
        pending.stream()
            .filter(Order::isExpired)
            .forEach(order -> {
                order.cancel();
                orderRepository.save(order);
            });
    }
}

// Reporting in separate read model/CQRS query
public interface OrderReportingQuery {
    RevenueReport getRevenueByMonth(Month month);
}
```

---

### Issue: Domain Layer Has Infrastructure Dependencies

**Symptom:** Domain entities import JPA, Spring, or other framework annotations

**Cause:** Not maintaining persistence ignorance

**Solution:**

```java
// Before - Domain polluted with infrastructure (ANTI-PATTERN)
@Entity  // JPA annotation in domain
@Table(name = "orders")
public class Order {
    @Id @GeneratedValue
    private Long id;

    @Autowired  // Spring in domain!
    private EmailService emailService;

    public void confirm() {
        emailService.sendConfirmation(this);  // Infrastructure in domain
    }
}

// After - Clean domain with infrastructure in adapters
// Domain layer (no framework imports)
public class Order {
    private OrderId id;

    public OrderConfirmedEvent confirm() {
        // Pure domain logic
        return new OrderConfirmedEvent(this.id, this.customerEmail);
    }
}

// Infrastructure layer (JPA adapter)
@Entity
@Table(name = "orders")
public class OrderJpaEntity {
    @Id private String id;
    // ... JPA mappings
}

// Application layer handles events
@EventListener
public void onOrderConfirmed(OrderConfirmedEvent event) {
    emailService.sendConfirmation(event);
}
```

---

## Strategic Design Issues

### Missing Ubiquitous Language

**Symptom:** Code uses technical terms, business stakeholders don't understand it

**Solution:** Rename code to match business terminology:

```java
// Before - Technical naming
CustomerDataTransferObject, processTransaction(), handleEvent()

// After - Ubiquitous language
CustomerProfile, placeOrder(), orderWasShipped()
```

### Wrong Context Boundaries

**Symptom:** Teams stepping on each other, constant coordination needed

**Solution:** Boundaries should align with:
- Team ownership
- Language changes (same term, different meaning)
- Business capability boundaries
- Rate of change
