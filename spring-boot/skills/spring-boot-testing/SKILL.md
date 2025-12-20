---
name: spring-boot-testing
description: Spring Boot 4 testing strategies and patterns. Use when writing unit tests, slice tests (@WebMvcTest, @DataJpaTest), integration tests, Testcontainers with @ServiceConnection, security testing (@WithMockUser, JWT), or Modulith event testing with Scenario API. Covers the critical @MockitoBean migration from @MockBean.
---

# Spring Boot 4 Testing

Comprehensive testing patterns including slice tests, Testcontainers, security testing, and Modulith Scenario API.

## Critical Breaking Change

| Old (Boot 3.x) | New (Boot 4.x) | Notes |
|----------------|----------------|-------|
| `@MockBean` | `@MockitoBean` | **Required migration** |
| `@SpyBean` | `@MockitoSpyBean` | **Required migration** |
| Implicit `@AutoConfigureMockMvc` | Explicit annotation required | Add to `@SpringBootTest` |

## Test Annotation Selection

| Test Type | Annotation | Use When |
|-----------|------------|----------|
| Controller | `@WebMvcTest` | Testing request/response, validation |
| Repository | `@DataJpaTest` | Testing queries, entity mapping |
| JSON | `@JsonTest` | Testing serialization/deserialization |
| REST Client | `@RestClientTest` | Testing external API clients |
| Full Integration | `@SpringBootTest` | End-to-end, with real dependencies |
| Module | `@ApplicationModuleTest` | Testing bounded context in isolation |

## Core Workflow

1. **Choose test slice** → Minimal context for fast tests
2. **Mock dependencies** → `@MockitoBean` for external services
3. **Use Testcontainers** → `@ServiceConnection` for databases
4. **Assert thoroughly** → Use AssertJ, MockMvcTester, WebTestClient
5. **Test security** → `@WithMockUser`, JWT mocking

## Quick Implementation Patterns

### @WebMvcTest with @MockitoBean

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    
    @Autowired
    private MockMvcTester mvc;  // New in Boot 4
    
    @MockitoBean  // Replaces @MockBean
    private OrderService orderService;
    
    @Test
    void shouldReturnOrder() {
        given(orderService.findById(1L))
            .willReturn(Optional.of(new Order(1L, "SUBMITTED")));
        
        assertThat(mvc.get().uri("/api/orders/1"))
            .hasStatusOk()
            .hasContentType(MediaType.APPLICATION_JSON)
            .bodyJson()
            .extractingPath("$.status").isEqualTo("SUBMITTED");
    }
    
    @Test
    void shouldReturn404WhenNotFound() {
        given(orderService.findById(999L)).willReturn(Optional.empty());
        
        assertThat(mvc.get().uri("/api/orders/999"))
            .hasStatus(HttpStatus.NOT_FOUND);
    }
}
```

```kotlin
@WebMvcTest(OrderController::class)
class OrderControllerTest(@Autowired val mvc: MockMvcTester) {
    
    @MockitoBean
    lateinit var orderService: OrderService
    
    @Test
    fun `should return order`() {
        given(orderService.findById(1L))
            .willReturn(Optional.of(Order(1L, "SUBMITTED")))
        
        assertThat(mvc.get().uri("/api/orders/1"))
            .hasStatusOk()
            .bodyJson()
            .extractingPath("$.status").isEqualTo("SUBMITTED")
    }
}
```

### @DataJpaTest with TestEntityManager

```java
@DataJpaTest
class OrderRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Test
    void shouldFindOrdersWithItems() {
        Order order = new Order(LocalDateTime.now());
        order.addItem(new OrderItem("Widget", 2));
        
        entityManager.persistAndFlush(order);
        entityManager.clear();  // Force re-fetch
        
        Order found = orderRepository.findById(order.getId()).orElseThrow();
        assertThat(found.getItems()).hasSize(1);
    }
}
```

### Testcontainers with @ServiceConnection

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
    
    @Container
    @ServiceConnection
    static RedisContainer redis = new RedisContainer("redis:7");
    
    @Autowired
    private WebTestClient webClient;
    
    @Test
    void shouldCreateOrder() {
        webClient.post()
            .uri("/api/orders")
            .bodyValue(new CreateOrderRequest("Widget", 5))
            .exchange()
            .expectStatus().isCreated()
            .expectBody()
            .jsonPath("$.id").isNotEmpty();
    }
}
```

### Security Testing

```java
@WebMvcTest(AdminController.class)
class AdminControllerSecurityTest {
    
    @Autowired
    private MockMvcTester mvc;
    
    @Test
    void shouldRejectUnauthenticated() {
        assertThat(mvc.get().uri("/api/admin/users"))
            .hasStatus(HttpStatus.UNAUTHORIZED);
    }
    
    @Test
    @WithMockUser(roles = "USER")
    void shouldRejectNonAdmin() {
        assertThat(mvc.get().uri("/api/admin/users"))
            .hasStatus(HttpStatus.FORBIDDEN);
    }
    
    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdmin() {
        assertThat(mvc.get().uri("/api/admin/users"))
            .hasStatusOk();
    }
}
```

### Modulith Event Testing

```java
@ApplicationModuleTest
class OrderModuleTest {
    
    @Autowired
    private OrderService orderService;
    
    @Test
    void shouldPublishOrderCreatedEvent(Scenario scenario) {
        scenario.stimulate(() -> orderService.createOrder(request))
            .andWaitForEventOfType(OrderCreated.class)
            .toArriveAndVerify(event -> {
                assertThat(event.orderId()).isNotNull();
                assertThat(event.customerId()).isEqualTo("customer-123");
            });
    }
}
```

## Detailed References

- **Slice Tests**: See [references/slice-tests.md](references/slice-tests.md) for @WebMvcTest, @DataJpaTest, @JsonTest patterns
- **Testcontainers**: See [references/testcontainers.md](references/testcontainers.md) for @ServiceConnection, container reuse
- **Security Testing**: See [references/security-testing.md](references/security-testing.md) for @WithMockUser, JWT mocking
- **Modulith Testing**: See [references/modulith-testing.md](references/modulith-testing.md) for Scenario API, event verification

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| Using `@MockBean` in Boot 4 | Replace with `@MockitoBean` |
| `@SpringBootTest` for unit tests | Use appropriate slice annotation |
| Missing `entityManager.clear()` | Add to verify lazy loading |
| High-cardinality test data | Use minimal, focused fixtures |
| Shared mutable test state | Use `@DirtiesContext` or fresh containers |
| No security tests | Add `@WithMockUser` tests for endpoints |

## Critical Reminders

1. **@MockitoBean is mandatory** — `@MockBean` removed in Boot 4
2. **Slice tests are fast** — Use them for focused testing
3. **Clear EntityManager** — Required to test lazy loading behavior
4. **@ServiceConnection simplifies Testcontainers** — No more `@DynamicPropertySource`
5. **Test security explicitly** — Don't rely on disabled security
