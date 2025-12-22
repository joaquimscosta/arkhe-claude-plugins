# Spring Security 7 Examples

Complete working examples for Spring Boot 4 security patterns.

## Minimal REST API Security

Stateless JWT/OAuth2 configuration with Lambda DSL.

### Java

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());  // Stateless API
        return http.build();
    }
}
```

### Kotlin

```kotlin
import org.springframework.security.config.annotation.web.invoke

@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    fun filterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            authorizeHttpRequests {
                authorize("/public/**", permitAll)
                authorize("/api/admin/**", hasRole("ADMIN"))
                authorize(anyRequest, authenticated)
            }
            oauth2ResourceServer { jwt { } }
            sessionManagement { sessionCreationPolicy = SessionCreationPolicy.STATELESS }
            csrf { disable() }
        }
        return http.build()
    }
}
```

**Key points:**
- Lambda DSL is mandatory in Security 7 (no `and()` chaining)
- Use `requestMatchers()` instead of deprecated `antMatchers()`
- Disable CSRF only for stateless JWT APIs

---

## Form Login with Session Security

Traditional web application with session management and CSRF.

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/login", "/register", "/css/**", "/js/**").permitAll()
            .anyRequest().authenticated()
        )
        .formLogin(form -> form
            .loginPage("/login")
            .defaultSuccessUrl("/dashboard", true)
            .failureUrl("/login?error=true")
            .permitAll()
        )
        .logout(logout -> logout
            .logoutSuccessUrl("/login?logout=true")
            .invalidateHttpSession(true)
            .deleteCookies("JSESSIONID")
        )
        .sessionManagement(session -> session
            .maximumSessions(1)
            .expiredUrl("/login?expired=true")
        )
        .csrf(csrf -> csrf.csrfTokenRepository(
            CookieCsrfTokenRepository.withHttpOnlyFalse()  // For SPA
        ));
    return http.build();
}
```

**Key points:**
- Keep CSRF enabled for session-based authentication
- Use `CookieCsrfTokenRepository` for SPA frontends
- Limit concurrent sessions for security

---

## Method Security

Fine-grained authorization with SpEL expressions.

```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class MethodSecurityConfig {}

@Service
public class OrderService {

    @PreAuthorize("hasRole('ADMIN') or #customerId == authentication.principal.id")
    public Order getOrder(Long customerId, Long orderId) {
        // Admin or owner can access
    }

    @PreAuthorize("@orderSecurity.canModify(authentication, #orderId)")
    public void updateOrder(Long orderId, OrderRequest request) {
        // Delegates to security bean
    }

    @PostFilter("filterObject.isPublic or filterObject.ownerId == authentication.name")
    public List<Order> findAll() {
        // Filters results after execution
    }
}

@Component("orderSecurity")
public class OrderSecurityEvaluator {
    public boolean canModify(Authentication auth, Long orderId) {
        // Custom authorization logic
        return orderRepository.findById(orderId)
            .map(order -> order.getOwnerId().equals(auth.getName()))
            .orElse(false);
    }
}
```

**Key points:**
- Enable with `@EnableMethodSecurity` (replaces `@EnableGlobalMethodSecurity`)
- Use `@PreAuthorize` for pre-execution checks
- Delegate complex logic to security beans with `@component.method()` syntax

---

## CORS Configuration

Complete CORS setup for cross-origin API access.

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://frontend.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-Requested-With"));
    config.setAllowCredentials(true);
    config.setMaxAge(3600L);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}

// In SecurityFilterChain:
http.cors(cors -> cors.configurationSource(corsConfigurationSource()));
```

**Key points:**
- Configure CORS in security filter chain, not separately
- Set `allowCredentials(true)` for cookie-based auth
- Use specific origins in production (never `*` with credentials)

---

## Password Encoder (Spring Boot 4)

Argon2 password encoder recommended for Security 7.

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return Argon2PasswordEncoder.defaultsForSpring7();
}
```

**Key points:**
- Argon2 is memory-hard (resistant to GPU attacks)
- `defaultsForSpring7()` provides secure default parameters
- Bcrypt still supported if needed for compatibility
