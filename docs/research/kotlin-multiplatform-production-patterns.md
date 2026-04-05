---
title: "Kotlin Multiplatform (KMP) Production Architecture & Patterns"
version: "1.0.0"
status: Published
created: 2026-04-04
last_updated: 2026-04-04
slug: kotlin-multiplatform-production-patterns
aliases: ["kmp-architecture", "kotlin-multiplatform", "kmp-patterns"]
tags: ["kotlin", "kmp", "multiplatform", "architecture", "sqldelight", "ktor", "koin", "compose-multiplatform"]
promoted_at: 2026-04-04T14:47:53.139073Z
last_refreshed: 2026-04-04T14:47:22.893888+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->

# Kotlin Multiplatform (KMP) Production Architecture & Patterns

## Executive Summary

Kotlin Multiplatform (KMP) reached Stable status in November 2023 and has matured significantly through 2024-2025. It enables sharing Kotlin code across Android, iOS, JVM (backend), JS, and native targets while allowing platform-specific implementations where needed. Unlike full cross-platform solutions (Flutter, React Native), KMP takes a "share logic, keep native UI" approach — a key reason Google, Netflix, and many enterprise teams have adopted it.

The core value proposition: share business logic, domain models, data access, and network layers while keeping UI fully native. This preserves the best developer experience for each platform while eliminating the logic duplication that plagues Android/iOS teams.

This document covers production-ready patterns as of early 2026, including library ecosystem state, architectural patterns, testing strategies, and migration paths.

---

## 1. KMP Project Structure Patterns

### Recommended Module Layout

Production KMP projects use a layered module structure that separates concerns by responsibility and shareability:

```
project-root/
├── build-logic/                         # Convention plugins (composite build)
│   ├── settings.gradle.kts
│   └── src/main/kotlin/
│       ├── kmp-library-convention.gradle.kts
│       ├── kmp-android-convention.gradle.kts
│       └── android-application-convention.gradle.kts
├── shared/
│   ├── domain/                          # Pure business logic — highest shareability
│   │   ├── src/commonMain/kotlin/
│   │   │   ├── model/                   # Data classes, value objects
│   │   │   ├── repository/              # Repository interfaces
│   │   │   └── usecase/                 # Use case / interactor classes
│   │   └── build.gradle.kts
│   ├── data/                            # Repository implementations, mappers
│   │   ├── src/
│   │   │   ├── commonMain/kotlin/
│   │   │   │   ├── repository/          # Implementations using DB + network
│   │   │   │   ├── mapper/              # Domain ↔ DTO mappers
│   │   │   │   └── cache/               # SQLDelight queries, daos
│   │   │   ├── androidMain/kotlin/
│   │   │   └── iosMain/kotlin/
│   │   └── build.gradle.kts
│   ├── network/                         # Ktor client, API services, DTOs
│   │   ├── src/commonMain/kotlin/
│   │   │   ├── api/                     # API interface + Ktor implementation
│   │   │   ├── dto/                     # @Serializable DTOs
│   │   │   └── interceptor/             # Auth, logging interceptors
│   │   └── build.gradle.kts
│   └── platform/                        # expect/actual implementations
│       ├── src/
│       │   ├── commonMain/kotlin/
│       │   ├── androidMain/kotlin/
│       │   └── iosMain/kotlin/
│       └── build.gradle.kts
├── features/
│   ├── auth/
│   │   ├── src/commonMain/kotlin/       # Shared auth logic
│   │   ├── androidMain/                 # Android UI (Compose)
│   │   └── iosMain/                     # iOS UI (SwiftUI via Kotlin interface)
│   └── dashboard/
├── androidApp/                          # Android application module
├── iosApp/                              # Xcode project
└── settings.gradle.kts
```

### Convention Plugins for KMP Builds

Convention plugins in `build-logic/` eliminate Gradle boilerplate across modules. This is the pattern used by Now in Android and large-scale KMP projects:

```kotlin
// build-logic/src/main/kotlin/kmp-library-convention.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.library")
}

kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = JavaVersion.VERSION_17.toString()
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "Shared"
            isStatic = true
        }
    }

    jvm()   // for JVM backend targets

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}

android {
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig { minSdk = libs.versions.minSdk.get().toInt() }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

```kotlin
// Module build.gradle.kts — clean and minimal with convention plugin
plugins {
    alias(libs.plugins.kmp.library.convention)
    alias(libs.plugins.sqldelight)
    alias(libs.plugins.kotlin.serialization)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(projects.shared.domain)
            implementation(libs.ktor.client.core)
            implementation(libs.sqldelight.coroutines.extensions)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.sqldelight.android.driver)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
    }
}
```

### Source Set Hierarchy

KMP 1.9+ introduced the default hierarchy template which automatically creates intermediate source sets:

```
commonMain
├── nativeMain          (all native targets)
│   ├── appleMain       (iOS, macOS, watchOS, tvOS)
│   │   ├── iosMain     (all iOS targets)
│   │   │   ├── iosArm64Main
│   │   │   ├── iosX64Main
│   │   │   └── iosSimulatorArm64Main
│   │   └── macosMain
│   └── linuxMain
├── jvmMain             (JVM and Android)
│   ├── androidMain
│   └── desktopMain     (if using Compose for Desktop)
└── jsMain
```

Enable the default hierarchy in your Kotlin block:

```kotlin
kotlin {
    applyDefaultHierarchyTemplate()   // enabled by default in KGP 1.9.20+

    androidTarget()
    iosArm64()
    iosX64()
    iosSimulatorArm64()
    jvm()
}
```

Custom intermediate source sets for shared Apple/JVM code:

```kotlin
kotlin {
    applyDefaultHierarchyTemplate()

    sourceSets {
        // Custom: share code between Android + JVM (e.g., JVM-only APIs)
        val jvmAndAndroid by creating {
            dependsOn(commonMain.get())
        }
        androidMain.get().dependsOn(jvmAndAndroid)
        jvmMain.get().dependsOn(jvmAndAndroid)
    }
}
```

---

## 2. expect/actual Strategies

### When to Use expect/actual vs Dependency Injection

| Scenario | Recommended Approach |
|---|---|
| Platform APIs with no common interface | `expect/actual` |
| Swappable implementations (testing, mocking) | DI (interface + inject) |
| Small utility functions (UUID, timestamp) | `expect/actual` |
| Complex services with multiple dependencies | Interface + DI |
| Kotlin stdlib gaps (e.g., `AtomicReference`) | `expect/actual` (or use `kotlinx.atomicfu`) |
| Database drivers | `expect/actual` factory function |
| HTTP engines (Ktor) | `expect/actual` or platform DI module |

### expect/actual for Platform Utilities

```kotlin
// commonMain: expect declaration
expect object Platform {
    val name: String
    val version: String
}

expect fun randomUUID(): String

expect fun currentTimeMillis(): Long
```

```kotlin
// androidMain: actual implementation
actual object Platform {
    actual val name: String = "Android"
    actual val version: String = Build.VERSION.RELEASE
}

actual fun randomUUID(): String = java.util.UUID.randomUUID().toString()

actual fun currentTimeMillis(): Long = System.currentTimeMillis()
```

```kotlin
// iosMain: actual implementation
actual object Platform {
    actual val name: String = "iOS"
    actual val version: String = UIDevice.currentDevice.systemVersion
}

actual fun randomUUID(): String = NSUUID().UUIDString()

actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()
```

### actual typealias for Wrappers

When a platform type matches the expected API exactly, use `typealias` to avoid wrapper overhead:

```kotlin
// commonMain
expect class AtomicInt(initialValue: Int) {
    fun get(): Int
    fun set(value: Int)
    fun getAndIncrement(): Int
    fun compareAndSet(expected: Int, new: Int): Boolean
}

// jvmMain — delegate to java.util.concurrent
actual typealias AtomicInt = java.util.concurrent.atomic.AtomicInteger

// nativeMain — use kotlinx.atomicfu or a hand-rolled implementation
actual class AtomicInt actual constructor(initialValue: Int) {
    private val lock = NSLock()
    private var _value = initialValue
    actual fun get(): Int { lock.lock(); return _value.also { lock.unlock() } }
    // ...
}
```

### Interface-Based Abstraction with DI (Preferred for Services)

For anything with real dependencies, prefer interfaces + DI over `expect/actual`:

```kotlin
// commonMain — define interface and use it everywhere
interface FileStorage {
    suspend fun read(path: String): ByteArray?
    suspend fun write(path: String, data: ByteArray)
    suspend fun delete(path: String)
}

// commonMain — use case consumes the interface
class SyncUseCase(
    private val fileStorage: FileStorage,
    private val api: SyncApi
) {
    suspend fun sync(): Result<Unit> = runCatching {
        val data = api.fetchLatest()
        fileStorage.write("sync_cache.json", data)
    }
}
```

```kotlin
// androidMain — Android implementation
class AndroidFileStorage(private val context: Context) : FileStorage {
    override suspend fun read(path: String): ByteArray? =
        withContext(Dispatchers.IO) {
            context.filesDir.resolve(path).takeIf { it.exists() }?.readBytes()
        }
    // ...
}

// androidMain — Koin module
val androidStorageModule = module {
    single<FileStorage> { AndroidFileStorage(get()) }
}
```

```kotlin
// iosMain — iOS implementation
class IosFileStorage : FileStorage {
    private val fileManager = NSFileManager.defaultManager
    override suspend fun read(path: String): ByteArray? {
        val fullPath = NSSearchPathForDirectoriesInDomains(
            NSDocumentDirectory, NSUserDomainMask, true
        ).first() as String + "/$path"
        return fileManager.contentsAtPath(fullPath)?.toByteArray()
    }
    // ...
}
```

### expect/actual Factory Pattern

A factory function is a clean middle ground — keep the interface in commonMain and use expect/actual only for the driver/engine creation:

```kotlin
// commonMain — DatabaseFactory abstraction
expect fun createSqlDriver(schema: SqlSchema<QueryResult.AsyncValue<Unit>>, name: String): SqlDriver

// commonMain — use it in DI setup
val databaseModule = module {
    single { createSqlDriver(AppDatabase.Schema, "app.db") }
    single { AppDatabase(get()) }
}
```

```kotlin
// androidMain
actual fun createSqlDriver(
    schema: SqlSchema<QueryResult.AsyncValue<Unit>>,
    name: String
): SqlDriver = AndroidSqliteDriver(schema, get(), name)

// iosMain
actual fun createSqlDriver(
    schema: SqlSchema<QueryResult.AsyncValue<Unit>>,
    name: String
): SqlDriver = NativeSqliteDriver(schema, name)

// jvmMain (for tests / backend)
actual fun createSqlDriver(
    schema: SqlSchema<QueryResult.AsyncValue<Unit>>,
    name: String
): SqlDriver = JdbcSqliteDriver("jdbc:sqlite:$name").also {
    schema.create(it).await()
}
```

---

## 3. Shared Code Boundaries

### What Belongs in commonMain

| Category | Examples | Notes |
|---|---|---|
| Domain models | `data class User(...)`, `sealed class AuthState` | Pure Kotlin, no platform imports |
| Repository interfaces | `interface UserRepository` | Contracts only |
| Use cases / interactors | `LoginUseCase`, `SyncUseCase` | Orchestrate domain + repos |
| ViewModels (shared) | `class DashboardViewModel` | Use `StateFlow`, share across platforms |
| Network DTOs | `@Serializable data class UserDto` | kotlinx-serialization |
| API service interfaces | `interface AuthApi` | Ktor impl in commonMain too |
| Business rules | Validation, calculation, state machines | Pure logic |
| Error models | `sealed class AppError` | Domain errors |
| Coroutine flows | `Flow<List<User>>` | Platform-agnostic async |

### What Stays Platform-Specific

| Category | Platform | Reason |
|---|---|---|
| UI layer | Android (Compose), iOS (SwiftUI) | Platform-native UI toolkits |
| DI configuration (root) | Each platform | `androidContext()`, iOS entry points |
| Push notification handling | Android/iOS | Different SDKs |
| Biometric auth | Android/iOS | Different APIs |
| Platform permissions | Android/iOS | Different permission models |
| Database drivers | Each platform | SQLiteDriver implementations |
| HTTP engines | Each platform | Ktor engine per platform |
| Crash reporting setup | Each platform | Different initialization |
| App lifecycle | Each platform | Activity/Fragment vs AppDelegate |

### Decision Framework

```
Is the code pure Kotlin with no platform APIs?
  YES → Put in commonMain

Does it use platform-specific APIs?
  NO EQUIVALENT → Use expect/actual or platform source set
  HAS INTERFACE EQUIVALENT → Interface in commonMain, impl in platform

Does it need to be tested in isolation?
  YES → Interface + DI (not expect/actual) enables mock injection

Will it differ significantly per platform?
  MINOR DIFFERENCES → expect/actual with shared default where possible
  MAJOR DIFFERENCES → Platform source sets with common interface

Is it UI code?
  YES → Platform-specific (unless using Compose Multiplatform)
```

### Incremental Sharing Strategy

Start with the layer that changes least and has zero platform dependencies:

```
Phase 1: Domain layer only
  - Data models, enums, sealed classes
  - Repository interfaces
  - Risk: Low — no runtime, no libraries

Phase 2: Network layer
  - Ktor client + DTOs + serialization
  - Risk: Medium — test on both platforms early

Phase 3: Data layer
  - SQLDelight schema + generated queries
  - Repository implementations
  - Risk: Medium — driver setup per platform

Phase 4: Business logic (use cases, ViewModels)
  - StateFlow-based ViewModels
  - Risk: Low after Phase 1-3

Phase 5: Shared ViewModels exposed to iOS
  - KMP ViewModels → SwiftUI via @StateObject wrapper
  - Risk: Medium — Swift/Kotlin interop

Phase 6 (optional): Compose Multiplatform UI
  - Risk: Higher — evaluate per screen
```

---

## 4. KMP Library Ecosystem (2025-2026)

### Ktor 3.x — HTTP Client

Ktor 3.0 (released late 2024) is the standard KMP HTTP client with full multiplatform support.

```kotlin
// shared/network/commonMain
val httpClient = HttpClient {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            isLenient = true
            coerceInputValues = true
        })
    }
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = tokenStorage.getAccessToken() ?: "",
                    refreshToken = tokenStorage.getRefreshToken() ?: ""
                )
            }
            refreshTokens {
                val tokens = client.post("$baseUrl/auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                    markAsRefreshTokenRequest()
                }.body<TokenResponse>()
                tokenStorage.saveTokens(tokens.accessToken, tokens.refreshToken)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }
        }
    }
    install(Logging) {
        logger = object : Logger {
            override fun log(message: String) { Napier.d(message, tag = "Ktor") }
        }
        level = LogLevel.INFO
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 30_000
        connectTimeoutMillis = 10_000
    }
    defaultRequest {
        url(baseUrl)
        contentType(ContentType.Application.Json)
        header(HttpHeaders.Accept, ContentType.Application.Json)
    }
}

// Platform-specific engines injected via DI or expect/actual
// androidMain: HttpClient(Android { })
// iosMain:     HttpClient(Darwin { })
// jvmMain:     HttpClient(CIO { })
```

Ktor 3.x additions: `HttpClient` is now fully suspending on all platforms, WebSocket improvements, improved server-sent events, and first-class KMP support in all plugins.

### SQLDelight 2.3+ — Multiplatform Database

SQLDelight generates type-safe Kotlin APIs from `.sq` files. Version 2.x supports async coroutines natively.

```sql
-- shared/data/src/commonMain/sqldelight/com/example/app/User.sq
CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    createdAt INTEGER NOT NULL
);

getUserById:
SELECT * FROM User WHERE id = ?;

getAllUsers:
SELECT * FROM User ORDER BY createdAt DESC;

insertUser:
INSERT OR REPLACE INTO User(id, name, email, createdAt) VALUES (?, ?, ?, ?);

deleteUser:
DELETE FROM User WHERE id = ?;
```

```kotlin
// shared/data/commonMain — Repository using SQLDelight + coroutines
class UserRepositoryImpl(
    private val db: AppDatabase,
    private val api: UserApi,
    private val dispatchers: CoroutineDispatchers
) : UserRepository {

    override fun getUsers(): Flow<List<User>> =
        db.userQueries.getAllUsers()
            .asFlow()
            .mapToList(dispatchers.io)
            .map { it.map(UserEntity::toDomain) }

    override suspend fun refreshUsers() = withContext(dispatchers.io) {
        val dtos = api.getUsers()
        db.transaction {
            dtos.forEach { dto ->
                db.userQueries.insertUser(
                    id = dto.id,
                    name = dto.name,
                    email = dto.email,
                    createdAt = dto.createdAt
                )
            }
        }
    }
}
```

SQLDelight build config:

```kotlin
// shared/data/build.gradle.kts
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.app.db")
            generateAsync = true       // coroutine-first async queries
        }
    }
}
```

### Room 2.7 KMP vs SQLDelight

| Feature | Room 2.7 KMP | SQLDelight 2.x |
|---|---|---|
| Query language | Kotlin DAO annotations + SQL | Pure `.sq` files |
| Code generation | Annotation processor (KSP) | Gradle plugin |
| Type safety | Generated Kotlin DAOs | Generated Kotlin queries |
| Migration support | Excellent (built-in) | Manual migration scripts |
| iOS support | Yes (since 2.7) | Yes (mature) |
| Coroutines | Flow + suspend | Flow + suspend |
| Testing | In-memory Room | JVM SQLite driver |
| Learning curve | Low for Android devs | Medium |
| Recommendation | Great for teams migrating from Android | Better for greenfield KMP |

### Koin 4.x — Multiplatform DI

Koin 4.0 (2024) added first-class KMP support with `koin-core` on all platforms.

```kotlin
// commonMain — shared DI modules
val domainModule = module {
    factory { LoginUseCase(get(), get()) }
    factory { GetUsersUseCase(get()) }
    factory { SyncUseCase(get(), get()) }
}

val networkModule = module {
    single { HttpClientFactory.create(get()) }
    single<UserApi> { UserApiImpl(get(), get()) }
    single<AuthApi> { AuthApiImpl(get()) }
}

val dataModule = module {
    single { createSqlDriver(AppDatabase.Schema, "app.db") }
    single { AppDatabase(get()) }
    single<UserRepository> { UserRepositoryImpl(get(), get(), get()) }
    single<AuthRepository> { AuthRepositoryImpl(get(), get(), get()) }
}

val viewModelModule = module {
    viewModel { DashboardViewModel(get(), get()) }
    viewModel { (userId: String) -> UserDetailViewModel(userId, get()) }
}
```

### kotlinx-serialization

```kotlin
// Multiplatform JSON serialization
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("created_at")
    val createdAt: Long,
    val roles: List<String> = emptyList()
)

// Polymorphic sealed class serialization
@Serializable
sealed class ApiResult<out T> {
    @Serializable
    data class Success<T>(val data: T) : ApiResult<T>()
    @Serializable
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
}

// Custom serializer for value classes
@JvmInline
@Serializable(with = UserIdSerializer::class)
value class UserId(val value: String)

object UserIdSerializer : KSerializer<UserId> {
    override val descriptor = PrimitiveSerialDescriptor("UserId", PrimitiveKind.STRING)
    override fun serialize(encoder: Encoder, value: UserId) = encoder.encodeString(value.value)
    override fun deserialize(decoder: Decoder) = UserId(decoder.decodeString())
}
```

### kotlinx-datetime

```kotlin
// Multiplatform date/time — replaces java.time on all platforms
import kotlinx.datetime.*

val now: Instant = Clock.System.now()
val today: LocalDate = now.toLocalDateTime(TimeZone.currentSystemDefault()).date
val utcDateTime: LocalDateTime = now.toLocalDateTime(TimeZone.UTC)

// Arithmetic
val tomorrow = today.plus(1, DateTimeUnit.DAY)
val oneWeekAgo: Instant = now - 7.days

// Serialization (implements @Serializable)
@Serializable
data class Event(
    val id: String,
    val title: String,
    val scheduledAt: Instant,   // serializes as ISO-8601 string
    val date: LocalDate         // serializes as "2025-03-15"
)
```

### Multiplatform Settings (russhwolf)

```kotlin
// Shared preferences / key-value store across platforms
// commonMain
interface AppSettings {
    var authToken: String?
    var userId: String?
    var isDarkMode: Boolean
}

class AppSettingsImpl(private val settings: Settings) : AppSettings {
    override var authToken: String?
        get() = settings.getStringOrNull(KEY_AUTH_TOKEN)
        set(value) = if (value != null) settings[KEY_AUTH_TOKEN] = value
                     else settings.remove(KEY_AUTH_TOKEN)
    override var userId: String?
        get() = settings.getStringOrNull(KEY_USER_ID)
        set(value) = value?.let { settings[KEY_USER_ID] = it } ?: settings.remove(KEY_USER_ID)
    override var isDarkMode: Boolean
        get() = settings.getBoolean(KEY_DARK_MODE, false)
        set(value) { settings[KEY_DARK_MODE] = value }

    companion object {
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_DARK_MODE = "dark_mode"
    }
}

// androidMain — Koin module
val androidSettingsModule = module {
    single<Settings> { SharedPreferencesSettings(get<Context>().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)) }
    single<AppSettings> { AppSettingsImpl(get()) }
}

// iosMain — Koin module
val iosSettingsModule = module {
    single<Settings> { NSUserDefaultsSettings(NSUserDefaults.standardUserDefaults) }
    single<AppSettings> { AppSettingsImpl(get()) }
}
```

### Kermit — Multiplatform Logging

```kotlin
// commonMain — configure Kermit
val log = Logger.withTag("AppTag")

// Usage anywhere in commonMain
log.d { "Debug message: $data" }
log.i { "User logged in: $userId" }
log.w { "Cache miss for key: $key" }
log.e(exception) { "Failed to sync" }

// androidMain — add Crashlytics sink
Logger.addLogWriter(CrashlyticsLogWriter())

// iosMain — add OSLog or Crashlytics
Logger.addLogWriter(OSLogWriter())
```

---

## 5. Platform-Specific DI with Koin Multiplatform

### Module Organization Pattern

```kotlin
// commonMain — all platform-agnostic modules
object SharedModules {
    val all = listOf(domainModule, networkModule, dataModule, viewModelModule)
}

// androidMain — Android-specific modules
val androidPlatformModule = module {
    single { androidContext().getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager }
    single<FileStorage> { AndroidFileStorage(get()) }
    single<BiometricAuth> { AndroidBiometricAuth(get()) }
}

fun initKoin(context: Context) = startKoin {
    androidContext(context)
    androidLogger(Level.DEBUG)
    modules(SharedModules.all + androidPlatformModule)
}

// iosMain — iOS entry point (called from Swift)
fun initKoin() = startKoin {
    modules(SharedModules.all + iosPlatformModule)
}
```

```swift
// iOS AppDelegate.swift
@main
struct iOSApp: App {
    init() {
        KoinKt.doInitKoin()
    }
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

### Scoping Strategies

```kotlin
val appModule = module {
    // Singleton: one instance for app lifetime
    single<TokenStorage> { SecureTokenStorage(get()) }
    single<AppDatabase> { AppDatabase(get()) }

    // Factory: new instance per injection
    factory { LoginUseCase(get(), get()) }
    factory { CoroutineDispatchers() }

    // ViewModel: scoped to ViewModel lifecycle (Android)
    viewModel { DashboardViewModel(get(), get()) }

    // Scoped: bound to a scope (e.g., auth session)
    scope<AuthSession> {
        scoped { UserProfileRepository(get(), get()) }
        scoped { SyncManager(get(), get(), get()) }
    }
}
```

### Testing with Koin

```kotlin
// commonTest — verify module configuration
class ModuleCheckTest : KoinTest {

    @Test
    fun checkKoinModules() {
        // Use checkModules to verify all bindings are satisfied
        checkKoinModules(
            SharedModules.all + testPlatformModule,
            appDeclaration = {
                // Provide test-only bindings
            }
        )
    }
}

// Test platform module providing fakes
val testPlatformModule = module {
    single<SqlDriver> { JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY) }
    single<FileStorage> { InMemoryFileStorage() }
    single<BiometricAuth> { FakeBiometricAuth() }
    single<AppSettings> { InMemorySettings() }
}
```

---

## 6. KMP + Compose Multiplatform (CMP)

### Status as of 2026

| Target | Status | Notes |
|---|---|---|
| Android | Stable | Production-ready, same as Jetpack Compose |
| iOS | Stable (1.6+) | Skia-rendered, not SwiftUI; GPU-accelerated |
| Desktop (JVM) | Stable | Windows, macOS, Linux |
| Web (Wasm) | Beta | Kotlin/Wasm target, replacing JS |
| Web (JS) | Alpha | Being superseded by Wasm target |

CMP 1.6 (released early 2024) stabilized iOS. CMP 1.7+ continues improvements in interop, performance, and accessibility.

### When to Adopt CMP vs Platform-Native UI

**Choose CMP when:**
- Team is Android-Compose-first with no iOS expertise
- UI is data-driven and similar across platforms
- Design system must be pixel-perfect consistent
- Rapid cross-platform iteration is the primary concern
- Internal tools / B2B where Apple HIG compliance is not critical

**Keep platform-native UI when:**
- App requires deep platform integration (widgets, extensions, CarPlay)
- Strong iOS team prefers SwiftUI with full HIG compliance
- Accessibility and platform conventions are critical
- Existing native apps with incremental KMP adoption

### Shared UI Code Strategy

```kotlin
// commonMain — shared screen composable with CMP
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = koinViewModel(),
    onNavigateToDetail: (String) -> Unit
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    when (val s = state) {
        is DashboardState.Loading -> CircularProgressIndicator()
        is DashboardState.Error -> ErrorView(s.message, onRetry = viewModel::retry)
        is DashboardState.Success -> DashboardContent(
            items = s.items,
            onItemClick = { onNavigateToDetail(it.id) }
        )
    }
}

// Platform entry points
// androidMain: DashboardFragment calls DashboardScreen()
// iosMain: UIViewController wraps DashboardScreen() via ComposeUIViewController
```

```swift
// iosMain (Kotlin)
fun DashboardViewController(): UIViewController =
    ComposeUIViewController { DashboardScreen() }

// iOS Swift side
struct DashboardView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        return SharedKt.DashboardViewController()
    }
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
```

### Resources Handling (CMP 1.6+)

```kotlin
// commonMain/composeResources/ — multiplatform resources
// commonMain/composeResources/drawable/logo.png
// commonMain/composeResources/font/Roboto-Regular.ttf
// commonMain/composeResources/values/strings.xml

// Usage in composables
@Composable
fun LogoImage() {
    Image(
        painter = painterResource(Res.drawable.logo),
        contentDescription = "Logo"
    )
}

@Composable
fun WelcomeText() {
    Text(stringResource(Res.string.welcome_title))
}
```

---

## 7. Testing KMP Modules

### commonTest Patterns

```kotlin
// commonTest — use kotlin.test (works on all platforms)
class LoginUseCaseTest {
    private val fakeAuthRepo = FakeAuthRepository()
    private val fakeUserRepo = FakeUserRepository()
    private val useCase = LoginUseCase(fakeAuthRepo, fakeUserRepo)

    @Test
    fun `login with valid credentials returns success`() = runTest {
        fakeAuthRepo.setLoginResponse(Result.success(AuthToken("token123")))
        fakeUserRepo.setUserResponse(Result.success(testUser))

        val result = useCase.execute(LoginParams("user@test.com", "password"))

        assertTrue(result.isSuccess)
        assertEquals("token123", result.getOrThrow().token)
    }

    @Test
    fun `login with invalid credentials returns error`() = runTest {
        fakeAuthRepo.setLoginResponse(Result.failure(InvalidCredentialsException()))

        val result = useCase.execute(LoginParams("user@test.com", "wrong"))

        assertTrue(result.isFailure)
        assertIs<InvalidCredentialsException>(result.exceptionOrNull())
    }
}
```

### Fake Implementations Pattern

```kotlin
// commonTest — shared fakes used across all platforms
class FakeUserRepository : UserRepository {
    private var users = MutableStateFlow<List<User>>(emptyList())
    private var shouldThrow: Exception? = null

    fun setUsers(list: List<User>) { users.value = list }
    fun setError(e: Exception) { shouldThrow = e }

    override fun getUsers(): Flow<List<User>> = users.asStateFlow()

    override suspend fun refreshUsers() {
        shouldThrow?.let { throw it }
    }
}
```

### Turbine for Flow Testing

```kotlin
// commonTest — Turbine works in commonTest via kotlin.test
class DashboardViewModelTest {
    private val fakeRepo = FakeUserRepository()
    private val viewModel by lazy { DashboardViewModel(fakeRepo) }

    @Test
    fun `initial state is loading then success`() = runTest {
        fakeRepo.setUsers(listOf(testUser1, testUser2))

        viewModel.state.test {
            assertEquals(DashboardState.Loading, awaitItem())
            val success = awaitItem()
            assertIs<DashboardState.Success>(success)
            assertEquals(2, success.items.size)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### SQLDelight Testing with JVM Driver

```kotlin
// commonTest (or jvmTest) — in-memory database
fun createTestDatabase(): AppDatabase {
    val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    AppDatabase.Schema.create(driver)
    return AppDatabase(driver)
}

class UserRepositoryTest {
    private val db = createTestDatabase()
    private val fakeApi = FakeUserApi()
    private val repo = UserRepositoryImpl(db, fakeApi, TestDispatchers())

    @Test
    fun `users are cached in database after refresh`() = runTest {
        fakeApi.setUsers(listOf(userDto1, userDto2))
        repo.refreshUsers()

        repo.getUsers().test {
            val users = awaitItem()
            assertEquals(2, users.size)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Ktor MockEngine

```kotlin
// commonTest — MockEngine works in all source sets
class UserApiTest {
    private val mockEngine = MockEngine { request ->
        when (request.url.encodedPath) {
            "/api/users" -> respond(
                content = ByteReadChannel("""[{"id":"1","name":"Alice"}]"""),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
            "/api/users/1" -> respond(
                content = ByteReadChannel("""{"id":"1","name":"Alice","email":"alice@test.com"}"""),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
            else -> respond(ByteReadChannel(""), HttpStatusCode.NotFound)
        }
    }

    private val client = HttpClient(mockEngine) {
        install(ContentNegotiation) { json() }
    }
    private val api = UserApiImpl(client, "https://api.test.com")

    @Test
    fun `getUsers returns parsed list`() = runTest {
        val users = api.getUsers()
        assertEquals(1, users.size)
        assertEquals("Alice", users.first().name)
    }
}
```

### Kotest Multiplatform

Kotest 5.x supports commonTest with its `FunSpec`, `BehaviorSpec`, and `ShouldSpec` styles:

```kotlin
// commonTest
class AuthRepositorySpec : FunSpec({
    val fakeApi = FakeAuthApi()
    val fakeStorage = FakeTokenStorage()
    val repo = AuthRepositoryImpl(fakeApi, fakeStorage)

    test("successful login stores tokens") {
        fakeApi.loginResponse = LoginResponse("access123", "refresh456")

        repo.login("user@test.com", "password")

        fakeStorage.accessToken shouldBe "access123"
        fakeStorage.refreshToken shouldBe "refresh456"
    }

    test("failed login throws AuthException") {
        fakeApi.shouldFail = true
        shouldThrow<AuthException> {
            repo.login("user@test.com", "bad")
        }
    }
})
```

### expect/actual for Test Infrastructure

```kotlin
// commonTest — test coroutine dispatcher
expect fun runTestWithDispatchers(block: suspend TestScope.() -> Unit): Unit

// jvmTest / androidTest
actual fun runTestWithDispatchers(block: suspend TestScope.() -> Unit) =
    runTest(UnconfinedTestDispatcher()) { block() }

// nativeTest (iOS)
actual fun runTestWithDispatchers(block: suspend TestScope.() -> Unit) =
    runTest { block() }
```

---

## 8. Migration Paths

### Android-Only to KMP Preparation

Before adding KMP, prepare your Android code to minimize migration effort:

1. **Separate domain layer**: Move all business logic to `domain/` module with zero Android imports
2. **Repository pattern**: Abstract data access behind interfaces in `domain/`
3. **Eliminate Android-isms from logic**: Replace `Context`-dependent code with interfaces, remove `android.util.Log`, use `kotlinx.coroutines` not RxJava
4. **Adopt kotlinx-serialization**: Replace Gson/Moshi (Gson has no KMP support)
5. **Replace java.time with kotlinx-datetime**
6. **Replace OkHttp/Retrofit with Ktor**: Or keep OkHttp for Android-only during transition
7. **Replace Room with SQLDelight** (or adopt Room 2.7+ KMP): SQLDelight is more KMP-native

### Adding iOS Target to Existing KMP Project

```kotlin
// 1. Add iOS targets to build.gradle.kts
kotlin {
    // existing targets...
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
    }
}

// 2. Create iOS framework configuration
kotlin {
    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach { target ->
        target.binaries.framework {
            baseName = "Shared"
            isStatic = true        // static preferred for Xcode integration
            export(projects.shared.domain)  // export public API
            embedBitcode(Framework.BitcodeEmbeddingMode.DISABLE)
        }
    }
}
```

```bash
# 3. Generate Xcode framework
./gradlew :shared:assembleXCFramework

# 4. Add to Xcode project
# Drag build/XCFrameworks/release/Shared.xcframework into Xcode
# OR use SPM with local package reference
```

```swift
// 5. Swift Package Manager local integration (Xcode 14+)
// File → Add Packages → Add Local → select project root
// Package.swift is generated by KGP (Kotlin Gradle Plugin)
```

### Gradual Module-by-Module Adoption

```
Week 1-2: Convert `domain` module to KMP
  - Add KMP plugin, configure targets
  - Ensure zero platform imports
  - Add commonTest with kotlin.test

Week 3-4: Convert `network` module
  - Migrate Retrofit → Ktor
  - Migrate Gson → kotlinx-serialization
  - Add MockEngine tests in commonTest

Week 5-6: Convert `data` module
  - Migrate Room → SQLDelight (or Room 2.7 KMP)
  - Add JVM driver tests
  - Wire up Android driver

Week 7-8: Shared ViewModels
  - Move state holders to commonMain
  - Use StateFlow instead of LiveData
  - Test with Turbine in commonTest

Week 9+: iOS integration
  - Add iOS targets
  - Set up Koin platform modules
  - Build thin Swift UI layer
```

### KMP Project Templates

The official JetBrains KMP Wizard at [kmp.jetbrains.com](https://kmp.jetbrains.com) generates project skeletons with:
- Gradle version catalog (`libs.versions.toml`)
- Convention plugins in `build-logic/`
- Configured targets (Android, iOS, Desktop, Web)
- Pre-configured Compose Multiplatform

For library projects, the [multiplatform-library-template](https://github.com/Kotlin/multiplatform-library-template) provides a clean starting point with `build-logic/`, version catalog, and GitHub Actions CI.

### Real-World Case Studies

**Netflix (2023-2024)**: Adopted KMP for their mobile architecture layer. Shared networking, caching, and business rules between Android/iOS while keeping native UI.

**VMware Workspace ONE (2024)**: Migrated authentication and policy logic to KMP, reducing code duplication and enabling faster feature parity between platforms.

**Touchlab Production KMP (ongoing)**: Touchlab maintains several open-source KMP reference apps demonstrating production patterns, including SKIE (Swift/Kotlin Interop Enhanced) for better Swift interoperability.

**cabo-verde-pos Architecture Reference**: Demonstrates KMP with `shared/domain` + `shared/data` + `features/auth` modules using SQLDelight + Koin + Ktor 3.0.2 targeting Android + JVM. Uses `expect/actual` for SQLite driver creation and DI factory pattern for platform modules. Represents the incremental sharing approach applied to a POS system.

---

## Trade-offs & Considerations

### KMP Strengths
- **No lock-in**: Platform-native UI, incremental adoption, escape hatches
- **Kotlin everywhere**: Same language, toolchain, and idioms across layers
- **Mature ecosystem**: Ktor, SQLDelight, Koin are all production-grade
- **Google backing**: Android team actively uses and contributes to KMP

### KMP Weaknesses
- **iOS debugging**: Debugging Kotlin code in Xcode is still awkward; LLDB integration improving
- **Swift interop**: Default Kotlin/Native → Swift mapping is verbose; SKIE (Touchlab) greatly improves this
- **Build times**: Kotlin/Native compilation is slow; use `iosSimulatorArm64` locally, CI builds full targets
- **expect/actual fragmentation**: Overuse leads to platform fragmentation of logic
- **Compose Multiplatform immaturity**: iOS CMP still has accessibility and text input gaps vs native

### Library Maturity Matrix

| Library | Android | iOS | JVM | Maturity |
|---|---|---|---|---|
| Ktor 3.x | Stable | Stable | Stable | Production |
| SQLDelight 2.x | Stable | Stable | Stable | Production |
| Koin 4.x | Stable | Stable | Stable | Production |
| kotlinx-serialization | Stable | Stable | Stable | Production |
| kotlinx-coroutines | Stable | Stable | Stable | Production |
| kotlinx-datetime | Stable | Stable | Stable | Production |
| Multiplatform Settings | Stable | Stable | Stable | Production |
| Kermit logging | Stable | Stable | Stable | Production |
| Room 2.7 KMP | Stable | Stable | N/A | Production |
| Compose MP (iOS) | Stable | Stable | Stable | Beta→Stable |
| Compose MP (Wasm) | Stable | N/A | Stable | Beta |
| Decompose (navigation) | Stable | Stable | Stable | Production |
| Voyager (navigation) | Stable | Stable | Stable | Production |

---

## References

1. [KMP Official Documentation](https://kotlinlang.org/docs/multiplatform-discover-project.html) — Project structure, source sets, targets
2. [Default Source Set Hierarchy](https://kotlinlang.org/docs/multiplatform-hierarchy.html) — Source set dependency graph
3. [expect/actual Declarations](https://kotlinlang.org/docs/multiplatform-expect-actual.html) — Official guide with best practices
4. [Ktor 3.x Client Docs](https://ktor.io/docs/client-create-new-application.html) — HTTP client configuration
5. [SQLDelight 2.x Docs](https://sqldelight.github.io/sqldelight/2.0.0/) — Schema, queries, drivers
6. [Koin Multiplatform Docs](https://insert-koin.io/docs/setup/koin-mp) — KMP DI configuration
7. [Compose Multiplatform Getting Started](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-getting-started.html) — CMP setup and targets
8. [kotlinx-serialization Guide](https://kotlinlang.org/docs/serialization.html) — JSON, Protobuf, custom serializers
9. [kotlinx-coroutines on KMP](https://github.com/Kotlin/kotlinx.coroutines) — Flow, StateFlow, coroutine builders
10. [Multiplatform Settings (russhwolf)](https://github.com/russhwolf/multiplatform-settings) — Key-value storage
11. [Kermit Logging (Touchlab)](https://github.com/touchlab/Kermit) — Multiplatform structured logging
12. [Turbine Flow Testing](https://github.com/cashapp/turbine) — Flow assertion library
13. [Touchlab KMP Production Guide](https://touchlab.co/kotlin-multiplatform-for-teams) — Enterprise adoption patterns
14. [KMP Wizard](https://kmp.jetbrains.com/) — Official project generator
15. [Multiplatform Library Template](https://github.com/Kotlin/multiplatform-library-template) — JetBrains official KMP library template
16. [SKIE (Touchlab)](https://skie.touchlab.co/) — Swift/Kotlin interop enhancement
17. [Kotlin Blog — KMP Roadmap 2025](https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/) — Official roadmap
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
