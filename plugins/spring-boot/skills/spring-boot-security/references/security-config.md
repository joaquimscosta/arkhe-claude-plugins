# Security Configuration Patterns

Complete SecurityFilterChain configurations for common scenarios.

## Table of Contents

- [Full REST API Configuration](#full-rest-api-configuration)
  - [Java](#java)
  - [Kotlin](#kotlin)
- [Multiple Security Filter Chains](#multiple-security-filter-chains)
- [Request Matchers Patterns](#request-matchers-patterns)
- [Exception Handling](#exception-handling)
- [Session Management](#session-management)
- [Headers Security](#headers-security)
- [Remember-Me](#remember-me)

## Full REST API Configuration

### Java

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.GET, "/api/**").hasAuthority("SCOPE_read")
                .requestMatchers(HttpMethod.POST, "/api/**").hasAuthority("SCOPE_write")
                .requestMatchers(HttpMethod.PUT, "/api/**").hasAuthority("SCOPE_write")
                .requestMatchers(HttpMethod.DELETE, "/api/**").hasAuthority("SCOPE_delete")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter()))
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((request, response, authException) -> {
                    response.setContentType("application/problem+json");
                    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    response.getWriter().write("""
                        {"type":"about:blank","title":"Unauthorized","status":401}
                        """);
                })
                .accessDeniedHandler((request, response, accessDeniedException) -> {
                    response.setContentType("application/problem+json");
                    response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                    response.getWriter().write("""
                        {"type":"about:blank","title":"Forbidden","status":403}
                        """);
                })
            )
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable());
        return http.build();
    }

    @Bean
    @Order(2)
    public SecurityFilterChain webFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login", "/register", "/error").permitAll()
                .requestMatchers("/css/**", "/js/**", "/images/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            );
        return http.build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter =
            new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("permissions");
        grantedAuthoritiesConverter.setAuthorityPrefix("");

        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return converter;
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of(
            "https://app.example.com",
            "http://localhost:3000"
        ));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setExposedHeaders(List.of("Location", "X-Total-Count"));
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
```

### Kotlin

```kotlin
import org.springframework.security.config.annotation.web.invoke

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
class SecurityConfig {

    @Bean
    @Order(1)
    fun apiFilterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            securityMatcher("/api/**")
            authorizeHttpRequests {
                authorize(HttpMethod.OPTIONS, "/**", permitAll)
                authorize(HttpMethod.GET, "/api/public/**", permitAll)
                authorize("/api/admin/**", hasRole("ADMIN"))
                authorize(HttpMethod.GET, "/api/**", hasAuthority("SCOPE_read"))
                authorize(HttpMethod.POST, "/api/**", hasAuthority("SCOPE_write"))
                authorize(anyRequest, authenticated)
            }
            oauth2ResourceServer { jwt { } }
            sessionManagement { sessionCreationPolicy = SessionCreationPolicy.STATELESS }
            csrf { disable() }
            cors { configurationSource = corsConfigurationSource() }
        }
        return http.build()
    }

    @Bean
    @Order(2)
    fun webFilterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            authorizeHttpRequests {
                authorize("/login", permitAll)
                authorize("/css/**", permitAll)
                authorize(anyRequest, authenticated)
            }
            formLogin {
                loginPage = "/login"
                defaultSuccessUrl("/dashboard", true)
            }
            logout {
                logoutSuccessUrl = "/login?logout"
            }
        }
        return http.build()
    }

    @Bean
    fun corsConfigurationSource(): CorsConfigurationSource {
        val config = CorsConfiguration().apply {
            allowedOrigins = listOf("https://app.example.com")
            allowedMethods = listOf("GET", "POST", "PUT", "DELETE", "OPTIONS")
            allowedHeaders = listOf("*")
            allowCredentials = true
            maxAge = 3600L
        }
        return UrlBasedCorsConfigurationSource().apply {
            registerCorsConfiguration("/api/**", config)
        }
    }
}
```

## Multiple Security Filter Chains

Use `@Order` and `securityMatcher()` for different authentication per path:

```java
@Configuration
@EnableWebSecurity
public class MultiSecurityConfig {

    // API endpoints - JWT authentication
    @Bean
    @Order(1)
    public SecurityFilterChain apiSecurity(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());
        return http.build();
    }

    // Actuator endpoints - Basic authentication
    @Bean
    @Order(2)
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                .anyRequest().hasRole("ACTUATOR")
            )
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }

    // Web pages - Form authentication
    @Bean
    @Order(3)
    public SecurityFilterChain webSecurity(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form.loginPage("/login").permitAll());
        return http.build();
    }
}
```

## Request Matchers Patterns

```java
.authorizeHttpRequests(auth -> auth
    // Exact path
    .requestMatchers("/api/orders").hasRole("USER")

    // Path pattern with wildcard
    .requestMatchers("/api/orders/**").hasRole("USER")

    // HTTP method specific
    .requestMatchers(HttpMethod.POST, "/api/orders").hasRole("ADMIN")
    .requestMatchers(HttpMethod.DELETE, "/api/**").hasRole("ADMIN")

    // Multiple patterns
    .requestMatchers("/public/**", "/assets/**", "/error").permitAll()

    // MVC pattern (recommended for MVC apps)
    .requestMatchers(new MvcRequestMatcher(introspector, "/users/{id}")).authenticated()

    // Regex pattern
    .requestMatchers(new RegexRequestMatcher("/api/v[0-9]+/.*", null)).authenticated()

    // IP-based (internal only)
    .requestMatchers(new IpAddressMatcher("192.168.1.0/24")).permitAll()

    // Actuator endpoints
    .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
    .requestMatchers(EndpointRequest.toAnyEndpoint()).hasRole("ACTUATOR")

    // Default deny
    .anyRequest().authenticated()
)
```

## Exception Handling

```java
.exceptionHandling(ex -> ex
    .authenticationEntryPoint(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED))
    .accessDeniedHandler((request, response, denied) -> {
        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.setContentType(MediaType.APPLICATION_PROBLEM_JSON_VALUE);

        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.FORBIDDEN,
            "Access denied: " + denied.getMessage()
        );
        new ObjectMapper().writeValue(response.getOutputStream(), problem);
    })
)
```

## Session Management

```java
.sessionManagement(session -> session
    // Stateless for APIs
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS)

    // Or for web apps with concurrent session control
    .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
    .maximumSessions(1)
    .maxSessionsPreventsLogin(false)  // Kicks out previous session
    .expiredUrl("/login?expired")

    // Session fixation protection
    .sessionFixation().migrateSession()
)
```

## Headers Security

```java
.headers(headers -> headers
    .frameOptions(frame -> frame.deny())
    .contentSecurityPolicy(csp -> csp
        .policyDirectives("default-src 'self'; script-src 'self' 'unsafe-inline'")
    )
    .httpStrictTransportSecurity(hsts -> hsts
        .includeSubDomains(true)
        .maxAgeInSeconds(31536000)
    )
    .referrerPolicy(referrer -> referrer
        .policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)
    )
)
```

## Remember-Me

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http,
        PersistentTokenRepository tokenRepository) throws Exception {
    http
        .rememberMe(remember -> remember
            .tokenRepository(tokenRepository)
            .tokenValiditySeconds(86400 * 14)  // 14 days
            .userDetailsService(userDetailsService)
            .key("uniqueAndSecretKey")
        );
    return http.build();
}

@Bean
public PersistentTokenRepository persistentTokenRepository(DataSource dataSource) {
    JdbcTokenRepositoryImpl repo = new JdbcTokenRepositoryImpl();
    repo.setDataSource(dataSource);
    return repo;
}
```
