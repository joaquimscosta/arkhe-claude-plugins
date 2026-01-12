# Authentication Patterns

UserDetailsService, password encoding, and authentication providers.

## Custom UserDetailsService

### Java

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return userRepository.findByEmail(username)
            .map(this::toUserDetails)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
    }
    
    private UserDetails toUserDetails(User user) {
        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getEmail())
            .password(user.getPassword())
            .authorities(mapAuthorities(user.getRoles()))
            .accountExpired(!user.isActive())
            .accountLocked(user.isLocked())
            .credentialsExpired(user.isPasswordExpired())
            .disabled(!user.isEnabled())
            .build();
    }
    
    private Collection<GrantedAuthority> mapAuthorities(Set<Role> roles) {
        return roles.stream()
            .flatMap(role -> {
                // Add role + its permissions
                Stream<GrantedAuthority> roleAuthority = 
                    Stream.of(new SimpleGrantedAuthority("ROLE_" + role.getName()));
                Stream<GrantedAuthority> permissions = role.getPermissions().stream()
                    .map(p -> new SimpleGrantedAuthority(p.getName()));
                return Stream.concat(roleAuthority, permissions);
            })
            .collect(Collectors.toSet());
    }
}
```

### Kotlin

```kotlin
@Service
class CustomUserDetailsService(private val userRepository: UserRepository) : UserDetailsService {
    
    override fun loadUserByUsername(username: String): UserDetails =
        userRepository.findByEmail(username)
            ?.toUserDetails()
            ?: throw UsernameNotFoundException("User not found: $username")
    
    private fun User.toUserDetails(): UserDetails = 
        org.springframework.security.core.userdetails.User.builder()
            .username(email)
            .password(password)
            .authorities(roles.flatMap { role ->
                listOf(SimpleGrantedAuthority("ROLE_${role.name}")) +
                    role.permissions.map { SimpleGrantedAuthority(it.name) }
            })
            .accountExpired(!isActive)
            .accountLocked(isLocked)
            .credentialsExpired(isPasswordExpired)
            .disabled(!isEnabled)
            .build()
}
```

## Custom UserDetails Implementation

For richer principal with additional fields:

```java
public class CustomUserDetails implements UserDetails {
    
    private final Long id;
    private final String email;
    private final String password;
    private final String fullName;
    private final String tenantId;
    private final Collection<GrantedAuthority> authorities;
    private final boolean enabled;
    private final boolean accountNonLocked;
    
    // Constructor, getters...
    
    @Override
    public String getUsername() { return email; }
    
    @Override
    public String getPassword() { return password; }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() { return authorities; }
    
    @Override
    public boolean isAccountNonExpired() { return true; }
    
    @Override
    public boolean isAccountNonLocked() { return accountNonLocked; }
    
    @Override
    public boolean isCredentialsNonExpired() { return true; }
    
    @Override
    public boolean isEnabled() { return enabled; }
    
    // Custom accessors
    public Long getId() { return id; }
    public String getFullName() { return fullName; }
    public String getTenantId() { return tenantId; }
}
```

Access in controller:

```java
@GetMapping("/profile")
public ProfileDto getProfile(@AuthenticationPrincipal CustomUserDetails user) {
    return new ProfileDto(user.getId(), user.getFullName(), user.getTenantId());
}
```

## Password Encoding

### Argon2 (Recommended for Spring Security 7)

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return Argon2PasswordEncoder.defaultsForSpring7();
}
```

### BCrypt (Legacy compatible)

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);  // Strength 12
}
```

### Delegating Encoder (Migration support)

Supports multiple encodings for gradual migration:

```java
@Bean
public PasswordEncoder passwordEncoder() {
    String defaultEncoderId = "argon2";
    Map<String, PasswordEncoder> encoders = Map.of(
        "argon2", Argon2PasswordEncoder.defaultsForSpring7(),
        "bcrypt", new BCryptPasswordEncoder(12),
        "scrypt", SCryptPasswordEncoder.defaultsForSpring7()
    );
    return new DelegatingPasswordEncoder(defaultEncoderId, encoders);
}
```

Stored passwords: `{argon2}$argon2id$v=19$m=16384...` or `{bcrypt}$2a$12$...`

## Registration Flow

```java
@Service
public class UserRegistrationService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    @Transactional
    public User register(RegistrationRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new EmailAlreadyExistsException(request.email());
        }
        
        User user = new User();
        user.setEmail(request.email());
        user.setPassword(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());
        user.setRoles(Set.of(roleRepository.findByName("USER").orElseThrow()));
        user.setEnabled(false);  // Require email verification
        user.setVerificationToken(UUID.randomUUID().toString());
        
        User saved = userRepository.save(user);
        eventPublisher.publishEvent(new UserRegisteredEvent(saved));
        
        return saved;
    }
    
    @Transactional
    public void verifyEmail(String token) {
        User user = userRepository.findByVerificationToken(token)
            .orElseThrow(() -> new InvalidTokenException("Invalid verification token"));
        
        user.setEnabled(true);
        user.setVerificationToken(null);
        userRepository.save(user);
    }
}
```

## Password Reset Flow

```java
@Service
public class PasswordResetService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final PasswordResetTokenRepository tokenRepository;
    
    @Transactional
    public void initiateReset(String email) {
        userRepository.findByEmail(email).ifPresent(user -> {
            // Invalidate existing tokens
            tokenRepository.deleteByUser(user);
            
            PasswordResetToken token = new PasswordResetToken();
            token.setUser(user);
            token.setToken(UUID.randomUUID().toString());
            token.setExpiryDate(Instant.now().plus(24, ChronoUnit.HOURS));
            tokenRepository.save(token);
            
            eventPublisher.publishEvent(new PasswordResetRequestedEvent(user, token.getToken()));
        });
        // Always return success to prevent email enumeration
    }
    
    @Transactional
    public void resetPassword(String token, String newPassword) {
        PasswordResetToken resetToken = tokenRepository.findByToken(token)
            .filter(t -> t.getExpiryDate().isAfter(Instant.now()))
            .orElseThrow(() -> new InvalidTokenException("Token expired or invalid"));
        
        User user = resetToken.getUser();
        user.setPassword(passwordEncoder.encode(newPassword));
        user.setPasswordExpired(false);
        userRepository.save(user);
        
        tokenRepository.delete(resetToken);
        // Invalidate all sessions for this user
        eventPublisher.publishEvent(new PasswordChangedEvent(user));
    }
}
```

## Authentication Events

```java
@Component
public class AuthenticationEventListener {
    
    private final LoginAttemptService loginAttemptService;
    
    @EventListener
    public void onSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getName();
        loginAttemptService.loginSucceeded(username);
        log.info("Successful login: {}", username);
    }
    
    @EventListener
    public void onFailure(AbstractAuthenticationFailureEvent event) {
        String username = (String) event.getAuthentication().getPrincipal();
        loginAttemptService.loginFailed(username);
        log.warn("Failed login attempt: {} - {}", username, event.getException().getMessage());
    }
}

@Service
public class LoginAttemptService {
    
    private final Cache<String, Integer> attemptsCache;
    private static final int MAX_ATTEMPTS = 5;
    
    public void loginFailed(String username) {
        int attempts = attemptsCache.get(username, k -> 0) + 1;
        attemptsCache.put(username, attempts);
        
        if (attempts >= MAX_ATTEMPTS) {
            userRepository.findByEmail(username).ifPresent(user -> {
                user.setLocked(true);
                user.setLockedUntil(Instant.now().plus(30, ChronoUnit.MINUTES));
                userRepository.save(user);
            });
        }
    }
    
    public void loginSucceeded(String username) {
        attemptsCache.invalidate(username);
    }
}
```

## Multi-Factor Authentication Setup

```java
@Service
public class TotpService {
    
    private final GoogleAuthenticator googleAuth = new GoogleAuthenticator();
    
    public TotpSetup generateSecret(User user) {
        GoogleAuthenticatorKey key = googleAuth.createCredentials();
        String qrCodeUrl = GoogleAuthenticatorQRGenerator.getOtpAuthTotpURL(
            "MyApp",
            user.getEmail(),
            key
        );
        return new TotpSetup(key.getKey(), qrCodeUrl);
    }
    
    public boolean verifyCode(String secret, int code) {
        return googleAuth.authorize(secret, code);
    }
}

// Custom authentication filter for 2FA
public class TwoFactorAuthenticationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
            HttpServletResponse response, FilterChain chain) {
        
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        
        if (auth != null && auth.isAuthenticated() && requiresTwoFactor(auth)) {
            if (!hasTwoFactorCompleted(auth)) {
                response.sendRedirect("/2fa/verify");
                return;
            }
        }
        
        chain.doFilter(request, response);
    }
}
```

## Role Hierarchy

```java
@Bean
public RoleHierarchy roleHierarchy() {
    return RoleHierarchyImpl.withDefaultRolePrefix()
        .role("ADMIN").implies("MANAGER")
        .role("MANAGER").implies("USER")
        .role("USER").implies("GUEST")
        .build();
}

@Bean
public MethodSecurityExpressionHandler methodSecurityExpressionHandler(
        RoleHierarchy roleHierarchy) {
    DefaultMethodSecurityExpressionHandler handler = 
        new DefaultMethodSecurityExpressionHandler();
    handler.setRoleHierarchy(roleHierarchy);
    return handler;
}
```

With this configuration, `hasRole('ADMIN')` automatically includes MANAGER, USER, and GUEST permissions.
