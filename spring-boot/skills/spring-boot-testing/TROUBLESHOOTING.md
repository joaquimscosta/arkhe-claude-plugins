# Spring Boot Testing Troubleshooting

Common issues and solutions for Spring Boot 4 testing.

## Common Issues

### Issue: @MockBean Not Found or Deprecated

**Symptom:** Compilation error `@MockBean cannot be resolved` or deprecation warning

**Cause:** Spring Boot 4 replaced `@MockBean` with `@MockitoBean`

**Solution:**
```java
// Before (Boot 3.x)
@MockBean
private OrderService orderService;

// After (Boot 4.x)
@MockitoBean
private OrderService orderService;
```

Also update `@SpyBean` to `@MockitoSpyBean`.

---

### Issue: MockMvc Assertions Not Working

**Symptom:** Cannot use fluent assertions with `MockMvc`

**Cause:** Boot 4 introduced `MockMvcTester` for AssertJ-style assertions

**Solution:**
```java
// Before (Boot 3.x)
@Autowired
private MockMvc mockMvc;

mockMvc.perform(get("/api/orders/1"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.status").value("SUBMITTED"));

// After (Boot 4.x) - use MockMvcTester
@Autowired
private MockMvcTester mvc;

assertThat(mvc.get().uri("/api/orders/1"))
    .hasStatusOk()
    .bodyJson()
    .extractingPath("$.status").isEqualTo("SUBMITTED");
```

---

### Issue: Testcontainers @ServiceConnection Not Auto-Configuring

**Symptom:** Tests fail with connection errors despite `@ServiceConnection` annotation

**Cause:** Missing Testcontainers dependency or wrong container type

**Solution:**

1. Ensure correct dependencies:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

2. Use correct container class:
```java
// Correct
@Container
@ServiceConnection
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

// Wrong - generic container won't auto-configure
@Container
@ServiceConnection
static GenericContainer<?> postgres = new GenericContainer<>("postgres:16");
```

---

### Issue: @DataJpaTest Transaction Rollback Hiding Bugs

**Symptom:** Tests pass but production code fails with lazy loading exceptions

**Cause:** Test transaction keeps entity manager open, masking `LazyInitializationException`

**Solution:**
```java
@Test
void shouldFindOrdersWithItems() {
    Order order = new Order();
    order.addItem(new OrderItem("Widget", 2));

    entityManager.persistAndFlush(order);
    entityManager.clear();  // <-- Force detachment to simulate real scenario

    Order found = orderRepository.findById(order.getId()).orElseThrow();
    // Now lazy loading will fail if not properly configured
    assertThat(found.getItems()).hasSize(1);
}
```

---

### Issue: @SpringBootTest Too Slow

**Symptom:** Integration tests take too long to start

**Cause:** Loading full application context when a slice would suffice

**Solution:** Use the appropriate slice annotation:

| Need | Use | Not |
|------|-----|-----|
| Controller test | `@WebMvcTest` | `@SpringBootTest` |
| Repository test | `@DataJpaTest` | `@SpringBootTest` |
| JSON test | `@JsonTest` | `@SpringBootTest` |
| REST client | `@RestClientTest` | `@SpringBootTest` |

Reserve `@SpringBootTest` for true end-to-end integration tests.

---

### Issue: @WithMockUser Not Working

**Symptom:** Security test still returns 401/403 despite `@WithMockUser`

**Cause:** Security configuration not loaded or wrong security context

**Solution:**

1. Ensure `@WebMvcTest` includes security configuration:
```java
@WebMvcTest(controllers = AdminController.class)
@Import(SecurityConfig.class)  // Add if using custom config
class AdminControllerSecurityTest {
```

2. Check role prefix:
```java
// If using hasRole("ADMIN"), the user needs ROLE_ADMIN
@WithMockUser(roles = "ADMIN")  // Correct - adds ROLE_ prefix

// If using hasAuthority("ADMIN"), use authorities
@WithMockUser(authorities = "ADMIN")  // Direct authority
```

---

### Issue: Modulith @ApplicationModuleTest Fails to Load

**Symptom:** `No module found for package` error

**Cause:** Module structure not following conventions or missing `package-info.java`

**Solution:**

1. Verify module structure:
```
com.example.order/
├── package-info.java  // Required for module definition
├── Order.java
├── OrderService.java
└── internal/          // Internal package
    └── OrderProcessor.java
```

2. Add `package-info.java`:
```java
@org.springframework.modulith.ApplicationModule(
    allowedDependencies = {"shared"}
)
package com.example.order;
```

---

## Spring Boot 4 Migration Issues

### MockMvc to MockMvcTester Migration

```java
// Step 1: Change injection
// Before
@Autowired MockMvc mockMvc;
// After
@Autowired MockMvcTester mvc;

// Step 2: Update test methods
// Before
mockMvc.perform(get("/api/orders"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.length()").value(3));

// After
assertThat(mvc.get().uri("/api/orders"))
    .hasStatusOk()
    .bodyJson()
    .extractingPath("$.length()").isEqualTo(3);
```

### @DynamicPropertySource to @ServiceConnection

```java
// Before (Boot 3.x)
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

@DynamicPropertySource
static void properties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
}

// After (Boot 4.x)
@Container
@ServiceConnection
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
// That's it - no @DynamicPropertySource needed!
```

### Imports for New Annotations

```java
// Boot 4 imports
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.context.bean.override.mockito.MockitoSpyBean;
import org.springframework.test.web.servlet.assertj.MockMvcTester;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
```
