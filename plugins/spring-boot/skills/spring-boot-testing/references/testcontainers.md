# Testcontainers Integration

@ServiceConnection, container patterns, and lifecycle management.

## @ServiceConnection (Spring Boot 4)

Automatically configures Spring Boot connection properties from containers.

### Basic Usage

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
    
    @Autowired
    private WebTestClient webClient;
    
    @Test
    void shouldCreateOrder() {
        webClient.post()
            .uri("/api/orders")
            .bodyValue(new CreateOrderRequest("Widget", 5))
            .exchange()
            .expectStatus().isCreated();
    }
}
```

No need for `@DynamicPropertySource` — `@ServiceConnection` handles:
- `spring.datasource.url`
- `spring.datasource.username`
- `spring.datasource.password`

### Kotlin

```kotlin
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest(@Autowired val webClient: WebTestClient) {
    
    companion object {
        @Container
        @ServiceConnection
        @JvmStatic
        val postgres = PostgreSQLContainer("postgres:16-alpine")
    }
    
    @Test
    fun `should create order`() {
        webClient.post()
            .uri("/api/orders")
            .bodyValue(CreateOrderRequest("Widget", 5))
            .exchange()
            .expectStatus().isCreated
    }
}
```

## Supported Containers

| Container | Auto-configured Properties |
|-----------|---------------------------|
| `PostgreSQLContainer` | datasource.url, username, password |
| `MySQLContainer` | datasource.url, username, password |
| `MongoDBContainer` | data.mongodb.uri |
| `RedisContainer` | data.redis.host, port |
| `KafkaContainer` | kafka.bootstrap-servers |
| `RabbitMQContainer` | rabbitmq.host, port, username, password |
| `ElasticsearchContainer` | elasticsearch.uris |
| `CassandraContainer` | cassandra.contact-points |

## Multiple Containers

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@Testcontainers
class FullStackIntegrationTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");
    
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
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    @Test
    void shouldProcessOrderEndToEnd() {
        // Test with all services
    }
}
```

## Container Reuse (Faster Tests)

### Singleton Pattern

```java
public abstract class AbstractIntegrationTest {
    
    static final PostgreSQLContainer<?> postgres;
    static final RedisContainer redis;
    
    static {
        postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withReuse(true);  // Reuse between test runs
        postgres.start();
        
        redis = new RedisContainer("redis:7-alpine")
            .withReuse(true);
        redis.start();
    }
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.data.redis.host", redis::getHost);
        registry.add("spring.data.redis.port", () -> redis.getMappedPort(6379));
    }
}

@SpringBootTest
class OrderIntegrationTest extends AbstractIntegrationTest {
    // Tests reuse containers
}

@SpringBootTest
class PaymentIntegrationTest extends AbstractIntegrationTest {
    // Same containers, faster startup
}
```

### Enable Reuse Globally

```properties
# ~/.testcontainers.properties
testcontainers.reuse.enable=true
```

## Database Initialization

### With Init Script

```java
@Container
@ServiceConnection
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
    .withInitScript("db/init.sql");
```

### With Flyway (Auto-detected)

```java
@SpringBootTest
@Testcontainers
class MigrationTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
    
    // Flyway migrations run automatically if spring-boot-starter-flyway is present
    
    @Test
    void shouldApplyMigrations(@Autowired Flyway flyway) {
        assertThat(flyway.info().applied().length).isGreaterThan(0);
    }
}
```

## Custom Connection Details

For containers without built-in @ServiceConnection support:

```java
@Container
static GenericContainer<?> customService = new GenericContainer<>("custom:latest")
    .withExposedPorts(8080);

@DynamicPropertySource
static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("custom.service.url", () -> 
        "http://" + customService.getHost() + ":" + customService.getMappedPort(8080));
}
```

## Docker Compose Support

```java
@SpringBootTest
@Testcontainers
class DockerComposeTest {
    
    @Container
    static DockerComposeContainer<?> environment = 
        new DockerComposeContainer<>(new File("src/test/resources/docker-compose-test.yml"))
            .withExposedService("postgres", 5432)
            .withExposedService("redis", 6379)
            .waitingFor("postgres", Wait.forHealthcheck());
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", () -> 
            "jdbc:postgresql://" + 
            environment.getServiceHost("postgres", 5432) + ":" +
            environment.getServicePort("postgres", 5432) + "/testdb");
    }
}
```

## Waiting Strategies

```java
// Wait for log message
@Container
static GenericContainer<?> container = new GenericContainer<>("custom:latest")
    .waitingFor(Wait.forLogMessage(".*Started.*\\n", 1));

// Wait for HTTP endpoint
@Container
static GenericContainer<?> container = new GenericContainer<>("custom:latest")
    .waitingFor(Wait.forHttp("/health").forStatusCode(200));

// Wait for port
@Container
static GenericContainer<?> container = new GenericContainer<>("custom:latest")
    .waitingFor(Wait.forListeningPort());

// Combined wait
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
    .waitingFor(Wait.forHealthcheck()
        .withStartupTimeout(Duration.ofMinutes(2)));
```

## Test Data Management

### Per-Test Cleanup

```java
@SpringBootTest
@Testcontainers
class OrderIntegrationTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @BeforeEach
    void cleanDatabase() {
        jdbcTemplate.execute("TRUNCATE TABLE orders CASCADE");
        jdbcTemplate.execute("TRUNCATE TABLE customers CASCADE");
    }
    
    @Test
    void test1() {
        // Fresh database
    }
    
    @Test
    void test2() {
        // Fresh database
    }
}
```

### Transaction Rollback

```java
@SpringBootTest
@Transactional  // Rollback after each test
class OrderServiceTest {
    
    @Autowired
    private OrderService orderService;
    
    @Test
    void shouldCreateOrder() {
        Order order = orderService.create(request);
        assertThat(order.getId()).isNotNull();
        // Rolled back after test
    }
}
```

## Network Configuration

```java
// Containers on same network
static Network network = Network.newNetwork();

@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
    .withNetwork(network)
    .withNetworkAliases("postgres");

@Container
static GenericContainer<?> app = new GenericContainer<>("myapp:latest")
    .withNetwork(network)
    .withEnv("DATABASE_URL", "jdbc:postgresql://postgres:5432/testdb")
    .dependsOn(postgres);
```

## Resource Cleanup

```java
@SpringBootTest
@Testcontainers
class CleanupTest {
    
    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
    
    @AfterAll
    static void cleanup() {
        // Containers stop automatically with @Container
        // But for manual cleanup:
        if (postgres.isRunning()) {
            postgres.stop();
        }
    }
}
```

## CI/CD Configuration

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      # No services needed - Testcontainers handles it
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
      - name: Run tests
        run: ./mvnw test
        env:
          TESTCONTAINERS_RYUK_DISABLED: false
```

### GitLab CI

```yaml
test:
  image: maven:3.9-eclipse-temurin-21
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    TESTCONTAINERS_HOST_OVERRIDE: docker
  script:
    - mvn test
```
