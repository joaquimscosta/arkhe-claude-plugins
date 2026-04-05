---
title: "Android Development Ecosystem & Tooling (2025-2026)"
version: "1.0.0"
status: Published
created: 2026-04-04
last_updated: 2026-04-04
slug: android-ecosystem-tooling
aliases: ["android-tooling", "agp-9", "kotlin-android-2025", "jetpack-2025"]
tags: ["android", "kotlin", "jetpack", "compose", "gradle", "agp", "kmp", "tooling", "material3", "room", "navigation", "lifecycle", "datastore", "workmanager"]
promoted_at: 2026-04-04T14:39:07.970755Z
last_refreshed: 2026-04-04T14:38:25.144245+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->

# Android Development Ecosystem & Tooling (2025-2026)

## Executive Summary

The Android development ecosystem entered a new maturity phase in 2025-2026, defined by three convergent shifts: the AGP 9 / Gradle 9 build system overhaul that hardened Kotlin as the only first-class language in the toolchain; the stabilization of Kotlin Multiplatform as a production-ready strategy with official AGP-level support; and the completion of the Jetpack library transition to Kotlin-first, coroutines-first, and KMP-compatible APIs.

Android Gradle Plugin 9.0 (released July 2025) delivered the most breaking change density since AGP 4: old variant APIs were removed, built-in Kotlin became the default (KGP 2.2.10 bundled at runtime), a new DSL interface model was enforced, and the KMP story was formalized via the `com.android.kotlin.multiplatform.library` plugin — replacing the fragile practice of co-applying `com.android.library` and `org.jetbrains.kotlin.multiplatform` in the same module. Gradle 9.0 (released July 2025) matched with its own wave of removals: Java 17 minimum, Groovy 4, Kotlin 2.2 in DSL scripts, and Configuration Cache promoted to the recommended mode.

Kotlin 2.2 (released mid-2025) promoted guard conditions and non-local break/continue to stable, introduced context parameters as an opt-in preview, and unified the Compose compiler plugin — `PausableComposition` and `OptimizeNonSkippingGroups` are now on by default. The Jetpack library layer followed: Room 2.7 became the first full KMP release covering Android, iOS, JVM, macOS, and Linux; Lifecycle 2.10 reached stable with KMP coverage across all major platforms; Navigation 2.9 added type-safe KClass APIs, multiplatform deep-link handling, and simultaneous-resume support for multi-pane layouts. Material 3 1.4.0 introduced Material Expressive components and integrated a `MotionScheme` system, while the Compose BOM advanced to the `2026.03` series.

For teams targeting the 2025-2026 state-of-the-art, the reference configuration is: AGP 9.x + Gradle 9.3+ + Kotlin 2.2+ + Compose BOM 2025.09+ + Room 2.7+/SQLDelight 2.x for KMP data layer + Navigation 2.9 with type-safe routes + Lifecycle 2.10 + Material 3 1.4+ + version catalog with convention plugins.

---

## 1. Android Gradle Plugin (AGP) 9.x

### 1.1 Version Timeline

| AGP Version | Release Date | Min Gradle | Notes |
|-------------|-------------|------------|-------|
| 9.0.0 | Aug 2025 | 9.1.0 | Major breaking release |
| 9.0.1 | Jan 2026 | 9.1.0 | Bug-fix patch |
| 9.1.0 | Mar 2026 | 9.3.1 | Minor feature release |

All 9.x versions require **JDK 17**, **SDK Build Tools 36.0.0**, and a minimum SDK API level target of 36.1.

### 1.2 Breaking Changes from AGP 8

**New DSL interfaces enforced.** AGP 9.0 replaced internal implementations (`BaseExtension`, etc.) with a new set of public DSL interfaces. The old deprecated variant API (`applicationVariants`, `libraryVariants`, etc.) is fully removed:

```kotlin
// AGP 8.x (removed)
android {
    applicationVariants.all { variant ->
        variant.signingConfig.enableV1Signing = false
    }
}

// AGP 9.0+ (required)
androidComponents {
    onVariants { variant ->
        variant.signingConfig.enableV1Signing.set(false)
    }
}
```

An opt-out property `android.newDsl=false` is available but deprecated — it will be removed in AGP 10.0.

**Built-in Kotlin enabled by default.** AGP 9.0 ships with KGP 2.2.10 as a runtime dependency. The `org.jetbrains.kotlin.android` plugin no longer needs to be applied separately. If a project specifies a higher KGP version, Gradle uses that version; if lower than 2.2.10, Gradle automatically upgrades. Opt-out via `android.builtInKotlin=false`.

**Removed DSL elements:**

| Removed API | Replacement |
|---|---|
| `applicationVariants`, `libraryVariants`, `testVariants` | `androidComponents.onVariants()` |
| `variantFilter` | `androidComponents.beforeVariants()` |
| `sdkDirectory`, `ndkDirectory`, `adbExecutable` | `androidComponents.sdkComponents` |
| `dexOptions` | Removed (dx replaced by d8/r8) |
| `generatePureSplits` | App Bundles |
| `AndroidSourceSet.jni` | Not functional, removed |
| `PostProcessing` block | Never stabilized, removed |
| `DensitySplit` | Use App Bundles |
| Embedded Wear OS app | Extract to separate module |

### 1.3 Gradle Property Defaults Changed in AGP 9.0

Many properties that were opt-in graduated to on-by-default:

| Property | Old Default | New Default |
|---|---|---|
| `android.newDsl` | `false` | `true` |
| `android.builtInKotlin` | `false` | `true` |
| `android.useAndroidx` | `false` | `true` |
| `android.uniquePackageNames` | `false` | `true` |
| `android.enableAppCompileTimeRClass` | `false` | `true` |
| `android.proguard.failOnMissingFiles` | `false` | `true` |
| `android.r8.optimizedResourceShrinking` | `false` | `true` |
| `android.defaults.buildfeatures.resvalues` | `true` | `false` |
| `android.defaults.buildfeatures.shaders` | `true` | `false` |
| `android.dependency.useConstraints` | `true` | `false` |

### 1.4 R8 Changes

- New `-processkotlinnullchecks keep|remove_message|remove` option (default: `remove_message`)
- Default `SourceFile` attribute changed to `r8-map-id-<MAP_ID>`
- Companion methods no longer receive keep rule propagation
- AGP 9.1 adds class repackaging into unnamed package by default (add `-dontrepackage` to opt out)
- Log level names (`ASSERT`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `VERBOSE`) now accepted in `-maximumremovedandroidloglevel`

### 1.5 Migration Path

1. Run the **AGP Upgrade Assistant** in Android Studio before manual edits
2. Check all third-party plugins for AGP 9.x compatibility
3. Replace all `applicationVariants`/`libraryVariants` usage with `androidComponents.onVariants()`
4. Remove explicit `org.jetbrains.kotlin.android` plugin application
5. Enable only the build features you actually use (`resValues`, `shaders`, `aidl`, `renderScript`)
6. Set `targetSdk` explicitly (no longer inferred from `compileSdk`)

---

## 2. KMP Plugin Model (`com.android.kotlin.multiplatform.library`)

### 2.1 Background

AGP 9.0 formally deprecated the legacy pattern of co-applying `com.android.library` and `org.jetbrains.kotlin.multiplatform` in the same Gradle subproject. The replacement is `com.android.kotlin.multiplatform.library`, available since AGP 8.10.0 and required from AGP 10.0 (H2 2026).

A KMP + Android Application combination in a single subproject is not supported — the Android app must live in a separate Gradle module.

### 2.2 Plugin Requirements

- AGP 8.10.0+ (9.x recommended)
- Kotlin Gradle Plugin 2.0.0+

### 2.3 Setup

```toml
# gradle/libs.versions.toml
[versions]
agp = "9.1.0"
kotlin = "2.2.10"

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
android-kmp-library  = { id = "com.android.kotlin.multiplatform.library", version.ref = "agp" }
```

```kotlin
// Module build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kmp.library)
}

kotlin {
    androidTarget {
        namespace    = "com.example.kmplib"
        compileSdk   = 35
        minSdk       = 23

        // Opt-in: Java interop
        withJava()

        // Opt-in: unit tests
        withHostTestBuilder {}.configure {}

        // Opt-in: instrumented tests
        withDeviceTestBuilder {
            sourceSetTreeName = "test"
        }

        // Enable Android resources (disabled by default)
        androidResources { enable = true }
    }

    iosX64(); iosArm64(); iosSimulatorArm64()
    jvm()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        androidMain.dependencies {
            implementation(libs.androidx.appcompat)
        }
    }
}
```

### 2.4 Source Set Mapping

| Purpose | New Directory | Old Directory |
|---|---|---|
| Main code | `src/androidMain/kotlin` | `src/main/kotlin` |
| Unit tests | `src/androidHostTest/kotlin` | `src/test/kotlin` |
| Instrumented tests | `src/androidDeviceTest/kotlin` | `src/androidTest/kotlin` |
| Resources | `src/androidMain/res` | `src/main/res` |

### 2.5 Unsupported Features

| Feature | Workaround |
|---|---|
| Build variants (flavors/types) | Separate `com.android.library` module |
| Data Binding / View Binding | Use Compose Multiplatform |
| `externalNativeBuild` | KMP native targets or separate module |
| `BuildConfig` class | Use `BuildKonfig` plugin |

---

## 3. Gradle 9.x

### 3.1 Release Timeline

| Version | Release Date |
|---|---|
| 9.0.0 | Jul 31, 2025 |
| 9.1.0 | Sep 18, 2025 |
| 9.2.0 | Oct 29, 2025 |
| 9.2.1 | Nov 17, 2025 |
| 9.3.0 | Jan 16, 2026 |
| 9.3.1 | Jan 29, 2026 |
| 9.4.0 | Mar 04, 2026 |
| 9.4.1 | Mar 19, 2026 |

AGP 9.1 requires Gradle 9.3.1. The cabo-verde-pos reference project uses Gradle 9.2.1 (compatible with AGP 9.0.x).

### 3.2 Major Features

**Configuration Cache — recommended execution mode.** Gradle 9 promotes Configuration Cache from opt-in to the recommended mode; it is enabled by default in projects generated via `gradle init`. Demonstrated gains: Android X team achieved 3.75× cache size reduction and 50% configuration time reduction on 600-project builds (2m4s → 55s). Parallel cache load/store has been available since Gradle 8.11.

```properties
# gradle.properties — enable explicitly in existing projects
org.gradle.cacheConfigurationCache=true
```

**Kotlin 2.2 DSL and 2.5× build-script compilation speedup.** Kotlin DSL build script compilation avoidance achieves ~2.5× speedup when build files change. The Gradle Kotlin runtime was upgraded to Kotlin 2.2 with language version 2.2.

**Java 17 minimum.** Gradle 9 requires JDK 17 to run the Gradle daemon. JDK up to 24 is supported, and `JAVA_HOME` is now detected automatically for toolchain resolution.

**Groovy 4.** The embedded Groovy runtime was upgraded from 3.0 to 4.0. Groovy DSL build scripts may need minor updates; third-party Groovy-based plugins need compatibility verification.

**Reproducible archives by default.** JARs and ZIPs now produce byte-for-byte identical output (fixed timestamps, consistent file ordering). This is a breaking change for builds that relied on timestamp-based file identity.

**JSpecify nullability annotations.** Gradle's own API now uses JSpecify instead of JSR-305 annotations. Kotlin-based plugins may emit new compiler warnings or errors.

**Isolated Projects (pre-alpha).** Isolated Projects remains in incubation and was not promoted to stable in Gradle 9.0. It requires Configuration Cache as a prerequisite and is expected in a later 9.x release.

**Dependabot supports Gradle lockfiles (June 2025).** Supply-chain tooling can now automatically detect and update locked dependency versions.

### 3.3 Android Build Performance Tips

```properties
# gradle.properties — recommended baseline for Android
org.gradle.cacheConfigurationCache=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.jvmargs=-Xmx4g -XX:+UseG1GC
kotlin.incremental=true
kotlin.incremental.useClasspathSnapshot=true
```

---

## 4. Kotlin 2.2+ for Android

### 4.1 Stable Features Promoted in 2.2

- **Guard conditions in `when` expressions** (stable)
- **Non-local `break` and `continue`** in inline functions (stable)
- **Multi-dollar string interpolation** (stable)

### 4.2 Preview Features (opt-in flags)

**Context parameters** — the successor to the experimental `context()` receivers, designed for cleaner DSL and dependency injection patterns:

```kotlin
context(users: UserService)
fun outputMessage(message: String) {
    users.log("Log: $message")
}
// Enable with: -Xcontext-parameters
```

**Context-sensitive resolution** — omit enum/sealed class prefixes when the type is unambiguous:

```kotlin
fun message(p: Problem): String = when (p) {
    CONNECTION     -> "connection"      // no "Problem." prefix
    AUTHENTICATION -> "authentication"
    DATABASE       -> "database"
    UNKNOWN        -> "unknown"
}
// Enable with: -Xcontext-sensitive-resolution
```

**Nested type aliases:**
```kotlin
class Dijkstra {
    typealias VisitedNodes = Set<Node>
    private fun step(visited: VisitedNodes) = ...
}
// Enable with: -Xnested-type-aliases
```

### 4.3 Kotlin/JVM Changes

**Interface default methods by default.** Functions in interfaces now compile to JVM default methods automatically. The new stable `-jvm-default` option replaces the old `-Xjvm-default`:

```kotlin
kotlin {
    compilerOptions {
        jvmDefault = JvmDefaultMode.NO_COMPATIBILITY
    }
}
```

**`@JvmExposeBoxed`** — expose boxed variants of inline value classes to Java callers without reflection.

**Annotations in Kotlin metadata** — enables reading/writing annotations from compiled `.class` files, useful for annotation processors and reflection tools.

### 4.4 Compose Compiler Integration

The Compose compiler plugin is now bundled with Kotlin 2.x and versioned together. In Kotlin 2.2:

- **`PausableComposition`** is enabled by default (pauses heavy compositions to avoid frame drops)
- **`OptimizeNonSkippingGroups`** is enabled by default (reduces group overhead for non-skippable composables)
- `StrongSkipping` and `IntrinsicRemember` feature flags are **deprecated**
- Composable function references are now stable:

```kotlin
val content: @Composable (String) -> Unit = ::Text

@Composable
fun App() {
    content("My App")
}
```

### 4.5 Breaking Changes in Kotlin 2.2

- Language versions 1.6 and 1.7 are dropped
- Ant build system deprecated
- `kotlinOptions {}` block now raises a **compiler error** — must migrate to `compilerOptions {}`
- `kotlin-android-extensions` plugin removed
- DCE DSLs removed from KGP
- `copy()` on `@JsPlainObject` moved to companion object

### 4.6 JVM Baseline

Android's minimum supported JVM bytecode target remained at JVM 8 in AGP 9.x for broad device compatibility, but the Kotlin compiler itself and Gradle daemon require JDK 17. Teams may set `jvmTarget = JvmTarget.JVM_17` in module-level compiler options when minSdk ≥ 26, enabling Java 17 language features through desugaring.

---

## 5. Jetpack Library Ecosystem

### 5.1 Compose BOM

The Compose BOM is the authoritative way to keep all Compose library versions in sync. BOM 2026.03.01 (latest as of Apr 2026) maps to:

| Library | Version |
|---|---|
| `compose.ui`, `compose.runtime`, `compose.animation` | 1.10.6 |
| `compose.material3` | 1.4.0 |
| `compose.material3.adaptive` | 1.2.0 |
| `compose.material:material` (M2) | 1.10.6 |

```toml
# libs.versions.toml
[versions]
compose-bom = "2026.03.01"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui  = { group = "androidx.compose.ui", name = "ui" }
compose-m3  = { group = "androidx.compose.material3", name = "material3" }
```

```kotlin
// Module build.gradle.kts
dependencies {
    val bom = platform(libs.compose.bom)
    implementation(bom)
    implementation(libs.compose.ui)
    implementation(libs.compose.m3)
    debugImplementation("androidx.compose.ui:ui-tooling")
}
```

The cabo-verde-pos project uses BOM 2024.12.01, which maps to Compose UI 1.7.x and Material 3 1.3.x. Upgrading to BOM 2025.09+ picks up Material 3 1.4.0 (Expressive) and Compose UI 1.8+.

### 5.2 Navigation — Type-Safe Routes (2.8+)

Navigation 2.8.0 introduced compile-time type safety via Kotlin Serialization. Navigation 2.9.x (stable: **2.9.7**, Jan 2026) extended it:

```kotlin
// Type-safe destinations
@Serializable object Home
@Serializable data class Profile(val id: String)

NavHost(navController, startDestination = Home) {
    composable<Home> {
        HomeScreen { id -> navController.navigate(Profile(id)) }
    }
    composable<Profile> { back ->
        ProfileScreen(back.toRoute<Profile>())
    }
}
```

**Supported argument types (2.8.5+):** `Int`, `Long`, `Float`, `Double`, `Boolean`, `String`, `Enum<*>`, nullable variants, `List<T>` for all primitives and enums, value classes (2.9.0+).

**Multi-pane resume (2.9.0):** `SupportingPane` interface allows multiple destinations to be `RESUMED` simultaneously, enabling proper two-pane layouts without lifecycle conflicts.

**KMP support (2.9.0+):** `NavController.handleDeepLink(NavDeepLinkRequest)` is platform-agnostic; `NavUri` parser works on non-Android platforms.

**Alpha (2.10.0-alpha02):** min SDK raised to API 23, `predictivePopEnterTransition` / `predictivePopExitTransition` for back gesture animations, multiplatform `navigation-common` / `navigation-runtime`.

```kotlin
// Dependencies (Kotlin DSL)
dependencies {
    val nav = "2.9.7"
    implementation("androidx.navigation:navigation-compose:$nav")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
}
```

### 5.3 Lifecycle (2.10.0 stable)

Lifecycle **2.10.0** (Nov 2025) is the current stable. KMP coverage is comprehensive:

| Artifact | Platforms |
|---|---|
| `lifecycle-common` | Android, JVM, iOS |
| `lifecycle-runtime` | Android, JVM, iOS |
| `lifecycle-viewmodel` | Android, JVM, iOS |
| `lifecycle-runtime-compose` | Android, JVM, Native, Web |
| `lifecycle-viewmodel-compose` | Android, JVM, Native, Web |

Key additions:

```kotlin
// 2.9.0 — KotlinX Serialization for SavedStateHandle
@Serializable data class Person(val firstName: String, val lastName: String)

class MyViewModel(handle: SavedStateHandle) : ViewModel() {
    var person by handle.saved { Person("John", "Doe") }
}

// 2.8.0 — overridable viewModelScope
class MyViewModel(
    scope: CoroutineScope = Dispatchers.Main.immediate + SupervisorJob()
) : ViewModel(scope)

// 2.10.0 — scoped lifecycles in Compose
val owner = rememberLifecycleOwner()
```

`collectAsStateWithLifecycle()` (from `lifecycle-runtime-compose`) is the recommended way to collect Flows in Compose — it automatically pauses collection when the lifecycle drops below the specified state.

### 5.4 Room vs SQLDelight for KMP

**Room 2.7.0+ (KMP stable, Apr 2025):**

Room now supports Android, iOS, JVM, macOS, Linux, WatchOS, and TvOS. The key migration for KMP:

```kotlin
// KMP Room setup (2.7.0+)
expect object MyDatabaseCtor : RoomDatabaseConstructor<MyDatabase>

@Database(entities = [User::class], version = 1)
@ConstructedBy(MyDatabaseCtor::class)
abstract class MyDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

fun createDatabase(path: String) =
    Room.databaseBuilder<MyDatabase>(name = path)
        .setDriver(BundledSQLiteDriver())
        .setQueryCoroutineContext(Dispatchers.IO)
        .build()
```

Room 2.7 requires KSP2 (KSP 2.x with Kotlin 2.0+) for Kotlin code generation. Room 2.8 adds WatchOS/TvOS targets and a `room-sqlite-wrapper` artifact for gradual migration.

**SQLDelight 2.x:**

SQLDelight remains the alternative for teams who prefer SQL-first schema definition and want a leaner dependency. It supports all KMP targets (Android, iOS, JVM, macOS, Linux, Windows, Web) and produces type-safe query APIs from `.sq` files. The primary differentiators:

| | Room | SQLDelight |
|---|---|---|
| API style | Annotation-based DAO | SQL-first `.sq` files |
| Code gen | KSP | Gradle plugin |
| Android-first | Yes (full feature set) | No (equal across platforms) |
| Build variants | Yes | No |
| Migrations | Auto/manual | Manual `.sqm` files |
| Dialect | Android SQLite | Multiple (SQLite, PostgreSQL, MySQL) |

For Android-only or Android-primary projects, Room 2.7+ is the natural choice given IDE tooling, AndroidX testing utilities, and auto-migrations. For truly symmetric KMP projects (equal weight on iOS/Desktop), SQLDelight's SQL-centric model avoids Room's Android-focused abstractions.

### 5.5 DataStore (1.2.1 stable)

DataStore **1.2.1** (Mar 2026) is the current stable. KMP support covers Android, JVM, and Web (via `localStorage`). Preferences and Proto/Typed variants:

```kotlin
// Preferences DataStore (key-value)
implementation("androidx.datastore:datastore-preferences:1.2.1")

// Typed DataStore (custom Serializable objects)
implementation("androidx.datastore:datastore:1.2.1")
```

Alpha 1.3.x adds `datastore-tink` for AEAD encryption, `DataStore.Builder<T>` API, and cross-tab synchronization on Web.

### 5.6 WorkManager (2.11.2 stable)

WorkManager **2.11.2** (Mar 2026). `CoroutineWorker` is now in the main `work-runtime` artifact (since 2.9.0 — no longer requires `work-runtime-ktx` for coroutines). Key API additions since 2.9:

```kotlin
// 2.9 — Flow-based observation
workManager.getWorkInfosByTagFlow("sync")
    .collect { infos -> /* handle state */ }

// 2.10 — Granular network constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkRequest(
        NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED)
            .build()
    )
    .build()

// 2.10 — Worker coroutine context
val config = Configuration.Builder()
    .setWorkerCoroutineContext(Dispatchers.IO)
    .build()
```

### 5.7 Security Crypto (1.1.0 stable)

Security Crypto **1.1.0** (Jul 2025) — both `security-crypto` and `security-crypto-ktx`. **All APIs in this library are now deprecated** in favor of platform APIs and direct use of Android Keystore. Teams should migrate to:
- `EncryptedFile` → `javax.crypto` + Android Keystore provider
- `EncryptedSharedPreferences` → `DataStore` + `datastore-tink` (alpha)

---

## 6. Version Catalogs and Convention Plugins

### 6.1 `libs.versions.toml` Structure

The TOML version catalog is the canonical approach for Android multi-module dependency management. Place it at `gradle/libs.versions.toml`:

```toml
[versions]
agp             = "9.1.0"
kotlin          = "2.2.10"
ksp             = "2.2.10-1.0.31"
compose-bom     = "2025.09.01"
hilt            = "2.59"
room            = "2.8.4"
navigation      = "2.9.7"
lifecycle       = "2.10.0"
coroutines      = "1.10.1"
serialization   = "1.8.0"
datastore       = "1.2.1"
work            = "2.11.2"

[libraries]
# BOM (no version, managed by BOM)
compose-bom     = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui      = { group = "androidx.compose.ui", name = "ui" }
compose-m3      = { group = "androidx.compose.material3", name = "material3" }
compose-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }

# Core
hilt-android    = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler   = { group = "com.google.dagger", name = "hilt-android-compiler", version.ref = "hilt" }
room-runtime    = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-compiler   = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
room-ktx        = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
nav-compose     = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }
lifecycle-vm    = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }
lifecycle-rt    = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycle" }
datastore-prefs = { group = "androidx.datastore", name = "datastore-preferences", version.ref = "datastore" }
work-runtime    = { group = "androidx.work", name = "work-runtime-ktx", version.ref = "work" }

[bundles]
compose-ui      = ["compose-ui", "compose-m3", "lifecycle-vm", "lifecycle-rt"]
room            = ["room-runtime", "room-ktx"]

[plugins]
android-app     = { id = "com.android.application", version.ref = "agp" }
android-lib     = { id = "com.android.library", version.ref = "agp" }
android-kmp     = { id = "com.android.kotlin.multiplatform.library", version.ref = "agp" }
kotlin-android  = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-kmp      = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
kotlin-compose  = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlin-serial   = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
hilt            = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp             = { id = "com.google.devtools.ksp", version.ref = "ksp" }
room            = { id = "androidx.room", version.ref = "room" }
```

### 6.2 Convention Plugins: `build-logic` Composite Build

The recommended pattern for sharing build logic across modules (used by Now in Android) is a **composite build** rather than `buildSrc`. The composite build approach avoids `buildSrc`'s limitation of always being recompiled:

```
my-app/
├── app/
├── feature/
│   ├── home/
│   └── settings/
├── core/
│   ├── data/
│   └── ui/
├── build-logic/              ← composite build
│   ├── settings.gradle.kts
│   ├── build.gradle.kts
│   └── convention/
│       ├── build.gradle.kts
│       └── src/main/kotlin/
│           ├── AndroidApplicationConventionPlugin.kt
│           ├── AndroidLibraryConventionPlugin.kt
│           ├── AndroidLibraryComposeConventionPlugin.kt
│           └── AndroidKmpLibraryConventionPlugin.kt
└── settings.gradle.kts      ← includeBuild("build-logic")
```

```kotlin
// settings.gradle.kts (root)
pluginManagement {
    includeBuild("build-logic")
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        with(pluginManager) {
            apply("com.android.library")
            apply("org.jetbrains.kotlin.android")
        }
        extensions.configure<LibraryExtension> {
            compileSdk = 35
            defaultConfig.minSdk = 23
            compileOptions {
                sourceCompatibility = JavaVersion.VERSION_17
                targetCompatibility = JavaVersion.VERSION_17
            }
        }
        tasks.withType<KotlinCompile>().configureEach {
            compilerOptions.jvmTarget.set(JvmTarget.JVM_17)
        }
    }
}
```

```kotlin
// In a feature module's build.gradle.kts
plugins {
    id("my-app.android.library")
    id("my-app.android.library.compose")
}
```

**Bundle definitions** group frequently co-declared dependencies:

```kotlin
dependencies {
    implementation(libs.bundles.compose.ui)  // compose-ui + compose-m3 + lifecycle-vm + lifecycle-rt
    implementation(libs.bundles.room)
    ksp(libs.room.compiler)
}
```

---

## 7. Material Design 3

### 7.1 Current State

Material 3 Compose **1.4.0** (Sep 2025) is the current stable, with **1.5.0-alpha** in progress. The Compose BOM tracks these versions automatically. The `material-icons` library is **no longer recommended** — use Material Symbols (vector drawable XMLs from fonts.google.com/icons) instead.

### 7.2 Theming System

The M3 theme has three subsystems:

```kotlin
MaterialTheme(
    colorScheme = colorScheme,  // ColorScheme (was Colors in M2)
    typography  = typography,   // 15-style scale (was 13 in M2)
    shapes      = shapes        // 5 sizes + extraLarge (was 3 in M2)
) { /* content */ }
```

**Dynamic color (Android 12+):**

```kotlin
val colorScheme = when {
    dynamicColor && darkTheme  -> dynamicDarkColorScheme(LocalContext.current)
    dynamicColor && !darkTheme -> dynamicLightColorScheme(LocalContext.current)
    darkTheme                  -> AppDarkColorScheme
    else                       -> AppLightColorScheme
}
```

### 7.3 Material Expressive (M3 1.4.0+)

Material Expressive introduces research-backed, motion-rich components:

- **`MotionScheme`** — components now read `MaterialTheme.motionScheme` for spring-based animation parameters
- **Expressive List Items** with additional color fields in `ListItemColors`
- **Expressive Menu** — toggleable items, selectable items with supporting text, menu groups, popup menus
- **`HorizontalCenteredHeroCarousel`** — new carousel variant
- **`SecureTextField` / `OutlinedSecureTextField`** — password entry with peek toggle
- **`VerticalDragHandle`** — standardized bottom sheet drag indicator
- **`autoSize` for Text** — automatic text resizing within bounds

Alpha (1.5.0): `Scrim`, `LevitatedPaneScrim`, `StaticSheet`, `ExpandedDockedSearchBarWithGap`, `AppBarWithSearch`.

### 7.4 Adaptive Layouts

```kotlin
// NavigationSuiteScaffold — auto-adapts nav style by window size
NavigationSuiteScaffold(
    navigationSuiteItems = {
        item(icon = { Icon(Icons.Default.Home, null) },
             label = { Text("Home") },
             selected = selected == 0,
             onClick = { selected = 0 })
    }
) { /* screen content */ }
```

The scaffold automatically switches between `NavigationBar` (compact), `NavigationRail` (medium), and `NavigationDrawer` (expanded) based on window size class.

```kotlin
dependencies {
    implementation("androidx.compose.material3:material3-adaptive-navigation-suite:1.5.0-alpha16")
}
```

### 7.5 Migration from Material 2

Key component renames:

| M2 | M3 |
|---|---|
| `BottomNavigation` / `BottomNavigationItem` | `NavigationBar` / `NavigationBarItem` |
| `ModalBottomSheetLayout` | `ModalBottomSheet` |
| `ModalDrawer` | `ModalNavigationDrawer` |
| `Chip` | `AssistChip` / `SuggestionChip` |
| `BackdropScaffold` | `Scaffold` + `BottomSheetScaffold` |

Typography name mapping:

| M2 | M3 |
|---|---|
| `h1` – `h3` | `displayLarge` – `displaySmall` |
| `h4` – `h6` | `headlineMedium`, `headlineSmall`, `titleLarge` |
| `subtitle1` / `subtitle2` | `titleMedium` / `titleSmall` |
| `body1` / `body2` | `bodyLarge` / `bodyMedium` |
| `caption` | `bodySmall` |
| `button` | `labelLarge` |
| `overline` | `labelSmall` |

Use [material.io/theme-builder](https://m3.material.io/theme-builder) to generate `ColorScheme` from existing M2 brand colors.

---

## 8. Dependency Management Strategies

### 8.1 BOM-Based Versioning

BOMs are the primary mechanism for keeping related libraries in sync:

```kotlin
// Compose BOM — pins all compose.* library versions
implementation(platform("androidx.compose:compose-bom:2025.09.01"))
implementation("androidx.compose.ui:ui")           // no version
implementation("androidx.compose.material3:material3")  // no version

// Kotlin BOM — pins all kotlinx.* library versions
implementation(platform("org.jetbrains.kotlin:kotlin-bom:2.2.10"))
implementation("org.jetbrains.kotlin:kotlin-stdlib") // no version
```

### 8.2 Dependency Update Automation

**Renovate** is the most capable automated dependency update tool for Android projects. It understands `libs.versions.toml` natively and can create PRs grouped by category (Compose updates, Kotlin updates, etc.). Configure via `renovate.json`:

```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchManagers": ["gradle"],
      "groupName": "Compose BOM",
      "matchPackageNames": ["androidx.compose:compose-bom"]
    },
    {
      "matchManagers": ["gradle"],
      "groupName": "Kotlin",
      "matchPackagePatterns": ["^org.jetbrains.kotlin"]
    }
  ]
}
```

**Dependabot** supports Gradle lockfiles (since June 2025) and version catalogs. Configuration in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      compose:
        patterns: ["androidx.compose*"]
      kotlin:
        patterns: ["org.jetbrains.kotlin*"]
```

**Android Studio SDK Insights** provides built-in lint warnings for outdated dependencies, policy violations, and known CVEs from the Google SDK Index.

### 8.3 Dependency Verification

Gradle 9 supports checksum verification for all resolved dependencies:

```bash
./gradlew --write-verification-metadata sha256
```

This generates `gradle/verification-metadata.xml` with checksums, which Gradle validates on subsequent builds — providing supply-chain protection similar to `package-lock.json`.

**Avoid dynamic versions** — they cause non-reproducible builds and are incompatible with Configuration Cache and dependency verification:

```kotlin
// Never do this in production
implementation("com.example:lib:1.+")

// Always pin to exact versions
implementation("com.example:lib:1.2.3")
```

---

## 9. Compatibility Matrix

### 9.1 AGP ↔ Kotlin ↔ Gradle

| AGP | Min Gradle | Min KGP | Bundled KGP | JDK |
|---|---|---|---|---|
| 9.1.x | 9.3.1 | 2.0.0 | 2.2.10 | 17 |
| 9.0.x | 9.1.0 | 2.0.0 | 2.2.10 | 17 |
| 8.10.x | 8.11.1 | 1.9.0 | — | 17 |
| 8.7.x | 8.9 | 1.9.0 | — | 17 |

### 9.2 Reference Project Configuration (cabo-verde-pos)

The cabo-verde-pos project uses:
- **AGP:** 9.0.0
- **Kotlin:** 2.2.21
- **Gradle:** 9.2.1
- **Compose BOM:** 2024.12.01 (maps to Compose UI 1.7.x, M3 1.3.x)

To upgrade to the 2025-2026 state-of-the-art:
1. Bump Gradle to 9.3.1+ (required for AGP 9.1)
2. Bump Compose BOM to 2025.09.01+ (picks up M3 1.4.0)
3. Adopt Navigation 2.9.7 type-safe routes
4. Adopt Lifecycle 2.10.0
5. For KMP modules, migrate to `com.android.kotlin.multiplatform.library`

### 9.3 KMP Library Versions

| Library | KMP Stable Since | Platforms |
|---|---|---|
| Room | 2.7.0 (Apr 2025) | Android, iOS, JVM, macOS, Linux, WatchOS, TvOS |
| Lifecycle | 2.8.0 | Android, JVM, iOS, Native, Web |
| DataStore | 1.1.0 | Android, JVM, Web |
| Navigation | 2.10.0-alpha | Android + partial |
| WorkManager | Not planned | Android only |
| Security Crypto | Not planned | Android only |

---

## 10. Android Studio Tooling

**Android Studio Panda 3 (2025.3.3)** is the current stable. Key tooling capabilities:

- **Gemini integration** — AI-powered code completion, bug detection, and refactoring suggestions inline in the editor
- **AGP Upgrade Assistant** — wizard-guided migration from AGP 7/8 to AGP 9 with automated refactoring
- **Build Analyzer** — identifies configuration cache misses, slow tasks, and dependency bottlenecks with actionable recommendations
- **CPU and Memory Profilers** — system trace recording, jank detection, heap dump capture, native allocation tracking
- **Compose Preview** — live preview with interactive mode, multi-preview, and animation inspector
- **Layout Inspector** — live inspection of Compose semantics tree and recomposition highlights
- **Build Scans** — integration with Gradle Enterprise for detailed build performance analytics

---

## References

1. Android Gradle Plugin 9.0 Release Notes — https://developer.android.com/build/releases/past-releases/agp-9-0-0-release-notes
2. Android Gradle Plugin 9.1 Release Notes — https://developer.android.com/build/releases/gradle-plugin
3. Android Gradle Library Plugin for KMP — https://developer.android.com/kotlin/multiplatform/plugin
4. Kotlin 2.2 What's New — https://kotlinlang.org/docs/whatsnew22.html
5. Gradle 9.0 What's New — https://gradle.org/whats-new/gradle-9/
6. Gradle Release History — https://gradle.org/releases/
7. Compose BOM Mapping — https://developer.android.com/jetpack/compose/bom/bom-mapping
8. Navigation Releases — https://developer.android.com/jetpack/androidx/releases/navigation
9. Room Releases — https://developer.android.com/jetpack/androidx/releases/room
10. Lifecycle Releases — https://developer.android.com/jetpack/androidx/releases/lifecycle
11. DataStore Releases — https://developer.android.com/jetpack/androidx/releases/datastore
12. WorkManager Releases — https://developer.android.com/jetpack/androidx/releases/work
13. Security Crypto Releases — https://developer.android.com/jetpack/androidx/releases/security
14. Material 3 in Compose — https://developer.android.com/develop/ui/compose/designsystems/material3
15. Material 2 to Material 3 Migration — https://developer.android.com/develop/ui/compose/designsystems/material2-material3
16. Compose Material 3 Releases — https://developer.android.com/jetpack/androidx/releases/compose-material3
17. Gradle Version Catalogs for Android — https://developer.android.com/build/migrate-to-catalogs
18. Now in Android Version Catalog — https://github.com/android/nowinandroid/blob/main/gradle/libs.versions.toml
19. Android Studio Panda 3 — https://developer.android.com/studio/releases/
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
