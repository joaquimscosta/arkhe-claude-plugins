# Spring Boot Observability Examples

Complete working examples for Spring Boot 4 observability patterns.

## Production Actuator Configuration

Comprehensive actuator setup with health groups and Kubernetes probes.

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s

management:
  server:
    port: 8081  # Separate management port
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /manage
    access:
      default: none
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
      group:
        liveness:
          include: livenessState,ping
        readiness:
          include: readinessState,db,redis,diskSpace
  health:
    defaults:
      enabled: true
```

**Key points:**
- Use separate management port for production security
- Enable graceful shutdown to complete in-flight requests
- Separate liveness (is alive?) from readiness (can handle traffic?) probes

---

## Custom Health Indicator

Health indicator with latency monitoring and threshold-based status.

### Java

```java
@Component
public class ExternalApiHealthIndicator implements HealthIndicator {

    private final ExternalApiClient apiClient;
    private static final Duration TIMEOUT = Duration.ofSeconds(5);

    @Override
    public Health health() {
        try {
            long start = System.currentTimeMillis();
            apiClient.ping();
            long latency = System.currentTimeMillis() - start;

            if (latency > 3000) {
                return Health.down()
                    .withDetail("latency_ms", latency)
                    .withDetail("reason", "Response time exceeded threshold")
                    .build();
            }
            return Health.up()
                .withDetail("latency_ms", latency)
                .build();
        } catch (Exception e) {
            return Health.down(e)
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

### Kotlin

```kotlin
@Component
class ExternalApiHealthIndicator(private val apiClient: ExternalApiClient) : HealthIndicator {

    override fun health(): Health = runCatching {
        val start = System.currentTimeMillis()
        apiClient.ping()
        val latency = System.currentTimeMillis() - start

        if (latency > 3000) {
            Health.down()
                .withDetail("latency_ms", latency)
                .withDetail("reason", "Response time exceeded threshold")
                .build()
        } else {
            Health.up().withDetail("latency_ms", latency).build()
        }
    }.getOrElse { Health.down(it).build() }
}
```

**Key points:**
- Include latency details for debugging
- Define clear thresholds for degraded state
- Catch exceptions to prevent health check failures

---

## Custom Micrometer Metrics

Complete metrics class with Counter, Timer, and Gauge patterns.

```java
@Component
public class OrderMetrics {

    private final Counter ordersCreated;
    private final Timer orderProcessingTime;
    private final AtomicInteger activeOrders = new AtomicInteger(0);

    public OrderMetrics(MeterRegistry registry) {
        this.ordersCreated = Counter.builder("orders.created.total")
            .description("Total orders created")
            .tag("channel", "web")
            .register(registry);

        this.orderProcessingTime = Timer.builder("orders.processing.duration")
            .description("Order processing duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .publishPercentileHistogram()
            .serviceLevelObjectives(
                Duration.ofMillis(100),
                Duration.ofMillis(500),
                Duration.ofSeconds(1)
            )
            .register(registry);

        Gauge.builder("orders.active", activeOrders, AtomicInteger::get)
            .description("Currently active orders")
            .register(registry);
    }

    public void recordOrderCreated() {
        ordersCreated.increment();
        activeOrders.incrementAndGet();
    }

    public <T> T recordProcessing(Supplier<T> operation) {
        return orderProcessingTime.record(operation);
    }

    public void orderCompleted() {
        activeOrders.decrementAndGet();
    }
}
```

**Key points:**
- Use Counter for monotonically increasing values
- Use Timer with percentiles for duration measurements
- Use Gauge for current state values
- Always add descriptions for metric discovery

---

## OpenTelemetry Span Customization

Custom spans with the Observation API.

```java
@Component
public class PaymentProcessor {

    private final ObservationRegistry observationRegistry;

    public PaymentResult process(PaymentRequest request) {
        return Observation.createNotStarted("payment.processing", observationRegistry)
            .lowCardinalityKeyValue("payment.method", request.method().name())
            .lowCardinalityKeyValue("currency", request.currency())
            .highCardinalityKeyValue("merchant.id", request.merchantId())
            .observe(() -> executePayment(request));
    }
}
```

**Key points:**
- Use `lowCardinalityKeyValue` for tags used in aggregations (enum values, status codes)
- Use `highCardinalityKeyValue` for tracing only (IDs, user names)
- Observation API creates both spans and metrics automatically

---

## OpenTelemetry Configuration

Complete OTLP exporter configuration.

```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% in production
  opentelemetry:
    resource-attributes:
      service.name: my-service
      deployment.environment: production
    tracing:
      export:
        otlp:
          endpoint: http://otel-collector:4318/v1/traces
```

**Key points:**
- Set sampling probability based on traffic volume
- Include service.name for trace identification
- Use deployment.environment for filtering in observability tools

---

## Actuator Endpoint Access Control (Boot 4)

Granular access control for endpoints.

```yaml
management:
  endpoints:
    access:
      default: none  # Deny by default
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      access: unrestricted
    prometheus:
      access: read-only
```

**Key points:**
- Default to `none` access for defense in depth
- Use `unrestricted` only for health probes
- `read-only` prevents endpoint state changes
