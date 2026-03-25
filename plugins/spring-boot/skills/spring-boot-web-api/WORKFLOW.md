# Spring Boot Web API Workflow

Detailed step-by-step process for implementing REST APIs with Spring Boot 4.

---

## Step 1: Create Controller

Set up a thin REST controller that delegates to services.

### 1a. Controller Structure

```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }
}
```

### 1b. Technology Choice

| Choose | When |
|--------|------|
| **Spring MVC** (`@RestController`) | JPA/JDBC backend, simpler debugging, team knows imperative style |
| **Spring WebFlux** (functional router) | High concurrency (10k+ connections), streaming, reactive DB (R2DBC) |

With Java 21+ Virtual Threads (`spring.threads.virtual.enabled=true`), MVC handles high concurrency without WebFlux complexity.

### 1c. Controller Rules

- **Thin controllers** — No business logic, delegate to services
- **DTOs for input/output** — Never expose domain entities
- **Consistent naming** — `/api/v1/{resource}` pattern

**Output**: Controller class with injected service dependencies.

---

## Step 2: Define Endpoints

Map HTTP methods to controller methods.

### 2a. Standard CRUD Mapping

```java
@GetMapping
public List<OrderDto> list() {
    return orderService.findAll();
}

@GetMapping("/{id}")
public OrderDto get(@PathVariable Long id) {
    return orderService.findById(id);
}

@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public OrderDto create(@Valid @RequestBody CreateOrderRequest request) {
    return orderService.create(request);
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
```

### 2b. Pagination

```java
@GetMapping
public Page<OrderDto> list(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(defaultValue = "createdAt,desc") String[] sort
) {
    Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
    return orderService.findAll(pageable);
}
```

### 2c. @HttpExchange Declarative Client (Spring 7)

For consuming external APIs:

```java
@HttpExchange(url = "/users", accept = "application/json")
public interface UserClient {
    @GetExchange("/{id}")
    User getUser(@PathVariable Long id);

    @PostExchange
    User createUser(@RequestBody CreateUserRequest request);
}
```

**Output**: Endpoints mapped with proper HTTP methods and status codes.

---

## Step 3: Add Validation

Validate request bodies at the API boundary.

### 3a. Bean Validation 3.1

```java
public record CreateOrderRequest(
    @NotNull Long customerId,
    @NotEmpty List<@Valid OrderLineRequest> items,
    @Size(max = 500) String notes
) {}

public record OrderLineRequest(
    @NotNull Long productId,
    @Positive int quantity,
    @PositiveOrZero BigDecimal unitPrice
) {}
```

### 3b. Custom Validators

```java
@Constraint(validatedBy = UniqueEmailValidator.class)
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueEmail {
    String message() default "Email already exists";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 3c. Validation Groups

```java
public interface OnCreate {}
public interface OnUpdate {}

public record UserRequest(
    @Null(groups = OnCreate.class) Long id,
    @NotBlank String name,
    @NotBlank(groups = OnCreate.class) String password
) {}
```

**Output**: Request validation with clear error messages.

---

## Step 4: Handle Exceptions

Implement global error handling with ProblemDetail (RFC 9457).

### 4a. Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ProblemDetail handleNotFound(OrderNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Order Not Found");
        problem.setType(URI.create("https://api.example.com/errors/order-not-found"));
        problem.setProperty("orderId", ex.getOrderId());
        return problem;
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ProblemDetail handleValidation(ConstraintViolationException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST, "Validation failed");
        problem.setTitle("Validation Error");
        problem.setProperty("violations", ex.getConstraintViolations().stream()
            .map(v -> Map.of(
                "field", v.getPropertyPath().toString(),
                "message", v.getMessage()))
            .toList());
        return problem;
    }
}
```

### 4b. ProblemDetail Response Format

```json
{
  "type": "https://api.example.com/errors/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order with ID 42 was not found",
  "instance": "/api/v1/orders/42",
  "orderId": 42
}
```

### 4c. Enable ProblemDetail (Boot 4)

ProblemDetail is enabled by default in Spring Boot 4:

```yaml
spring:
  mvc:
    problemdetails:
      enabled: true  # Default: true in Boot 4
```

### 4d. Exception Hierarchy

Define a structured exception hierarchy for clean error handling:

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `ResourceNotFoundException` | 404 | Entity not found by ID |
| `BusinessRuleViolationException` | 422 | Domain invariant violated |
| `ConflictException` | 409 | Concurrent modification or duplicate |
| `ConstraintViolationException` | 400 | Bean validation failure |

**Output**: Structured error responses following RFC 9457.

---

## Step 5: Configure Versioning

Set up API versioning for backward compatibility.

### 5a. Header-Based Versioning (Spring Boot 4)

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @GetMapping(version = "1")
    public OrderV1Dto getOrderV1(@PathVariable Long id) { ... }

    @GetMapping(version = "2")
    public OrderV2Dto getOrderV2(@PathVariable Long id) { ... }
}
```

### 5b. Content Negotiation

```yaml
spring:
  mvc:
    contentnegotiation:
      favor-parameter: false
      favor-path-extension: false
```

### 5c. Jackson 3 Configuration (Spring Boot 4)

Jackson 3 uses the `tools.jackson` package:

```java
@Configuration
public class JacksonConfig {
    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jsonCustomizer() {
        return builder -> builder
            .featuresToEnable(SerializationFeature.INDENT_OUTPUT)
            .featuresToDisable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .modules(new JavaTimeModule());
    }
}
```

**Important**: Jackson 3 uses `tools.jackson` namespace, not `com.fasterxml.jackson`.

**Output**: Versioned API with proper content negotiation.

---

## Verification Checklist

After implementing the web API:

- [ ] Controllers are thin — no business logic
- [ ] All `@RequestBody` parameters use `@Valid`
- [ ] `@RestControllerAdvice` handles all exceptions with ProblemDetail
- [ ] Response DTOs used (never entities)
- [ ] Proper HTTP status codes (`201 Created`, `204 No Content`)
- [ ] Jackson 3 configuration uses `tools.jackson` package
- [ ] Tests with `@WebMvcTest` cover endpoints — see `spring-boot-testing` skill
