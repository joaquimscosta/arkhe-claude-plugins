---
name: spring-boot-observability
description: Spring Boot 4 observability with Actuator, Micrometer, and OpenTelemetry. Use when configuring health indicators, custom metrics, distributed tracing, production endpoint exposure, or Kubernetes/Cloud Run probes. Covers Actuator security, Micrometer Timer/Counter/Gauge patterns, and OpenTelemetry span customization.
---

# Spring Boot Observability

Production observability with Actuator endpoints, Micrometer metrics, and OpenTelemetry tracing.

## Core Components

| Component | Purpose |
|-----------|---------|
| **Actuator** | Health checks, info, metrics exposure, operational endpoints |
| **Micrometer** | Metrics abstraction (Timer, Counter, Gauge, DistributionSummary) |
| **OpenTelemetry** | Distributed tracing (default in Spring Boot 4) |

## Core Workflow

1. **Add starters** → `actuator`, `micrometer-registry-*`, `opentelemetry`
2. **Configure endpoint exposure** → Secure sensitive endpoints
3. **Define health groups** → Separate liveness from readiness
4. **Add custom metrics** → Business-specific measurements
5. **Configure tracing** → Sampling, propagation, export

## Quick Implementation Patterns

### Production Actuator Configuration

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

### Custom Health Indicator

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

### Custom Micrometer Metrics

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

### OpenTelemetry Span Customization

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

## Spring Boot 4 Specifics

### OpenTelemetry as Default Tracer

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

### New Health Indicator Package

```java
// Spring Boot 4 imports
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
```

### Actuator Endpoint Access Control

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

## Detailed References

- **Actuator Endpoints**: See [references/actuator.md](references/actuator.md) for endpoint configuration, security, custom endpoints
- **Micrometer Metrics**: See [references/metrics.md](references/metrics.md) for Timer, Counter, Gauge, DistributionSummary patterns
- **Distributed Tracing**: See [references/tracing.md](references/tracing.md) for OpenTelemetry, span customization, context propagation

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| DB checks in liveness probe | Move to readiness group only |
| 100% trace sampling in production | Use 10% or less |
| Exposing all endpoints publicly | Separate management port + auth |
| High-cardinality metric tags | Use low-cardinality tags only |
| Missing graceful shutdown | Add `server.shutdown=graceful` |
| No health probe groups | Separate liveness and readiness |

## Critical Reminders

1. **Separate liveness from readiness** — Liveness: "is process alive?", Readiness: "can handle traffic?"
2. **Low cardinality tags only** — User IDs, request IDs = bad; status codes, regions = good
3. **Secure Actuator endpoints** — Use separate port or authentication
4. **Sample traces in production** — 100% sampling overwhelms collectors
5. **Graceful shutdown** — Allow in-flight requests to complete
