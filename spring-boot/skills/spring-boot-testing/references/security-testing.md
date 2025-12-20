# Security Testing

@WithMockUser, JWT testing, and secured endpoint verification.

## @WithMockUser

Simplest way to test authenticated endpoints.

### Basic Usage

```java
@WebMvcTest(OrderController.class)
class OrderControllerSecurityTest {
    
    @Autowired
    private MockMvcTester mvc;
    
    @MockitoBean
    private OrderService orderService;
    
    @Test
    void shouldRejectUnauthenticatedRequest() {
        assertThat(mvc.get().uri("/api/orders"))
            .hasStatus(HttpStatus.UNAUTHORIZED);
    }
    
    @Test
    @WithMockUser
    void shouldAllowAuthenticatedUser() {
        given(orderService.findAll()).willReturn(List.of());
        
        assertThat(mvc.get().uri("/api/orders"))
            .hasStatusOk();
    }
    
    @Test
    @WithMockUser(username = "admin", roles = {"ADMIN"})
    void shouldAllowAdmin() {
        assertThat(mvc.get().uri("/api/admin/orders"))
            .hasStatusOk();
    }
    
    @Test
    @WithMockUser(roles = {"USER"})
    void shouldDenyNonAdminFromAdminEndpoint() {
        assertThat(mvc.get().uri("/api/admin/orders"))
            .hasStatus(HttpStatus.FORBIDDEN);
    }
}
```

### Kotlin

```kotlin
@WebMvcTest(OrderController::class)
class OrderControllerSecurityTest(@Autowired val mvc: MockMvcTester) {
    
    @MockitoBean
    lateinit var orderService: OrderService
    
    @Test
    fun `should reject unauthenticated`() {
        assertThat(mvc.get().uri("/api/orders"))
            .hasStatus(HttpStatus.UNAUTHORIZED)
    }
    
    @Test
    @WithMockUser(roles = ["ADMIN"])
    fun `should allow admin`() {
        assertThat(mvc.get().uri("/api/admin/orders"))
            .hasStatusOk()
    }
}
```

### With Authorities (not roles)

```java
@Test
@WithMockUser(authorities = {"order:read", "order:write"})
void shouldAllowWithAuthorities() {
    assertThat(mvc.get().uri("/api/orders"))
        .hasStatusOk();
}
```

## @WithUserDetails

Uses actual UserDetailsService to load user.

```java
@WebMvcTest(OrderController.class)
@Import(TestSecurityConfig.class)
class OrderControllerWithUserDetailsTest {
    
    @Autowired
    private MockMvcTester mvc;
    
    @Test
    @WithUserDetails("admin@example.com")
    void shouldLoadUserFromService() {
        assertThat(mvc.get().uri("/api/orders"))
            .hasStatusOk();
    }
}

@TestConfiguration
class TestSecurityConfig {
    
    @Bean
    public UserDetailsService userDetailsService() {
        UserDetails admin = User.builder()
            .username("admin@example.com")
            .password("{noop}password")
            .roles("ADMIN")
            .build();
        
        UserDetails user = User.builder()
            .username("user@example.com")
            .password("{noop}password")
            .roles("USER")
            .build();
        
        return new InMemoryUserDetailsManager(admin, user);
    }
}
```

## Custom Authentication Annotation

Create reusable security contexts:

```java
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@WithSecurityContext(factory = WithAdminUserSecurityContextFactory.class)
public @interface WithAdminUser {
    String username() default "admin@example.com";
    String tenantId() default "default-tenant";
}

public class WithAdminUserSecurityContextFactory 
        implements WithSecurityContextFactory<WithAdminUser> {
    
    @Override
    public SecurityContext createSecurityContext(WithAdminUser annotation) {
        SecurityContext context = SecurityContextHolder.createEmptyContext();
        
        CustomPrincipal principal = new CustomPrincipal(
            annotation.username(),
            annotation.tenantId()
        );
        
        Authentication auth = new UsernamePasswordAuthenticationToken(
            principal,
            null,
            List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))
        );
        
        context.setAuthentication(auth);
        return context;
    }
}

// Usage
@Test
@WithAdminUser(tenantId = "tenant-123")
void shouldAccessTenantData() {
    assertThat(mvc.get().uri("/api/tenant/data"))
        .hasStatusOk();
}
```

## JWT Testing

### Using jwt() Request Post-Processor

```java
@WebMvcTest(ApiController.class)
class JwtSecuredControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldAcceptValidJwt() throws Exception {
        mockMvc.perform(get("/api/resource")
                .with(jwt()
                    .authorities(new SimpleGrantedAuthority("SCOPE_read"))
                    .jwt(jwt -> jwt
                        .subject("user@example.com")
                        .claim("scope", "read write")
                        .claim("tenant_id", "tenant-123"))))
            .andExpect(status().isOk());
    }
    
    @Test
    void shouldRejectMissingScope() throws Exception {
        mockMvc.perform(get("/api/admin")
                .with(jwt()
                    .authorities(new SimpleGrantedAuthority("SCOPE_read"))))
            .andExpect(status().isForbidden());
    }
    
    @Test
    void shouldRejectExpiredJwt() throws Exception {
        mockMvc.perform(get("/api/resource")
                .with(jwt()
                    .jwt(jwt -> jwt
                        .expiresAt(Instant.now().minusSeconds(3600)))))
            .andExpect(status().isUnauthorized());
    }
}
```

### With MockMvcTester (Boot 4)

```java
@WebMvcTest(ApiController.class)
class JwtSecuredControllerTest {
    
    @Autowired
    private MockMvcTester mvc;
    
    @Test
    void shouldAcceptValidJwt() {
        assertThat(mvc.get().uri("/api/resource")
                .with(jwt()
                    .authorities(new SimpleGrantedAuthority("SCOPE_read"))))
            .hasStatusOk();
    }
}
```

### Custom JWT Authorities Converter in Test

```java
@WebMvcTest(ApiController.class)
@Import(JwtTestConfig.class)
class JwtWithCustomClaimsTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldExtractCustomClaims() throws Exception {
        mockMvc.perform(get("/api/resource")
                .with(jwt()
                    .jwt(jwt -> jwt
                        .claim("permissions", List.of("order:read", "order:write"))
                        .claim("roles", List.of("admin", "user")))))
            .andExpect(status().isOk());
    }
}

@TestConfiguration
class JwtTestConfig {
    
    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter converter = new JwtGrantedAuthoritiesConverter();
        converter.setAuthoritiesClaimName("permissions");
        converter.setAuthorityPrefix("");
        
        JwtAuthenticationConverter jwtConverter = new JwtAuthenticationConverter();
        jwtConverter.setJwtGrantedAuthoritiesConverter(converter);
        return jwtConverter;
    }
}
```

## OAuth2 Login Testing

```java
@WebMvcTest(ProfileController.class)
class OAuth2LoginTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldAccessWithOAuth2Login() throws Exception {
        mockMvc.perform(get("/profile")
                .with(oauth2Login()
                    .attributes(attrs -> attrs.put("name", "John Doe"))
                    .authorities(new SimpleGrantedAuthority("ROLE_USER"))))
            .andExpect(status().isOk());
    }
    
    @Test
    void shouldAccessWithOidcLogin() throws Exception {
        mockMvc.perform(get("/profile")
                .with(oidcLogin()
                    .idToken(token -> token
                        .claim("email", "user@example.com")
                        .claim("name", "John Doe"))))
            .andExpect(status().isOk());
    }
}
```

## Method Security Testing

```java
@SpringBootTest
class MethodSecurityTest {
    
    @Autowired
    private OrderService orderService;
    
    @Test
    @WithMockUser(username = "customer-123")
    void ownerCanAccessOwnOrder() {
        Order order = orderService.findByIdAndCustomer(1L, "customer-123");
        assertThat(order).isNotNull();
    }
    
    @Test
    @WithMockUser(username = "other-customer")
    void nonOwnerCannotAccessOrder() {
        assertThatThrownBy(() -> orderService.findByIdAndCustomer(1L, "customer-123"))
            .isInstanceOf(AccessDeniedException.class);
    }
    
    @Test
    @WithMockUser(roles = "ADMIN")
    void adminCanAccessAnyOrder() {
        Order order = orderService.findByIdAndCustomer(1L, "customer-123");
        assertThat(order).isNotNull();
    }
}
```

## CSRF Testing

```java
@WebMvcTest(OrderController.class)
class CsrfTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    @WithMockUser
    void shouldRequireCsrfForPost() throws Exception {
        mockMvc.perform(post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
            .andExpect(status().isForbidden());  // Missing CSRF token
    }
    
    @Test
    @WithMockUser
    void shouldAcceptWithCsrf() throws Exception {
        mockMvc.perform(post("/api/orders")
                .with(csrf())  // Add CSRF token
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
            .andExpect(status().isCreated());
    }
    
    @Test
    @WithMockUser
    void shouldAcceptWithCsrfAsHeader() throws Exception {
        mockMvc.perform(post("/api/orders")
                .with(csrf().asHeader())  // X-CSRF-TOKEN header
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
            .andExpect(status().isCreated());
    }
}
```

## Integration Test with Full Security

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class SecurityIntegrationTest {
    
    @Autowired
    private WebTestClient webClient;
    
    @Test
    void shouldRejectUnauthenticatedRequest() {
        webClient.get()
            .uri("/api/orders")
            .exchange()
            .expectStatus().isUnauthorized();
    }
    
    @Test
    void shouldAcceptBearerToken() {
        String token = generateTestJwt();
        
        webClient.get()
            .uri("/api/orders")
            .headers(headers -> headers.setBearerAuth(token))
            .exchange()
            .expectStatus().isOk();
    }
    
    @Test
    void shouldRejectInvalidToken() {
        webClient.get()
            .uri("/api/orders")
            .headers(headers -> headers.setBearerAuth("invalid-token"))
            .exchange()
            .expectStatus().isUnauthorized();
    }
    
    private String generateTestJwt() {
        // Generate valid JWT for testing
        return Jwts.builder()
            .subject("test-user")
            .claim("scope", "read write")
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + 3600000))
            .signWith(testKey)
            .compact();
    }
}
```

## Disable Security for Specific Tests

```java
@WebMvcTest(PublicController.class)
@AutoConfigureMockMvc(addFilters = false)  // Disable security filters
class PublicControllerTest {
    
    @Autowired
    private MockMvcTester mvc;
    
    @Test
    void shouldAccessWithoutAuth() {
        assertThat(mvc.get().uri("/public/health"))
            .hasStatusOk();
    }
}
```

Or import a test security config:

```java
@TestConfiguration
public class NoSecurityTestConfig {
    
    @Bean
    @Order(Ordered.HIGHEST_PRECEDENCE)
    public SecurityFilterChain testSecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth.anyRequest().permitAll())
            .csrf(csrf -> csrf.disable());
        return http.build();
    }
}
```
