# Spring Boot Web API Examples

Complete working examples for Spring Boot 4 REST API patterns.

## REST Controller

Standard CRUD controller with pagination, validation, and proper HTTP status codes.

### Java

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

### Kotlin

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

**Key points:**
- Use `@Validated` at class level for method parameter validation
- Return `ResponseEntity.created()` with Location header for POST
- Use `@PageableDefault` for sensible pagination defaults

---

## Request/Response DTOs

Records for immutable request/response objects with Bean Validation 3.1.

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

**Key points:**
- Use records for immutable DTOs
- Add `@Valid` before `List<>` type for nested validation
- Provide static factory `from()` for entity-to-DTO conversion

---

## Global Exception Handler

Structured error responses using RFC 9457 ProblemDetail.

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

**Key points:**
- Extend `ResponseEntityExceptionHandler` for validation error handling
- Use unique URIs for error types (documentation references)
- Add custom properties with `setProperty()` for error details

---

## Native API Versioning (Spring Boot 4)

Built-in API versioning via header or path.

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

**Key points:**
- Use `version` attribute in mapping annotations
- Configure default version for backward compatibility
- Header-based versioning keeps URLs clean

---

## Jackson 3 Configuration

Custom JSON serialization for Spring Boot 4.

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

**Key points:**
- Jackson 3 uses `tools.jackson` package (not `com.fasterxml.jackson`)
- ISO dates by default with `WRITE_DATES_AS_TIMESTAMPS` disabled
- Fail on unknown properties for strict API contracts

---

## Controller Testing

WebMvcTest with MockitoBean for slice testing.

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

**Key points:**
- Use `@MockitoBean` (not `@MockBean`) in Spring Boot 4
- Test validation, status codes, and response structure
- Verify Location header for POST endpoints
