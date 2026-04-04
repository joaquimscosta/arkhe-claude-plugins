---
title: "Jetpack Compose Advanced Patterns & Best Practices"
version: "1.0.0"
status: Published
created: 2026-04-04
last_updated: 2026-04-04
slug: jetpack-compose-patterns
aliases: ["compose-patterns", "jetpack-compose", "android-compose"]
tags: ["android", "jetpack-compose", "kotlin", "ui", "state-management", "navigation", "material3", "accessibility", "kmp"]
promoted_at: 2026-04-04T14:43:19.404570Z
last_refreshed: 2026-04-04T14:42:45.880611+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->

# Jetpack Compose Advanced Patterns & Best Practices

## Overview

Jetpack Compose (stable since 1.0 in 2021) has matured into the primary Android UI toolkit, with the ecosystem converging on well-understood architectural patterns. As of 2025-2026, the state of the art is defined by: type-safe navigation (Compose Navigation 2.8+), strong skipping mode (default in Kotlin 2.2+ / Compose 1.8+), MVI as the dominant event-handling pattern, Material3 with dynamic color, and Circuit/Molecule as higher-level architecture abstractions. Kotlin Multiplatform (KMP) has also elevated Compose to the cross-platform space, making navigation and state patterns increasingly important to design with portability in mind.

This document covers eight topic areas with practical Kotlin code examples, trade-off analysis, and guidance for teams using MVVM + StateFlow/SharedFlow + Compose Navigation + Material3 + Koin (a common production stack).

## 1. State Management Patterns

### 1.1 Unidirectional Data Flow (UDF) – The Foundation

All Compose state patterns are UDF variants. The core principle: **state flows down, events flow up**. A composable receives immutable state and emits typed events; it never mutates state directly.

```kotlin
// Composable is a pure function of state
@Composable
fun LoginScreen(
    state: LoginState,
    onEvent: (LoginEvent) -> Unit,
) {
    // Renders state, forwards events upward
}
```

### 1.2 MVVM with StateFlow + SharedFlow

The standard Android recommendation and the pattern used in cabo-verde-pos. `StateFlow` carries UI state; `SharedFlow` (or `Channel`) carries one-time events.

```kotlin
// --- State + Event model ---
data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: String? = null,
)

sealed interface LoginUiEvent {
    data object NavigateToHome : LoginUiEvent
    data class ShowSnackbar(val message: String) : LoginUiEvent
}

// --- ViewModel ---
@HiltViewModel // or @KoinViewModel
class LoginViewModel @Inject constructor(
    private val authRepo: AuthRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    // Channel is preferred over SharedFlow for one-shot events:
    // it buffers exactly one undelivered event and does not replay.
    private val _events = Channel<LoginUiEvent>(Channel.BUFFERED)
    val events: Flow<LoginUiEvent> = _events.receiveAsFlow()

    fun onEmailChange(value: String) {
        _uiState.update { it.copy(email = value) }
    }

    fun onLoginClick() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            authRepo.login(_uiState.value.email, _uiState.value.password)
                .onSuccess { _events.send(LoginUiEvent.NavigateToHome) }
                .onFailure { e -> _uiState.update { it.copy(error = e.message) } }
            _uiState.update { it.copy(isLoading = false) }
        }
    }
}

// --- Screen composable ---
@Composable
fun LoginRoute(
    viewModel: LoginViewModel = koinViewModel(),
    onNavigateToHome: () -> Unit,
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is LoginUiEvent.NavigateToHome -> onNavigateToHome()
                is LoginUiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }
        }
    }

    LoginScreen(state = state, onEvent = viewModel::handleEvent)
}
```

**Key decisions:**
- Separate Route (wires ViewModel) from Screen (pure composable) — the "Route/Screen split" improves testability.
- Use `Channel` over `SharedFlow` for navigation events to avoid double-delivery when the observer resubscribes.
- Use `collectAsStateWithLifecycle()` (Lifecycle 2.6+) instead of `collectAsState()` to pause collection when the app is backgrounded.

### 1.3 MVI (Model-View-Intent)

MVI tightens MVVM by making the event model explicit and processing events through a single reducer. Preferred when business logic is complex or when testability of state transitions is critical.

```kotlin
// Reducer pattern
fun reduce(state: LoginUiState, intent: LoginIntent): LoginUiState = when (intent) {
    is LoginIntent.EmailChanged -> state.copy(email = intent.value)
    is LoginIntent.PasswordChanged -> state.copy(password = intent.value)
    LoginIntent.LoginClicked -> state.copy(isLoading = true)
    is LoginIntent.LoginSuccess -> state.copy(isLoading = false)
    is LoginIntent.LoginFailed -> state.copy(isLoading = false, error = intent.message)
}
```

MVI pros: pure reducer is trivially unit-tested; time-travel debugging is possible. Cons: boilerplate for simple screens.

### 1.4 Circuit by Slack (Presenter Pattern)

Circuit introduces a first-class **Presenter** abstraction that converts events into state using a composable function. This makes the presenter natively Compose-aware — it can call `rememberCoroutineScope`, `LaunchedEffect`, etc.

```kotlin
// Circuit dependency: com.slack.circuit:circuit-foundation
@Parcelize
data object LoginScreen : Screen

data class LoginState(
    val email: String,
    val password: String,
    val isLoading: Boolean,
    val eventSink: (LoginEvent) -> Unit,
) : CircuitUiState

sealed interface LoginEvent : CircuitUiEvent {
    data class EmailChanged(val value: String) : LoginEvent
    data object LoginClicked : LoginEvent
}

class LoginPresenter @AssistedInject constructor(
    private val navigator: Navigator,
    private val authRepo: AuthRepository,
) : Presenter<LoginState> {

    @Composable
    override fun present(): LoginState {
        var email by remember { mutableStateOf("") }
        var isLoading by remember { mutableStateOf(false) }
        val scope = rememberCoroutineScope()

        return LoginState(email = email, password = "", isLoading = isLoading) { event ->
            when (event) {
                is LoginEvent.EmailChanged -> email = event.value
                LoginEvent.LoginClicked -> scope.launch {
                    isLoading = true
                    authRepo.login(email, "").onSuccess { navigator.goTo(HomeScreen) }
                    isLoading = false
                }
            }
        }
    }
}
```

Circuit's strength is that `present()` is a composable, so it uses Compose's own diffing and lifecycle — no need for a separate coroutine scope management layer.

### 1.5 Molecule by Cash App

Molecule replaces `StateFlow` + coroutines with a `@Composable` function that **is** the state computation. The Compose runtime runs the function and emits new state values as a `StateFlow` or `Flow`.

```kotlin
// Cash App Molecule: app.cash.molecule:molecule-runtime
class LoginPresenter(private val repo: AuthRepository) {
    @Composable
    fun present(events: Flow<LoginEvent>): LoginUiState {
        var email by remember { mutableStateOf("") }
        var isLoading by remember { mutableStateOf(false) }

        LaunchedEffect(Unit) {
            events.collect { event ->
                when (event) {
                    is LoginEvent.EmailChanged -> email = event.value
                    LoginEvent.LoginClicked -> {
                        isLoading = true
                        repo.login(email)
                        isLoading = false
                    }
                }
            }
        }
        return LoginUiState(email = email, isLoading = isLoading)
    }
}

// ViewModel wires it
class LoginViewModel(presenter: LoginPresenter) : ViewModel() {
    private val _events = MutableSharedFlow<LoginEvent>()
    val state: StateFlow<LoginUiState> = moleculeFlow(RecompositionClock.ContextClock) {
        presenter.present(_events)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), LoginUiState())
}
```

### 1.6 Pattern Comparison

| Pattern | Complexity | Testability | Compose-nativeness | Best for |
|---|---|---|---|---|
| MVVM + StateFlow/Channel | Low | Good | Moderate | Most apps; standard Google rec |
| MVI (reducer) | Medium | Excellent | Moderate | Complex business logic; time-travel debug |
| Circuit | Medium | Excellent | Native | Teams wanting composable presenters, KMP |
| Molecule | Medium | Excellent | Native | Replacing coroutine-heavy presenters with composables |

For a typical production app (cabo-verde-pos style): **MVVM + StateFlow + Channel** is the pragmatic default. Graduate to Circuit or Molecule when you need richer lifecycle integration or KMP compatibility.

---

## 2. Navigation (Compose Navigation 2.8+)

### 2.1 Type-Safe Routes with Kotlin Serialization

Navigation 2.8 (released Nov 2024) replaced string-based routes with `@Serializable` data classes. Routes are compile-safe, support arguments natively, and integrate with the Safe Args paradigm without a Gradle plugin.

```kotlin
// build.gradle.kts
implementation("androidx.navigation:navigation-compose:2.8.5")
implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

// Route declarations (can live in a routes/ package)
@Serializable
object HomeRoute

@Serializable
data class ProductDetailRoute(val productId: String)

@Serializable
data class OrderRoute(val orderId: Long, val showReceipt: Boolean = false)
```

```kotlin
// NavHost setup
@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(onProductClick = { id ->
                navController.navigate(ProductDetailRoute(productId = id))
            })
        }
        composable<ProductDetailRoute> { backStackEntry ->
            val route: ProductDetailRoute = backStackEntry.toRoute()
            ProductDetailScreen(
                productId = route.productId,
                onAddToCart = { navController.navigate(OrderRoute(orderId = it)) },
            )
        }
        composable<OrderRoute> { backStackEntry ->
            val route: OrderRoute = backStackEntry.toRoute()
            OrderScreen(orderId = route.orderId, showReceipt = route.showReceipt)
        }
    }
}
```

### 2.2 Nested Navigation Graphs

Group related destinations into sub-graphs. Useful for feature modules and authentication flows.

```kotlin
@Serializable object AuthGraph
@Serializable object LoginRoute
@Serializable object RegisterRoute

@Serializable object MainGraph
@Serializable object HomeRoute
@Serializable object ProfileRoute

fun NavGraphBuilder.authGraph(navController: NavHostController) {
    navigation<AuthGraph>(startDestination = LoginRoute) {
        composable<LoginRoute> { LoginScreen(onSuccess = { navController.navigate(MainGraph) }) }
        composable<RegisterRoute> { RegisterScreen() }
    }
}

fun NavGraphBuilder.mainGraph(navController: NavHostController) {
    navigation<MainGraph>(startDestination = HomeRoute) {
        composable<HomeRoute> { HomeScreen() }
        composable<ProfileRoute> { ProfileScreen() }
    }
}
```

### 2.3 Deep Linking

```kotlin
composable<ProductDetailRoute>(
    deepLinks = listOf(
        navDeepLink<ProductDetailRoute>(
            basePath = "https://example.com/products"
        )
    )
) { ... }
```

With type-safe routes, `navDeepLink<T>()` auto-generates the URL pattern from the route class fields. Declare the intent filter in `AndroidManifest.xml`:

```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" android:host="example.com" />
</intent-filter>
```

### 2.4 Back Stack Management

```kotlin
// Pop to a specific destination, removing intermediates
navController.navigate(HomeRoute) {
    popUpTo<HomeRoute> { inclusive = false }
    launchSingleTop = true
}

// Pop back with a result
navController.previousBackStackEntry
    ?.savedStateHandle
    ?.set("result", "value")
navController.popBackStack()
```

### 2.5 Multi-Module Navigation

In multi-module setups, each feature module provides a `NavGraphBuilder` extension. The app module assembles the graph:

```kotlin
// :feature:orders module
fun NavGraphBuilder.ordersGraph(navController: NavHostController) { ... }

// :app module
NavHost(navController, startDestination = HomeRoute) {
    ordersGraph(navController)
    catalogGraph(navController)
}
```

Keep route definitions in a shared `:navigation` module to avoid circular dependencies.

### 2.6 KMP Alternatives: Voyager and Decompose

| Library | Approach | KMP support | Complexity | Best for |
|---|---|---|---|---|
| Compose Navigation | Official, NavController | Android only | Low | Android-only apps |
| Voyager | Screen objects, Navigator | Yes (KMP) | Low-Medium | CMP apps wanting familiar patterns |
| Decompose | Component tree, back handler | Yes (KMP) | High | Complex back-stack, deep linking in KMP |

---

## 3. Performance Optimization

### 3.1 Understanding Recomposition

Compose skips a composable on recomposition only if all its parameters are **stable and unchanged**. A type is stable if Compose can determine whether two instances are equal without deep inspection:
- Primitive types, `String`
- `@Stable` or `@Immutable` annotated classes
- Kotlin `data class` where all fields are stable (compiler may infer this)
- Immutable Kotlin collections (`List` is NOT stable — use `ImmutableList`)

```kotlin
// Problematic: List<T> is not stable → ProfileList recomposes on every parent recompose
@Composable
fun ProfileList(profiles: List<Profile>) { ... }

// Fix option 1: wrap in @Immutable
@Immutable
data class ProfileListState(val profiles: List<Profile>)

// Fix option 2: use kotlinx.collections.immutable
@Composable
fun ProfileList(profiles: ImmutableList<Profile>) { ... }
```

### 3.2 Strong Skipping Mode (Compose 1.8+ / Kotlin 2.2+)

Strong skipping mode (enabled by default in Kotlin 2.2+ / Compose compiler 1.8+) relaxes the stability requirement: **unstable parameters are skipped by reference equality**. Lambda parameters are always considered stable.

Impact: most apps no longer need `@Stable`/`@Immutable` workarounds for data classes. However, stable annotations still help for:
- Explicit API contracts
- Classes crossing module boundaries
- `List<T>` (still unstable even with strong skipping)

Enable explicitly for older compiler versions:
```kotlin
// build.gradle.kts
composeCompiler {
    enableStrongSkippingMode = true // now default in 1.8+
}
```

### 3.3 LazyColumn / LazyGrid Optimization

```kotlin
LazyColumn {
    items(
        items = products,
        key = { product -> product.id },          // stable identity → prevents reordering re-layouts
        contentType = { product -> product.type }, // Compose reuses item compositions of the same type
    ) { product ->
        ProductCard(product = product)
    }
}
```

Use `contentType` to allow composition reuse across different item types in a mixed list.

### 3.4 derivedStateOf, remember, rememberSaveable

```kotlin
// derivedStateOf: expensive computation from state, re-runs only when inputs change
val isSubmitEnabled by remember {
    derivedStateOf { email.isNotBlank() && password.length >= 8 }
}

// remember: survive recompositions but not config changes
val coroutineScope = rememberCoroutineScope()

// rememberSaveable: survive config changes and process death (uses Bundle)
var counter by rememberSaveable { mutableIntStateOf(0) }

// rememberSaveable with custom saver for non-Parcelable types
var customState by rememberSaveable(stateSaver = customSaver) { mutableStateOf(CustomType()) }
```

### 3.5 Debugging: Layout Inspector + Composition Traces

- **Layout Inspector** (Android Studio Hedgehog+): shows recomposition counts per composable in real time. Red highlights = hot paths.
- **Composition tracing**: add `implementation("androidx.compose.runtime:runtime-tracing")` and record a Perfetto trace. Composition boundaries appear in the trace timeline.
- **Avoid creating lambdas inside composables** — they are recreated on every recomposition:

```kotlin
// Bad: new lambda instance on each recomposition
Button(onClick = { viewModel.onClick(item.id) })

// Better: remember the lambda
val onClick = remember(item.id) { { viewModel.onClick(item.id) } }
Button(onClick = onClick)
```

### 3.6 Baseline Profiles

Baseline Profiles pre-compile hot code paths, reducing startup and jank. Generate them with Macrobenchmark:

```kotlin
// Baseline profile generator
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(packageName = "com.example.app") {
        pressHome()
        startActivityAndWait()
        // Navigate critical paths
    }
}
```

Add `implementation("androidx.profileinstaller:profileinstaller:1.3.1")` to the app module so profiles are installed at app install time.

---

## 4. Accessibility

### 4.1 Semantics Tree

Every composable exposes a semantic tree used by TalkBack and accessibility services. Most Material3 components set appropriate semantics automatically.

```kotlin
// Custom content description
Image(
    painter = painterResource(R.drawable.ic_logo),
    contentDescription = stringResource(R.string.logo_description),
)

// Merge children semantics (treat a card as a single focusable unit)
Card(
    modifier = Modifier.semantics(mergeDescendants = true) {}
) {
    Text("Product name")
    Text("$9.99")
}
```

### 4.2 Custom Accessibility Actions

```kotlin
Box(
    modifier = Modifier.semantics {
        contentDescription = "Swipeable item: ${item.name}"
        customActions = listOf(
            CustomAccessibilityAction("Delete") { onDelete(item.id); true },
            CustomAccessibilityAction("Archive") { onArchive(item.id); true },
        )
    }
)
```

### 4.3 Focus Management

```kotlin
val focusRequester = remember { FocusRequester() }

TextField(
    modifier = Modifier.focusRequester(focusRequester),
    ...
)

LaunchedEffect(Unit) {
    focusRequester.requestFocus() // Auto-focus on screen entry
}

// Keyboard navigation order
Modifier.focusProperties { next = nextFocusRequester }
```

### 4.4 Screen Reader Patterns for Complex UIs

```kotlin
// Announce live data changes (e.g., cart count update)
var cartCount by remember { mutableIntStateOf(0) }
Box(
    modifier = Modifier.semantics {
        liveRegion = LiveRegionMode.Polite
        contentDescription = "Cart: $cartCount items"
    }
)

// Role for non-standard interactive elements
Modifier.semantics { role = Role.Button }

// State descriptions (better than re-reading full content description)
Modifier.semantics { stateDescription = if (isExpanded) "Expanded" else "Collapsed" }
```

### 4.5 Testing Accessibility

```kotlin
@Test
fun loginButton_hasCorrectSemantics() {
    composeTestRule.setContent { LoginScreen(...) }
    composeTestRule
        .onNodeWithContentDescription("Sign in")
        .assertHasClickAction()
        .assertIsEnabled()
}

// Verify no accessibility issues with a11y checks (Espresso Accessibility Checks)
composeTestRule.onRoot().assert(
    SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Button)
)
```

---

## 5. Theming & Design Systems

### 5.1 Material3 with Dynamic Color

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true, // Android 12+ MonetCompat
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content,
    )
}
```

### 5.2 Custom Color Schemes and Typography

```kotlin
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF006491),
    onPrimary = Color.White,
    secondary = Color(0xFF4E6479),
    surface = Color(0xFFF8F9FF),
    // ... all 29 M3 color roles
)

val AppTypography = Typography(
    headlineLarge = TextStyle(
        fontFamily = BrandFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
    ),
    // ... all 15 M3 type scale roles
)
```

### 5.3 Building a Design System on Material3

Use `CompositionLocal` to expose design tokens beyond Material3's built-in set:

```kotlin
// Custom token extensions
data class AppColorExtensions(
    val success: Color,
    val warning: Color,
    val info: Color,
)

val LocalAppColors = staticCompositionLocalOf { AppColorExtensions(...) }

// Access via MaterialTheme extension property
val MaterialTheme.appColors: AppColorExtensions
    @Composable get() = LocalAppColors.current

// Usage
Text(color = MaterialTheme.appColors.success)
```

### 5.4 MotionScheme and Animation Tokens (Material3 1.3+)

Material3 1.3 introduced `MotionScheme` — a set of `AnimationSpec` tokens matching Material's motion guidelines:

```kotlin
// Spatial transitions (enter/exit) — spring with overshoot
val enterSpec = MaterialTheme.motionScheme.fastSpatialSpec<Float>()

// Expressive effect transitions — spring without overshoot
val effectSpec = MaterialTheme.motionScheme.defaultEffectsSpec<Dp>()

AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn(animationSpec = MaterialTheme.motionScheme.fastEffectsSpec()),
    exit = fadeOut(animationSpec = MaterialTheme.motionScheme.fastEffectsSpec()),
)
```

### 5.5 Shape Theming and Elevation

```kotlin
val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(4.dp),
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large = RoundedCornerShape(16.dp),
    extraLarge = RoundedCornerShape(28.dp),
)

// Elevation with tonal color (M3 Surface uses color + elevation)
Surface(
    tonalElevation = 3.dp, // adds a tonal overlay in light mode
    shadowElevation = 1.dp,
) { ... }
```

---

## 6. Side Effects & Lifecycle

### 6.1 Effect API Summary

| Effect | Runs when | Use for |
|---|---|---|
| `LaunchedEffect(key)` | key changes (or on first composition) | Coroutines triggered by state |
| `DisposableEffect(key)` | key changes (or first); `onDispose` on leave | Register/unregister listeners |
| `SideEffect` | Every successful recomposition | Sync Compose state → non-Compose system |
| `rememberCoroutineScope` | Provides a scope tied to composition | User-initiated coroutines (button click) |
| `produceState` | On enter, cancel on leave | Convert non-Compose state sources |

```kotlin
// LaunchedEffect: load data when productId changes
LaunchedEffect(productId) {
    viewModel.loadProduct(productId)
}

// DisposableEffect: analytics screen tracking
DisposableEffect(screenName) {
    analytics.trackScreenView(screenName)
    onDispose { analytics.trackScreenLeave(screenName) }
}

// SideEffect: update system bars color
SideEffect {
    systemUiController.setStatusBarColor(color = statusBarColor)
}
```

### 6.2 collectAsStateWithLifecycle

Use `collectAsStateWithLifecycle()` (from `androidx.lifecycle:lifecycle-runtime-compose`) instead of `collectAsState()` to respect the Lifecycle and stop collecting when the app is backgrounded, saving CPU and battery:

```kotlin
// Requires: androidx.lifecycle:lifecycle-runtime-compose:2.8+
val state by viewModel.uiState.collectAsStateWithLifecycle()
// Defaults to Lifecycle.State.STARTED — pauses in background
```

### 6.3 ViewModel Scoping

```kotlin
// Activity-scoped (shared across all composables in activity)
val viewModel: SharedViewModel = viewModel()

// Navigation graph-scoped (shared within a nav graph, cleared when graph is popped)
val backStackEntry = navController.getBackStackEntry<CartGraph>()
val viewModel: CartViewModel = viewModel(backStackEntry)

// Koin-style
val viewModel: LoginViewModel = koinViewModel()
val viewModel: LoginViewModel = koinNavGraphViewModel(R.id.auth_graph)
```

### 6.4 Process Death and State Restoration

`rememberSaveable` automatically saves to the `SavedStateHandle`-backed bundle. For ViewModel state:

```kotlin
class LoginViewModel(
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    // Automatically saved/restored across process death
    val email: StateFlow<String> = savedStateHandle.getStateFlow("email", "")

    fun onEmailChange(value: String) {
        savedStateHandle["email"] = value
    }
}
```

---

## 7. Compose + ViewModel Integration

### 7.1 Route / Screen Split Pattern

The Route/Screen separation is the gold standard for testability:

```kotlin
// Route: wires ViewModel, handles navigation side effects
@Composable
fun ProductDetailRoute(
    onNavigateBack: () -> Unit,
    onNavigateToCart: () -> Unit,
    viewModel: ProductDetailViewModel = koinViewModel(),
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                ProductDetailEvent.NavigateToCart -> onNavigateToCart()
                ProductDetailEvent.NavigateBack -> onNavigateBack()
            }
        }
    }

    ProductDetailScreen(
        state = state,
        onEvent = viewModel::onEvent,
    )
}

// Screen: pure composable, fully testable without ViewModel
@Composable
fun ProductDetailScreen(
    state: ProductDetailState,
    onEvent: (ProductDetailUiEvent) -> Unit,
) { ... }
```

### 7.2 State Hoisting Best Practices

Hoist state to the **lowest common ancestor** that needs it. Avoid hoisting too high (creates unnecessary coupling) or too low (can't be shared).

```kotlin
// Stateful composable (owns state) — good for isolated UI state
@Composable
fun ExpandableCard(content: @Composable () -> Unit) {
    var expanded by rememberSaveable { mutableStateOf(false) }
    Card(modifier = Modifier.clickable { expanded = !expanded }) {
        if (expanded) content()
    }
}

// Hoisted (caller controls state) — good when parent needs to react
@Composable
fun ExpandableCard(
    expanded: Boolean,
    onExpandToggle: () -> Unit,
    content: @Composable () -> Unit,
) { ... }
```

### 7.3 Event Handling: SharedFlow vs Channel vs Lambda

| Mechanism | Delivery | When to use |
|---|---|---|
| Callback lambda | Synchronous, direct call | UI events with no async work |
| `Channel(BUFFERED)` | Exactly once, queues if no collector | Navigation, snackbar (one-shot) |
| `SharedFlow(replay=0)` | All current collectors | Multiple observers, no buffering |
| `SharedFlow(replay=1)` | Last value + new collectors | State-like events |

For cabo-verde-pos and similar apps: use **lambda callbacks** for pure UI events (text input, clicks that update local state) and **Channel** for navigation/toast events.

---

## 8. Advanced Compose Patterns

### 8.1 Slot-Based API Design

Slots (via `@Composable () -> Unit` parameters) allow callers to inject arbitrary content without coupling layout to content:

```kotlin
@Composable
fun AppScaffoldCard(
    modifier: Modifier = Modifier,
    header: @Composable () -> Unit,
    actions: (@Composable RowScope.() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    Card(modifier = modifier) {
        Column {
            Row {
                Box(Modifier.weight(1f)) { header() }
                actions?.let { Row { it() } }
            }
            Divider()
            content()
        }
    }
}

// Usage
AppScaffoldCard(
    header = { Text("Order #1234") },
    actions = { IconButton(onClick = { ... }) { Icon(Icons.Default.MoreVert, null) } },
) {
    Text("Order details...")
}
```

### 8.2 CompositionLocal: Usage and Anti-Patterns

```kotlin
// Good: truly ambient data (theme, locale, analytics context)
val LocalAnalytics = staticCompositionLocalOf<Analytics> {
    error("No Analytics provided")
}

CompositionLocalProvider(LocalAnalytics provides analytics) {
    AppContent()
}

// Anti-pattern: passing data that should be explicit parameters
// BAD: hides dependencies, makes composables harder to test
val LocalCurrentUser = compositionLocalOf<User?> { null }
```

Use `staticCompositionLocalOf` when the value rarely changes (avoids full subtree recomposition). Use `compositionLocalOf` when it changes frequently (triggers only affected composables).

### 8.3 Custom Layouts and Modifier Chains

```kotlin
// Custom layout: staggered grid
@Composable
fun StaggeredGrid(
    modifier: Modifier = Modifier,
    columns: Int = 2,
    content: @Composable () -> Unit,
) {
    Layout(content = content, modifier = modifier) { measurables, constraints ->
        val columnWidths = IntArray(columns) { constraints.maxWidth / columns }
        val columnHeights = IntArray(columns) { 0 }

        val placeables = measurables.mapIndexed { index, measurable ->
            val col = index % columns
            measurable.measure(constraints.copy(maxWidth = columnWidths[col]))
        }

        val totalHeight = columnHeights.max()
        layout(constraints.maxWidth, totalHeight) {
            placeables.forEachIndexed { index, placeable ->
                val col = index % columns
                placeable.placeRelative(
                    x = col * (constraints.maxWidth / columns),
                    y = columnHeights[col],
                )
                columnHeights[col] += placeable.height
            }
        }
    }
}
```

### 8.4 Shared Element Transitions (Compose 1.7+)

Shared element transitions animate content between two composables during navigation:

```kotlin
// In the list
SharedTransitionLayout {
    AnimatedContent(targetState = selectedProduct) { product ->
        if (product == null) {
            ProductList(
                onProductClick = { selectedProduct = it },
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this,
            )
        } else {
            ProductDetail(
                product = product,
                sharedTransitionScope = this@SharedTransitionLayout,
                animatedVisibilityScope = this,
            )
        }
    }
}

// In ProductCard
Image(
    modifier = Modifier
        .sharedElement(
            state = rememberSharedContentState(key = "product-image-${product.id}"),
            animatedVisibilityScope = animatedVisibilityScope,
        )
)
```

### 8.5 Adaptive Layouts (Window Size Classes)

```kotlin
@Composable
fun AdaptiveProductScreen(
    windowSizeClass: WindowSizeClass,
    state: ProductUiState,
) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Single pane: list OR detail
            ProductListPane(state = state)
        }
        WindowWidthSizeClass.Medium, WindowWidthSizeClass.Expanded -> {
            // Two-pane: list AND detail side by side
            Row {
                ProductListPane(modifier = Modifier.weight(1f), state = state)
                ProductDetailPane(modifier = Modifier.weight(1f), state = state)
            }
        }
    }
}
```

The `calculateWindowSizeClass()` API (from `androidx.window:window:1.3+`) provides `WindowSizeClass`. On Android, pass it from the `Activity`.

### 8.6 PausableComposition (Kotlin 2.2+ / Compose 1.8+)

`PausableComposition` allows Compose to pause and resume composition — enabling lazy loading of composable trees and better off-screen performance. This is primarily a framework-level feature used by lazy lists and `Pager`. App developers benefit automatically, but can also leverage it explicitly:

```kotlin
// Pager now uses PausableComposition internally (Compose 1.8+)
// Off-screen pages are composed but paused, reducing wasted work
HorizontalPager(pageCount = items.size) { page ->
    // This content is paused when off-screen in Compose 1.8+
    HeavyContent(item = items[page])
}
```

---

## Trade-offs & Considerations

### Choosing a State Architecture

- **MVVM + StateFlow/Channel**: The Google-recommended baseline. Familiar to Android developers, well-supported by tooling, works with Hilt and Koin. Choose this unless you have a specific reason to change.
- **MVI**: Adds reducer boilerplate but makes state transitions deterministic and purely testable. Valuable for fintech, checkout flows, complex form validation.
- **Circuit**: Best when you want composable-native presenter logic and are building for KMP. The learning curve is the Circuit-specific DI setup.
- **Molecule**: Elegant but niche — best for teams already heavily invested in Compose who want to unify state computation with Compose semantics.

### Navigation

- Use Compose Navigation 2.8+ type-safe routes for all new Android-only projects. It eliminates the entire class of runtime crashes from string route typos.
- For KMP, Voyager is the lower-friction choice; Decompose gives finer control over back stack but requires more architecture investment.

### Performance

- Strong skipping mode (Compose 1.8+) makes most `@Stable`/`@Immutable` annotations unnecessary for data classes, but does not fix `List<T>` stability. Wrap lists in `ImmutableList` or a stable wrapper data class.
- Always provide `key` lambdas in `LazyColumn` — the single highest-impact performance change for list screens.
- Measure before optimizing: use Layout Inspector recomposition counts and Perfetto composition traces to identify actual hot paths.

### Accessibility

- Material3 components handle most accessibility automatically. The primary gap is complex custom components (swipeable rows, drag handles, data visualizations).
- Always test with TalkBack on a real device — the semantic tree can be misleading in tests.

---

## References

1. [Android Developers – State and Jetpack Compose](https://developer.android.com/jetpack/compose/state) — Official state documentation, UDF principles
2. [Android Developers – Architecture: UI Layer](https://developer.android.com/topic/architecture/ui-layer) — Event/state separation, ViewModel patterns
3. [Android Developers – Navigation with Compose](https://developer.android.com/jetpack/compose/navigation) — Type-safe routes, NavHost, deep links
4. [Android Developers – Compose Performance](https://developer.android.com/jetpack/compose/performance) — Recomposition, stability, profiling
5. [Android Developers – Compose Stability Explained](https://developer.android.com/jetpack/compose/performance/stability) — @Stable, @Immutable, strong skipping
6. [Android Developers – Strong Skipping Mode](https://developer.android.com/jetpack/compose/performance/stability/strongskipping) — Default in Compose 1.8+
7. [Android Developers – Compose Accessibility](https://developer.android.com/jetpack/compose/accessibility) — Semantics, TalkBack, custom actions
8. [Android Developers – Material3 Theming](https://developer.android.com/jetpack/compose/designsystems/material3) — Color schemes, typography, shapes
9. [Android Developers – Side-effects in Compose](https://developer.android.com/jetpack/compose/side-effects) — Effect API reference
10. [Android Developers – collectAsStateWithLifecycle](https://developer.android.com/topic/libraries/architecture/coroutines#collectasstatewithlifecycle) — Lifecycle-aware Flow collection
11. [Android Developers – Shared Element Transitions](https://developer.android.com/jetpack/compose/animation/shared-elements) — SharedTransitionLayout API
12. [Android Developers – Adaptive Layouts](https://developer.android.com/guide/topics/large-screens/support-different-screen-sizes) — WindowSizeClass, two-pane layouts
13. [Android Developers – Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles) — Startup optimization, Macrobenchmark
14. [Slack Circuit](https://slackhq.github.io/circuit/) — Presenter pattern for Compose, KMP support
15. [Cash App Molecule](https://github.com/cashapp/molecule) — State as @Composable Flow, Molecule runtime
16. [Voyager](https://voyager.adriel.cafe) — KMP navigation library
17. [Decompose](https://arkivanov.github.io/Decompose/) — KMP component-based decomposition
18. [Google I/O 2024 – What's new in Jetpack Compose](https://io.google/2024/explore/session/jetpack-compose) — PausableComposition, shared elements, MotionScheme
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
