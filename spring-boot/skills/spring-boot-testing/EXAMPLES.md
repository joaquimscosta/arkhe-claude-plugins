# Spring Boot Testing Examples

Complete working examples for Spring Boot 4 testing patterns.

## @WebMvcTest with @MockitoBean

Controller slice test using the new `MockMvcTester` and `@MockitoBean` (replaces deprecated `@MockBean`).

### Java

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

### Kotlin

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

**Key points:**
- `MockMvcTester` provides fluent assertions built on AssertJ
- `@MockitoBean` is mandatory in Boot 4 (replaces `@MockBean`)
- Use `bodyJson().extractingPath()` for JSON assertions

---

## @DataJpaTest with TestEntityManager

Repository slice test with entity persistence and lazy loading verification.

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
        entityManager.clear();  // Force re-fetch to verify lazy loading

        Order found = orderRepository.findById(order.getId()).orElseThrow();
        assertThat(found.getItems()).hasSize(1);
    }
}
```

**Key points:**
- Use `persistAndFlush()` to ensure entity is in database
- Call `entityManager.clear()` before assertions to verify lazy loading works
- `@DataJpaTest` auto-configures in-memory database by default

---

## Testcontainers with @ServiceConnection

Full integration test with real PostgreSQL and Redis containers.

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {

    @Container
    @ServiceConnection  // Boot 4: auto-configures datasource
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @Container
    @ServiceConnection  // Boot 4: auto-configures Redis
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

**Key points:**
- `@ServiceConnection` eliminates need for `@DynamicPropertySource`
- Static containers are shared across tests in the class
- Use `WebTestClient` for reactive-style assertions

---

## Security Testing

Test authentication and authorization with `@WithMockUser`.

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

**Key points:**
- Test unauthenticated, wrong role, and correct role scenarios
- `@WithMockUser` provides a mock `Authentication` object
- Default user has `ROLE_USER` if not specified

---

## Modulith Event Testing with Scenario API

Test event publishing and handling in Spring Modulith bounded contexts.

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

**Key points:**
- `@ApplicationModuleTest` loads only the module under test
- `Scenario` is injected as a test parameter
- Use `stimulate()` to trigger actions and `andWaitForEventOfType()` to verify events
- Events are captured asynchronously with configurable timeout
