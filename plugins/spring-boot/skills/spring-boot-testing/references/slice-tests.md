# Slice Tests

Focused testing with minimal application context.

## @WebMvcTest

Tests Spring MVC controllers without starting full server.

### Java

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {
    
    @Autowired
    private MockMvcTester mvc;  // New AssertJ-style API in Boot 4
    
    @MockitoBean
    private ProductService productService;
    
    @MockitoBean
    private ProductMapper productMapper;
    
    @Test
    void shouldReturnProductById() {
        Product product = new Product(1L, "Laptop", BigDecimal.valueOf(999.99));
        given(productService.findById(1L)).willReturn(Optional.of(product));
        given(productMapper.toDto(product)).willReturn(new ProductDto(1L, "Laptop", "999.99"));
        
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
    
    @Test
    void shouldValidateCreateRequest() {
        String invalidRequest = """
            {"name": "", "price": -10}
            """;
        
        assertThat(mvc.post().uri("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidRequest))
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .extractingPath("$.errors").isNotEmpty();
    }
    
    @Test
    void shouldCreateProduct() {
        String request = """
            {"name": "Tablet", "price": 499.99}
            """;
        Product saved = new Product(2L, "Tablet", BigDecimal.valueOf(499.99));
        
        given(productService.create(any())).willReturn(saved);
        given(productMapper.toDto(saved)).willReturn(new ProductDto(2L, "Tablet", "499.99"));
        
        assertThat(mvc.post().uri("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(request))
            .hasStatus(HttpStatus.CREATED)
            .hasHeader("Location", "/api/products/2")
            .bodyJson()
            .extractingPath("$.id").isEqualTo(2);
    }
}
```

### Kotlin

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
    
    @Test
    fun `should validate create request`() {
        val invalidRequest = """{"name": "", "price": -10}"""
        
        assertThat(mvc.post().uri("/api/products")
            .contentType(MediaType.APPLICATION_JSON)
            .content(invalidRequest))
            .hasStatus(HttpStatus.BAD_REQUEST)
    }
}
```

### Classic MockMvc (still supported)

```java
@WebMvcTest(ProductController.class)
@AutoConfigureMockMvc
class ProductControllerClassicTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockitoBean
    private ProductService productService;
    
    @Test
    void shouldReturnProduct() throws Exception {
        given(productService.findById(1L))
            .willReturn(Optional.of(new Product(1L, "Laptop")));
        
        mockMvc.perform(get("/api/products/1"))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.name").value("Laptop"));
    }
}
```

## @DataJpaTest

Tests JPA repositories with embedded database.

### Java

```java
@DataJpaTest
class OrderRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Test
    void shouldSaveOrderWithItems() {
        Order order = new Order(CustomerId.generate(), LocalDateTime.now());
        order.addItem(new OrderItem("Widget", 2, BigDecimal.TEN));
        order.addItem(new OrderItem("Gadget", 1, BigDecimal.valueOf(25)));
        
        Order saved = orderRepository.save(order);
        entityManager.flush();
        entityManager.clear();  // Critical: forces re-fetch from DB
        
        Order found = orderRepository.findById(saved.getId()).orElseThrow();
        assertThat(found.getItems()).hasSize(2);
        assertThat(found.getTotal()).isEqualByComparingTo(BigDecimal.valueOf(45));
    }
    
    @Test
    void shouldFindByCustomerId() {
        CustomerId customerId = CustomerId.generate();
        Order order1 = entityManager.persist(new Order(customerId, LocalDateTime.now()));
        Order order2 = entityManager.persist(new Order(customerId, LocalDateTime.now()));
        entityManager.persist(new Order(CustomerId.generate(), LocalDateTime.now())); // Different customer
        entityManager.flush();
        
        List<Order> orders = orderRepository.findByCustomerId(customerId);
        
        assertThat(orders).hasSize(2)
            .extracting(Order::getId)
            .containsExactlyInAnyOrder(order1.getId(), order2.getId());
    }
    
    @Test
    void shouldCascadeDeleteItems() {
        Order order = entityManager.persistAndFlush(new Order(CustomerId.generate()));
        order.addItem(new OrderItem("Widget", 1, BigDecimal.TEN));
        entityManager.persistAndFlush(order);
        Long orderId = order.getId();
        
        orderRepository.deleteById(orderId);
        entityManager.flush();
        entityManager.clear();
        
        assertThat(orderRepository.findById(orderId)).isEmpty();
        // Items also deleted via cascade
    }
    
    @Test
    void shouldUseEntityGraph() {
        Order order = new Order(CustomerId.generate());
        order.addItem(new OrderItem("Widget", 2, BigDecimal.TEN));
        entityManager.persistAndFlush(order);
        entityManager.clear();
        
        // This should NOT cause N+1
        Order found = orderRepository.findWithItemsById(order.getId()).orElseThrow();
        
        // Items already loaded (no lazy fetch)
        assertThat(Hibernate.isInitialized(found.getItems())).isTrue();
    }
}
```

### Kotlin

```kotlin
@DataJpaTest
class OrderRepositoryTest(
    @Autowired val entityManager: TestEntityManager,
    @Autowired val orderRepository: OrderRepository
) {
    @Test
    fun `should save order with items`() {
        val order = Order(CustomerId.generate()).apply {
            addItem(OrderItem("Widget", 2, BigDecimal.TEN))
        }
        
        orderRepository.save(order)
        entityManager.flush()
        entityManager.clear()
        
        val found = orderRepository.findById(order.id!!).orElseThrow()
        assertThat(found.items).hasSize(1)
    }
}
```

### Using Real Database with Testcontainers

```java
@DataJpaTest
@Testcontainers
@AutoConfigureTestDatabase(replace = Replace.NONE)
class OrderRepositoryPostgresTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Test
    void shouldWorkWithPostgres() {
        // Test with real Postgres features
    }
}
```

## @JsonTest

Tests JSON serialization/deserialization.

```java
@JsonTest
class ProductDtoJsonTest {
    
    @Autowired
    private JacksonTester<ProductDto> json;
    
    @Test
    void shouldSerialize() throws Exception {
        ProductDto dto = new ProductDto(1L, "Laptop", BigDecimal.valueOf(999.99));
        
        assertThat(json.write(dto))
            .hasJsonPathNumberValue("$.id", 1)
            .hasJsonPathStringValue("$.name", "Laptop")
            .hasJsonPathNumberValue("$.price", 999.99)
            .doesNotHaveJsonPath("$.internalCode");
    }
    
    @Test
    void shouldDeserialize() throws Exception {
        String content = """
            {"id": 1, "name": "Laptop", "price": 999.99}
            """;
        
        assertThat(json.parse(content))
            .usingRecursiveComparison()
            .isEqualTo(new ProductDto(1L, "Laptop", BigDecimal.valueOf(999.99)));
    }
    
    @Test
    void shouldHandleNullFields() throws Exception {
        ProductDto dto = new ProductDto(1L, "Laptop", null);
        
        assertThat(json.write(dto))
            .doesNotHaveJsonPath("$.price");  // Null excluded
    }
}
```

## @RestClientTest

Tests REST clients.

```java
@RestClientTest(ExternalApiClient.class)
class ExternalApiClientTest {
    
    @Autowired
    private ExternalApiClient client;
    
    @Autowired
    private MockRestServiceServer server;
    
    @Test
    void shouldFetchData() {
        server.expect(requestTo("/api/data/123"))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withSuccess("""
                {"id": "123", "value": "test"}
                """, MediaType.APPLICATION_JSON));
        
        ExternalData data = client.fetchData("123");
        
        assertThat(data.id()).isEqualTo("123");
        assertThat(data.value()).isEqualTo("test");
        server.verify();
    }
    
    @Test
    void shouldHandleError() {
        server.expect(requestTo("/api/data/999"))
            .andRespond(withStatus(HttpStatus.NOT_FOUND));
        
        assertThatThrownBy(() -> client.fetchData("999"))
            .isInstanceOf(ResourceNotFoundException.class);
    }
}
```

## @WebFluxTest

Tests reactive controllers.

```java
@WebFluxTest(ReactiveProductController.class)
class ReactiveProductControllerTest {
    
    @Autowired
    private WebTestClient webClient;
    
    @MockitoBean
    private ReactiveProductService productService;
    
    @Test
    void shouldReturnProduct() {
        given(productService.findById("1"))
            .willReturn(Mono.just(new Product("1", "Laptop")));
        
        webClient.get()
            .uri("/api/products/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$.name").isEqualTo("Laptop");
    }
    
    @Test
    void shouldStreamProducts() {
        given(productService.findAll())
            .willReturn(Flux.just(
                new Product("1", "Laptop"),
                new Product("2", "Tablet")
            ));
        
        webClient.get()
            .uri("/api/products")
            .accept(MediaType.TEXT_EVENT_STREAM)
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(Product.class)
            .hasSize(2);
    }
}
```

## Custom Slice Annotation

Create reusable test slice:

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE)
@Testcontainers
@Import(TestConfig.class)
public @interface PostgresRepositoryTest {
}

// Usage
@PostgresRepositoryTest
class OrderRepositoryTest {
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
    
    // Tests...
}
```

## Test Configuration

```java
@TestConfiguration
public class TestConfig {
    
    @Bean
    public Clock testClock() {
        return Clock.fixed(Instant.parse("2025-01-15T10:00:00Z"), ZoneOffset.UTC);
    }
    
    @Bean
    public TestDataFactory testDataFactory() {
        return new TestDataFactory();
    }
}

// Import in tests
@DataJpaTest
@Import(TestConfig.class)
class OrderRepositoryTest {
    @Autowired
    private TestDataFactory testData;
}
```
