# Phase 2 Implementation Guide & Next Steps

## Step-by-Step Implementation Checklist

### ✅ 1. Dependencies Update
```bash
cd apps/backend
./gradlew clean build --refresh-dependencies
```

If you get dependency conflicts:
```bash
./gradlew dependencies --configuration compileClasspath
```

### ✅ 2. Create Directory Structure
```bash
# From apps/backend/src/main/kotlin/dev/byteconf/backend/
mkdir -p security config controller/auth dto
```

### ✅ 3. Common Implementation Issues & Solutions

#### Issue: "Cannot resolve symbol 'UserDetails'"
**Solution:** Ensure you have the security starter:
```kotlin
implementation("org.springframework.boot:spring-boot-starter-security")
```

#### Issue: JWT Secret too short
**Solution:** Generate a proper 256-bit secret:
```bash
# Generate a secure secret
openssl rand -base64 32
# Output: Use this as your JWT_SECRET
```

#### Issue: OAuth2 redirect mismatch
**Solution:** Configure Google OAuth2 properly:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth2 credentials
3. Add authorized redirect URIs:
   - `http://localhost:8080/oauth2/callback/google`
   - `http://localhost:8080/login/oauth2/code/google`

### ✅ 4. Testing Your Implementation

#### Test 1: Health Check with Security
```bash
# Should work (public endpoint)
curl http://localhost:8080/actuator/health

# Should return 401 (protected endpoint)
curl http://localhost:8080/api/auth/me
```

#### Test 2: OAuth2 Flow
```bash
# Open in browser
http://localhost:8080/oauth2/authorization/google?redirect_uri=http://localhost:3000/auth/callback
```

#### Test 3: JWT Token Validation
```bash
# After OAuth2, extract token and test
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8080/api/auth/me
```

## Phase 3 Preview: YouTube API Integration

Once Phase 2 is working, we'll implement:

### 🎥 YouTube Data API Integration
```kotlin
@Service
class YouTubeApiService(
    @Value("\${youtube.api.key}") private val apiKey: String,
    private val webClient: WebClient
) {
    suspend fun syncChannelVideos(channelId: String): List<YouTubeVideo> {
        // Fetch videos from YouTube API
        // Auto-create Video entities
        // Extract metadata and thumbnails
    }
}
```

### 🔄 Background Video Processing
```kotlin
@Component
class VideoSyncScheduler {
    @Scheduled(fixedRate = 3600000) // Every hour
    @PreAuthorize("hasRole('ADMIN')") 
    fun syncConferenceVideos() {
        // Sync new videos from configured channels
        // Generate transcripts with Whisper API
        // Auto-tag technologies with AI
    }
}
```

### 🤖 AI-Powered Content Enhancement
```kotlin
@Service
class AIContentService {
    suspend fun generateVideoTags(title: String, description: String): List<String>
    suspend fun generateTranscript(youtubeId: String): Transcript
    suspend fun generateArticle(transcript: Transcript): Article
}
```

## Frontend Integration Preparation

### JWT Token Management (React/Next.js)
```typescript
// lib/auth.ts
export class AuthService {
  static async loginWithGoogle(): Promise<string> {
    // Redirect to OAuth2 endpoint
    // Handle callback with token
    // Store in secure HTTP-only cookie
  }
  
  static async refreshToken(): Promise<string> {
    // Call refresh endpoint
    // Update stored tokens
  }
  
  static async getCurrentUser(): Promise<User> {
    // Call /api/auth/me with JWT
  }
}
```

### Protected Route Component
```typescript
// components/auth/ProtectedRoute.tsx
export function ProtectedRoute({ 
  children, 
  requireRole = 'USER' 
}: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  
  if (loading) return <LoadingSpinner />
  if (!user) return <LoginPage />
  if (requireRole === 'ADMIN' && user.role !== 'ADMIN') {
    return <UnauthorizedPage />
  }
  
  return <>{children}</>
}
```

## Common Gotchas & Solutions

### 1. CORS Issues with Frontend
**Problem:** Frontend can't connect to backend
**Solution:** Update `SecurityConfig.corsConfigurationSource()`:
```kotlin
configuration.allowedOriginPatterns = listOf(
    "http://localhost:*",
    "https://your-domain.com"
)
```

### 2. JWT Token Not Persisting
**Problem:** User gets logged out on refresh
**Solution:** Store JWT in HTTP-only cookies:
```kotlin
// In OAuth2AuthenticationSuccessHandler
val cookie = Cookie("jwt", token).apply {
    isHttpOnly = true
    secure = true // for HTTPS
    maxAge = 7 * 24 * 3600 // 7 days
}
response.addCookie(cookie)
```

### 3. Database Connection Issues
**Problem:** Security context can't load users
**Solution:** Verify database connectivity:
```bash
kubectl port-forward svc/byteconf-postgres 5432:5432
psql -h localhost -p 5432 -U byteconf -d byteconf -c "\dt"
```

### 4. OAuth2 Callback Not Working
**Problem:** Google OAuth redirects to wrong URL
**Solution:** Check your Google Cloud Console settings:
- Authorized JavaScript origins: `http://localhost:8080`
- Authorized redirect URIs: `http://localhost:8080/login/oauth2/code/google`

## Performance Optimizations for Phase 2

### 1. Cache User Details
```kotlin
@Cacheable("users")
fun loadUserById(id: UUID): UserPrincipal {
    // Cache user principal to avoid DB hits
}
```

### 2. JWT Token Caching
```kotlin
@Service
class JwtTokenCache {
    @Cacheable("jwt-validation")
    fun validateAndCache(token: String): Boolean {
        return jwtTokenService.validateToken(token)
    }
}
```

### 3. Database Indexes for Auth
```sql
-- Add these indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id);
```

## Monitoring & Logging

### Security Event Logging
```kotlin
@Component
class SecurityEventLogger {
    
    @EventListener
    fun handleAuthenticationSuccess(event: AuthenticationSuccessEvent) {
        logger.info("User logged in: ${event.authentication.name}")
    }
    
    @EventListener 
    fun handleAuthenticationFailure(event: AbstractAuthenticationFailureEvent) {
        logger.warn("Login failed: ${event.exception.message}")
    }
}
```

### Health Check for Auth System
```kotlin
@Component
class AuthHealthIndicator : HealthIndicator {
    override fun health(): Health {
        return try {
            // Test JWT token generation
            val testToken = jwtTokenService.generateTestToken()
            val isValid = jwtTokenService.validateToken(testToken)
            
            if (isValid) {
                Health.up().withDetail("jwt", "operational").build()
            } else {
                Health.down().withDetail("jwt", "token validation failed").build()
            }
        } catch (e: Exception) {
            Health.down().withException(e).build()
        }
    }
}
```

## Ready for Phase 3?

Once you have Phase 2 working with:
- ✅ OAuth2 login flow
- ✅ JWT token generation
- ✅ Protected endpoints working
- ✅ User profile management

We can move to **Phase 3: YouTube API Integration** which includes:

1. **YouTube Data API** - Sync video metadata automatically
2. **Background Processing** - Scheduled video discovery
3. **AI Integration** - Auto-tagging and transcript generation
4. **Admin Dashboard** - Manage video sync and content
5. **Webhook Support** - Real-time video updates

Let me know if you run into any issues with Phase 2 or if you're ready to tackle Phase 3! 🚀