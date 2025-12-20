# Spring Boot 4 implementation skills: Security, Observability, and Testing

**Spring Boot 4.0** introduces significant breaking changes alongside powerful new capabilities across its security, observability, and testing stacks. The **Lambda DSL is now mandatory** for Spring Security 7, `@MockitoBean` replaces the deprecated `@MockBean`, and OpenTelemetry becomes the default tracing solution. This report provides implementation-ready guidance with Java and Kotlin code examples for building production-grade applications.

## Spring Security 7 fundamentals and breaking changes

Spring Security 7.0 removes several deprecated APIs and makes the Lambda DSL the **only supported configuration style**. The most critical migrations involve replacing `authorizeRequests()` with `authorizeHttpRequests()`, `antMatchers()` with `requestMatchers()`, and all uses of the `and()` chaining method with Lambda closures.

| Removed API | Replacement | Migration Urgency |
|------------|-------------|-------------------|
| `and()` method | Lambda DSL closures | **Required** |
| `authorizeRequests()` | `authorizeHttpRequests()` | **Required** |
| `antMatchers()` | `requestMatchers()` | **Required** |
| `WebSecurityConfigurerAdapter` | `SecurityFilterChain` bean | **Required** |
| `AccessDecisionManager` | `AuthorizationManager` | **Required** |
| Jackson 2 modules | Jackson 3 `JsonMapper.builder()` | **Required** |

**Complete SecurityFilterChain configuration (Java):**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/public/**", "/login", "/error").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.GET, "/api/**").hasAuthority("SCOPE_read")
                .requestMatchers(HttpMethod.POST, "/api/**").hasAuthority("SCOPE_write")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard", true)
                .permitAll()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(Customizer.withDefaults())
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1)
            )
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.spa()); // New SPA-friendly CSRF in Security 7
        return http.build();
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return Argon2PasswordEncoder.defaultsForSpring7(); // New in Security 7
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://frontend.example.com"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

**Kotlin equivalent using the DSL extension:**

```kotlin
import org.springframework.security.config.annotation.web.invoke

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
class SecurityConfig {
    
    @Bean
    fun filterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            authorizeHttpRequests {
                authorize("/public/**", permitAll)
                authorize("/api/admin/**", hasRole("ADMIN"))
                authorize(HttpMethod.GET, "/api/**", hasAuthority("SCOPE_read"))
                authorize(anyRequest, authenticated)
            }
            formLogin {
                loginPage = "/login"
                defaultSuccessUrl("/dashboard", true)
            }
            oauth2ResourceServer { jwt { } }
            csrf { spa() }
        }
        return http.build()
    }
}
```

### UserDetailsService and method security patterns

Custom authentication requires implementing `UserDetailsService` and applying method-level authorization with `@PreAuthorize`. Spring Security 7's SpEL expressions support bean references, allowing complex authorization logic to be extracted into dedicated security services.

**Custom UserDetailsService (Java):**

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return userRepository.findByEmail(username)
            .map(user -> User.builder()
                .username(user.getEmail())
                .password(user.getPassword())
                .authorities(mapAuthorities(user.getRoles()))
                .build())
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
    }
    
    private Collection<GrantedAuthority> mapAuthorities(Set<Role> roles) {
        return roles.stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .collect(Collectors.toSet());
    }
}
```

**Method security with @PreAuthorize (Java):**

```java
@Service
public class DocumentService {
    
    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    public Document getDocument(Long userId, Long documentId) {
        // Owner or admin can access
    }
    
    @PreAuthorize("@documentSecurity.canEdit(authentication, #documentId)")
    public Document updateDocument(Long documentId, DocumentRequest request) {
        // Delegates to custom security bean
    }
    
    @PostFilter("filterObject.isPublic or filterObject.owner == authentication.name")
    public List<Document> findAllDocuments() {
        // Filters results after method execution
    }
}

@Component("documentSecurity")
public class DocumentSecurityEvaluator {
    public boolean canEdit(Authentication auth, Long documentId) {
        // Custom authorization logic
    }
}
```

### JWT Resource Server with custom claims extraction

JWT validation in Spring Security 7 uses `NimbusJwtDecoder` with configurable validators for issuer, audience, and custom claims. The `JwtAuthenticationConverter` maps JWT claims to Spring Security authorities.

**JWT configuration (Java):**

```java
@Configuration
public class JwtConfig {
    
    @Bean
    public JwtDecoder jwtDecoder() {
        NimbusJwtDecoder decoder = NimbusJwtDecoder
            .withIssuerLocation("https://auth.example.com")
            .jwsAlgorithm(SignatureAlgorithm.RS256)
            .build();
        
        OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(
            new JwtTimestampValidator(Duration.ofSeconds(60)),
            new JwtIssuerValidator("https://auth.example.com"),
            new JwtClaimValidator<List<String>>("aud", aud -> aud.contains("my-api"))
        );
        decoder.setJwtValidator(validator);
        return decoder;
    }
    
    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = 
            new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("permissions");
        grantedAuthoritiesConverter.setAuthorityPrefix(""); // No ROLE_ prefix for authorities
        
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return converter;
    }
}
```

**Testing secured endpoints (Java):**

```java
@WebMvcTest(SecuredController.class)
class SecuredControllerTest {
    
    @Autowired MockMvc mockMvc;
    
    @Test
    @WithMockUser(username = "admin", roles = {"ADMIN"})
    void adminCanAccessProtectedEndpoint() throws Exception {
        mockMvc.perform(get("/admin/dashboard"))
            .andExpect(status().isOk());
    }
    
    @Test
    void jwtAuthenticatedRequestSucceeds() throws Exception {
        mockMvc.perform(get("/api/resource")
                .with(jwt()
                    .authorities(new SimpleGrantedAuthority("SCOPE_read"))
                    .jwt(jwt -> jwt
                        .claim("sub", "user@example.com")
                        .claim("scope", "read write"))))
            .andExpect(status().isOk());
    }
}
```

---

## Observability with Actuator, Micrometer, and OpenTelemetry

Spring Boot 4 elevates OpenTelemetry to the **default tracing implementation**, with `spring-boot-starter-opentelemetry` providing integrated support for OTLP export. Micrometer remains the metrics abstraction, while Actuator exposes operational endpoints with granular security controls.

### Actuator endpoint configuration for production

Production deployments require careful endpoint exposure. Spring Boot 4 introduces a new access control model with `none`, `read-only`, and `unrestricted` options per endpoint.

**Production configuration (application-production.yml):**

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
        include: "health,info,metrics,prometheus,loggers"
    access:
      default: none  # Opt-in approach
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
        add-additional-paths: true  # Exposes /livez and /readyz
      group:
        liveness:
          include: "livenessState,ping"
        readiness:
          include: "readinessState,db,redis"
  health:
    ssl:
      certificate-validity-warning-threshold: 30d
  tracing:
    sampling:
      probability: 0.1  # 10% sampling in production
  opentelemetry:
    tracing:
      export:
        otlp:
          endpoint: "http://otel-collector:4318/v1/traces"
```

**Custom health indicator (Java):**

```java
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class ExternalApiHealthIndicator implements HealthIndicator {
    
    private final ExternalApiClient apiClient;
    
    @Override
    public Health health() {
        try {
            long latency = apiClient.ping();
            if (latency > 5000) {
                return Health.down()
                    .withDetail("latency", latency)
                    .withDetail("reason", "Response time exceeded threshold")
                    .build();
            }
            return Health.up().withDetail("latency", latency).build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

**Custom health indicator (Kotlin):**

```kotlin
import org.springframework.boot.health.contributor.Health
import org.springframework.boot.health.contributor.HealthIndicator
import org.springframework.stereotype.Component

@Component
class ExternalApiHealthIndicator(private val apiClient: ExternalApiClient) : HealthIndicator {
    
    override fun health(): Health = runCatching { apiClient.ping() }
        .fold(
            onSuccess = { latency ->
                if (latency > 5000) Health.down()
                    .withDetail("latency", latency)
                    .withDetail("reason", "Response time exceeded threshold")
                    .build()
                else Health.up().withDetail("latency", latency).build()
            },
            onFailure = { Health.down(it).build() }
        )
}
```

### Micrometer custom metrics implementation

Micrometer provides **Timer**, **Counter**, **Gauge**, and **DistributionSummary** meter types. Inject `MeterRegistry` directly or use the `MeterBinder` pattern for automatic registration.

**Custom metrics service (Java):**

```java
@Component
public class OrderMetrics {
    
    private final Counter ordersCreated;
    private final Timer orderProcessingTime;
    private final AtomicInteger activeOrders;
    
    public OrderMetrics(MeterRegistry registry) {
        this.ordersCreated = Counter.builder("orders.created.total")
            .description("Total number of orders created")
            .tag("channel", "web")
            .register(registry);
        
        this.orderProcessingTime = Timer.builder("orders.processing.duration")
            .description("Order processing time")
            .publishPercentiles(0.5, 0.95, 0.99)
            .publishPercentileHistogram()
            .serviceLevelObjectives(
                Duration.ofMillis(100),
                Duration.ofMillis(500),
                Duration.ofSeconds(1)
            )
            .register(registry);
        
        this.activeOrders = new AtomicInteger(0);
        Gauge.builder("orders.active", activeOrders, AtomicInteger::get)
            .description("Currently active orders")
            .register(registry);
    }
    
    public void recordOrderCreation() {
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

**Custom metrics (Kotlin):**

```kotlin
@Component
class OrderMetrics(registry: MeterRegistry) {
    
    private val ordersCreated = Counter.builder("orders.created.total")
        .description("Total orders created")
        .tag("channel", "web")
        .register(registry)
    
    private val orderProcessingTime = Timer.builder("orders.processing.duration")
        .publishPercentiles(0.5, 0.95, 0.99)
        .publishPercentileHistogram()
        .register(registry)
    
    private val activeOrders = AtomicInteger(0).also {
        Gauge.builder("orders.active", it) { it.get().toDouble() }
            .register(registry)
    }
    
    fun recordOrderCreation() {
        ordersCreated.increment()
        activeOrders.incrementAndGet()
    }
    
    fun <T> recordProcessing(operation: () -> T): T = orderProcessingTime.recordCallable(operation)!!
}
```

### OpenTelemetry span customization

Spring Boot 4 uses **Micrometer Observation API** as the bridge to OpenTelemetry. Custom spans are created via `ObservationRegistry`, providing vendor-neutral instrumentation.

**Custom span creation (Java):**

```java
@Component
public class PaymentProcessor {
    
    private final ObservationRegistry observationRegistry;
    private final Tracer tracer;
    
    public PaymentResult processPayment(PaymentRequest request) {
        return Observation.createNotStarted("payment.processing", observationRegistry)
            .lowCardinalityKeyValue("payment.method", request.getMethod().name())
            .lowCardinalityKeyValue("currency", request.getCurrency())
            .highCardinalityKeyValue("merchant.id", request.getMerchantId())
            .observe(() -> {
                // Add baggage for downstream propagation
                try (BaggageInScope baggage = tracer.createBaggageInScope(
                        "transaction.id", request.getTransactionId())) {
                    return executePayment(request);
                }
            });
    }
}
```

**Actuator security configuration (Java):**

```java
@Configuration(proxyBeanMethods = false)
public class ActuatorSecurityConfiguration {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        http.securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> requests
                .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                .requestMatchers(EndpointRequest.to("prometheus")).hasRole("METRICS")
                .anyRequest().hasRole("ENDPOINT_ADMIN")
            )
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```

---

## Testing strategies with slice tests and Testcontainers

Spring Boot 4 introduces **modular test starters** and replaces `@MockBean` with Spring Framework's `@MockitoBean`. The `@ServiceConnection` annotation for Testcontainers eliminates boilerplate dynamic property configuration.

### Critical breaking change: @MockitoBean replaces @MockBean

The migration from `@MockBean` to `@MockitoBean` is **mandatory** in Spring Boot 4. Key differences include the `REPLACE_OR_CREATE` strategy and prohibition on usage within `@Configuration` classes.

**@WebMvcTest with @MockitoBean (Java):**

```java
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.assertj.MockMvcTester;

@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvcTester mvc;  // New AssertJ-style MockMvc in Boot 4

    @MockitoBean  // Replaces @MockBean
    private ProductService productService;

    @Test
    void shouldReturnProductById() {
        given(productService.findById(1L))
            .willReturn(Optional.of(new Product(1L, "Laptop", BigDecimal.valueOf(999.99))));
        
        assertThat(mvc.get().uri("/api/products/1"))
            .hasStatusOk()
            .hasContentType(MediaType.APPLICATION_JSON)
            .bodyJson()
            .extractingPath("$.name").isEqualTo("Laptop");
    }

    @Test
    void shouldReturn404WhenProductNotFound() {
        given(productService.findById(999L)).willReturn(Optional.empty());
        
        assertThat(mvc.get().uri("/api/products/999"))
            .hasStatus(HttpStatus.NOT_FOUND);
    }
}
```

**@WebMvcTest (Kotlin):**

```kotlin
@WebMvcTest(ProductController::class)
class ProductControllerTest(@Autowired val mvc: MockMvcTester) {

    @MockitoBean
    lateinit var productService: ProductService

    @Test
    fun `should return product by id`() {
        given(productService.findById(1L))
            .willReturn(Optional.of(Product(1L, "Laptop", BigDecimal("999.99"))))
        
        assertThat(mvc.get().uri("/api/products/1"))
            .hasStatusOk()
            .bodyJson()
            .extractingPath("$.name").isEqualTo("Laptop")
    }
}
```

### @DataJpaTest with TestEntityManager patterns

Repository testing requires understanding flush/clear semantics for accurate lazy loading verification. `TestEntityManager` wraps the standard JPA `EntityManager` with testing conveniences.

**@DataJpaTest with TestEntityManager (Java):**

```java
@DataJpaTest
class OrderRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private OrderRepository orderRepository;

    @Test
    void shouldFindOrdersWithItems() {
        // Arrange
        Order order = new Order(LocalDateTime.now(), BigDecimal.valueOf(299.99));
        OrderItem item = new OrderItem(order, "Widget", 2, BigDecimal.valueOf(149.99));
        order.addItem(item);
        
        entityManager.persist(order);
        entityManager.flush();
        entityManager.clear();  // Critical: forces re-fetch, tests lazy loading
        
        // Act
        Optional<Order> found = orderRepository.findById(order.getId());
        
        // Assert
        assertThat(found).isPresent();
        assertThat(found.get().getItems()).hasSize(1);  // Triggers lazy load
    }

    @Test
    void shouldCascadeDeleteItems() {
        Order order = entityManager.persistFlushFind(
            new Order(LocalDateTime.now(), BigDecimal.ZERO));
        entityManager.persist(new OrderItem(order, "Item", 1, BigDecimal.TEN));
        entityManager.flush();
        
        orderRepository.delete(order);
        entityManager.flush();
        entityManager.clear();
        
        assertThat(entityManager.find(Order.class, order.getId())).isNull();
    }
}
```

**@DataJpaTest (Kotlin):**

```kotlin
@DataJpaTest
class OrderRepositoryTest(
    @Autowired val entityManager: TestEntityManager,
    @Autowired val orderRepository: OrderRepository
) {
    @Test
    fun `should find orders with items`() {
        val order = Order(LocalDateTime.now(), BigDecimal("299.99"))
        order.addItem(OrderItem(order, "Widget", 2, BigDecimal("149.99")))
        
        entityManager.persistAndFlush(order)
        entityManager.clear()
        
        val found = orderRepository.findById(order.id!!)
        assertThat(found).isPresent
        assertThat(found.get().items).hasSize(1)
    }
}
```

### Testcontainers with @ServiceConnection

The `@ServiceConnection` annotation automatically configures Spring Boot connection properties from container instances, replacing manual `@DynamicPropertySource` configuration.

**Testcontainers integration (Java):**

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
    
    @Container
    @ServiceConnection
    static RedisContainer redis = new RedisContainer("redis:7-alpine");
    
    @Container
    @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));

    @Autowired
    private WebTestClient webClient;
    
    @Autowired
    private OrderRepository orderRepository;

    @Test
    void shouldCreateAndRetrieveOrder() {
        OrderRequest request = new OrderRequest("Widget", 5, BigDecimal.valueOf(49.99));
        
        webClient.post()
            .uri("/api/orders")
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated()
            .expectBody()
            .jsonPath("$.id").isNotEmpty()
            .jsonPath("$.productName").isEqualTo("Widget");
        
        assertThat(orderRepository.findAll()).hasSize(1);
    }
}
```

**Testcontainers (Kotlin):**

```kotlin
@Testcontainers
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OrderIntegrationTest(
    @Autowired val webClient: WebTestClient,
    @Autowired val orderRepository: OrderRepository
) {
    companion object {
        @Container
        @ServiceConnection
        @JvmStatic
        val postgres = PostgreSQLContainer("postgres:16-alpine")
        
        @Container
        @ServiceConnection
        @JvmStatic
        val redis = RedisContainer("redis:7-alpine")
    }

    @Test
    fun `should create and retrieve order`() {
        val request = OrderRequest("Widget", 5, BigDecimal("49.99"))
        
        webClient.post()
            .uri("/api/orders")
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated
            .expectBody()
            .jsonPath("$.productName").isEqualTo("Widget")
        
        assertThat(orderRepository.findAll()).hasSize(1)
    }
}
```

### @ApplicationModuleTest with Scenario API for event-driven testing

Spring Modulith's Scenario API provides fluent testing for domain events and asynchronous interactions, essential for event-sourced and CQRS architectures.

**@ApplicationModuleTest (Java):**

```java
package com.example.order;

import org.springframework.modulith.test.ApplicationModuleTest;
import org.springframework.modulith.test.Scenario;

@ApplicationModuleTest
class OrderModuleIntegrationTest {

    @Autowired
    private OrderService orderService;

    @Test
    void shouldPublishOrderCompletedEvent(Scenario scenario) {
        Order order = new Order("customer-123", BigDecimal.valueOf(299.99));
        
        scenario.stimulate(() -> orderService.completeOrder(order))
            .andWaitForEventOfType(OrderCompletedEvent.class)
            .toArriveAndVerify(event -> {
                assertThat(event.getOrderId()).isEqualTo(order.getId());
                assertThat(event.getCustomerId()).isEqualTo("customer-123");
            });
    }

    @Test
    void shouldTriggerInventoryUpdateOnOrderCreation(Scenario scenario) {
        CreateOrderCommand command = new CreateOrderCommand("SKU-001", 5);
        
        scenario.stimulate(() -> orderService.createOrder(command))
            .andWaitForStateChange(() -> inventoryService.getStock("SKU-001"))
            .andVerify(stock -> assertThat(stock).isEqualTo(95));
    }

    @Test
    void shouldHandleEventWithTimeout(Scenario scenario) {
        scenario.stimulate(() -> orderService.processRefund(orderId))
            .andWaitAtMost(Duration.ofSeconds(5))
            .andWaitForEventOfType(RefundProcessedEvent.class)
            .toArriveAndVerify(event -> 
                assertThat(event.getStatus()).isEqualTo(RefundStatus.COMPLETED));
    }
}
```

**@ApplicationModuleTest (Kotlin):**

```kotlin
@ApplicationModuleTest
class OrderModuleIntegrationTest(@Autowired val orderService: OrderService) {

    @Test
    fun `should publish order completed event`(scenario: Scenario) {
        val order = Order("customer-123", BigDecimal("299.99"))
        
        scenario.stimulate { orderService.completeOrder(order) }
            .andWaitForEventOfType(OrderCompletedEvent::class.java)
            .toArriveAndVerify { event ->
                assertThat(event.orderId).isEqualTo(order.id)
                assertThat(event.customerId).isEqualTo("customer-123")
            }
    }
}
```

### Integration test with WebTestClient

`WebTestClient` works with both WebFlux and servlet-based MVC applications when `@AutoConfigureWebTestClient` is applied.

**WebTestClient integration test (Java):**

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
class ApiIntegrationTest {

    @Autowired
    private WebTestClient webClient;

    @Test
    void shouldStreamServerSentEvents() {
        webClient.get()
            .uri("/api/events/stream")
            .accept(MediaType.TEXT_EVENT_STREAM)
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(ServerEvent.class)
            .hasSize(5)
            .consumeWith(result -> {
                List<ServerEvent> events = result.getResponseBody();
                assertThat(events).extracting(ServerEvent::type)
                    .containsExactly("STARTED", "PROGRESS", "PROGRESS", "PROGRESS", "COMPLETED");
            });
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldRequireAdminRoleForManagementEndpoint() {
        webClient.delete()
            .uri("/api/admin/cache")
            .exchange()
            .expectStatus().isNoContent();
    }
}
```

---

## Cross-cutting concerns for Spring Boot 4 migration

### Jakarta EE 11 namespace migration

All `javax.*` imports must change to `jakarta.*`. This affects servlet filters, persistence annotations, validation constraints, and security classes.

```java
// Before (Boot 3.x with Jakarta EE 10)
import jakarta.servlet.http.HttpServletRequest;
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotNull;

// Same in Boot 4.x, but ensure all dependencies use Jakarta EE 11
```

### Virtual threads compatibility

Spring Boot 4 supports virtual threads (Project Loom) across all stacks. Security context and trace context propagate automatically to virtual threads.

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

**Virtual threads work seamlessly with:**
- Spring Security's `SecurityContextHolder`
- Micrometer's `ObservationRegistry`
- OpenTelemetry trace propagation
- Testcontainers (no special configuration needed)

### JSpecify null-safety annotations

Spring Boot 4 integrates JSpecify for null-safety. Use `@Nullable` and `@NonNull` from `org.jspecify.annotations`.

```java
import org.jspecify.annotations.Nullable;
import org.jspecify.annotations.NonNull;

@Service
public class UserService {
    
    public @Nullable User findByEmail(@NonNull String email) {
        return userRepository.findByEmail(email).orElse(null);
    }
}
```

### Common anti-patterns to avoid

| Anti-Pattern | Correct Approach |
|-------------|------------------|
| Using `@MockBean` in Boot 4.x | Use `@MockitoBean` |
| Creating `RestTemplate` with `new` | Use `RestTemplateBuilder` (preserves tracing) |
| Including DB checks in liveness probe | Only in readiness probe |
| 100% trace sampling in production | Use 10% sampling |
| `http.csrf().disable()` without JWT | Use `csrf().spa()` for SPAs |
| High-cardinality metric tags | Use low-cardinality tags only |
| `@SpringBootTest` for unit tests | Use appropriate slice test |

### Migration checklist

- [ ] Update to Spring Boot 4.0.0 and Spring Framework 7.0
- [ ] Replace all `@MockBean` with `@MockitoBean`
- [ ] Add `@AutoConfigureMockMvc` explicitly to `@SpringBootTest` tests
- [ ] Convert Security config to Lambda DSL (remove all `and()` calls)
- [ ] Replace `authorizeRequests()` with `authorizeHttpRequests()`
- [ ] Replace `antMatchers()` with `requestMatchers()`
- [ ] Replace `@EnableGlobalMethodSecurity` with `@EnableMethodSecurity`
- [ ] Migrate `@DynamicPropertySource` to `@ServiceConnection`
- [ ] Update Jackson 2 modules to Jackson 3 `JsonMapper.builder()`
- [ ] Configure OpenTelemetry with `spring-boot-starter-opentelemetry`
- [ ] Update health indicator imports to `org.springframework.boot.health.contributor`
- [ ] Verify all `javax.*` imports changed to `jakarta.*`

---

## Conclusion

Spring Boot 4 represents a significant evolution requiring careful migration planning. The **mandatory Lambda DSL** in Spring Security 7 improves configuration readability while enforcing modern patterns. The `@MockitoBean` annotation brings testing closer to Spring Framework conventions, and `@ServiceConnection` dramatically simplifies Testcontainers integration.

For observability, the elevation of **OpenTelemetry as the default tracer** alongside Micrometer's metrics abstraction provides a vendor-neutral observability stack. Production deployments should use the new **endpoint access model** with separate management ports and appropriate sampling rates.

Key technical decisions include using `Argon2PasswordEncoder.defaultsForSpring7()` for password hashing, implementing health groups that separate liveness from readiness concerns, and leveraging `MockMvcTester` for AssertJ-style test assertions. The Scenario API in Spring Modulith provides essential tooling for testing event-driven architectures that are increasingly common in microservices.