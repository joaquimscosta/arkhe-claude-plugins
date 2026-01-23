# Transaction Management

Transaction patterns for aggregate consistency in DDD.

## Table of Contents

- [Core Principle](#core-principle)
- [@Transactional Basics](#transactional-basics)
- [Propagation Levels](#propagation-levels)
  - [Propagation Examples](#propagation-examples)
- [Isolation Levels](#isolation-levels)
- [Rollback Behavior](#rollback-behavior)
- [Cross-Aggregate Consistency](#cross-aggregate-consistency)
  - [Java](#java)
  - [Kotlin](#kotlin)
- [TransactionalEventListener Phases](#transactionaleventlistener-phases)
- [Optimistic Locking](#optimistic-locking)
- [Testing Transactions](#testing-transactions)
- [Common Mistakes](#common-mistakes)
  - [Self-Invocation Fix](#self-invocation-fix)
- [Programmatic Transactions](#programmatic-transactions)

## Core Principle

**One aggregate = one transaction.** Cross-aggregate consistency achieved via domain events.

## @Transactional Basics

```java
@Service
@Transactional  // Class-level default
public class OrderService {
    
    // Inherits class-level @Transactional (REQUIRED)
    public Order createOrder(CreateOrderCommand cmd) {
        Order order = new Order(cmd.customerId());
        return orderRepository.save(order);
    }
    
    // Override for read-only (performance optimization)
    @Transactional(readOnly = true)
    public OrderDto findById(Long id) {
        return orderRepository.findById(id)
            .map(OrderDto::from)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }
    
    // Explicit propagation for nested calls
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment(Long orderId, PaymentDetails payment) {
        // Runs in separate transaction
    }
}
```

## Propagation Levels

| Level | Behavior | Use When |
|-------|----------|----------|
| `REQUIRED` (default) | Join existing or create new | Standard operations |
| `REQUIRES_NEW` | Always new, suspend existing | Independent operation (audit log, payment) |
| `SUPPORTS` | Use if exists, otherwise non-tx | Read that's often called from tx |
| `NOT_SUPPORTED` | Non-transactional, suspend existing | Long-running reads |
| `MANDATORY` | Require existing, fail otherwise | Must be called within tx |
| `NEVER` | Fail if tx exists | Validation that must not be in tx |
| `NESTED` | Nested tx with savepoint | Partial rollback (JDBC only) |

### Propagation Examples

```java
@Service
public class OrderService {
    
    private final PaymentService paymentService;
    private final AuditService auditService;
    
    @Transactional
    public void submitOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.submit();
        orderRepository.save(order);
        
        // Payment in separate tx - if it fails, order still submitted
        paymentService.processPayment(order.getId(), order.getTotal());
        
        // Audit always succeeds independently
        auditService.log("ORDER_SUBMITTED", order.getId());
    }
}

@Service
public class PaymentService {
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment(Long orderId, Money amount) {
        // Independent transaction
        // Failure here doesn't rollback the order
    }
}

@Service
public class AuditService {
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void log(String action, Long entityId) {
        // Always succeeds, never affects caller's tx
    }
}
```

## Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|-------|------------|---------------------|--------------|-------------|
| `READ_UNCOMMITTED` | ✓ | ✓ | ✓ | Fastest |
| `READ_COMMITTED` | ✗ | ✓ | ✓ | Default (most DBs) |
| `REPEATABLE_READ` | ✗ | ✗ | ✓ | Good |
| `SERIALIZABLE` | ✗ | ✗ | ✗ | Slowest |

```java
// Use higher isolation for financial operations
@Transactional(isolation = Isolation.REPEATABLE_READ)
public void transferFunds(AccountId from, AccountId to, Money amount) {
    // Consistent reads within transaction
}

// Use serializable for inventory checks
@Transactional(isolation = Isolation.SERIALIZABLE)
public void reserveStock(ProductId productId, int quantity) {
    // Prevents phantom reads during stock check
}
```

## Rollback Behavior

```java
@Transactional
public class OrderService {
    
    // Default: rollback on RuntimeException, commit on checked
    public void defaultBehavior() {
        throw new RuntimeException("Rolls back");
    }
    
    // Explicit rollback on checked exception
    @Transactional(rollbackFor = PaymentFailedException.class)
    public void withCheckedRollback() throws PaymentFailedException {
        throw new PaymentFailedException("Rolls back");
    }
    
    // No rollback on specific runtime exception
    @Transactional(noRollbackFor = OptimisticLockingFailureException.class)
    public void withNoRollback() {
        // Retry logic handles this, don't rollback
    }
}
```

## Cross-Aggregate Consistency

Use domain events for eventual consistency across aggregates.

### Java

```java
@Service
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;
    
    @Transactional
    public void submitOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.submit();  // Registers OrderSubmitted event
        
        Order saved = orderRepository.save(order);
        
        // Events dispatched after save, within same tx
        // AbstractAggregateRoot handles this automatically
    }
}

// Event handler in different module
@Component
public class InventoryEventHandler {
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderSubmitted(OrderSubmitted event) {
        // Runs after order tx commits
        // In separate tx (eventual consistency)
        inventoryService.reserveStock(event.orderLines());
    }
}
```

### Kotlin

```kotlin
@Service
class OrderService(
    private val orderRepository: OrderRepository
) {
    @Transactional
    fun submitOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException(orderId) }
        order.submit()
        orderRepository.save(order)
    }
}

@Component
class InventoryEventHandler(private val inventoryService: InventoryService) {
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    fun handle(event: OrderSubmitted) {
        inventoryService.reserveStock(event.orderLines)
    }
}
```

## TransactionalEventListener Phases

| Phase | When | Use Case |
|-------|------|----------|
| `BEFORE_COMMIT` | Before tx commits | Validation, last-minute changes |
| `AFTER_COMMIT` | After successful commit | Notifications, external calls |
| `AFTER_ROLLBACK` | After tx rollback | Cleanup, alerts |
| `AFTER_COMPLETION` | After commit or rollback | Logging |

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void sendNotification(OrderSubmitted event) {
    // Only runs if order saved successfully
    emailService.sendOrderConfirmation(event.customerId(), event.orderId());
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
public void handleFailure(OrderSubmitted event) {
    // Cleanup if tx rolled back
    log.warn("Order submission failed: {}", event.orderId());
}
```

## Optimistic Locking

Prevent lost updates with version field.

```java
@Entity
public class Order {
    @Version
    private Long version;
    // ...
}

// Handle in service
@Transactional
public void updateOrder(Long orderId, UpdateOrderCommand cmd) {
    try {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.update(cmd);
        orderRepository.save(order);
    } catch (OptimisticLockingFailureException e) {
        throw new ConcurrentModificationException("Order was modified by another user");
    }
}
```

## Testing Transactions

```java
@DataJpaTest
@Transactional  // Each test runs in tx, rolled back after
class OrderRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Test
    void savesOrderWithLines() {
        Order order = new Order(CustomerId.generate());
        order.addLine(ProductId.generate(), 2, Money.of(10));
        
        orderRepository.save(order);
        entityManager.flush();
        entityManager.clear();  // Force reload from DB
        
        Order found = orderRepository.findById(order.getId()).orElseThrow();
        assertThat(found.getLines()).hasSize(1);
    }
}
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `@Transactional` on private method | Proxy can't intercept | Use public methods |
| Self-invocation within class | Bypasses proxy | Inject self or extract to another service |
| Long-running tx with user input | Connection held, locks held | Fetch, return, then start new tx |
| Missing `readOnly = true` | Unnecessary flush checks | Add to read operations |
| Catching exception inside tx | Swallows rollback trigger | Let exception propagate or explicit rollback |

### Self-Invocation Fix

```java
@Service
public class OrderService {
    
    @Lazy
    @Autowired
    private OrderService self;  // Inject proxy
    
    @Transactional
    public void processOrders(List<Long> orderIds) {
        for (Long id : orderIds) {
            self.processOrder(id);  // Through proxy, tx works
        }
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processOrder(Long orderId) {
        // Each order in its own tx
    }
}
```

## Programmatic Transactions

When annotation-based isn't flexible enough:

```java
@Service
public class OrderService {
    
    private final TransactionTemplate txTemplate;
    
    public OrderService(PlatformTransactionManager txManager) {
        this.txTemplate = new TransactionTemplate(txManager);
        this.txTemplate.setIsolationLevel(TransactionDefinition.ISOLATION_REPEATABLE_READ);
    }
    
    public Order processWithRetry(Long orderId) {
        return txTemplate.execute(status -> {
            try {
                Order order = orderRepository.findById(orderId).orElseThrow();
                order.process();
                return orderRepository.save(order);
            } catch (OptimisticLockingFailureException e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```
