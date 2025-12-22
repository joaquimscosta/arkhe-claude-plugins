# Spring Security 7 Troubleshooting

Common issues and solutions for Spring Boot 4 security.

## Common Issues

### Issue: Lambda DSL Migration from Method Chaining

**Symptom:** Compilation error `and() method not found` or deprecation warnings

**Cause:** Security 7 removed `and()` chaining, Lambda DSL is mandatory

**Solution:**

```java
// Before (Boot 3.x / Security 6) - DOES NOT COMPILE
http
    .authorizeHttpRequests()
        .requestMatchers("/public/**").permitAll()
        .anyRequest().authenticated()
    .and()  // Removed in Security 7!
    .oauth2ResourceServer()
        .jwt();

// After (Boot 4.x / Security 7) - Lambda DSL
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/public/**").permitAll()
        .anyRequest().authenticated()
    )
    .oauth2ResourceServer(oauth2 -> oauth2
        .jwt(Customizer.withDefaults())
    );
```

---

### Issue: OAuth2 Resource Server JWT Validation Failures

**Symptom:** 401 Unauthorized with valid JWT token

**Cause:** Wrong issuer URI, missing JWKS endpoint, or clock skew

**Solution:**

1. Verify issuer URI matches token's `iss` claim:
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com/
```

2. Or configure JWK Set URI directly:
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          jwk-set-uri: https://auth.example.com/.well-known/jwks.json
```

3. Allow clock skew for distributed systems:
```java
@Bean
public JwtDecoder jwtDecoder() {
    NimbusJwtDecoder decoder = NimbusJwtDecoder
        .withJwkSetUri(jwkSetUri)
        .build();
    decoder.setClaimSetConverter(new JwtTimestampValidator(
        Duration.ofSeconds(60)  // Allow 60s clock skew
    ));
    return decoder;
}
```

---

### Issue: CSRF Token Not Being Sent with SPA

**Symptom:** POST/PUT/DELETE requests fail with 403 Forbidden

**Cause:** CSRF token not accessible to JavaScript or not sent in request

**Solution:**

1. Use cookie-based CSRF for SPAs:
```java
.csrf(csrf -> csrf.csrfTokenRepository(
    CookieCsrfTokenRepository.withHttpOnlyFalse()  // JS can read
))
```

2. Send token in request header (JavaScript):
```javascript
const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('XSRF-TOKEN='))
    ?.split('=')[1];

fetch('/api/orders', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-XSRF-TOKEN': csrfToken
    },
    body: JSON.stringify(data)
});
```

3. For pure stateless APIs with JWT:
```java
.csrf(csrf -> csrf.disable())  // Only with JWT, never with sessions
```

---

### Issue: @PreAuthorize Not Working

**Symptom:** Method executes without authorization check

**Cause:** Method security not enabled or wrong annotation

**Solution:**

1. Enable method security:
```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true)  // Required!
public class SecurityConfig {}
```

2. Check annotation placement:
```java
// Wrong - on interface method (may not work)
public interface OrderService {
    @PreAuthorize("hasRole('ADMIN')")
    void deleteOrder(Long id);
}

// Correct - on implementation class
@Service
public class OrderServiceImpl implements OrderService {
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteOrder(Long id) { ... }
}
```

3. Verify SpEL expression syntax:
```java
// Wrong - role without ROLE_ prefix in hasAuthority
@PreAuthorize("hasAuthority('ADMIN')")  // Needs 'ROLE_ADMIN'

// Correct options:
@PreAuthorize("hasRole('ADMIN')")  // Auto-adds ROLE_ prefix
@PreAuthorize("hasAuthority('ROLE_ADMIN')")  // Explicit prefix
```

---

### Issue: requestMatchers Order Causing Unexpected Access

**Symptom:** More restrictive rule ignored, everyone can access endpoint

**Cause:** More general pattern matched before specific pattern

**Solution:**

```java
// Wrong - /api/** matches first, /api/admin never checked
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/**").authenticated()
    .requestMatchers("/api/admin/**").hasRole("ADMIN")  // Never reached!
);

// Correct - specific patterns before general
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/admin/**").hasRole("ADMIN")  // Checked first
    .requestMatchers("/api/**").authenticated()
);
```

---

### Issue: CORS Preflight Requests Failing

**Symptom:** OPTIONS requests return 401/403 before actual request

**Cause:** Security filter blocking preflight requests

**Solution:**

Configure CORS in security filter chain:
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        // ... rest of config
    return http.build();
}
```

Not separately with `@CrossOrigin` or `WebMvcConfigurer`.

---

## Spring Boot 4 / Security 7 Migration Issues

### WebSecurityConfigurerAdapter Removal

```java
// Before - DOES NOT COMPILE in Security 7
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) { ... }
}

// After - use SecurityFilterChain bean
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        // ... configuration
        return http.build();
    }
}
```

### Method Annotation Changes

```java
// Before
@EnableGlobalMethodSecurity(prePostEnabled = true)

// After
@EnableMethodSecurity(prePostEnabled = true)
```

### Request Matcher Changes

```java
// Before
.antMatchers("/api/**")
.mvcMatchers("/api/**")
.regexMatchers("/api/.*")

// After (all unified)
.requestMatchers("/api/**")
.requestMatchers(new AntPathRequestMatcher("/api/**"))
.requestMatchers(new RegexRequestMatcher("/api/.*", null))
```

### Import Changes

```java
// Security 7 imports
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.config.Customizer;
```
