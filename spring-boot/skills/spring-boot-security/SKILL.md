---
name: spring-boot-security
description: Spring Security 7 implementation for Spring Boot 4. Use when configuring authentication, authorization, OAuth2/JWT resource servers, method security, or CORS/CSRF. Covers the mandatory Lambda DSL migration, SecurityFilterChain patterns, @PreAuthorize, and password encoding. For testing secured endpoints, see spring-boot-testing skill.
---

# Spring Security 7 for Spring Boot 4

Implements authentication and authorization with Spring Security 7's mandatory Lambda DSL.

## Critical Breaking Changes

| Removed API | Replacement | Status |
|-------------|-------------|--------|
| `and()` method | Lambda DSL closures | **Required** |
| `authorizeRequests()` | `authorizeHttpRequests()` | **Required** |
| `antMatchers()` | `requestMatchers()` | **Required** |
| `WebSecurityConfigurerAdapter` | `SecurityFilterChain` bean | **Required** |
| `@EnableGlobalMethodSecurity` | `@EnableMethodSecurity` | **Required** |

## Core Workflow

1. **Create SecurityFilterChain bean** → Configure with Lambda DSL
2. **Define authorization rules** → `authorizeHttpRequests()` with `requestMatchers()`
3. **Configure authentication** → Form login, HTTP Basic, or OAuth2
4. **Add method security** → `@EnableMethodSecurity` + `@PreAuthorize`
5. **Handle CORS/CSRF** → Configure for REST APIs

## Quick Implementation Patterns

### Minimal REST API Security

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

### Form Login + Session Security

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

### Method Security

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

## Spring Boot 4 Specifics

### Password Encoder (Argon2 recommended)

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return Argon2PasswordEncoder.defaultsForSpring7();
}
```

### SPA-Friendly CSRF

```java
.csrf(csrf -> csrf.csrfTokenRepository(
    CookieCsrfTokenRepository.withHttpOnlyFalse()
))
// Or for stateless APIs with JWT:
.csrf(csrf -> csrf.disable())
```

### CORS Configuration

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
.cors(cors -> cors.configurationSource(corsConfigurationSource()))
```

## Detailed References

- **Security Configuration**: See [references/security-config.md](references/security-config.md) for complete SecurityFilterChain patterns
- **Authentication**: See [references/authentication.md](references/authentication.md) for UserDetailsService, password encoding
- **JWT/OAuth2**: See [references/jwt-oauth2.md](references/jwt-oauth2.md) for resource server, token validation

## Anti-Pattern Checklist

| Anti-Pattern | Fix |
|--------------|-----|
| Using `and()` chaining | Use Lambda DSL closures |
| `antMatchers()` | Replace with `requestMatchers()` |
| `authorizeRequests()` | Replace with `authorizeHttpRequests()` |
| CSRF disabled without JWT | Keep CSRF for session-based auth |
| Hardcoded credentials | Use environment variables or Secret Manager |
| `permitAll()` on sensitive endpoints | Audit all permit rules |
| Missing `authenticated()` default | End with `.anyRequest().authenticated()` |

## Critical Reminders

1. **Lambda DSL is mandatory** — No more `and()` chaining in Security 7
2. **Order matters** — More specific `requestMatchers` before general ones
3. **CSRF for sessions** — Only disable for stateless JWT APIs
4. **Method security needs enabling** — Add `@EnableMethodSecurity`
5. **Test your security** — Use `@WithMockUser` and JWT test support (see `spring-boot-testing`)
