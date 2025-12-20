# Error Handling with ProblemDetail

RFC 9457 (formerly RFC 7807) compliant error responses in Spring Boot 4.

## ProblemDetail Structure

```json
{
  "type": "https://api.example.com/errors/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order with ID 12345 was not found",
  "instance": "/api/orders/12345",
  "orderId": 12345,
  "timestamp": "2025-12-20T10:30:00Z"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | URI identifying error type (for client handling) |
| `title` | Yes | Short human-readable summary |
| `status` | Yes | HTTP status code |
| `detail` | No | Human-readable explanation |
| `instance` | No | URI of specific occurrence |
| Custom fields | No | Additional context (orderId, timestamp, etc.) |

## Global Exception Handler

### Java

```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {
    
    private static final String ERROR_BASE_URI = "https://api.example.com/errors/";
    
    // Domain exceptions
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex, HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            ex.getMessage()
        );
        problem.setType(URI.create(ERROR_BASE_URI + "resource-not-found"));
        problem.setTitle("Resource Not Found");
        problem.setInstance(URI.create(request.getRequestURI()));
        problem.setProperty("resourceType", ex.getResourceType());
        problem.setProperty("resourceId", ex.getResourceId());
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }
    
    @ExceptionHandler(BusinessRuleViolationException.class)
    public ProblemDetail handleBusinessRule(BusinessRuleViolationException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.UNPROCESSABLE_ENTITY,
            ex.getMessage()
        );
        problem.setType(URI.create(ERROR_BASE_URI + "business-rule-violation"));
        problem.setTitle("Business Rule Violation");
        problem.setProperty("ruleCode", ex.getRuleCode());
        return problem;
    }
    
    @ExceptionHandler(ConcurrentModificationException.class)
    public ProblemDetail handleConcurrency(ConcurrentModificationException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.CONFLICT,
            "Resource was modified by another request. Please retry."
        );
        problem.setType(URI.create(ERROR_BASE_URI + "concurrent-modification"));
        problem.setTitle("Concurrent Modification");
        return problem;
    }
    
    // Validation errors (override from ResponseEntityExceptionHandler)
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex,
            HttpHeaders headers,
            HttpStatusCode status,
            WebRequest request
    ) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST,
            "Validation failed for the request"
        );
        problem.setType(URI.create(ERROR_BASE_URI + "validation-error"));
        problem.setTitle("Validation Error");
        
        List<Map<String, String>> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(error -> Map.of(
                "field", error.getField(),
                "message", error.getDefaultMessage() != null ? error.getDefaultMessage() : "Invalid value",
                "rejectedValue", String.valueOf(error.getRejectedValue())
            ))
            .toList();
        
        problem.setProperty("errors", errors);
        problem.setProperty("errorCount", errors.size());
        
        return ResponseEntity.of(problem).build();
    }
    
    // Constraint violations (path/query params)
    @ExceptionHandler(ConstraintViolationException.class)
    public ProblemDetail handleConstraintViolation(ConstraintViolationException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST,
            "Request parameters validation failed"
        );
        problem.setType(URI.create(ERROR_BASE_URI + "constraint-violation"));
        problem.setTitle("Parameter Validation Error");
        
        List<Map<String, String>> errors = ex.getConstraintViolations().stream()
            .map(v -> Map.of(
                "path", v.getPropertyPath().toString(),
                "message", v.getMessage()
            ))
            .toList();
        
        problem.setProperty("errors", errors);
        return problem;
    }
    
    // Catch-all for unexpected exceptions
    @ExceptionHandler(Exception.class)
    public ProblemDetail handleUnexpected(Exception ex, HttpServletRequest request) {
        log.error("Unexpected error at {}: {}", request.getRequestURI(), ex.getMessage(), ex);
        
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred. Please try again later."
        );
        problem.setType(URI.create(ERROR_BASE_URI + "internal-error"));
        problem.setTitle("Internal Server Error");
        problem.setInstance(URI.create(request.getRequestURI()));
        problem.setProperty("traceId", MDC.get("traceId"));
        return problem;
    }
}
```

### Kotlin

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler : ResponseEntityExceptionHandler() {
    
    companion object {
        private const val ERROR_BASE_URI = "https://api.example.com/errors/"
    }
    
    @ExceptionHandler(ResourceNotFoundException::class)
    fun handleNotFound(ex: ResourceNotFoundException, request: HttpServletRequest): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.message ?: "Not found").apply {
            type = URI.create("${ERROR_BASE_URI}resource-not-found")
            title = "Resource Not Found"
            instance = URI.create(request.requestURI)
            setProperty("resourceId", ex.resourceId)
            setProperty("timestamp", Instant.now())
        }
    
    @ExceptionHandler(BusinessRuleViolationException::class)
    fun handleBusinessRule(ex: BusinessRuleViolationException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, ex.message ?: "").apply {
            type = URI.create("${ERROR_BASE_URI}business-rule-violation")
            title = "Business Rule Violation"
            setProperty("ruleCode", ex.ruleCode)
        }
}
```

## Exception Hierarchy

```java
// Base exception
public abstract class DomainException extends RuntimeException {
    private final String errorCode;
    
    protected DomainException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
    }
    
    public String getErrorCode() { return errorCode; }
}

// Specific exceptions
public class ResourceNotFoundException extends DomainException {
    private final String resourceType;
    private final Object resourceId;
    
    public ResourceNotFoundException(String resourceType, Object resourceId) {
        super(resourceType + " with ID " + resourceId + " was not found", "RESOURCE_NOT_FOUND");
        this.resourceType = resourceType;
        this.resourceId = resourceId;
    }
    
    // Convenience factory methods
    public static ResourceNotFoundException order(Long id) {
        return new ResourceNotFoundException("Order", id);
    }
    
    public static ResourceNotFoundException customer(CustomerId id) {
        return new ResourceNotFoundException("Customer", id.value());
    }
}

public class BusinessRuleViolationException extends DomainException {
    private final String ruleCode;
    
    public BusinessRuleViolationException(String message, String ruleCode) {
        super(message, "BUSINESS_RULE_VIOLATION");
        this.ruleCode = ruleCode;
    }
    
    public static BusinessRuleViolationException emptyOrder() {
        return new BusinessRuleViolationException(
            "Cannot submit an empty order",
            "ORDER_EMPTY"
        );
    }
    
    public static BusinessRuleViolationException insufficientStock(ProductId productId) {
        return new BusinessRuleViolationException(
            "Insufficient stock for product " + productId.value(),
            "INSUFFICIENT_STOCK"
        );
    }
}
```

## Error Type Registry

Define error URIs in a central place:

```java
public final class ErrorTypes {
    private static final String BASE = "https://api.example.com/errors/";
    
    // 4xx Client Errors
    public static final URI VALIDATION_ERROR = URI.create(BASE + "validation-error");
    public static final URI RESOURCE_NOT_FOUND = URI.create(BASE + "resource-not-found");
    public static final URI BUSINESS_RULE = URI.create(BASE + "business-rule-violation");
    public static final URI CONCURRENT_MODIFICATION = URI.create(BASE + "concurrent-modification");
    public static final URI UNAUTHORIZED = URI.create(BASE + "unauthorized");
    public static final URI FORBIDDEN = URI.create(BASE + "forbidden");
    
    // 5xx Server Errors
    public static final URI INTERNAL_ERROR = URI.create(BASE + "internal-error");
    public static final URI SERVICE_UNAVAILABLE = URI.create(BASE + "service-unavailable");
    
    private ErrorTypes() {}
}
```

## Custom ProblemDetail Subclass

For consistent additional fields:

```java
public class ApiProblemDetail extends ProblemDetail {
    
    private Instant timestamp;
    private String traceId;
    
    public ApiProblemDetail(HttpStatus status, String detail) {
        super(status.value());
        setDetail(detail);
        this.timestamp = Instant.now();
        this.traceId = MDC.get("traceId");
    }
    
    public Instant getTimestamp() { return timestamp; }
    public String getTraceId() { return traceId; }
    
    public static ApiProblemDetail notFound(String detail) {
        ApiProblemDetail problem = new ApiProblemDetail(HttpStatus.NOT_FOUND, detail);
        problem.setType(ErrorTypes.RESOURCE_NOT_FOUND);
        problem.setTitle("Resource Not Found");
        return problem;
    }
}
```

## Per-Controller Exception Handling

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    // Controller-specific handler
    @ExceptionHandler(OrderNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ProblemDetail handleOrderNotFound(OrderNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            ex.getMessage()
        );
        problem.setType(ErrorTypes.RESOURCE_NOT_FOUND);
        problem.setTitle("Order Not Found");
        problem.setProperty("orderId", ex.getOrderId());
        return problem;
    }
}
```

## Testing Error Responses

```java
@WebMvcTest(OrderController.class)
class OrderControllerErrorTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockitoBean
    private OrderService orderService;
    
    @Test
    void getOrder_NotFound_ReturnsProblemDetail() throws Exception {
        when(orderService.findById(999L))
            .thenThrow(ResourceNotFoundException.order(999L));
        
        mockMvc.perform(get("/api/orders/999"))
            .andExpect(status().isNotFound())
            .andExpect(content().contentType(APPLICATION_PROBLEM_JSON))
            .andExpect(jsonPath("$.type").value(containsString("resource-not-found")))
            .andExpect(jsonPath("$.title").value("Resource Not Found"))
            .andExpect(jsonPath("$.status").value(404))
            .andExpect(jsonPath("$.resourceId").value("999"));
    }
    
    @Test
    void createOrder_InvalidInput_ReturnsValidationErrors() throws Exception {
        String invalidRequest = """
            {
                "customerId": null,
                "lines": []
            }
            """;
        
        mockMvc.perform(post("/api/orders")
                .contentType(APPLICATION_JSON)
                .content(invalidRequest))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.type").value(containsString("validation-error")))
            .andExpect(jsonPath("$.errors").isArray())
            .andExpect(jsonPath("$.errors[?(@.field == 'customerId')]").exists())
            .andExpect(jsonPath("$.errors[?(@.field == 'lines')]").exists());
    }
}
```

## Configuration

```properties
# Enable ProblemDetail for all Spring MVC exceptions (default in Boot 4)
spring.mvc.problemdetails.enabled=true

# Include exception message in response (development only!)
server.error.include-message=always
server.error.include-binding-errors=always
server.error.include-stacktrace=never
server.error.include-exception=false
```

## Best Practices

1. **Use URIs for types** — Enables client-side error handling logic
2. **Keep titles short** — Human-readable category, not full explanation
3. **Put details in detail** — Specific explanation for this occurrence
4. **Add traceId** — Correlate with logs for debugging
5. **Don't expose internals** — No stack traces or internal paths in production
6. **Document error types** — Publish your error type URIs in API docs
7. **Test error responses** — Verify ProblemDetail structure in tests
