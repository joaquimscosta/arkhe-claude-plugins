# Spring Boot Web API Troubleshooting

Common issues and solutions for Spring Boot 4 REST APIs.

## Common Issues

### Issue: ProblemDetail Not Returning Correct Content-Type

**Symptom:** Error responses return `text/plain` instead of `application/problem+json`

**Cause:** Missing or incorrect Accept header handling

**Solution:**
```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ProblemDetail> handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage()
        );
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .contentType(MediaType.APPLICATION_PROBLEM_JSON)
            .body(problem);
    }
}
```

Or ensure ProblemDetail is enabled globally:
```properties
spring.mvc.problemdetails.enabled=true
```

---

### Issue: Jackson 3 Serialization Changes Breaking API

**Symptom:** JSON output format changed after Boot 4 upgrade

**Cause:** Jackson 3 has different default behaviors

**Solution:**

1. Check package imports - Jackson 3 uses `tools.jackson`:
```java
// Before (Jackson 2)
import com.fasterxml.jackson.annotation.JsonProperty;

// After (Jackson 3)
import tools.jackson.annotation.JsonProperty;
```

2. Configure explicit serialization rules:
```java
@Bean
public Jackson3ObjectMapperBuilderCustomizer jsonCustomizer() {
    return builder -> builder
        .featuresToDisable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
        .serializationInclusion(JsonInclude.Include.NON_NULL);
}
```

---

### Issue: API Versioning Not Matching Routes

**Symptom:** Requests return 404 despite valid path

**Cause:** Version header not sent or misconfigured

**Solution:**

1. Verify version is in request:
```bash
curl -H "API-Version: 2" http://localhost:8080/api/products/123
```

2. Check configuration:
```properties
spring.mvc.apiversion.use.header=API-Version
spring.mvc.apiversion.default=1
spring.mvc.apiversion.supported=1,2
```

3. Ensure endpoint has version:
```java
@GetMapping(path = "/{id}", version = "2.0")
public ProductV2 getV2(@PathVariable String id) { ... }
```

---

### Issue: CORS Preflight Failures

**Symptom:** Browser requests fail with CORS error, OPTIONS returns 403

**Cause:** Security configuration blocking preflight requests

**Solution:**

Configure CORS in security filter chain:
```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    return http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        .csrf(csrf -> csrf.disable())  // For stateless API
        .build();
}

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

---

### Issue: @Valid Not Triggering Validation

**Symptom:** Invalid request bodies accepted without error

**Cause:** Missing `@Valid` annotation or validation dependency

**Solution:**

1. Add `@Valid` annotation:
```java
@PostMapping
public OrderDto create(@Valid @RequestBody CreateOrderRequest request) {
    // request is now validated
}
```

2. Ensure validation starter is present:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

3. For nested objects, add `@Valid` in the DTO:
```java
public record CreateOrderRequest(
    @NotNull CustomerId customerId,
    @NotEmpty List<@Valid OrderLineRequest> lines  // @Valid for nested
) {}
```

---

### Issue: Pagination Parameters Not Binding

**Symptom:** `Pageable` always returns default values

**Cause:** Parameter names don't match Spring expectations

**Solution:**

Spring expects these parameter names by default:
- `page` - page number (0-indexed)
- `size` - page size
- `sort` - sort property and direction

```bash
# Correct
GET /api/orders?page=0&size=20&sort=createdAt,desc

# Wrong - using offset instead of page
GET /api/orders?offset=0&limit=20
```

To customize parameter names:
```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        PageableHandlerMethodArgumentResolver resolver = new PageableHandlerMethodArgumentResolver();
        resolver.setPageParameterName("offset");
        resolver.setSizeParameterName("limit");
        resolvers.add(resolver);
    }
}
```

---

### Issue: ResponseEntity Location Header Missing Protocol

**Symptom:** Location header returns `/api/orders/1` instead of full URL

**Cause:** Using relative URI instead of absolute

**Solution:**

Use `ServletUriComponentsBuilder` for full URL:
```java
@PostMapping
public ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest request) {
    OrderDto created = orderService.create(request);

    URI location = ServletUriComponentsBuilder
        .fromCurrentRequest()
        .path("/{id}")
        .buildAndExpand(created.id())
        .toUri();

    return ResponseEntity.created(location).body(created);
}
```

---

## Spring Boot 4 Migration Issues

### ResponseEntityExceptionHandler Changes

```java
// Boot 4 - override with ProblemDetail return type
@Override
protected ResponseEntity<Object> handleMethodArgumentNotValid(
    MethodArgumentNotValidException ex,
    HttpHeaders headers,
    HttpStatusCode status,
    WebRequest request
) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(
        status, "Validation failed"
    );

    Map<String, String> errors = ex.getBindingResult().getFieldErrors().stream()
        .collect(Collectors.toMap(
            FieldError::getField,
            FieldError::getDefaultMessage
        ));

    problem.setProperty("errors", errors);
    return ResponseEntity.status(status).body(problem);
}
```

### MockMvc to MockMvcTester Migration

```java
// Before (Boot 3.x)
mockMvc.perform(get("/api/orders/1"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.status").value("SUBMITTED"));

// After (Boot 4.x) - optional, MockMvc still works
@Autowired
private MockMvcTester mvc;

assertThat(mvc.get().uri("/api/orders/1"))
    .hasStatusOk()
    .bodyJson()
    .extractingPath("$.status").isEqualTo("SUBMITTED");
```

### Content Negotiation Defaults

Boot 4 changes default content negotiation:
```properties
# Explicit configuration for backward compatibility
spring.mvc.contentnegotiation.favor-parameter=false
spring.mvc.contentnegotiation.favor-path-extension=false
spring.mvc.contentnegotiation.parameter-name=format
```
