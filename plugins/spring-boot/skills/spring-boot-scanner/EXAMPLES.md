# Spring Boot Scanner Examples

Real-world scenarios showing how the scanner detects and routes.

## Example 1: Controller File (Low Risk - Auto-Invoke)

**User Action:** Editing `UserController.java`

**File Content:**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        // ...
    }

    @PostMapping
    public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserRequest request) {
        // ...
    }
}
```

**Scanner Detection:**
```
Detected annotations: @RestController, @GetMapping, @PostMapping, @RequestMapping
Skill match: spring-boot-web-api
Risk level: LOW
```

**Scanner Response:**
```
I notice you're working with REST controller patterns. Here's guidance from spring-boot-web-api:

**Request/Response Best Practices:**
- Use DTOs instead of entities in API responses
- Apply `@Valid` for request body validation
- Return `ResponseEntity<T>` for explicit status codes

**Error Handling:**
- Use `ProblemDetail` (RFC 9457) for error responses
- Define `@ExceptionHandler` in `@ControllerAdvice`

See spring-boot-web-api skill for detailed patterns and examples.
```

---

## Example 2: Security Configuration (High Risk - Confirm)

**User Action:** Creating `SecurityConfig.java`

**File Content:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

**Scanner Detection:**
```
Detected annotations: @EnableWebSecurity, SecurityFilterChain
Skill match: spring-boot-security
Risk level: HIGH
```

**Scanner Response:**
```
I detected security configuration patterns. This involves authentication and authorization setup.

[AskUserQuestion]
Question: "Would you like security guidance for this configuration?"
Options:
1. "Load spring-boot-security skill" - Full Lambda DSL patterns, JWT/OAuth2 setup
2. "Quick validation only" - Check for common security issues
3. "Continue without guidance" - I understand security config
```

**If User Selects Option 1:**
```
Loading spring-boot-security skill...

**Spring Security 7 Requirements:**
- ✅ Using Lambda DSL (correct)
- ✅ Using `requestMatchers()` (correct)
- ✅ Using `authorizeHttpRequests()` (correct)

**Recommendations:**
- Consider adding CSRF protection for state-changing endpoints
- Add method security with `@PreAuthorize` for fine-grained access

See EXAMPLES.md in spring-boot-security for complete patterns.
```

---

## Example 3: Deprecated Pattern (Escalation)

**User Action:** Opening legacy `TestConfig.java`

**File Content:**
```java
@SpringBootTest
public class UserServiceTest {

    @MockBean  // Deprecated in Boot 3.4+
    private UserRepository userRepository;

    @Test
    void shouldCreateUser() {
        // ...
    }
}
```

**Scanner Detection:**
```
Detected annotations: @SpringBootTest, @MockBean
Skill match: spring-boot-testing
Risk level: HIGH
Escalation: @MockBean is deprecated
```

**Scanner Response:**
```
⚠️ **Deprecated Pattern Detected**

Found `@MockBean` which is deprecated since Spring Boot 3.4. Use `@MockitoBean` instead.

**Migration:**
```java
// Before (deprecated)
@MockBean
private UserRepository userRepository;

// After (Spring Boot 4.x)
@MockitoBean
private UserRepository userRepository;
```

**Note:** `@MockitoBean` requires import from `org.springframework.test.context.bean.override.mockito`

Would you like me to help migrate this test file?

[AskUserQuestion]
Options:
1. "Migrate all @MockBean usages" - Find and replace in this file
2. "Scan project for @MockBean" - Check all test files
3. "Load spring-boot-testing skill" - Full testing patterns
```

---

## Example 4: Entity with Repository (Low Risk - Batched)

**User Action:** Creating `Order.java` and `OrderRepository.java`

**Order.java:**
```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
}
```

**OrderRepository.java:**
```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);

    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
    Optional<Order> findByIdWithItems(@Param("id") Long id);
}
```

**Scanner Detection:**
```
Detected annotations: @Entity, @Repository, @ManyToOne, @OneToMany
Skill matches: spring-boot-data-ddd, domain-driven-design
Risk level: LOW (both)
```

**Scanner Response:**
```
I notice you're working with JPA entities and repositories. Here's combined guidance:

**From spring-boot-data-ddd:**
- Use `JOIN FETCH` to avoid N+1 queries (you're doing this ✓)
- Consider `@EntityGraph` for reusable fetch strategies
- Use `orphanRemoval = true` for owned collections (you're doing this ✓)

**From domain-driven-design:**
- Consider if Order is an Aggregate Root
- OrderItems should be Value Objects if they have no independent identity
- Customer reference suggests a different Aggregate - use ID reference instead

**Potential improvement:**
```java
// Instead of entity reference (crosses aggregate boundary)
@ManyToOne
private Customer customer;

// Use ID reference (respects aggregate boundaries)
@Column(name = "customer_id")
private Long customerId;
```

Would you like more details on DDD aggregate patterns?
```

---

## Example 5: Mixed Patterns (Low + High Risk)

**User Action:** Creating integration test with security

**File Content:**
```java
@SpringBootTest
@AutoConfigureMockMvc
public class UserApiIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;

    @Test
    @WithMockUser(roles = "ADMIN")
    void adminCanDeleteUser() throws Exception {
        mockMvc.perform(delete("/api/users/1"))
            .andExpect(status().isNoContent());
    }
}
```

**Scanner Detection:**
```
Detected annotations:
  - @SpringBootTest, @MockitoBean → spring-boot-testing (HIGH)
  - @WithMockUser → spring-boot-security (HIGH)
  - MockMvc patterns → spring-boot-web-api (LOW)
```

**Scanner Response:**
```
I detected multiple patterns in your integration test:

**Auto-loaded (web-api):**
- MockMvc patterns detected - use `contentType(APPLICATION_JSON)` for JSON requests

**Confirmation needed:**
This test involves security testing patterns (@WithMockUser) and slice testing (@SpringBootTest).

[AskUserQuestion]
Question: "Which guidance would you like for this test?"
Options:
1. "Both security + testing skills" - Comprehensive test patterns
2. "Security testing only" - Focus on @WithMockUser, JWT mocking
3. "Integration testing only" - @SpringBootTest, MockMvc patterns
4. "Continue without guidance"
```

---

## Example 6: Build File (Verify Trigger)

**User Action:** Opening `pom.xml`

**File Content:**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.1</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
</dependencies>
```

**Scanner Detection:**
```
Spring Boot version: 3.2.1 (< 4.0)
Detected: com.fasterxml.jackson (Jackson 2.x)
Skill match: spring-boot-verify
Risk level: HIGH
Escalations:
  - Version < 4.0 (migration opportunity)
  - Jackson 2.x namespace (will change in Boot 4)
```

**Scanner Response:**
```
I analyzed your Spring Boot project configuration:

**Current State:**
- Spring Boot version: 3.2.1
- Jackson: 2.x (com.fasterxml namespace)

⚠️ **Migration Considerations:**

Spring Boot 4.0 introduces breaking changes:

| Current | Spring Boot 4.0 |
|---------|-----------------|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` |
| `com.fasterxml.jackson` | `tools.jackson` |
| Java 17+ | Java 21+ recommended |

[AskUserQuestion]
Question: "Would you like migration analysis?"
Options:
1. "Run full upgrade verification" - Launch verify-upgrade agent
2. "Load spring-boot-verify skill" - Dependency guidance only
3. "Not planning to upgrade yet" - Continue as-is
```

---

## Example 7: Comprehensive Review Request

**User Action:** "Can you review my Spring Boot project for best practices?"

**Scanner Response:**
```
For a comprehensive review, I'll delegate to the spring-boot-reviewer agent which can:

1. **Discover** - Scan all Java files, detect which skills are relevant
2. **Parallel Review** - Launch specialized reviewers for each detected area
3. **Report** - Consolidate findings with severity levels

[Task tool invocation]
Launching spring-boot-reviewer agent with scope: "all"

The reviewer will check:
- ✓ Web API patterns (if controllers found)
- ✓ Data/Repository patterns (if entities found)
- ✓ Security configuration (if security files found)
- ✓ Testing patterns (if tests found)
- ✓ Dependency versions (always checked)

Review in progress...
```

---

## Quick Reference: Trigger → Response

| Trigger | Risk | Response |
|---------|------|----------|
| @RestController | LOW | Auto-invoke web-api guidance |
| @Entity | LOW | Auto-invoke data-ddd guidance |
| @Service in domain/** | LOW | Auto-invoke DDD guidance |
| @EnableWebSecurity | HIGH | Ask before loading security |
| @SpringBootTest | HIGH | Ask before loading testing |
| @MockBean | HIGH + WARN | Show deprecation + ask |
| pom.xml < 4.0 | HIGH | Ask about migration |
| "review my project" | DELEGATE | Launch reviewer agent |
