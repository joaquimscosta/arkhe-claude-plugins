# JWT and OAuth2 Resource Server

Token validation, claims extraction, and OAuth2 configuration.

## JWT Resource Server Configuration

### Basic Setup

```java
@Configuration
@EnableWebSecurity
public class JwtSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .decoder(jwtDecoder())
                    .jwtAuthenticationConverter(jwtAuthenticationConverter())
                )
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .csrf(csrf -> csrf.disable());
        return http.build();
    }
    
    @Bean
    public JwtDecoder jwtDecoder() {
        NimbusJwtDecoder decoder = NimbusJwtDecoder
            .withIssuerLocation("https://auth.example.com")
            .build();
        
        OAuth2TokenValidator<Jwt> validator = new DelegatingOAuth2TokenValidator<>(
            new JwtTimestampValidator(Duration.ofSeconds(60)),
            new JwtIssuerValidator("https://auth.example.com"),
            audienceValidator()
        );
        decoder.setJwtValidator(validator);
        return decoder;
    }
    
    private OAuth2TokenValidator<Jwt> audienceValidator() {
        return new JwtClaimValidator<List<String>>(
            "aud",
            aud -> aud != null && aud.contains("my-api")
        );
    }
    
    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = 
            new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("permissions");
        grantedAuthoritiesConverter.setAuthorityPrefix("");  // No prefix
        
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        converter.setPrincipalClaimName("sub");
        return converter;
    }
}
```

### Kotlin

```kotlin
@Configuration
@EnableWebSecurity
class JwtSecurityConfig {
    
    @Bean
    fun filterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            authorizeHttpRequests {
                authorize("/api/public/**", permitAll)
                authorize(anyRequest, authenticated)
            }
            oauth2ResourceServer {
                jwt {
                    jwtDecoder = jwtDecoder()
                    jwtAuthenticationConverter = jwtAuthenticationConverter()
                }
            }
            sessionManagement { sessionCreationPolicy = SessionCreationPolicy.STATELESS }
            csrf { disable() }
        }
        return http.build()
    }
    
    @Bean
    fun jwtDecoder(): JwtDecoder {
        val decoder = NimbusJwtDecoder
            .withIssuerLocation("https://auth.example.com")
            .build()
        
        val validator = DelegatingOAuth2TokenValidator(
            JwtTimestampValidator(Duration.ofSeconds(60)),
            JwtIssuerValidator("https://auth.example.com"),
            JwtClaimValidator<List<String>>("aud") { it?.contains("my-api") == true }
        )
        decoder.setJwtValidator(validator)
        return decoder
    }
    
    @Bean
    fun jwtAuthenticationConverter() = JwtAuthenticationConverter().apply {
        setJwtGrantedAuthoritiesConverter(
            JwtGrantedAuthoritiesConverter().apply {
                setAuthoritiesClaimName("permissions")
                setAuthorityPrefix("")
            }
        )
    }
}
```

## Custom Claims Extraction

### Custom JWT Authentication Converter

```java
@Component
public class CustomJwtAuthenticationConverter implements Converter<Jwt, AbstractAuthenticationToken> {
    
    @Override
    public AbstractAuthenticationToken convert(Jwt jwt) {
        Collection<GrantedAuthority> authorities = extractAuthorities(jwt);
        CustomPrincipal principal = extractPrincipal(jwt);
        
        return new CustomJwtAuthenticationToken(jwt, principal, authorities);
    }
    
    private Collection<GrantedAuthority> extractAuthorities(Jwt jwt) {
        Set<GrantedAuthority> authorities = new HashSet<>();
        
        // Extract roles
        List<String> roles = jwt.getClaimAsStringList("roles");
        if (roles != null) {
            roles.stream()
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role.toUpperCase()))
                .forEach(authorities::add);
        }
        
        // Extract permissions/scopes
        List<String> permissions = jwt.getClaimAsStringList("permissions");
        if (permissions != null) {
            permissions.stream()
                .map(SimpleGrantedAuthority::new)
                .forEach(authorities::add);
        }
        
        // Extract scope claim (space-separated)
        String scope = jwt.getClaimAsString("scope");
        if (scope != null) {
            Arrays.stream(scope.split(" "))
                .map(s -> new SimpleGrantedAuthority("SCOPE_" + s))
                .forEach(authorities::add);
        }
        
        return authorities;
    }
    
    private CustomPrincipal extractPrincipal(Jwt jwt) {
        return new CustomPrincipal(
            jwt.getSubject(),
            jwt.getClaimAsString("email"),
            jwt.getClaimAsString("name"),
            jwt.getClaimAsString("tenant_id")
        );
    }
}

public record CustomPrincipal(
    String userId,
    String email,
    String name,
    String tenantId
) {}

public class CustomJwtAuthenticationToken extends AbstractAuthenticationToken {
    
    private final Jwt jwt;
    private final CustomPrincipal principal;
    
    public CustomJwtAuthenticationToken(Jwt jwt, CustomPrincipal principal, 
            Collection<? extends GrantedAuthority> authorities) {
        super(authorities);
        this.jwt = jwt;
        this.principal = principal;
        setAuthenticated(true);
    }
    
    @Override
    public Object getPrincipal() { return principal; }
    
    @Override
    public Object getCredentials() { return jwt; }
    
    public Jwt getJwt() { return jwt; }
}
```

### Access in Controller

```java
@RestController
@RequestMapping("/api")
public class SecuredController {
    
    @GetMapping("/me")
    public UserInfo getCurrentUser(@AuthenticationPrincipal CustomPrincipal principal) {
        return new UserInfo(principal.userId(), principal.email(), principal.name());
    }
    
    @GetMapping("/tenant-data")
    @PreAuthorize("#principal.tenantId == @tenantResolver.getCurrentTenant()")
    public TenantData getTenantData(@AuthenticationPrincipal CustomPrincipal principal) {
        return tenantService.getData(principal.tenantId());
    }
    
    // Direct JWT access
    @GetMapping("/token-info")
    public Map<String, Object> getTokenInfo(@AuthenticationPrincipal Jwt jwt) {
        return Map.of(
            "subject", jwt.getSubject(),
            "issuer", jwt.getIssuer().toString(),
            "issuedAt", jwt.getIssuedAt(),
            "expiresAt", jwt.getExpiresAt(),
            "claims", jwt.getClaims()
        );
    }
}
```

## Multiple JWT Issuers

```java
@Configuration
public class MultiIssuerJwtConfig {
    
    @Bean
    public JwtDecoder jwtDecoder() {
        Map<String, JwtDecoder> decoders = Map.of(
            "https://auth.example.com", createDecoder("https://auth.example.com"),
            "https://partner-auth.example.com", createDecoder("https://partner-auth.example.com")
        );
        
        return token -> {
            String issuer = JWTParser.parse(token).getJWTClaimsSet().getIssuer();
            JwtDecoder decoder = decoders.get(issuer);
            if (decoder == null) {
                throw new JwtException("Unknown issuer: " + issuer);
            }
            return decoder.decode(token);
        };
    }
    
    private JwtDecoder createDecoder(String issuer) {
        return NimbusJwtDecoder.withIssuerLocation(issuer).build();
    }
}
```

## OAuth2 Client (for calling external APIs)

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          external-api:
            client-id: ${CLIENT_ID}
            client-secret: ${CLIENT_SECRET}
            authorization-grant-type: client_credentials
            scope: api.read, api.write
        provider:
          external-api:
            token-uri: https://auth.external.com/oauth/token
```

```java
@Configuration
public class OAuth2ClientConfig {
    
    @Bean
    public OAuth2AuthorizedClientManager authorizedClientManager(
            ClientRegistrationRepository clientRegistrationRepository,
            OAuth2AuthorizedClientService clientService) {
        
        OAuth2AuthorizedClientProvider provider = OAuth2AuthorizedClientProviderBuilder.builder()
            .clientCredentials()
            .refreshToken()
            .build();
        
        AuthorizedClientServiceOAuth2AuthorizedClientManager manager =
            new AuthorizedClientServiceOAuth2AuthorizedClientManager(
                clientRegistrationRepository, clientService);
        manager.setAuthorizedClientProvider(provider);
        return manager;
    }
    
    @Bean
    public RestClient externalApiClient(OAuth2AuthorizedClientManager clientManager) {
        OAuth2ClientHttpRequestInterceptor interceptor = 
            new OAuth2ClientHttpRequestInterceptor(clientManager);
        interceptor.setClientRegistrationId("external-api");
        
        return RestClient.builder()
            .baseUrl("https://api.external.com")
            .requestInterceptor(interceptor)
            .build();
    }
}
```

## Opaque Token (Token Introspection)

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        opaquetoken:
          introspection-uri: https://auth.example.com/oauth/introspect
          client-id: ${INTROSPECTION_CLIENT_ID}
          client-secret: ${INTROSPECTION_CLIENT_SECRET}
```

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .oauth2ResourceServer(oauth2 -> oauth2
            .opaqueToken(opaque -> opaque
                .introspector(opaqueTokenIntrospector())
            )
        );
    return http.build();
}

@Bean
public OpaqueTokenIntrospector opaqueTokenIntrospector() {
    return new NimbusOpaqueTokenIntrospector(
        "https://auth.example.com/oauth/introspect",
        "client-id",
        "client-secret"
    );
}
```

## JWT with JWKS Endpoint

```java
@Bean
public JwtDecoder jwtDecoder() {
    return NimbusJwtDecoder
        .withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
        .jwsAlgorithms(algorithms -> {
            algorithms.add(SignatureAlgorithm.RS256);
            algorithms.add(SignatureAlgorithm.RS384);
        })
        .build();
}
```

## Configuration Properties

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com
          # OR specify JWKS directly:
          jwk-set-uri: https://auth.example.com/.well-known/jwks.json
          # Optional: specify expected audiences
          audiences: my-api, my-other-api
```

## Error Handling for OAuth2

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(jwt -> jwt.decoder(jwtDecoder()))
            .authenticationEntryPoint((request, response, exception) -> {
                response.setStatus(HttpStatus.UNAUTHORIZED.value());
                response.setContentType(MediaType.APPLICATION_PROBLEM_JSON_VALUE);
                
                String error = "invalid_token";
                String description = "The access token is invalid or expired";
                
                if (exception instanceof InvalidBearerTokenException) {
                    description = exception.getMessage();
                }
                
                ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.UNAUTHORIZED);
                problem.setTitle("Unauthorized");
                problem.setDetail(description);
                problem.setProperty("error", error);
                
                new ObjectMapper().writeValue(response.getOutputStream(), problem);
            })
            .accessDeniedHandler((request, response, exception) -> {
                response.setStatus(HttpStatus.FORBIDDEN.value());
                response.setContentType(MediaType.APPLICATION_PROBLEM_JSON_VALUE);
                
                ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.FORBIDDEN);
                problem.setTitle("Forbidden");
                problem.setDetail("Insufficient permissions");
                
                new ObjectMapper().writeValue(response.getOutputStream(), problem);
            })
        );
    return http.build();
}
```

## Public Key Configuration (No JWKS endpoint)

```java
@Bean
public JwtDecoder jwtDecoder(@Value("${jwt.public-key}") RSAPublicKey publicKey) {
    return NimbusJwtDecoder.withPublicKey(publicKey).build();
}
```

Or from PEM file:

```java
@Bean
public JwtDecoder jwtDecoder(@Value("classpath:public-key.pem") Resource publicKeyResource) 
        throws Exception {
    String key = new String(publicKeyResource.getInputStream().readAllBytes());
    key = key.replace("-----BEGIN PUBLIC KEY-----", "")
             .replace("-----END PUBLIC KEY-----", "")
             .replaceAll("\\s", "");
    
    byte[] decoded = Base64.getDecoder().decode(key);
    X509EncodedKeySpec spec = new X509EncodedKeySpec(decoded);
    RSAPublicKey publicKey = (RSAPublicKey) KeyFactory.getInstance("RSA").generatePublic(spec);
    
    return NimbusJwtDecoder.withPublicKey(publicKey).build();
}
```
