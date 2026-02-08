# Micrometer Metrics

Timer, Counter, Gauge, and DistributionSummary patterns.

## Table of Contents

- [Meter Types](#meter-types)
- [Counter Patterns](#counter-patterns)
  - [Basic Counter](#basic-counter)
  - [Counter with Tags](#counter-with-tags)
  - [Kotlin Counter](#kotlin-counter)
- [Timer Patterns](#timer-patterns)
  - [Basic Timer](#basic-timer)
  - [Timer with SLOs](#timer-with-slos)
  - [Timer with Tags](#timer-with-tags)
  - [@Timed Annotation](#timed-annotation)
- [Gauge Patterns](#gauge-patterns)
  - [Gauge from AtomicInteger](#gauge-from-atomicinteger)
  - [Gauge from Collection](#gauge-from-collection)
  - [Gauge from Method](#gauge-from-method)
  - [Kotlin Gauge](#kotlin-gauge)
- [DistributionSummary Patterns](#distributionsummary-patterns)
  - [Request Size Tracking](#request-size-tracking)
  - [Batch Size Tracking](#batch-size-tracking)
- [MeterBinder Pattern](#meterbinder-pattern)
- [Common Tags (Global)](#common-tags-global)
- [Tag Best Practices](#tag-best-practices)
- [Registry Types](#registry-types)
  - [Prometheus](#prometheus)
  - [Datadog](#datadog)
  - [Multiple Registries](#multiple-registries)

## Meter Types

| Type | Purpose | Example |
|------|---------|---------|
| **Counter** | Monotonically increasing value | Requests, errors, orders created |
| **Gauge** | Current value that can go up/down | Active connections, queue size |
| **Timer** | Duration + count | Request latency, processing time |
| **DistributionSummary** | Distribution of values | Request sizes, batch sizes |

## Counter Patterns

### Basic Counter

```java
@Component
public class OrderMetrics {

    private final Counter ordersCreated;
    private final Counter ordersFailed;

    public OrderMetrics(MeterRegistry registry) {
        this.ordersCreated = Counter.builder("orders.created")
            .description("Total orders created")
            .register(registry);

        this.ordersFailed = Counter.builder("orders.failed")
            .description("Total failed order attempts")
            .register(registry);
    }

    public void orderCreated() {
        ordersCreated.increment();
    }

    public void orderFailed() {
        ordersFailed.increment();
    }
}
```

### Counter with Tags

```java
@Component
public class PaymentMetrics {

    private final MeterRegistry registry;

    public void recordPayment(String method, String status, double amount) {
        Counter.builder("payments.total")
            .description("Total payments processed")
            .tag("method", method)      // credit_card, paypal, bank_transfer
            .tag("status", status)       // success, failed, pending
            .register(registry)
            .increment();

        // Also track amount
        DistributionSummary.builder("payments.amount")
            .description("Payment amounts")
            .tag("method", method)
            .tag("status", status)
            .baseUnit("dollars")
            .register(registry)
            .record(amount);
    }
}
```

### Kotlin Counter

```kotlin
@Component
class OrderMetrics(registry: MeterRegistry) {

    private val ordersCreated = Counter.builder("orders.created")
        .description("Total orders created")
        .register(registry)

    private val ordersByChannel = mutableMapOf<String, Counter>()

    fun orderCreated(channel: String) {
        ordersCreated.increment()
        ordersByChannel.getOrPut(channel) {
            Counter.builder("orders.by_channel")
                .tag("channel", channel)
                .register(registry)
        }.increment()
    }
}
```

## Timer Patterns

### Basic Timer

```java
@Component
public class ProcessingMetrics {

    private final Timer processingTimer;

    public ProcessingMetrics(MeterRegistry registry) {
        this.processingTimer = Timer.builder("processing.duration")
            .description("Processing duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .publishPercentileHistogram()
            .register(registry);
    }

    public <T> T recordProcessing(Supplier<T> operation) {
        return processingTimer.record(operation);
    }

    public void recordDuration(Duration duration) {
        processingTimer.record(duration);
    }
}
```

### Timer with SLOs

```java
Timer orderTimer = Timer.builder("order.processing.duration")
    .description("Order processing duration")
    .publishPercentiles(0.5, 0.75, 0.95, 0.99)
    .publishPercentileHistogram()
    .serviceLevelObjectives(
        Duration.ofMillis(100),   // Fast
        Duration.ofMillis(500),   // Normal
        Duration.ofSeconds(1),    // Slow
        Duration.ofSeconds(5)     // Very slow
    )
    .minimumExpectedValue(Duration.ofMillis(1))
    .maximumExpectedValue(Duration.ofSeconds(30))
    .register(registry);
```

### Timer with Tags

```java
public void recordApiCall(String endpoint, String method, int statusCode, Duration duration) {
    Timer.builder("http.client.requests")
        .description("HTTP client request duration")
        .tag("uri", endpoint)
        .tag("method", method)
        .tag("status", String.valueOf(statusCode))
        .tag("outcome", statusCode >= 400 ? "error" : "success")
        .register(registry)
        .record(duration);
}
```

### @Timed Annotation

```java
@Configuration
public class TimedConfig {
    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
}

@Service
public class OrderService {

    @Timed(value = "order.creation", percentiles = {0.5, 0.95, 0.99})
    public Order createOrder(CreateOrderRequest request) {
        // Method execution is automatically timed
    }

    @Timed(value = "order.processing", histogram = true)
    public void processOrder(Long orderId) {
        // With histogram for percentile approximation
    }
}
```

## Gauge Patterns

### Gauge from AtomicInteger

```java
@Component
public class ConnectionMetrics {

    private final AtomicInteger activeConnections = new AtomicInteger(0);

    public ConnectionMetrics(MeterRegistry registry) {
        Gauge.builder("connections.active", activeConnections, AtomicInteger::get)
            .description("Number of active connections")
            .register(registry);
    }

    public void connectionOpened() {
        activeConnections.incrementAndGet();
    }

    public void connectionClosed() {
        activeConnections.decrementAndGet();
    }
}
```

### Gauge from Collection

```java
@Component
public class QueueMetrics {

    public QueueMetrics(MeterRegistry registry, BlockingQueue<?> workQueue) {
        Gauge.builder("queue.size", workQueue, BlockingQueue::size)
            .description("Current queue size")
            .register(registry);

        Gauge.builder("queue.remaining_capacity", workQueue, BlockingQueue::remainingCapacity)
            .description("Remaining queue capacity")
            .register(registry);
    }
}
```

### Gauge from Method

```java
@Component
public class CacheMetrics {

    private final CacheManager cacheManager;

    public CacheMetrics(MeterRegistry registry, CacheManager cacheManager) {
        this.cacheManager = cacheManager;

        Gauge.builder("cache.size", this, CacheMetrics::getTotalCacheSize)
            .description("Total items across all caches")
            .register(registry);
    }

    private double getTotalCacheSize() {
        return cacheManager.getCacheNames().stream()
            .mapToLong(name -> getCacheSize(cacheManager.getCache(name)))
            .sum();
    }
}
```

### Kotlin Gauge

```kotlin
@Component
class QueueMetrics(registry: MeterRegistry, private val workQueue: BlockingQueue<*>) {

    init {
        Gauge.builder("queue.size", workQueue) { it.size.toDouble() }
            .description("Current queue size")
            .register(registry)
    }
}
```

## DistributionSummary Patterns

### Request Size Tracking

```java
@Component
public class RequestMetrics {

    private final DistributionSummary requestSize;
    private final DistributionSummary responseSize;

    public RequestMetrics(MeterRegistry registry) {
        this.requestSize = DistributionSummary.builder("http.request.size")
            .description("Request body size")
            .baseUnit("bytes")
            .publishPercentiles(0.5, 0.95)
            .register(registry);

        this.responseSize = DistributionSummary.builder("http.response.size")
            .description("Response body size")
            .baseUnit("bytes")
            .publishPercentiles(0.5, 0.95)
            .register(registry);
    }

    public void recordRequest(long bytes) {
        requestSize.record(bytes);
    }

    public void recordResponse(long bytes) {
        responseSize.record(bytes);
    }
}
```

### Batch Size Tracking

```java
DistributionSummary batchSize = DistributionSummary.builder("batch.size")
    .description("Batch processing size")
    .publishPercentileHistogram()
    .serviceLevelObjectives(10, 50, 100, 500, 1000)
    .register(registry);

// Record batch sizes
batchSize.record(items.size());
```

## MeterBinder Pattern

Auto-register metrics on startup:

```java
@Component
public class DatabasePoolMetricsBinder implements MeterBinder {

    private final HikariDataSource dataSource;

    @Override
    public void bindTo(MeterRegistry registry) {
        Gauge.builder("db.pool.active", dataSource, ds -> ds.getHikariPoolMXBean().getActiveConnections())
            .description("Active database connections")
            .register(registry);

        Gauge.builder("db.pool.idle", dataSource, ds -> ds.getHikariPoolMXBean().getIdleConnections())
            .description("Idle database connections")
            .register(registry);

        Gauge.builder("db.pool.pending", dataSource, ds -> ds.getHikariPoolMXBean().getThreadsAwaitingConnection())
            .description("Threads waiting for connection")
            .register(registry);

        Gauge.builder("db.pool.total", dataSource, ds -> ds.getHikariPoolMXBean().getTotalConnections())
            .description("Total connections in pool")
            .register(registry);
    }
}
```

## Common Tags (Global)

```java
@Configuration
public class MetricsConfig {

    @Bean
    public MeterRegistryCustomizer<MeterRegistry> commonTags() {
        return registry -> registry.config()
            .commonTags(
                "application", "order-service",
                "environment", System.getenv("ENVIRONMENT"),
                "region", System.getenv("REGION")
            );
    }
}
```

## Tag Best Practices

| Good (Low Cardinality) | Bad (High Cardinality) |
|------------------------|------------------------|
| `status=success` | `user_id=12345` |
| `method=POST` | `request_id=abc-123` |
| `region=us-east-1` | `timestamp=2025-01-01T10:00:00` |
| `payment_method=credit_card` | `email=user@example.com` |
| `error_type=validation` | `stack_trace=...` |

## Registry Types

### Prometheus

```yaml
management:
  prometheus:
    metrics:
      export:
        enabled: true
        step: 1m
```

### Datadog

```yaml
management:
  datadog:
    metrics:
      export:
        api-key: ${DATADOG_API_KEY}
        enabled: true
```

### Multiple Registries

```java
@Configuration
public class MultiRegistryConfig {

    @Bean
    public CompositeMeterRegistry compositeMeterRegistry(
            PrometheusMeterRegistry prometheus,
            DatadogMeterRegistry datadog) {
        CompositeMeterRegistry composite = new CompositeMeterRegistry();
        composite.add(prometheus);
        composite.add(datadog);
        return composite;
    }
}
```
