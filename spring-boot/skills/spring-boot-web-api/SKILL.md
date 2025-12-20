---
name: spring-boot-web-api
description: Spring Boot 4 REST API implementation patterns. Use when creating REST controllers, request validation, exception handlers with ProblemDetail (RFC 9457), API versioning, content negotiation, or WebFlux reactive endpoints. Covers @RestController patterns, Bean Validation 3.1, global error handling, and Jackson 3 configuration.
---

# Spring Boot Web API Layer

REST API implementation patterns for Spring Boot 4 with Spring MVC and WebFlux.

## Technology Selection

| Choose | When |
|--------|------|
| **Spring MVC** | JPA/JDBC backend, simpler debugging, team knows imperative style |
| **Spring WebFlux** | High concurrency (10k+ connections), streaming, reactive DB (R2DBC) |

With Virtual Threads (Java 21+), MVC handles high concurrency without WebFlux complexity.

## Core Workflow

1. **Create controller** → `@RestController` with `@RequestMapping` base path
2. **Define endpoints** → `@GetMapping`, `@PostMapping`, etc.
3. **Add validation** → `@Valid` on request body, custom validators
4. **Handle exceptions** → `@RestControllerAdvice` with `ProblemDetail`
5. **Configure versioning** → Native API versioning (Spring Boot 4)

## Quick Implementation Patterns

### REST Controller

```java
@RestController
@RequestMapping("/api/orders")
@Validated
public class OrderController {
    
    private final OrderService orderService;
    
    @GetMapping("/{id}")
    public OrderDto getById(@PathVariable Long id) {
        return orderService.findById(id);
    }
    
    @GetMapping
    public Page<OrderSummary> list(
        @RequestParam(defaultValue = "SUBMITTED") OrderStatus status,
        @PageableDefault(size = 20, sort = "createdAt", direction = DESC) Pageable pageable
    ) {
        return orderService.findByStatus(status, pageable);
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest request) {
        OrderDto created = orderService.create(request);
        URI location = URI.create("/api/orders/" + created.id());
        return ResponseEntity.created(location).body(created);
    }
    
    @PutMapping("/{id}")
    public OrderDto update(@PathVariable Long id, @Valid @RequestBody UpdateOrderRequest request) {
        return orderService.update(id, request);
    }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        orderService.delete(id);
    }
}
```

```kotlin
@RestController
@RequestMapping("/api/orders")
@Validated
class OrderController(private val orderService: OrderService) {
    
    @GetMapping("/{id}")
    fun getById(@PathVariable id: Long): OrderDto = orderService.findById(id)
    
    @PostMapping
    fun create(@Valid @RequestBody request: CreateOrderRequest): ResponseEntity<OrderDto> {
        val created = orderService.create(request)
        return ResponseEntity
            .created(URI.create("/api/orders/${created.id}"))
            .body(created)
    }
}
```

### Request/Response DTOs (Records)

```java
public record CreateOrderRequest(
    @NotNull CustomerId customerId,
    @NotEmpty List<@Valid OrderLineRequest> lines
) {}

public record OrderLineRequest(
    @NotNull ProductId productId,
    @Min(1) int quantity
) {}

public record OrderDto(
    Long id,
    String status,
    BigDecimal totalAmount,
    List<OrderLineDto> lines,
    Instant createdAt
) {
    public static OrderDto from(Order order) {
        return new OrderDto(
            order.getId(),
            order.getStatus().name(),
            order.getTotal().amount(),
            order.getLines().stream().map(OrderLineDto::from).toList(),
            order.getCreatedAt()
        );
    }
}
```

### Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex, HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage()
        );
        problem.setType(URI.create("https://api.example.com/errors/not-found"));
        problem.setTitle("Resource Not Found");
        problem.setInstance(URI.create(request.getRequestURI()));
        problem.setProperty("resourceId", ex.getResourceId());
        return problem;
    }
    
    @ExceptionHandler(BusinessRuleException.class)
    public ProblemDetail handleBusinessRule(BusinessRuleException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage()
        );
        problem.setType(URI.create("https://api.example.com/errors/business-rule"));
        problem.setTitle("Business Rule Violation");
        return problem;
    }
}
```

## Spring Boot 4 Specifics

### Native API Versioning

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @GetMapping(path = "/{id}", version = "1.0")
    public ProductV1 getV1(@PathVariable String id) {
        return productService.findByIdV1(id);
    }
    
    @GetMapping(path = "/{id}", version = "2.0")
    public ProductV2 getV2(@PathVariable String id) {
        return productService.findByIdV2(id);
    }
}
```

```properties
# application.properties
spring.mvc.apiversion.use.header=API-Version
spring.mvc.apiversion.default=1
spring.mvc.apiversion.supported=1,2
```

### Jackson 3 Configuration

```java
@Configuration
public class JacksonConfig {
    
    @Bean
    public Jackson3ObjectMapperBuilderCustomizer jsonCustomizer() {
        return builder -> builder
            .featuresToDisable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .featuresToEnable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
            .serializationInclusion(JsonInclude.Include.NON_NULL);
    }
}
```

**Note:** Jackson 3 uses `tools.jackson` package (not `com.fasterxml.jackson`).

### ProblemDetail Enabled by Default

```properties
spring.mvc.problemdetails.enabled=true  # Default in Boot 4
```

## Detailed References

- **Controllers & Validation**: See [references/controllers.md](references/controllers.md) for validation groups, custom validators, content negotiation
- **Error Handling**: See [references/error-handling.md](references/error-handling.md) for ProblemDetail patterns, exception hierarchy
- **WebFlux Patterns**: See [references/webflux.md](references/webflux.md) for reactive endpoints, functional routers, WebTestClient

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| Business logic in controllers | Delegate to application services |
| Returning entities directly | Convert to DTOs |
| Generic error messages | Use typed ProblemDetail with error URIs |
| Missing validation | Add `@Valid` on `@RequestBody` |
| Blocking calls in WebFlux | Use reactive operators only |
| Catching exceptions silently | Let propagate to `@RestControllerAdvice` |

## Testing

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockitoBean
    private OrderService orderService;
    
    @Test
    void createOrder_ValidInput_ReturnsCreated() throws Exception {
        var request = new CreateOrderRequest(CustomerId.generate(), List.of());
        var response = new OrderDto(1L, "DRAFT", BigDecimal.ZERO, List.of(), Instant.now());
        
        when(orderService.create(any())).thenReturn(response);
        
        mockMvc.perform(post("/api/orders")
                .contentType(APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"))
            .andExpect(jsonPath("$.id").value(1));
    }
}
```

## Critical Reminders

1. **Controllers are thin** — Delegate to services, no business logic
2. **Validate at the boundary** — `@Valid` on all request bodies
3. **Use ProblemDetail** — Structured errors for all exceptions
4. **Version from day one** — Easier than retrofitting
5. **`@MockitoBean` not `@MockBean`** — Spring Boot 4 change
