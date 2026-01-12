# Event-Driven Module Communication

Event publishing, handling, and testing patterns for Spring Modulith.

## Event Design

### Domain Event Structure

```java
// Immutable record with all data handlers need
public record OrderSubmitted(
    Long orderId,
    CustomerId customerId,
    Money totalAmount,
    List<OrderLineDto> lines,
    Instant occurredAt
) {
    // Convenience constructor
    public OrderSubmitted(Long orderId, CustomerId customerId, Money totalAmount, List<OrderLineDto> lines) {
        this(orderId, customerId, totalAmount, lines, Instant.now());
    }
    
    // Nested DTO for aggregate data
    public record OrderLineDto(ProductId productId, int quantity, Money unitPrice) {}
}
```

```kotlin
data class OrderSubmitted(
    val orderId: Long,
    val customerId: CustomerId,
    val totalAmount: Money,
    val lines: List<OrderLineDto>,
    val occurredAt: Instant = Instant.now()
) {
    data class OrderLineDto(
        val productId: ProductId,
        val quantity: Int,
        val unitPrice: Money
    )
}
```

### Event Naming Conventions

- Past tense: `OrderSubmitted`, `PaymentProcessed`, `InventoryReserved`
- Include aggregate ID and relevant data
- Self-contained: handler shouldn't need to query back

## Event Publishing

### From Service

```java
@Service
@Transactional
public class OrderService {
    
    private final OrderRepository orders;
    private final ApplicationEventPublisher events;
    
    public Order submit(Long orderId) {
        Order order = orders.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        
        order.submit();
        Order saved = orders.save(order);
        
        // Publish after save
        events.publishEvent(new OrderSubmitted(
            saved.getId(),
            saved.getCustomerId(),
            saved.getTotal(),
            mapLines(saved.getLines())
        ));
        
        return saved;
    }
}
```

### From Aggregate (AbstractAggregateRoot)

```java
@Entity
public class Order extends AbstractAggregateRoot<Order> {
    
    public void submit() {
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot submit non-draft order");
        }
        this.status = OrderStatus.SUBMITTED;
        
        // Register event - published when repository.save() called
        registerEvent(new OrderSubmitted(this.id, this.customerId, this.total, mapLines()));
    }
}

// Service just saves - events published automatically
@Transactional
public Order submit(Long orderId) {
    Order order = orders.findById(orderId).orElseThrow();
    order.submit();
    return orders.save(order);  // Events dispatched here
}
```

## Event Handling

### @ApplicationModuleListener

Combines:
- `@Async` — Non-blocking
- `@Transactional(propagation = REQUIRES_NEW)` — New transaction
- `@TransactionalEventListener(phase = AFTER_COMMIT)` — After publisher commits

```java
@Component
public class InventoryEventHandler {
    
    private final StockRepository stocks;
    private final StockReservationService reservations;
    
    @ApplicationModuleListener
    void on(OrderSubmitted event) {
        // Runs after order transaction commits
        // In its own transaction
        // Async (non-blocking for caller)
        
        event.lines().forEach(line -> {
            stocks.decrementStock(line.productId(), line.quantity());
            reservations.create(event.orderId(), line.productId(), line.quantity());
        });
    }
    
    @ApplicationModuleListener
    void on(OrderCancelled event) {
        reservations.releaseForOrder(event.orderId());
    }
}
```

### Multiple Handlers

```java
// Notification module
@Component
public class NotificationEventHandler {
    
    @ApplicationModuleListener
    void sendConfirmation(OrderSubmitted event) {
        emailService.sendOrderConfirmation(event.customerId(), event.orderId());
    }
}

// Analytics module
@Component
public class AnalyticsEventHandler {
    
    @ApplicationModuleListener
    void trackOrder(OrderSubmitted event) {
        analytics.track("order_submitted", Map.of(
            "orderId", event.orderId(),
            "amount", event.totalAmount().amount()
        ));
    }
}
```

### Conditional Handling

```java
@ApplicationModuleListener
void on(OrderSubmitted event) {
    if (event.totalAmount().amount().compareTo(BigDecimal.valueOf(1000)) > 0) {
        // Only for high-value orders
        fraudDetection.analyze(event);
    }
}
```

## Event Externalization

### Mark Event for External Publication

```java
@Externalized("orders::#{#this.orderId}")
public record OrderSubmitted(Long orderId, CustomerId customerId, ...) {}
```

Routing key: `orders::123` (for Kafka/RabbitMQ partitioning)

### Configuration

```properties
# Enable externalization
spring.modulith.events.externalization.enabled=true

# Use JDBC event publication log (recommended)
spring.modulith.events.jdbc.enabled=true
spring.modulith.events.jdbc.schema-initialization.enabled=true

# Kafka
spring.modulith.events.kafka.enabled=true
spring.kafka.bootstrap-servers=localhost:9092

# RabbitMQ
spring.modulith.events.amqp.enabled=true
spring.rabbitmq.host=localhost
```

### Custom Event Routing

```java
@Configuration
public class EventExternalizationConfig {
    
    @Bean
    EventExternalizationConfiguration eventConfig() {
        return EventExternalizationConfiguration.externalizing()
            .select(annotatedAsExternalized())
            .mapping(OrderSubmitted.class, event -> new OrderDTO(
                event.orderId(),
                event.totalAmount().amount()
            ))
            .routeKey(OrderSubmitted.class, event -> 
                "orders." + event.customerId().value())
            .build();
    }
}
```

## Event Publication Log

Ensures at-least-once delivery with JDBC-backed log.

```sql
-- Auto-created schema
CREATE TABLE event_publication (
    id UUID PRIMARY KEY,
    listener_id VARCHAR(255),
    event_type VARCHAR(255),
    serialized_event TEXT,
    publication_date TIMESTAMP,
    completion_date TIMESTAMP
);
```

### Incomplete Publication Handling

```java
@Component
public class IncompleteEventResubmitter {
    
    private final IncompleteEventPublications publications;
    
    @Scheduled(fixedRate = 60000)  // Every minute
    public void resubmitIncomplete() {
        publications.resubmitIncompletePublicationsOlderThan(Duration.ofMinutes(5));
    }
}
```

## Testing with Scenario API

### Basic Event Testing

```java
@ApplicationModuleTest
class OrderModuleTest {
    
    @Autowired
    OrderService orders;
    
    @Test
    void orderSubmissionPublishesEvent(Scenario scenario) {
        // Given
        Long orderId = createTestOrder();
        
        // When/Then
        scenario.stimulate(() -> orders.submit(orderId))
            .andWaitForEventOfType(OrderSubmitted.class)
            .matching(event -> event.orderId().equals(orderId))
            .toArriveAndVerify(event -> {
                assertThat(event.totalAmount()).isNotNull();
                assertThat(event.lines()).isNotEmpty();
            });
    }
}
```

### State Change Verification

```java
@Test
void inventoryUpdatedOnOrderSubmission(Scenario scenario) {
    // Given
    ProductId productId = ProductId.generate();
    stockRepository.save(new Stock(productId, 100));
    Long orderId = createOrderWithProduct(productId, 5);
    
    // When/Then
    scenario.stimulate(() -> orders.submit(orderId))
        .andWaitForEventOfType(OrderSubmitted.class)
        .toArriveAndVerify(event -> {
            Stock stock = stockRepository.findByProductId(productId);
            assertThat(stock.getQuantity()).isEqualTo(95);
        });
}
```

### Publishing Events Directly

```java
@Test
void inventoryHandlesOrderSubmitted(Scenario scenario) {
    // Given
    ProductId productId = ProductId.generate();
    stockRepository.save(new Stock(productId, 100));
    
    // When - publish event directly
    OrderSubmitted event = new OrderSubmitted(
        1L,
        CustomerId.generate(),
        Money.of(100),
        List.of(new OrderLineDto(productId, 10, Money.of(10)))
    );
    
    // Then
    scenario.publish(event)
        .andWaitForStateChange(() -> stockRepository.findByProductId(productId))
        .andVerify(stock -> assertThat(stock.getQuantity()).isEqualTo(90));
}
```

### Timeout Configuration

```java
scenario.stimulate(() -> orders.submit(orderId))
    .andWaitForEventOfType(OrderSubmitted.class)
    .toArriveWithin(Duration.ofSeconds(5))
    .andVerify(event -> { ... });
```

## Error Handling

### Handler Failure

If a handler fails, the event publication log retains the event for reprocessing.

```java
@ApplicationModuleListener
void on(OrderSubmitted event) {
    try {
        inventoryService.reserve(event);
    } catch (InsufficientStockException e) {
        // Publish compensating event
        events.publishEvent(new InventoryReservationFailed(
            event.orderId(),
            e.getProductId(),
            e.getRequestedQuantity()
        ));
    }
}
```

### Dead Letter Handling

```java
@Configuration
public class EventConfig {
    
    @Bean
    EventPublicationRegistry eventPublicationRegistry(
            EventPublicationRepository repository
    ) {
        return new DefaultEventPublicationRegistry(repository) {
            @Override
            protected void onPublicationFailure(EventPublication publication, Throwable cause) {
                log.error("Event publication failed: {}", publication.getEvent(), cause);
                alerting.notify("Event processing failed", cause);
            }
        };
    }
}
```

## Event Versioning

For evolving event schemas:

```java
// V1
public record OrderSubmittedV1(Long orderId, BigDecimal amount) {}

// V2 - added customerId
public record OrderSubmitted(
    Long orderId,
    CustomerId customerId,
    BigDecimal amount
) {
    // Migration from V1
    public static OrderSubmitted fromV1(OrderSubmittedV1 v1, CustomerId customerId) {
        return new OrderSubmitted(v1.orderId(), customerId, v1.amount());
    }
}
```

## Best Practices

1. **Events are contracts** — Don't change structure without versioning
2. **Include all needed data** — Handlers shouldn't query back
3. **One handler per concern** — Separate inventory, notifications, analytics
4. **Idempotent handlers** — Events may be redelivered
5. **Test with Scenario API** — Verify event flow, not just publication
6. **Monitor publication log** — Alert on stuck events
