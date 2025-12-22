# Spring Boot Observability Troubleshooting

Common issues and solutions for Spring Boot 4 observability.

## Common Issues

### Issue: Actuator Endpoints Returning 404

**Symptom:** `/actuator/health` returns 404 Not Found

**Cause:** Endpoints not exposed or incorrect base path

**Solution:**

1. Check endpoint exposure:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
```

2. Verify base path configuration:
```yaml
management:
  endpoints:
    web:
      base-path: /actuator  # Default
```

3. Check if using separate management port:
```yaml
management:
  server:
    port: 8081  # Access at localhost:8081/actuator/health
```

---

### Issue: OpenTelemetry Traces Not Appearing

**Symptom:** No traces in Jaeger/Zipkin/OTLP collector

**Cause:** Missing dependencies, sampling at 0%, or wrong endpoint

**Solution:**

1. Verify dependencies:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

2. Check sampling configuration:
```yaml
management:
  tracing:
    sampling:
      probability: 1.0  # 100% for debugging, reduce in production
```

3. Verify OTLP endpoint:
```yaml
management:
  opentelemetry:
    tracing:
      export:
        otlp:
          endpoint: http://localhost:4318/v1/traces
```

---

### Issue: Custom Metrics Not Registered

**Symptom:** Custom metrics don't appear in `/actuator/metrics`

**Cause:** Metrics created but not registered to MeterRegistry

**Solution:**

```java
// Wrong - metric not registered
Timer timer = Timer.builder("my.timer").build();

// Correct - register to MeterRegistry
@Component
public class MyMetrics {
    private final Timer timer;

    public MyMetrics(MeterRegistry registry) {
        this.timer = Timer.builder("my.timer")
            .description("My custom timer")
            .register(registry);  // <-- Essential!
    }
}
```

---

### Issue: Health Indicator Timeout

**Symptom:** Health check times out, returns UNKNOWN status

**Cause:** Slow external dependency blocking health check

**Solution:**

1. Add timeout to health checks:
```yaml
management:
  endpoint:
    health:
      components:
        myIndicator:
          enabled: true
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

2. Implement async health indicator:
```java
@Component
public class AsyncExternalApiHealthIndicator implements ReactiveHealthIndicator {

    private final WebClient webClient;

    @Override
    public Mono<Health> health() {
        return webClient.get()
            .uri("/health")
            .retrieve()
            .bodyToMono(String.class)
            .timeout(Duration.ofSeconds(5))
            .map(response -> Health.up().build())
            .onErrorResume(e -> Mono.just(Health.down(e).build()));
    }
}
```

3. Move slow checks to readiness only:
```yaml
management:
  endpoint:
    health:
      group:
        liveness:
          include: livenessState,ping  # Fast checks only
        readiness:
          include: readinessState,db,externalApi  # Slower checks
```

---

### Issue: Prometheus Endpoint Not Available

**Symptom:** `/actuator/prometheus` returns 404

**Cause:** Missing micrometer-registry-prometheus dependency

**Solution:**

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

And ensure endpoint is exposed:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
```

---

### Issue: High-Cardinality Tag Explosion

**Symptom:** OOM or slow metrics queries

**Cause:** Using user IDs, request IDs, or other high-cardinality values as tags

**Solution:**

```java
// Wrong - high cardinality (millions of unique values)
Counter.builder("requests.total")
    .tag("user_id", userId)  // DON'T DO THIS
    .tag("request_id", requestId)  // DON'T DO THIS
    .register(registry);

// Correct - low cardinality (bounded set of values)
Counter.builder("requests.total")
    .tag("method", httpMethod)  // GET, POST, PUT, DELETE
    .tag("status", statusCode)  // 200, 201, 400, 404, 500
    .tag("endpoint", "/api/orders")  // Known endpoints
    .register(registry);
```

For high-cardinality data, use spans instead:
```java
Observation.createNotStarted("request", observationRegistry)
    .highCardinalityKeyValue("user_id", userId)  // OK for tracing
    .observe(() -> processRequest());
```

---

## Spring Boot 4 Migration Issues

### Health Indicator Import Changes

```java
// Before (Boot 3.x)
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;

// After (Boot 4.x)
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
```

### Endpoint Access Control Migration

```yaml
# Before (Boot 3.x)
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      enabled: true

# After (Boot 4.x) - add explicit access control
management:
  endpoints:
    access:
      default: none
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      access: unrestricted
```

### OpenTelemetry Default Tracer

Boot 4 uses OpenTelemetry by default instead of Brave:

```xml
<!-- Remove if present - no longer needed -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>

<!-- Add for Boot 4 -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
```
