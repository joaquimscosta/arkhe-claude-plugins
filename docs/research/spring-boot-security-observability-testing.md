---
title: "Spring Boot 4: Security, Observability, and Testing"
version: "1.0.0"
status: Published
created: 2025-12-20
last_updated: 2026-03-26
---

# Spring Boot 4 implementation skills: Security, Observability, and Testing

## Executive Summary

This document provides implementation-ready guidance for Spring Boot 4's security, observability, and testing stacks, covering Spring Security 7's mandatory Lambda DSL migration, built-in Multi-Factor Authentication and Passkeys/WebAuthn support, OpenTelemetry as the default tracing solution, and the replacement of `@MockBean` with `@MockitoBean`. Key recommendations include adopting `Argon2PasswordEncoder.defaultsForSpring7()` for password hashing, using `spring-boot-starter-opentelemetry` for vendor-neutral observability independent of Actuator, and leveraging `@ServiceConnection` for Testcontainers integration. The report also covers critical CVE fixes in Spring Boot 4.0.4, the consolidation of Spring Authorization Server and Kerberos into Spring Security 7, and Spring Modulith's Scenario API improvements for event-driven testing. This is essential reading for backend engineers and architects migrating to or building new applications on Spring Boot 4.

**Spring Boot 4.0** (now at 4.0.4, March 2026) introduces significant breaking changes alongside powerful new capabilities across its security, observability, and testing stacks. The **Lambda DSL is now mandatory** for Spring Security 7 (now at 7.0.4), `@MockitoBean` replaces the deprecated `@MockBean`, and OpenTelemetry becomes the default tracing solution. Spring Security 7 also adds first-class **Multi-Factor Authentication**, **Passkeys/WebAuthn** support, and consolidates **Spring Authorization Server** and **Kerberos** into the core project. This report provides implementation-ready guidance with Java and Kotlin code examples for building production-grade applications.

## Spring Security 7 fundamentals and breaking changes

Spring Security 7.0 removes several deprecated APIs and makes the Lambda DSL the **only supported configuration style**. The most critical migrations involve replacing `authorizeRequests()` with `authorizeHttpRequests()`, `antMatchers()` with `requestMatchers()`, and all uses of the `and()` chaining method with Lambda closures.

| Removed API | Replacement | Migration Urgency |
|------------|-------------|-------------------|
| `and()` method | Lambda DSL closures | **Required** |
| `authorizeRequests()` | `authorizeHttpRequests()` | **Required** |
| `antMatchers()` | `requestMatchers()` | **Required** |
| `WebSecurityConfigurerAdapter` | `SecurityFilterChain` bean | **Required** |
| `AccessDecisionManager` | `AuthorizationManager` | **Required** |
| `AuthorizationManager#check` | `AuthorizationManager#authorize` | **Required** |
| Jackson 2 modules | Jackson 3 `JsonMapper.builder()` | **Required** |
| Separate Spring Authorization Server | Merged into Spring Security 7 | **Required** |
| External Spring Security Kerberos | Merged into Spring Security 7 core | **Required** |

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

### Multi-Factor Authentication (MFA) [Updated 2026-03]

Spring Security 7 introduces built-in Multi-Factor Authentication, one of its most requested features (originally proposed in 2013). MFA is enabled via `@EnableMultiFactorAuthentication` and uses the new `FactorGrantedAuthority` concept to track which authentication factors a user has completed.

**Key concepts:**
- **FactorGrantedAuthority**: Determines whether a user has authenticated through every required factor. Until all factors are satisfied, the user is not considered fully authenticated.
- **Supported factors**: Password, WebAuthn/Passkeys, TOTP, and custom factors.
- **Automatic enforcement**: Spring Security handles factor-step redirection and session management.

**MFA configuration (Java):**

```java
@Configuration
@EnableWebSecurity
@EnableMultiFactorAuthentication
public class MfaSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login/**", "/mfa/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
            )
            .multiFactor(mfa -> mfa
                .factors(FactorType.PASSWORD, FactorType.TOTP)
            );
        return http.build();
    }
}
```

**MFA with declarative properties:**

```yaml
# Simplified configuration approach (e.g., with framework wrappers)
user:
  mfa:
    enabled: true
    factors: PASSWORD, WEBAUTHN
```

### Passkeys/WebAuthn support [Updated 2026-03]

Spring Security 7 provides production-ready Passkeys/WebAuthn support based on the FIDO2/WebAuthn standard. This enables passwordless authentication using biometric keys (fingerprint, Face ID) or hardware security keys.

**Key features:**
- Public/private key pair authentication (no shared secrets)
- Synced passkeys across devices
- Built-in registration and authentication endpoints
- Jackson 3 support with mixins for `WebAuthnAuthentication` (fixed in 7.0.4)

### Module consolidation [Updated 2026-03]

Spring Security 7 consolidates two previously separate projects:
- **Spring Authorization Server** is now part of Spring Security under the OAuth 2.0 Authorization Server module. Dependencies change from `spring-security-oauth2-authorization-server` (separate project) to being included in the Spring Security BOM.
- **Spring Security Kerberos Extension** is now a core module of Spring Security, providing SPNEGO/Kerberos authentication without a separate dependency.

This consolidation provides a streamlined developer experience: OAuth2 Client, Resource Server, and Authorization Server are all in one project with unified source, javadoc, and reference documentation.

### JWT validation updates [Updated 2026-03]

Spring Security 7 introduces `JwtTypeValidator` for `typ` header validation in `NimbusJwtDecoder`, replacing reliance on Nimbus for type validation. If you are customizing Nimbus's default type validation via `jwtProcessorCustomizer`, migrate that logic to `JwtTypeValidator` or a custom `OAuth2TokenValidator`.

```java
@Bean
JwtDecoder jwtDecoder() {
    NimbusJwtDecoder jwtDecoder = NimbusJwtDecoder
        .withIssuerLocation(issuerLocation)
        .validateTypes(false) // Disable Nimbus type validation
        .build();
    // Add JwtTypeValidator to your validator chain instead
    jwtDecoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
        JwtTypeValidator.jwt(), // New in Security 7
        new JwtTimestampValidator(),
        new JwtIssuerValidator(issuerLocation)
    ));
    return jwtDecoder;
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

## Observability with Actuator, Micrometer, and OpenTelemetry [Updated 2026-03]

Spring Boot 4 elevates OpenTelemetry to the **default tracing implementation**, with `spring-boot-starter-opentelemetry` providing integrated support for OTLP export **without requiring Spring Boot Actuator**. This is a significant architectural change: observability and operational endpoints are now independently addressable. Micrometer (1.16.x in Boot 4.0.4) remains the metrics abstraction, while Actuator exposes operational endpoints with granular security controls. Spring Boot 4.0.4 includes Micrometer 1.16.4.

### Actuator endpoint configuration for production

Production deployments require careful endpoint exposure. Spring Boot 4 introduces a new access control model with `none`, `read-only`, and `unrestricted` options per endpoint.

**Security advisory (March 2026):** Spring Boot 4.0.4 fixes CVE-2026-22731 (Authentication Bypass under Actuator Health groups paths) and CVE-2026-22733 (Authentication Bypass under Actuator CloudFoundry endpoints). All production deployments should upgrade to 4.0.4 or later.

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

### Spring Boot 4.1 OpenTelemetry enhancements (preview) [Updated 2026-03]

Spring Boot 4.1.0-M3 (March 2026) introduces significant OpenTelemetry improvements:

- **SslBundles support** for OTLP traces, metrics, and logging export (mutual TLS)
- **Fine-grained metric exemplar selection** and auto-configuration for OTLP exemplars
- **Configurable OpenTelemetry sampler** via properties (no custom beans required)
- **SDK disable toggle**: A property to completely disable the OpenTelemetry SDK
- **BatchLogRecordProcessor configuration** via properties
- **Deprecation notice**: OpenTelemetry's `ZipkinSpanExporter` is deprecated and will be removed in Spring Boot 4.2. Migrate to native OTLP export.

### Micrometer vs OpenTelemetry: choosing the right approach [Updated 2026-03]

A common question in the Spring Boot 4 ecosystem is whether to use Micrometer or OpenTelemetry. The answer is that they are **complementary**, not competing:

| Aspect | Micrometer | OpenTelemetry |
|--------|-----------|---------------|
| **Role** | Metrics facade + Observation API | Export protocol + full telemetry stack |
| **In Spring Boot 4** | Built-in, always available | Via `spring-boot-starter-opentelemetry` |
| **Best for** | Application-level metrics, SLOs | Distributed tracing, vendor-neutral export |
| **Approach** | Instrument with `ObservationRegistry` | Data exported via OTLP protocol |

**Recommended pattern**: Use the Micrometer Observation API as your instrumentation facade in code (`Observation.createNotStarted()`), and configure OpenTelemetry as the export backend for traces and metrics. This gives you vendor neutrality with a clean programming model.

---

## Testing strategies with slice tests and Testcontainers [Updated 2026-03]

Spring Boot 4 introduces **modular test starters** and replaces `@MockBean` with Spring Framework's `@MockitoBean`. The `@ServiceConnection` annotation for Testcontainers eliminates boilerplate dynamic property configuration. JUnit 4 support has been fully retired, and `RestTestClient` provides a unified HTTP testing client.

### Critical breaking change: @MockitoBean replaces @MockBean

The migration from `@MockBean` to `@MockitoBean` is **mandatory** in Spring Boot 4. The annotation now lives in Spring Framework (not Spring Boot): `org.springframework.test.context.bean.override.mockito.MockitoBean`. Key differences include the `REPLACE_OR_CREATE` strategy, prohibition on usage within `@Configuration` classes, and support for `@Nested` test classes via type-level or enclosing class annotations.

**Annotation placement options** (expanded in Spring Framework 7):
- On a non-static field in a test class or superclass
- On a non-static field in an enclosing class for `@Nested` test classes
- At the type level on a test class, superclass, or implemented interface
- At the type level on an enclosing class for `@Nested` test classes

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

### RestTestClient: unified HTTP testing [Updated 2026-03]

Spring Boot 4 introduces `RestTestClient` as a unified HTTP testing client that works with both WebFlux and servlet-based MVC applications. This replaces the previous pattern of choosing between `MockMvc` (servlet) and `WebTestClient` (reactive).

**RestTestClient advantages:**
- Works identically regardless of the underlying web stack
- Supports both full server and mock server testing modes
- Designed to test `@HttpExchange` interfaces directly
- Integrates with security test annotations like `@WithMockUser`

### Modular test dependencies [Updated 2026-03]

Reflecting the broader modularization of Spring Boot 4, test auto-configuration is organized into focused modules:

| Old (Boot 3.x) | New (Boot 4.x) |
|----------------|-----------------|
| `spring-boot-test-autoconfigure` (single jar) | `spring-boot-webmvc-test-autoconfigure` |
| | `spring-boot-data-jpa-test-autoconfigure` |
| | `spring-boot-json-test-autoconfigure` |
| | (and other technology-specific test modules) |

For applications using Starter POMs (e.g., `spring-boot-starter-test`), this change is transparent. Direct references to auto-configuration classes may require updated imports.

### Spring Modulith Scenario API updates [Updated 2026-03]

Spring Modulith 2.0.4 and the 2.1 milestone bring important testing improvements:

- **Application-wide event visibility**: `PublishedEvents` and `Scenario` now see events from all threads by default (previously thread-bound). This fixes a common issue where events published on virtual threads or async executors were invisible to tests.
- **Slice test combination**: `@ApplicationModuleTest` can now be combined with Spring Boot's slice test annotations (`@WebMvcTest`, `@DataJpaTest`, etc.), enabling more focused module tests.
- **JDBC schema auto-creation**: The event publication schema for JDBC is now created by default, removing setup boilerplate.

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
| Using `@MockBean` in Boot 4.x | Use `@MockitoBean` from Spring Framework |
| Creating `RestTemplate` with `new` | Use `RestTemplateBuilder` (preserves tracing) |
| Including DB checks in liveness probe | Only in readiness probe |
| 100% trace sampling in production | Use 10% sampling |
| `http.csrf().disable()` without JWT | Use `csrf().spa()` for SPAs |
| High-cardinality metric tags | Use low-cardinality tags only |
| `@SpringBootTest` for unit tests | Use appropriate slice test |
| Custom MFA filter chains | Use built-in `@EnableMultiFactorAuthentication` |
| Using `spring-retry` externally | Use built-in `org.springframework.resilience` |
| Copying pre-2025 retry tutorials | Use new `@Retryable` from `resilience.annotation` package |
| Using `ZipkinSpanExporter` | Migrate to native OTLP export (deprecated in 4.1) |
| Separate Authorization Server dependency | Use merged Spring Security 7 module |

### Migration checklist [Updated 2026-03]

- [ ] Update to Spring Boot 4.0.4+ and Spring Framework 7.0.6+ (includes critical CVE fixes)
- [ ] Replace all `@MockBean` with `@MockitoBean` (import from `org.springframework.test.context.bean.override.mockito`)
- [ ] Add `@AutoConfigureMockMvc` explicitly to `@SpringBootTest` tests
- [ ] Convert Security config to Lambda DSL (remove all `and()` calls)
- [ ] Replace `authorizeRequests()` with `authorizeHttpRequests()`
- [ ] Replace `antMatchers()` with `requestMatchers()`
- [ ] Replace `@EnableGlobalMethodSecurity` with `@EnableMethodSecurity`
- [ ] Replace `AuthorizationManager#check` with `AuthorizationManager#authorize`
- [ ] Migrate `@DynamicPropertySource` to `@ServiceConnection`
- [ ] Update Jackson 2 modules to Jackson 3 `JsonMapper.builder()` (note: null handling for primitives changed)
- [ ] Configure OpenTelemetry with `spring-boot-starter-opentelemetry`
- [ ] Update health indicator imports to `org.springframework.boot.health.contributor`
- [ ] Verify all `javax.*` imports changed to `jakarta.*`
- [ ] If using Spring Authorization Server: update to merged Spring Security 7 coordinates
- [ ] If using Kerberos: update to Spring Security 7 built-in Kerberos module
- [ ] If using `spring-retry`: migrate to `org.springframework.resilience` built-in retry
- [ ] Review auto-configuration imports for modularized dependencies
- [ ] If using `ZipkinSpanExporter`: plan migration to native OTLP (removal in Boot 4.2)
- [ ] If implementing MFA: evaluate built-in `@EnableMultiFactorAuthentication` over custom filters

---

## Conclusion [Updated 2026-03]

Spring Boot 4, now at 4.0.4 (March 2026) with Spring Security 7.0.4 and Spring Framework 7.0.6, represents a significant evolution requiring careful migration planning. The **mandatory Lambda DSL** in Spring Security 7 improves configuration readability while enforcing modern patterns. The addition of **built-in MFA** via `@EnableMultiFactorAuthentication` and **Passkeys/WebAuthn** support brings enterprise-grade authentication capabilities out of the box. The consolidation of **Spring Authorization Server** and **Kerberos** into Spring Security 7 simplifies the dependency landscape for OAuth2 scenarios.

The `@MockitoBean` annotation (now in Spring Framework, not Boot) brings testing closer to framework conventions, `@ServiceConnection` dramatically simplifies Testcontainers integration, and `RestTestClient` unifies HTTP testing across web stacks. Spring Modulith's `Scenario` API now captures events across all threads, fixing a common pain point with virtual thread testing.

For observability, the elevation of **OpenTelemetry as the default tracer** — now available independently of Actuator via `spring-boot-starter-opentelemetry` — alongside Micrometer's metrics abstraction provides a vendor-neutral observability stack. Production deployments should use the new **endpoint access model** with separate management ports and appropriate sampling rates. The upcoming 4.1 release enhances OpenTelemetry with SslBundles support and fine-grained sampler configuration.

Key technical decisions include using `Argon2PasswordEncoder.defaultsForSpring7()` for password hashing, implementing health groups that separate liveness from readiness concerns, leveraging `MockMvcTester` for AssertJ-style test assertions, and adopting the built-in `org.springframework.resilience` retry/throttling over external libraries. All production deployments should update to 4.0.4+ to address the Actuator authentication bypass CVEs.

---

## References

- **Spring Boot 4.0** — Application framework with auto-configuration, modular test starters, and production-ready features. Latest: 4.0.4 (March 2026). https://spring.io/projects/spring-boot
- **Spring Security 7** — Security framework with mandatory Lambda DSL, built-in MFA via `@EnableMultiFactorAuthentication`, Passkeys/WebAuthn support, and consolidated Authorization Server and Kerberos modules. Latest: 7.0.4. https://spring.io/projects/spring-security
- **Spring Framework 7** — Core framework providing `@MockitoBean` (replacing `@MockBean`), built-in resilience API (`org.springframework.resilience`), and JSpecify null safety. Latest: 7.0.6. https://spring.io/projects/spring-framework
- **Micrometer** — Metrics facade providing Observation API, Timer, Counter, Gauge, and DistributionSummary meter types for application-level instrumentation. Latest: 1.16.4 (in Boot 4.0.4). https://micrometer.io/
- **OpenTelemetry** — Vendor-neutral observability standard for distributed tracing, metrics, and log export via OTLP protocol. Default tracer in Spring Boot 4 via `spring-boot-starter-opentelemetry`. https://opentelemetry.io/
- **Testcontainers** — Library for ephemeral Docker containers in integration tests, integrated with Spring Boot via `@ServiceConnection` for automatic property injection. https://testcontainers.com/
- **Spring Modulith 2.0 / 2.1** — Modular monolith toolkit with `@ApplicationModuleTest`, Scenario API for event-driven testing, and application-wide event visibility (no longer thread-bound). https://spring.io/projects/spring-modulith
- **Jakarta EE 11** — Enterprise Java specifications including Servlet 6.1, JPA 3.2, and Bean Validation 3.1 required by Spring Boot 4. https://jakarta.ee/
- **Jackson 3** — JSON processing library with relocated `tools.jackson` package namespace. Security-related serialization modules require migration from Jackson 2. https://github.com/FasterXML/jackson
- **JSpecify** — Standardized null-safety annotations (`@Nullable`, `@NonNull`) adopted portfolio-wide by Spring Framework 7 and Spring Boot 4. https://jspecify.dev/
- **NimbusJwtDecoder** — JWT decoder used by Spring Security 7 for token validation, with new `JwtTypeValidator` for `typ` header validation. Part of the Nimbus JOSE+JWT library. https://connect2id.com/products/nimbus-jose-jwt
- **FIDO2/WebAuthn** — W3C standard for passwordless authentication using public key cryptography, supported natively in Spring Security 7. https://fidoalliance.org/fido2/
- **Argon2** — Password hashing algorithm used by `Argon2PasswordEncoder.defaultsForSpring7()` as the recommended encoder in Spring Security 7. https://github.com/P-H-C/phc-winner-argon2
- **CVE-2026-22731 / CVE-2026-22733** — Actuator authentication bypass vulnerabilities fixed in Spring Boot 4.0.4. https://spring.io/security