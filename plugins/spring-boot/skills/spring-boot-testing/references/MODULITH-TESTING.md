# Modulith Testing

@ApplicationModuleTest, Scenario API, and event verification.

## Table of Contents

- [@ApplicationModuleTest](#applicationmoduletest)
  - [Basic Usage](#basic-usage)
  - [Kotlin](#kotlin)
- [Bootstrap Modes](#bootstrap-modes)
- [Scenario API](#scenario-api)
  - [Verify Event Publication](#verify-event-publication)
  - [Kotlin Scenario](#kotlin-scenario)
  - [Verify State Changes](#verify-state-changes)
  - [Multiple Events](#multiple-events)
  - [Event Matching](#event-matching)
  - [Timeout Configuration](#timeout-configuration)
- [Testing Event Handlers](#testing-event-handlers)
  - [Publish Event Directly](#publish-event-directly)
  - [Verify Handler Called](#verify-handler-called)
- [Module Structure Verification](#module-structure-verification)
- [Testing with Testcontainers](#testing-with-testcontainers)
- [Testing Event Externalization](#testing-event-externalization)
- [Custom Test Scenario Configuration](#custom-test-scenario-configuration)
- [Testing Sagas / Process Managers](#testing-sagas--process-managers)
- [Best Practices](#best-practices)

## @ApplicationModuleTest

Tests a single module in isolation with controlled dependencies.

### Basic Usage

```java
package com.example.order;

import org.springframework.modulith.test.ApplicationModuleTest;
import org.springframework.modulith.test.Scenario;

@ApplicationModuleTest
class OrderModuleTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldCreateOrder() {
        Order order = orderService.create(new CreateOrderRequest("customer-123"));

        assertThat(order.getId()).isNotNull();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.DRAFT);
    }
}
```

### Kotlin

```kotlin
package com.example.order

import org.springframework.modulith.test.ApplicationModuleTest
import org.springframework.modulith.test.Scenario

@ApplicationModuleTest
class OrderModuleTest(@Autowired val orderService: OrderService) {

    @Test
    fun `should create order`() {
        val order = orderService.create(CreateOrderRequest("customer-123"))

        assertThat(order.id).isNotNull()
        assertThat(order.status).isEqualTo(OrderStatus.DRAFT)
    }
}
```

## Bootstrap Modes

| Mode | Loads | Use When |
|------|-------|----------|
| `STANDALONE` | Current module only | Unit-like testing |
| `DIRECT_DEPENDENCIES` | Module + direct dependencies | Most common |
| `ALL_DEPENDENCIES` | Full dependency tree | Integration testing |

```java
@ApplicationModuleTest(mode = BootstrapMode.DIRECT_DEPENDENCIES)
class OrderModuleWithDependenciesTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private InventoryService inventoryService;  // Direct dependency available

    // ShippingService NOT available if not direct dependency
}
```

## Scenario API

Fluent API for testing asynchronous event-driven behavior.

### Verify Event Publication

```java
@ApplicationModuleTest
class OrderEventTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldPublishOrderCreatedEvent(Scenario scenario) {
        CreateOrderRequest request = new CreateOrderRequest("customer-123", "Widget", 5);

        scenario.stimulate(() -> orderService.create(request))
            .andWaitForEventOfType(OrderCreated.class)
            .toArriveAndVerify(event -> {
                assertThat(event.customerId()).isEqualTo("customer-123");
                assertThat(event.productName()).isEqualTo("Widget");
                assertThat(event.quantity()).isEqualTo(5);
            });
    }
}
```

### Kotlin Scenario

```kotlin
@ApplicationModuleTest
class OrderEventTest(@Autowired val orderService: OrderService) {

    @Test
    fun `should publish order created event`(scenario: Scenario) {
        val request = CreateOrderRequest("customer-123", "Widget", 5)

        scenario.stimulate { orderService.create(request) }
            .andWaitForEventOfType(OrderCreated::class.java)
            .toArriveAndVerify { event ->
                assertThat(event.customerId).isEqualTo("customer-123")
                assertThat(event.quantity).isEqualTo(5)
            }
    }
}
```

### Verify State Changes

```java
@ApplicationModuleTest
class InventoryEventHandlerTest {

    @Autowired
    private StockRepository stockRepository;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @Test
    void shouldDecrementStockOnOrderCreated(Scenario scenario) {
        // Setup initial stock
        stockRepository.save(new Stock("product-123", 100));

        // Publish event
        OrderCreated event = new OrderCreated(1L, "customer-1", "product-123", 5);

        scenario.publish(event)
            .andWaitForStateChange(() -> stockRepository.findByProductId("product-123"))
            .andVerify(stock -> {
                assertThat(stock.getQuantity()).isEqualTo(95);
            });
    }
}
```

### Multiple Events

```java
@Test
void shouldPublishMultipleEvents(Scenario scenario) {
    scenario.stimulate(() -> orderService.submitOrder(orderId))
        .andWaitForEventOfType(OrderSubmitted.class)
        .toArrive()
        .andWaitForEventOfType(PaymentRequested.class)
        .toArriveAndVerify(event -> {
            assertThat(event.orderId()).isEqualTo(orderId);
        });
}
```

### Event Matching

```java
@Test
void shouldMatchSpecificEvent(Scenario scenario) {
    scenario.stimulate(() -> orderService.createOrders(requests))
        .andWaitForEventOfType(OrderCreated.class)
        .matching(event -> event.customerId().equals("priority-customer"))
        .toArriveAndVerify(event -> {
            assertThat(event.priority()).isTrue();
        });
}
```

### Timeout Configuration

```java
@Test
void shouldCompleteWithinTimeout(Scenario scenario) {
    scenario.stimulate(() -> orderService.processLargeOrder(request))
        .andWaitForEventOfType(OrderProcessed.class)
        .toArriveWithin(Duration.ofSeconds(10))
        .andVerify(event -> {
            assertThat(event.status()).isEqualTo("COMPLETED");
        });
}
```

## Testing Event Handlers

### Publish Event Directly

```java
@ApplicationModuleTest
class NotificationEventHandlerTest {

    @Autowired
    private NotificationRepository notificationRepository;

    @Test
    void shouldCreateNotificationOnOrderShipped(Scenario scenario) {
        OrderShipped event = new OrderShipped(
            1L,
            "customer-123",
            "TRACK-12345"
        );

        scenario.publish(event)
            .andWaitForStateChange(() ->
                notificationRepository.findByCustomerId("customer-123"))
            .andVerify(notifications -> {
                assertThat(notifications).hasSize(1);
                assertThat(notifications.get(0).getMessage())
                    .contains("TRACK-12345");
            });
    }
}
```

### Verify Handler Called

```java
@ApplicationModuleTest
class AnalyticsEventHandlerTest {

    @MockitoBean
    private AnalyticsClient analyticsClient;

    @Test
    void shouldTrackOrderEvent(Scenario scenario) {
        OrderCreated event = new OrderCreated(1L, "customer-123", "Widget", 5);

        scenario.publish(event)
            .andWaitForEventOfType(OrderCreated.class)
            .toArrive();

        verify(analyticsClient, timeout(5000)).track(
            eq("order_created"),
            argThat(props -> props.get("orderId").equals(1L))
        );
    }
}
```

## Module Structure Verification

```java
class ModularityTests {

    private static final ApplicationModules modules =
        ApplicationModules.of(Application.class);

    @Test
    void shouldHaveNoCircularDependencies() {
        modules.verify();
    }

    @Test
    void shouldDocumentModules() {
        new Documenter(modules)
            .writeModulesAsPlantUml()
            .writeIndividualModulesAsPlantUml();
    }

    @Test
    void shouldDetectAllModules() {
        assertThat(modules.stream())
            .extracting(ApplicationModule::getName)
            .containsExactlyInAnyOrder(
                "order",
                "inventory",
                "shipping",
                "notification"
            );
    }
}
```

## Testing with Testcontainers

```java
@ApplicationModuleTest
@Testcontainers
class OrderModuleIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @Container
    @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

    @Autowired
    private OrderService orderService;

    @Test
    void shouldPersistAndPublish(Scenario scenario) {
        scenario.stimulate(() -> orderService.create(request))
            .andWaitForEventOfType(OrderCreated.class)
            .toArriveAndVerify(event -> {
                // Verify persisted
                assertThat(orderRepository.findById(event.orderId())).isPresent();
            });
    }
}
```

## Testing Event Externalization

```java
@ApplicationModuleTest
@EmbeddedKafka
class EventExternalizationTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    @Autowired
    private EmbeddedKafkaBroker embeddedKafka;

    @Test
    void shouldExternalizeEventToKafka(Scenario scenario) {
        Consumer<String, String> consumer = createConsumer("orders-topic");

        scenario.stimulate(() -> orderService.create(request))
            .andWaitForEventOfType(OrderCreated.class)
            .toArrive();

        ConsumerRecords<String, String> records =
            KafkaTestUtils.getRecords(consumer, Duration.ofSeconds(10));

        assertThat(records.count()).isEqualTo(1);
        assertThat(records.iterator().next().value())
            .contains("\"type\":\"OrderCreated\"");
    }
}
```

## Custom Test Scenario Configuration

```java
@ApplicationModuleTest
@Import(TestScenarioConfig.class)
class CustomScenarioTest {

    @Test
    void shouldUseCustomTimeout(Scenario scenario) {
        scenario.stimulate(() -> slowService.process())
            .andWaitForEventOfType(ProcessCompleted.class)
            .toArriveAndVerify(event -> {
                assertThat(event.success()).isTrue();
            });
    }
}

@TestConfiguration
class TestScenarioConfig {

    @Bean
    public ScenarioCustomizer scenarioCustomizer() {
        return ScenarioCustomizer.builder()
            .defaultTimeout(Duration.ofSeconds(30))
            .build();
    }
}
```

## Testing Sagas / Process Managers

```java
@ApplicationModuleTest
class OrderFulfillmentSagaTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldCompleteFulfillmentSaga(Scenario scenario) {
        // Start saga
        scenario.stimulate(() -> orderService.submit(orderId))
            // Wait for each step
            .andWaitForEventOfType(OrderSubmitted.class)
            .toArrive()
            .andWaitForEventOfType(PaymentProcessed.class)
            .toArrive()
            .andWaitForEventOfType(InventoryReserved.class)
            .toArrive()
            .andWaitForEventOfType(ShipmentCreated.class)
            .toArriveAndVerify(event -> {
                assertThat(event.trackingNumber()).isNotNull();
            });

        // Verify final state
        Order order = orderService.findById(orderId);
        assertThat(order.getStatus()).isEqualTo(OrderStatus.SHIPPED);
    }

    @Test
    void shouldCompensateOnFailure(Scenario scenario) {
        // Setup payment to fail
        paymentService.setForceFail(true);

        scenario.stimulate(() -> orderService.submit(orderId))
            .andWaitForEventOfType(OrderSubmitted.class)
            .toArrive()
            .andWaitForEventOfType(PaymentFailed.class)
            .toArrive()
            .andWaitForEventOfType(OrderCancelled.class)
            .toArriveAndVerify(event -> {
                assertThat(event.reason()).contains("Payment failed");
            });

        // Verify compensating actions
        Order order = orderService.findById(orderId);
        assertThat(order.getStatus()).isEqualTo(OrderStatus.CANCELLED);
    }
}
```

## Best Practices

1. **Test module boundaries** — Verify events cross modules correctly
2. **Use Scenario for async** — Don't use `Thread.sleep()`
3. **Verify state changes** — Not just event publication
4. **Test failure paths** — Compensating events, rollbacks
5. **Keep modules small** — Easier to test in isolation
6. **Document with tests** — Tests show how modules interact
