# Spring Security 7 Configuration Workflow

Detailed step-by-step process for implementing security with Spring Security 7 and Spring Boot 4.

---

## Step 1: Create SecurityFilterChain Bean

Define the security configuration using the mandatory Lambda DSL.

### 1a. Basic Configuration Structure

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                // Define rules here
            )
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```

### 1b. Lambda DSL (Mandatory in Security 7)

| Old Pattern (Removed) | New Pattern (Required) |
|-----------------------|-----------------------|
| `http.authorizeRequests().and()...` | `http.authorizeHttpRequests(auth -> auth...)` |
| `http.formLogin().and().csrf()` | `http.formLogin(form -> form...).csrf(csrf -> csrf...)` |
| `.antMatchers("/api/**")` | `.requestMatchers("/api/**")` |

### 1c. Multiple Filter Chains

For different security requirements on different paths:

```java
@Bean
@Order(1)
public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
    http.securityMatcher("/api/**")
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
    return http.build();
}

@Bean
@Order(2)
public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .formLogin(Customizer.withDefaults());
    return http.build();
}
```

**Output**: SecurityFilterChain bean configured with Lambda DSL.

---

## Step 2: Define Authorization Rules

Configure which endpoints require which access levels.

### 2a. Request Matcher Rules

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/public/**").permitAll()
    .requestMatchers("/api/admin/**").hasRole("ADMIN")
    .requestMatchers(HttpMethod.POST, "/api/orders").hasAuthority("SCOPE_write")
    .requestMatchers("/api/**").authenticated()
    .anyRequest().authenticated()
)
```

### 2b. Ordering Rules

1. **Most specific first** — `/api/admin/**` before `/api/**`
2. **Permit rules before restrict** — Public endpoints first
3. **Always end with default** — `.anyRequest().authenticated()` as catch-all

### 2c. Common Patterns

| Pattern | Use Case |
|---------|----------|
| `permitAll()` | Public endpoints (health, login, static resources) |
| `authenticated()` | Any logged-in user |
| `hasRole("ADMIN")` | Specific role (adds `ROLE_` prefix automatically) |
| `hasAuthority("SCOPE_write")` | Specific authority (no prefix) |
| `denyAll()` | Block endpoint entirely |

**Output**: Authorization rules matching your endpoint security requirements.

---

## Step 3: Configure Authentication

Set up the authentication mechanism.

### 3a. Password Encoding (Security 7)

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return Argon2PasswordEncoder.defaultsForSpring7();
}
```

Argon2 is the recommended encoder for Spring Security 7 (replaces BCrypt as default).

### 3b. UserDetailsService

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
    }
}
```

### 3c. OAuth2/JWT Resource Server

```java
http.oauth2ResourceServer(oauth2 -> oauth2
    .jwt(jwt -> jwt
        .jwtAuthenticationConverter(jwtAuthConverter())
    )
);
```

See [references/JWT-OAUTH2.md](references/JWT-OAUTH2.md) for complete JWT configuration.

**Output**: Authentication mechanism configured with password encoding.

---

## Step 4: Add Method Security

Enable fine-grained access control on individual methods.

### 4a. Enable Method Security

```java
@Configuration
@EnableMethodSecurity  // Replaces @EnableGlobalMethodSecurity
public class MethodSecurityConfig {
}
```

### 4b. @PreAuthorize with SpEL

```java
@Service
public class OrderService {

    @PreAuthorize("hasRole('ADMIN') or #order.customerId == authentication.principal.id")
    public void cancelOrder(Order order) { ... }

    @PreAuthorize("hasAuthority('SCOPE_read')")
    public List<Order> listOrders() { ... }
}
```

### 4c. @PostAuthorize for Response Filtering

```java
@PostAuthorize("returnObject.customerId == authentication.principal.id")
public Order getOrder(Long id) { ... }
```

### 4d. Common SpEL Expressions

| Expression | Checks |
|-----------|--------|
| `hasRole('ADMIN')` | User has ROLE_ADMIN authority |
| `hasAuthority('SCOPE_write')` | User has exact authority |
| `#id == authentication.principal.id` | Method param matches authenticated user |
| `returnObject.owner == authentication.name` | Return value belongs to caller |
| `isAuthenticated()` | User is authenticated |

**Output**: Method-level security with SpEL expressions.

---

## Step 5: Handle CORS and CSRF

Configure cross-origin and cross-site request forgery protection.

### 5a. CORS for REST APIs

```java
http.cors(cors -> cors
    .configurationSource(request -> {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://app.example.com"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        return config;
    })
);
```

### 5b. CSRF Configuration

| Scenario | CSRF Setting |
|----------|-------------|
| Session-based auth (forms) | **Keep enabled** (default) |
| Stateless JWT API | Disable: `csrf(csrf -> csrf.disable())` |
| SPA with session | Use cookie-based: `CookieCsrfTokenRepository.withHttpOnlyFalse()` |

```java
// For SPAs
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
    .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler())
);
```

### 5c. Headers Security

```java
http.headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
        .policyDirectives("default-src 'self'; script-src 'self'")
    )
    .frameOptions(frame -> frame.deny())
    .httpStrictTransportSecurity(hsts -> hsts
        .includeSubDomains(true)
        .maxAgeInSeconds(31536000)
    )
);
```

**Output**: CORS and CSRF configured for your application type.

---

## Verification Checklist

After implementing security:

- [ ] No `and()` chaining — Lambda DSL only
- [ ] No `antMatchers()` — Use `requestMatchers()`
- [ ] No `authorizeRequests()` — Use `authorizeHttpRequests()`
- [ ] Password encoder is Argon2 (Security 7 default)
- [ ] Most specific request matchers before general ones
- [ ] `anyRequest().authenticated()` as catch-all
- [ ] CSRF enabled for session-based auth
- [ ] Method security uses `@EnableMethodSecurity` (not `@EnableGlobalMethodSecurity`)
- [ ] Security tested with `@WithMockUser` — see `spring-boot-testing` skill
