# Distributed Tracing

OpenTelemetry integration, span customization, and context propagation.

## OpenTelemetry Configuration

### Dependencies

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

### Configuration

```yaml
management:
  tracing:
    enabled: true
    sampling:
      probability: 1.0  # 100% for dev, 0.1 for prod
    propagation:
      type: w3c  # or b3 for Zipkin compatibility
  opentelemetry:
    resource-attributes:
      service.name: order-service
      service.version: 1.0.0
      deployment.environment: ${ENVIRONMENT:local}
    tracing:
      export:
        otlp:
          endpoint: http://otel-collector:4318/v1/traces
          # For gRPC: http://otel-collector:4317
```

### Production Configuration

```yaml
# application-prod.yml
management:
  tracing:
    sampling:
      probability: 0.1  # 10% sampling
  opentelemetry:
    tracing:
      export:
        otlp:
          endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
          headers:
            Authorization: Bearer ${OTEL_AUTH_TOKEN}
```

## Custom Spans with Observation API

### Basic Span Creation

```java
@Service
public class PaymentService {
    
    private final ObservationRegistry observationRegistry;
    
    public PaymentResult processPayment(PaymentRequest request) {
        return Observation.createNotStarted("payment.process", observationRegistry)
            .lowCardinalityKeyValue("payment.method", request.method().name())
            .lowCardinalityKeyValue("currency", request.currency())
            .observe(() -> doProcessPayment(request));
    }
    
    private PaymentResult doProcessPayment(PaymentRequest request) {
        // Business logic
    }
}
```

### Kotlin Span Creation

```kotlin
@Service
class PaymentService(private val observationRegistry: ObservationRegistry) {
    
    fun processPayment(request: PaymentRequest): PaymentResult =
        Observation.createNotStarted("payment.process", observationRegistry)
            .lowCardinalityKeyValue("payment.method", request.method.name)
            .lowCardinalityKeyValue("currency", request.currency)
            .observe { doProcessPayment(request) }
}
```

### Span with Error Handling

```java
public Order createOrder(CreateOrderRequest request) {
    Observation observation = Observation.createNotStarted("order.create", observationRegistry)
        .lowCardinalityKeyValue("channel", request.channel());
    
    return observation.observe(() -> {
        try {
            Order order = orderRepository.save(mapToOrder(request));
            observation.lowCardinalityKeyValue("status", "success");
            return order;
        } catch (Exception e) {
            observation.lowCardinalityKeyValue("status", "error");
            observation.lowCardinalityKeyValue("error.type", e.getClass().getSimpleName());
            throw e;
        }
    });
}
```

### Nested Spans

```java
public OrderResult processOrder(Long orderId) {
    return Observation.createNotStarted("order.process", observationRegistry)
        .observe(() -> {
            Order order = fetchOrder(orderId);      // Creates child span
            validateOrder(order);                    // Creates child span
            PaymentResult payment = chargePayment(order);  // Creates child span
            return fulfillOrder(order, payment);     // Creates child span
        });
}

private Order fetchOrder(Long orderId) {
    return Observation.createNotStarted("order.fetch", observationRegistry)
        .highCardinalityKeyValue("order.id", orderId.toString())
        .observe(() -> orderRepository.findById(orderId).orElseThrow());
}
```

## @Observed Annotation

```java
@Configuration
public class ObservationConfig {
    @Bean
    public ObservedAspect observedAspect(ObservationRegistry registry) {
        return new ObservedAspect(registry);
    }
}

@Service
public class OrderService {
    
    @Observed(name = "order.creation",
              contextualName = "creating-order",
              lowCardinalityKeyValues = {"operation", "create"})
    public Order createOrder(CreateOrderRequest request) {
        // Automatically traced
    }
}
```

## Baggage Propagation

Baggage propagates context across service boundaries:

```java
@Component
public class TenantContextPropagator {
    
    private final Tracer tracer;
    
    public void setTenantContext(String tenantId) {
        try (BaggageInScope baggage = tracer.createBaggageInScope("tenant.id", tenantId)) {
            // Tenant ID propagates to all downstream calls
        }
    }
    
    public String getCurrentTenant() {
        Baggage baggage = tracer.getBaggage("tenant.id");
        return baggage != null ? baggage.get() : null;
    }
}
```

Configuration:

```yaml
management:
  tracing:
    baggage:
      remote-fields:
        - tenant-id
        - correlation-id
      local-fields:
        - tenant-id
      correlation:
        fields:
          - tenant-id
```

## Logging Correlation

### Automatic MDC Integration

```yaml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%X{traceId:-},%X{spanId:-}] %-5level %logger{36} - %msg%n"
```

Logs automatically include trace and span IDs:

```
2025-01-15 10:30:45 [abc123def456,789xyz] INFO  c.e.OrderService - Processing order 12345
```

### Custom Context in Logs

```java
@Component
public class TracingFilter extends OncePerRequestFilter {
    
    private final Tracer tracer;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
            HttpServletResponse response, FilterChain chain) {
        
        Span currentSpan = tracer.currentSpan();
        if (currentSpan != null) {
            MDC.put("traceId", currentSpan.context().traceId());
            MDC.put("spanId", currentSpan.context().spanId());
        }
        
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.remove("traceId");
            MDC.remove("spanId");
        }
    }
}
```

## HTTP Client Tracing

### RestClient (Spring Boot 4)

```java
@Configuration
public class RestClientConfig {
    
    @Bean
    public RestClient restClient(RestClient.Builder builder) {
        return builder
            .baseUrl("https://api.example.com")
            .build();
        // Tracing automatically instrumented
    }
}
```

### WebClient

```java
@Configuration
public class WebClientConfig {
    
    @Bean
    public WebClient webClient(WebClient.Builder builder) {
        return builder
            .baseUrl("https://api.example.com")
            .build();
        // Tracing automatically instrumented
    }
}
```

## Database Tracing

JPA/JDBC operations are automatically traced. Add span tags:

```java
@Repository
public class OrderRepositoryImpl {
    
    private final ObservationRegistry observationRegistry;
    private final JdbcTemplate jdbcTemplate;
    
    public List<Order> findLargeOrders(BigDecimal threshold) {
        return Observation.createNotStarted("db.query.large_orders", observationRegistry)
            .lowCardinalityKeyValue("db.operation", "SELECT")
            .lowCardinalityKeyValue("db.table", "orders")
            .observe(() -> 
                jdbcTemplate.query(
                    "SELECT * FROM orders WHERE total > ?",
                    orderRowMapper,
                    threshold
                )
            );
    }
}
```

## Async Tracing

Context propagates to async operations:

```java
@Service
public class AsyncOrderProcessor {
    
    private final ObservationRegistry observationRegistry;
    
    @Async
    public CompletableFuture<ProcessingResult> processAsync(Order order) {
        // Observation context automatically propagated
        return Observation.createNotStarted("order.async_process", observationRegistry)
            .observe(() -> CompletableFuture.completedFuture(doProcess(order)));
    }
}
```

For manual propagation:

```java
@Service
public class ManualAsyncService {
    
    private final Tracer tracer;
    private final ExecutorService executor;
    
    public void processInBackground(Runnable task) {
        Span currentSpan = tracer.currentSpan();
        
        executor.submit(() -> {
            try (Tracer.SpanInScope ws = tracer.withSpan(currentSpan)) {
                task.run();
            }
        });
    }
}
```

## Span Events and Attributes

```java
public void processOrder(Order order) {
    Observation observation = Observation.start("order.process", observationRegistry);
    
    try {
        observation.event(Observation.Event.of("validation.started"));
        validateOrder(order);
        observation.event(Observation.Event.of("validation.completed"));
        
        observation.event(Observation.Event.of("payment.started"));
        processPayment(order);
        observation.event(Observation.Event.of("payment.completed"));
        
        observation.lowCardinalityKeyValue("order.status", "completed");
    } catch (Exception e) {
        observation.error(e);
        throw e;
    } finally {
        observation.stop();
    }
}
```

## Sampling Strategies

### Probability Sampling

```yaml
management:
  tracing:
    sampling:
      probability: 0.1  # 10%
```

### Custom Sampler

```java
@Bean
public Sampler customSampler() {
    return new Sampler() {
        @Override
        public SamplingResult shouldSample(
                Context parentContext,
                String traceId,
                String name,
                SpanKind spanKind,
                Attributes attributes,
                List<LinkData> parentLinks) {
            
            // Always sample errors
            if (name.contains("error")) {
                return SamplingResult.recordAndSample();
            }
            
            // Always sample health checks
            if (name.contains("health")) {
                return SamplingResult.drop();
            }
            
            // 10% for everything else
            return Math.random() < 0.1 
                ? SamplingResult.recordAndSample() 
                : SamplingResult.drop();
        }
        
        @Override
        public String getDescription() {
            return "CustomSampler";
        }
    };
}
```

## Exporters

### OTLP (OpenTelemetry Protocol)

```yaml
management:
  opentelemetry:
    tracing:
      export:
        otlp:
          endpoint: http://otel-collector:4318/v1/traces
```

### Zipkin

```yaml
management:
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

### Jaeger (via OTLP)

```yaml
management:
  opentelemetry:
    tracing:
      export:
        otlp:
          endpoint: http://jaeger:4317
```

## Testing with Traces

```java
@SpringBootTest
class TracingTest {
    
    @Autowired
    private TestObservationRegistry observationRegistry;
    
    @Autowired
    private OrderService orderService;
    
    @Test
    void shouldCreateSpanForOrderProcessing() {
        orderService.processOrder(testOrder);
        
        TestObservationRegistryAssert.assertThat(observationRegistry)
            .hasObservationWithNameEqualTo("order.process")
            .that()
            .hasLowCardinalityKeyValue("status", "success");
    }
}
```
