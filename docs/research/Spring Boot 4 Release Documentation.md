# Spring Boot 4 DDD implementation: A complete technical reference

Spring Boot 4.0.0, released November 20, 2025, fundamentally reshapes enterprise Java development with complete codebase modularization, Jakarta EE 11 alignment, and first-class JSpecify null safety. This report provides expert-level guidance for implementing Domain-Driven Design across the data access layer, web layer, and modular architecture—with production-ready code examples in both Java and Kotlin.

The new modular architecture breaks Spring Boot into **focused, technology-specific JARs** that reduce artifact size dramatically (the old `spring-boot-autoconfigure` jar grew to 2 MiB). Java 17 remains the baseline, but **Java 25 is strongly recommended** for virtual thread support and optimal performance. Spring Framework 7 underpins all changes, bringing native API versioning, declarative retry with `@Retryable`, and a portfolio-wide transition to Jackson 3.

---

## Data access layer: Aggregates, repositories, and DDD patterns

Spring Data JPA 2025.1 and Spring Data JDBC form the foundation for DDD-compliant persistence. Spring Data JDBC inherently aligns with DDD by treating **aggregates as first-class concepts**—everything reachable from an aggregate root through non-transient references belongs to that aggregate.

### Repository patterns and Spring Boot 4 changes

Spring Boot 4 introduces several enhancements: **AOT Repositories** compile query methods to source code for faster startup, **JSpecify annotations** provide standardized null safety, and new specification types (`PredicateSpecification`, `UpdateSpecification`, `DeleteSpecification`) enable more expressive queries.

The repository hierarchy provides increasing functionality: `Repository<T, ID>` (marker), `CrudRepository` (basic CRUD), `ListCrudRepository` (returns List instead of Iterable), `PagingAndSortingRepository` (pagination/sorting), and `JpaRepository` (JPA-specific operations including `flush()` and `saveAndFlush()`).

**Java aggregate root with value objects:**

```java
@Entity
@Table(name = "orders")
@EntityListeners(AuditingEntityListener.class)
public class Order extends AbstractAggregateRoot<Order> {
    
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Embedded
    @AttributeOverride(name = "value", column = @Column(name = "customer_id"))
    private CustomerId customerId;
    
    @Embedded
    private Money totalAmount;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private Set<OrderLine> orderLines = new HashSet<>();
    
    @CreatedDate
    private Instant createdAt;
    
    @Version
    private Long version;
    
    protected Order() {} // JPA required
    
    public Order(CustomerId customerId) {
        this.customerId = customerId;
        this.status = OrderStatus.DRAFT;
        this.totalAmount = Money.ZERO;
    }
    
    public void addOrderLine(ProductId productId, int quantity, Money price) {
        orderLines.add(new OrderLine(productId, quantity, price));
        recalculateTotal();
    }
    
    public void submit() {
        if (orderLines.isEmpty()) {
            throw new IllegalStateException("Cannot submit empty order");
        }
        this.status = OrderStatus.SUBMITTED;
        registerEvent(new OrderSubmittedEvent(this.id)); // Domain event
    }
    
    private void recalculateTotal() {
        this.totalAmount = orderLines.stream()
            .map(OrderLine::getLineTotal)
            .reduce(Money.ZERO, Money::add);
    }
}
```

**Kotlin aggregate root:**

```kotlin
@Entity
@Table(name = "orders")
@EntityListeners(AuditingEntityListener::class)
class Order private constructor() : AbstractAggregateRoot<Order>() {
    
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null
        private set
    
    @Embedded
    lateinit var customerId: CustomerId
        private set
    
    @Embedded
    var totalAmount: Money = Money.ZERO
        private set
    
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private val _orderLines: MutableSet<OrderLine> = mutableSetOf()
    val orderLines: Set<OrderLine> get() = _orderLines.toSet()
    
    constructor(customerId: CustomerId) : this() {
        this.customerId = customerId
    }
    
    fun addOrderLine(productId: ProductId, quantity: Int, price: Money) {
        _orderLines.add(OrderLine(productId, quantity, price))
        recalculateTotal()
    }
    
    fun submit(): Order {
        check(_orderLines.isNotEmpty()) { "Cannot submit empty order" }
        status = OrderStatus.SUBMITTED
        registerEvent(OrderSubmittedEvent(id!!))
        return this
    }
}
```

### Transaction management essentials

The `@Transactional` annotation supports seven propagation levels: **REQUIRED** (default—join or create), **REQUIRES_NEW** (always new, suspend existing), **SUPPORTS** (use if present), **NOT_SUPPORTED** (non-transactional), **MANDATORY** (require existing), **NEVER** (fail if exists), and **NESTED** (savepoint).

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-----------------|------------|---------------------|--------------|
| READ_UNCOMMITTED | ✓ | ✓ | ✓ |
| READ_COMMITTED | ✗ | ✓ | ✓ |
| REPEATABLE_READ | ✗ | ✗ | ✓ |
| SERIALIZABLE | ✗ | ✗ | ✗ |

**Transactional service layer (Java):**

```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    
    @Transactional
    public Order createOrder(CustomerId customerId) {
        return orderRepository.save(new Order(customerId));
    }
    
    @Transactional(readOnly = true)
    public List<OrderSummary> getOrdersByStatus(OrderStatus status) {
        return orderRepository.findByStatus(status);
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW, 
                   isolation = Isolation.REPEATABLE_READ)
    public void processPayment(Long orderId, PaymentDetails payment) {
        Order order = orderRepository.findWithLinesById(orderId)
            .orElseThrow(() -> new EntityNotFoundException("Order not found"));
        // Payment processing with stronger isolation
    }
}
```

### Solving the N+1 problem

Three primary solutions exist for the N+1 query problem:

1. **JOIN FETCH in JPQL**: `@Query("SELECT o FROM Order o JOIN FETCH o.orderLines WHERE o.id = :id")`
2. **@EntityGraph annotation**: Declarative eager fetching without modifying queries
3. **Batch fetching**: Configure `hibernate.default_batch_fetch_size=10` globally

**Repository with EntityGraph and custom queries:**

```java
public interface OrderRepository extends JpaRepository<Order, Long>, 
                                        JpaSpecificationExecutor<Order> {
    
    @EntityGraph(attributePaths = {"orderLines", "orderLines.product"})
    Optional<Order> findWithLinesById(Long id);
    
    @Query("SELECT o FROM Order o WHERE o.customerId.value = :customerId")
    List<Order> findByCustomerId(@Param("customerId") String customerId);
    
    // Projection for read operations
    List<OrderSummary> findByStatus(OrderStatus status);
    
    @Modifying
    @Query("UPDATE Order o SET o.status = :status WHERE o.createdAt < :date")
    int archiveOldOrders(@Param("status") OrderStatus status, @Param("date") Instant date);
}
```

### Projections maximize read performance

Interface-based projections create proxy objects supporting nested projections; class-based DTOs (especially Java records) avoid proxying overhead:

```java
// Interface projection with nested projection
public interface OrderSummary {
    Long getId();
    OrderStatus getStatus();
    Money getTotalAmount();
    CustomerInfo getCustomer();
    
    interface CustomerInfo {
        String getName();
    }
}

// Class-based DTO projection (better performance)
public record OrderDto(Long id, String status, BigDecimal totalAmount) {}

// Dynamic projection in repository
<T> Collection<T> findByStatus(OrderStatus status, Class<T> type);
```

---

## Web layer: Controllers, validation, and reactive patterns

Spring Boot 4 introduces **native API versioning**, migrates to **Jackson 3** as the preferred JSON library, and provides enhanced **ProblemDetail (RFC 9457/7807)** support for structured error responses.

### API versioning is now built-in

Spring Framework 7 provides first-class API versioning through the `version` attribute on mapping annotations:

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @GetMapping(path = "/{id}", version = "1.0")
    public ProductV1 getProductV1(@PathVariable String id) {
        return productServiceV1.findById(id);
    }
    
    @GetMapping(path = "/{id}", version = "2.0")
    public ProductV2 getProductV2(@PathVariable String id) {
        return productServiceV2.findById(id);
    }
}
```

Configuration supports header-based (`API-Version`), query parameter, path segment, and media type versioning strategies:

```properties
spring.mvc.apiversion.use.header=API-Version
spring.mvc.apiversion.default=1
spring.mvc.apiversion.supported=1,2
spring.mvc.apiversion.required=true
```

### Exception handling with ProblemDetail

**Global exception handler (Java):**

```java
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleResourceNotFound(ResourceNotFoundException ex, 
                                                 HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage()
        );
        problem.setType(URI.create("https://api.example.com/errors/not-found"));
        problem.setTitle("Resource Not Found");
        problem.setInstance(URI.create(request.getRequestURI()));
        problem.setProperty("resourceId", ex.getResourceId());
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }
    
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex, HttpHeaders headers,
            HttpStatusCode status, WebRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST, "Validation failed"
        );
        problem.setType(URI.create("https://api.example.com/errors/validation"));
        problem.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
            .map(e -> Map.of("field", e.getField(), "message", e.getDefaultMessage()))
            .toList());
        return ResponseEntity.of(problem).build();
    }
}
```

**Kotlin exception handler:**

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler : ResponseEntityExceptionHandler() {
    
    @ExceptionHandler(ResourceNotFoundException::class)
    fun handleNotFound(ex: ResourceNotFoundException, request: HttpServletRequest): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.message ?: "Not found").apply {
            type = URI.create("https://api.example.com/errors/not-found")
            title = "Resource Not Found"
            instance = URI.create(request.requestURI)
            setProperty("resourceId", ex.resourceId)
        }
}
```

### WebFlux functional router

**Java functional endpoints:**

```java
@Configuration
public class ProductRouter {
    
    @Bean
    public RouterFunction<ServerResponse> productRoutes(ProductHandler handler) {
        return RouterFunctions.route()
            .path("/api/v1/products", builder -> builder
                .GET("", accept(APPLICATION_JSON), handler::getAll)
                .GET("/{id}", accept(APPLICATION_JSON), handler::getById)
                .POST("", contentType(APPLICATION_JSON), handler::create)
            )
            .onError(ProductNotFoundException.class, (e, req) ->
                ServerResponse.notFound().build())
            .build();
    }
}

@Component
public class ProductHandler {
    private final ProductService productService;
    
    public Mono<ServerResponse> getById(ServerRequest request) {
        String id = request.pathVariable("id");
        return productService.findById(id)
            .flatMap(p -> ServerResponse.ok().bodyValue(p))
            .switchIfEmpty(ServerResponse.notFound().build());
    }
}
```

**Kotlin coRouter DSL:**

```kotlin
@Configuration
class ProductRouter(private val handler: ProductHandler) {
    
    @Bean
    fun routes() = coRouter {
        "/api/v1/products".nest {
            GET("/{id}") { handler.getById(it) }
            GET("") { handler.getAll(it) }
            POST("") { handler.create(it) }
        }
    }
}
```

### When to choose WebFlux over MVC

Choose **Spring MVC** when using JPA/JDBC (blocking APIs), requiring simpler debugging, or working with teams unfamiliar with reactive programming. Choose **Spring WebFlux** when handling high concurrency (thousands of concurrent connections), streaming real-time data, using reactive databases (R2DBC, MongoDB Reactive), or building microservices with extensive remote service calls.

### Testing with WebTestClient

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class ProductApiTests {
    
    @Autowired
    private WebTestClient webClient;
    
    @Test
    void createProduct_ValidInput_ReturnsCreated() {
        var request = new CreateProductRequest("Test Product", new BigDecimal("29.99"));
        
        webClient.post()
            .uri("/api/v1/products")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated()
            .expectHeader().exists("Location")
            .expectBody()
            .jsonPath("$.name").isEqualTo("Test Product");
    }
    
    @Test
    void getProduct_NotFound_ReturnsProblemDetail() {
        webClient.get()
            .uri("/api/v1/products/NOTFOUND")
            .exchange()
            .expectStatus().isNotFound()
            .expectBody()
            .jsonPath("$.type").value(containsString("not-found"))
            .jsonPath("$.title").isEqualTo("Resource Not Found");
    }
}
```

---

## Spring Modulith: Bounded contexts as modules

Spring Modulith 2.0 (for Spring Boot 4) provides an opinionated toolkit for building modular monolithic applications. Each module maps directly to a DDD bounded context, with **package conventions enforcing encapsulation** and **event-driven communication** maintaining loose coupling.

### Module structure and boundaries

The standard package layout defines module boundaries:

```
src/main/java
├── com.example                    ← Application root
│   └── Application.java           ← @SpringBootApplication
├── com.example.order              ← Module API package (public)
│   ├── OrderService.java          ← Public service
│   └── OrderCreated.java          ← Public event
├── com.example.order.internal     ← Internal (inaccessible externally)
│   └── OrderRepository.java
└── com.example.inventory          ← Another module
    └── InventoryService.java
```

Types in the module's base package are public API; sub-packages are internal implementation.

**Module configuration:**

```java
// package-info.java in com.example.order
@ApplicationModule(
    allowedDependencies = {"inventory :: api", "customer"},
    type = Type.CLOSED  // Enforce encapsulation
)
package com.example.order;
```

### Event-driven inter-module communication

The `@ApplicationModuleListener` combines `@Async`, `@Transactional(REQUIRES_NEW)`, and `@TransactionalEventListener`—events are delivered asynchronously in new transactions after the original transaction commits:

**Java event publishing and handling:**

```java
// Publishing module
@Service
@RequiredArgsConstructor
public class OrderService {
    private final ApplicationEventPublisher events;
    
    @Transactional
    public void completeOrder(UUID orderId) {
        Order order = repository.findById(orderId).orElseThrow();
        order.complete();
        events.publishEvent(new OrderCompleted(order.getId(), order.getItems()));
    }
}

// Domain event
public record OrderCompleted(UUID orderId, List<OrderItem> items, Instant occurredAt) {
    public OrderCompleted(UUID orderId, List<OrderItem> items) {
        this(orderId, items, Instant.now());
    }
}

// Consuming module
@Component
@RequiredArgsConstructor
public class InventoryEventHandler {
    private final StockRepository stocks;
    
    @ApplicationModuleListener
    void on(OrderCompleted event) {
        event.items().forEach(item -> 
            stocks.decrementStock(item.productId(), item.quantity())
        );
    }
}
```

**Kotlin event handling:**

```kotlin
@Component
class InventoryEventHandler(private val stocks: StockRepository) {
    
    @ApplicationModuleListener
    fun on(event: OrderCompleted) {
        event.items.forEach { item ->
            stocks.decrementStock(item.productId, item.quantity)
        }
    }
}
```

### Testing with @ApplicationModuleTest and Scenario API

```java
@ApplicationModuleTest
class OrderModuleTests {
    
    @Autowired
    private OrderService orders;
    
    @Test
    void orderCompletionPublishesEvent(Scenario scenario) {
        UUID orderId = createTestOrder();
        
        scenario.stimulate(() -> orders.completeOrder(orderId))
            .andWaitForEventOfType(OrderCompleted.class)
            .matching(e -> e.orderId().equals(orderId))
            .toArriveAndVerify(event -> {
                assertThat(event.items()).isNotEmpty();
            });
    }
    
    @Test
    void inventoryUpdatedOnOrderCompletion(Scenario scenario) {
        scenario.publish(new OrderCompleted(orderId, items))
            .andWaitForStateChange(() -> inventory.getStock(productId))
            .andVerify(stock -> assertThat(stock).isEqualTo(99));
    }
}
```

Bootstrap modes control module isolation: `STANDALONE` (current module only), `DIRECT_DEPENDENCIES` (module plus direct dependencies), `ALL_DEPENDENCIES` (entire dependency tree).

### Event externalization to Kafka/AMQP

```java
@Externalized("orders::#{#this.customerId}")
public record OrderCompleted(UUID orderId, String customerId) {}

@Bean
EventExternalizationConfiguration eventExternalization() {
    return EventExternalizationConfiguration.externalizing()
        .select(annotatedAsExternalized())
        .mapping(OrderCompleted.class, e -> new OrderDTO(e.orderId()))
        .routeKey(OrderCompleted.class, OrderCompleted::customerId)
        .build();
}
```

---

## Spring Boot 4 migration essentials

### Breaking changes require immediate attention

**Removed technologies:** Undertow (incompatible with Servlet 6.1), Pulsar Reactive, embedded uber-jar launch scripts, Spring Session Hazelcast/MongoDB (now community-maintained).

**Jackson 3 migration:** Packages relocated from `com.fasterxml.jackson` to `tools.jackson`. Annotations renamed: `@JsonComponent` → `@JacksonComponent`, `@JsonMixin` → `@JacksonMixin`. A Jackson 2 compatibility module (`spring-boot-jackson2`) eases migration.

**Testing changes:** `@SpringBootTest` no longer auto-configures MockMvc—add `@AutoConfigureMockMvc` explicitly. WebClient and TestRestTemplate beans also require explicit configuration.

### Starter dependencies restructured

| Old Starter | New Starter |
|------------|-------------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` |
| `spring-boot-starter-aop` | `spring-boot-starter-aspectj` |
| `spring-boot-starter-oauth2-client` | `spring-boot-starter-security-oauth2-client` |

Every technology now has a dedicated test starter: `spring-boot-starter-webmvc-test`, `spring-boot-starter-data-jpa-test`, etc.

**Gradual migration path using classic starters:**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-classic</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test-classic</artifactId>
    <scope>test</scope>
</dependency>
```

### JSpecify null safety adoption

Spring Framework 7 and Spring Boot 4 use JSpecify annotations (`@Nullable`, `@NonNull`, `@NullMarked`) portfolio-wide. Kotlin 2.2 automatically translates these to native nullability types, and IntelliJ IDEA 2025.3 provides first-class IDE support.

```java
@NullMarked
@Service
public class UserService {
    @Nullable
    public User findByEmail(String email) {
        return userRepository.findByEmail(email);
    }
}
```

---

## Anti-patterns and best practices checklist

### Data access layer pitfalls

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| EAGER fetching by default | N+1 queries, excessive data loading | Use `FetchType.LAZY`; fetch explicitly with `@EntityGraph` or JOIN FETCH |
| Missing `@Transactional` on writes | Data inconsistency, partial commits | Always annotate service methods that modify data |
| Returning entities from controllers | Tight coupling, LazyInitializationException | Convert to DTOs in service layer |
| `@Transactional` on private methods | Transaction not applied (proxy bypass) | Use public methods or AspectJ mode |
| Missing `readOnly = true` on queries | Write locks, reduced throughput | Add `@Transactional(readOnly = true)` for read operations |
| Open Session in View enabled | Hidden N+1 in view layer, debugging difficulty | Disable and initialize associations in service layer |

**Best practices:**
- Use interface projections for flexible read operations; class-based DTOs for performance-critical paths
- Configure `hibernate.default_batch_fetch_size=10` to mitigate unforeseen N+1 issues
- Implement auditing with `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`
- Test with `@DataJpaTest` and `TestEntityManager`; call `entityManager.clear()` to verify lazy loading behavior

### Web layer pitfalls

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Business logic in controllers | Untestable code, violation of SRP | Move logic to application services; controllers only delegate |
| Ignoring validation groups | Duplicate validation logic | Use `@Validated(OnCreate.class)` for operation-specific validation |
| Generic exception messages | Security risk, poor debugging | Use ProblemDetail with typed error URIs |
| Missing `@AutoConfigureMockMvc` in Boot 4 | Tests fail silently | Add annotation explicitly |
| Blocking calls in WebFlux | Thread pool exhaustion | Use reactive operators; avoid `.block()` |

**Best practices:**
- Enable ProblemDetail globally: `spring.mvc.problemdetails.enabled=true`
- Implement CQRS with separate command and query controllers for complex domains
- Use `@Valid` on `@RequestBody` parameters; create custom validators for domain-specific rules
- Choose WebFlux only when concurrency requirements justify reactive complexity

### Modulith pitfalls

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Direct bean injection across modules | Tight coupling, monolith architecture | Use events for inter-module communication |
| Synchronous event handling | Transaction coupling, cascade failures | Use `@ApplicationModuleListener` for async processing |
| Module dependencies not declared | Hidden coupling, verification failures | Explicitly declare `allowedDependencies` in `@ApplicationModule` |
| Missing module verification tests | Boundary violations undetected | Add `ApplicationModules.of(Application.class).verify()` test |

**Best practices:**
- Map each module to exactly one bounded context
- Reference other aggregates by ID, not direct object references
- Use the Scenario API to test event flows across modules
- Generate module documentation with `new Documenter(modules).writeDocumentation()`

### Configuration pitfalls

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Not upgrading through 3.5.x first | Missing deprecation warnings | Migrate incrementally: 3.x → 3.5.x → 4.0 |
| Ignoring Jackson 3 package changes | Runtime ClassNotFoundException | Update imports from `com.fasterxml.jackson` to `tools.jackson` |
| Using Undertow | Application won't start | Switch to Tomcat 11+ or Jetty 12.1+ |
| Not adding test starters | Missing test infrastructure | Add `spring-boot-starter-*-test` for each technology |

---

## Version compatibility matrix

| Component | Spring Boot 4.0 Requirement |
|-----------|----------------------------|
| Java | 17+ (25 recommended) |
| Kotlin | 2.2+ |
| GraalVM | 25+ (for native) |
| Spring Framework | 7.0 |
| Jakarta EE | 11 |
| Servlet | 6.1 |
| Hibernate | 7.1 |
| Jackson | 3.x |
| Tomcat | 11+ |
| Jetty | 12.1+ |
| Spring Modulith | 2.0 |

---

## Conclusion

Spring Boot 4 represents a significant architectural evolution toward **modularity, null safety, and DDD alignment**. The codebase modularization reduces application footprint while providing stronger architectural boundaries. Native API versioning and enhanced ProblemDetail support improve REST API design. Spring Modulith 2.0 bridges the gap between monolithic development simplicity and microservices-style bounded context isolation.

For DDD practitioners, the combination of Spring Data JDBC's aggregate-first design, Spring Modulith's event-driven inter-module communication, and the comprehensive JSpecify null safety creates a robust foundation for domain modeling. Migration from Spring Boot 3.x requires attention to Jackson 3 package changes, explicit test annotations, and the new starter naming conventions—but the classic starters provide a gradual transition path.

Key adoption priorities: upgrade through 3.5.x to catch deprecation warnings, add technology-specific test starters, enable ProblemDetail globally, verify module structure with `ApplicationModules.verify()`, and embrace `@ApplicationModuleListener` for loosely coupled event handling across bounded contexts.