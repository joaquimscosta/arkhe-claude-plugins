---
title: "Android Testing Ecosystem: Libraries, Patterns & Strategies"
version: "1.0.0"
status: Published
created: 2026-04-04
last_updated: 2026-04-04
slug: android-testing-ecosystem
aliases: ["android-testing", "kmp-testing", "compose-testing"]
tags: ["android", "testing", "kotlin", "kmp", "compose-testing", "turbine", "kotest", "robolectric", "screenshot-testing"]
promoted_at: 2026-04-04T16:32:55.170650Z
last_refreshed: 2026-04-04T16:32:23.862166+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->

# Android Testing Ecosystem: Libraries, Patterns & Strategies

## Overview

The Android testing ecosystem in 2025-2026 has matured significantly, driven by Kotlin Multiplatform (KMP) adoption, Jetpack Compose's dominance for UI, and tooling that increasingly blurs the line between JVM and device tests. The central goal is the same as in any modern backend stack: fast feedback loops, high confidence, and maintainable test suites.

This document covers the full testing stack for Android/KMP projects -- from unit tests through screenshot regression to contract testing -- with practical Kotlin code examples throughout. It complements the `kotlin-spring-boot-testing-ecosystem.md` (backend) with Android/mobile-specific patterns.

Key version coordinates referenced throughout: JUnit 4/5, Kotest 5.9.1, Turbine 1.2.0, in-memory SQLDelight via JVM driver, Compose UI testing, and Robolectric 4.13.

---

## 1. Testing Pyramid for Android / KMP

### Recommended Ratios

```
         +------------------+
         |   E2E / UI (5%)  |   Espresso, UIAutomator, Appium
         +------------------+
         |   Integration    |   Robolectric, AndroidX Test,
         |      (20%)       |   in-process DB, MockWebServer
         +------------------+
         |   Unit (75%)     |   JUnit 5, Kotest, kotlin.test,
         +------------------+   commonTest (KMP-shared)
```

For KMP projects the pyramid gains a **horizontal layer**: `commonTest` sources are first-class and run on all targets (JVM, Android, iOS/native) -- avoid duplicating logic in `androidTest` that belongs in `commonTest`.

### Source Set Mapping

| Source Set | Runs on | Tooling |
|---|---|---|
| `commonTest` | All KMP targets | `kotlin.test`, Kotest multiplatform |
| `jvmTest` / `androidUnitTest` | JVM/Robolectric | JUnit 4/5, Kotest |
| `androidInstrumentedTest` | Device / Emulator | Espresso, Compose UI test |
| `iosTest` | iOS Simulator / device | kotlin.test, XCTest bridge |

### Guiding Principles

- Write business logic in `commonMain`; test it in `commonTest` -- never duplicate in platform tests.
- Prefer Robolectric unit tests over instrumented tests for all non-hardware features.
- Reserve instrumented tests for Compose UI, real hardware sensors, and end-to-end smoke suites.
- A test that takes more than 500 ms probably belongs in a higher tier.

---

## 2. Unit Testing Frameworks

### JUnit 5 Jupiter on Android

Android Gradle Plugin (AGP) 8.x supports JUnit 5 for **unit tests** (not instrumented) via the `android-junit5` plugin by Marcel Bro:

```kotlin
// build.gradle.kts
plugins {
    id("de.mannodermaus.android-junit5") version "1.11.0"
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.3")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.11.3")
    testImplementation("org.junit.jupiter:junit-jupiter-params:5.11.3")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

```kotlin
// JUnit 5 parameterized test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.assertEquals

class PriceCalculatorTest {

    private val calculator = PriceCalculator()

    @ParameterizedTest
    @CsvSource("100.0, 0.2, 80.0", "200.0, 0.1, 180.0", "50.0, 0.5, 25.0")
    fun `apply discount returns correct net price`(
        base: Double, discount: Double, expected: Double
    ) {
        assertEquals(expected, calculator.applyDiscount(base, discount))
    }
}
```

### JUnit 4 Migration Path

Projects still on JUnit 4: Kotest 5 runs on top of JUnit 4 via the `junit-vintage-engine`. Incremental migration approach:

1. Keep existing `@Test` + `@Rule` tests under `junit-vintage-engine`.
2. Add JUnit 5 for all new tests going forward.
3. Replace `@RunWith(MockitoJUnitRunner)` with `@ExtendWith(MockitoExtension)`.

```kotlin
// JUnit 4 (legacy pattern)
@RunWith(MockitoJUnitRunner::class)
class OldUserServiceTest {
    @Mock lateinit var repo: UserRepository
    @Test fun `fetch user returns entity`() { /* ... */ }
}

// JUnit 5 equivalent
@ExtendWith(MockitoExtension::class)
class UserServiceTest {
    @Mock lateinit var repo: UserRepository
    @Test fun `fetch user returns entity`() { /* ... */ }
}
```

### kotlin.test for KMP (commonTest)

`kotlin.test` is the stdlib multiplatform test API. It maps to JUnit 4/5 on JVM, XCTest on iOS:

```kotlin
// commonTest -- compiles and runs on ALL targets
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class MoneyTest {
    @Test
    fun `adding two amounts returns correct sum`() {
        val result = Money(10.0, "EUR") + Money(5.0, "EUR")
        assertEquals(Money(15.0, "EUR"), result)
    }

    @Test
    fun `cannot add different currencies throws exception`() {
        val ex = assertFailsWith<CurrencyMismatchException> {
            Money(10.0, "EUR") + Money(5.0, "USD")
        }
        assertTrue(ex.message!!.contains("EUR"))
    }
}
```

---

## 3. Assertion Libraries

### Comparison Table

| Library | Style | KMP | Fluent | Soft Assertions | Notes |
|---|---|---|---|---|---|
| **kotlin.test** | Standard | Yes | No | No | Zero deps, commonTest first choice |
| **Kotest Assertions** | Infix/fluent | Yes (partial) | Yes | Yes (assertSoftly) | Richest Android/KMP option |
| **Truth** | Fluent | No (JVM) | Yes | No | Google-backed, strong Android support |
| **AssertJ** | Fluent | No (JVM) | Yes | Yes (SoftAssertions) | Java-origin, verbose in Kotlin |
| **Strikt** | Infix | No (JVM) | Yes | Yes (expectThat blocks) | Kotlin-first, type-safe chains |

### Kotest Assertions (Recommended for Android/KMP)

```kotlin
// build.gradle.kts
testImplementation("io.kotest:kotest-assertions-core:5.9.1")
```

```kotlin
import io.kotest.matchers.shouldBe
import io.kotest.matchers.collections.shouldContainExactly
import io.kotest.matchers.string.shouldStartWith
import io.kotest.assertions.assertSoftly

class CartTest {
    @Test
    fun `cart contains correct items after add`() {
        val cart = Cart()
        cart.add(Item("apple", 1.5))
        cart.add(Item("bread", 2.0))

        assertSoftly(cart) {
            items.size shouldBe 2
            total shouldBe 3.5
            items.map { it.name } shouldContainExactly listOf("apple", "bread")
        }
    }
}
```

### Truth (Android-instrumented / Google stack)

```kotlin
import com.google.common.truth.Truth.assertThat

@Test
fun `product list is not empty`() {
    val products = repository.getAll()
    assertThat(products).isNotEmpty()
    assertThat(products.first().name).isEqualTo("Widget")
}
```

### Strikt (type-safe chains, JVM)

```kotlin
import strikt.api.expectThat
import strikt.assertions.*

@Test
fun `invoice has correct line items`() {
    val invoice = Invoice.of(order)
    expectThat(invoice) {
        get { lineItems }.hasSize(3)
        get { total }.isGreaterThan(BigDecimal.ZERO)
        get { status } isEqualTo InvoiceStatus.DRAFT
    }
}
```

---

## 4. Compose UI Testing

### Setup

```kotlin
// build.gradle.kts (Android module)
androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.7.x")
debugImplementation("androidx.compose.ui:ui-test-manifest:1.7.x")
```

### ComposeTestRule Basics

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `login button is disabled when fields are empty`() {
        composeTestRule.setContent {
            LoginScreen(onLogin = {})
        }

        composeTestRule.onNodeWithText("Sign In")
            .assertIsDisplayed()
            .assertIsNotEnabled()
    }

    @Test
    fun `entering credentials enables login button`() {
        composeTestRule.setContent {
            LoginScreen(onLogin = {})
        }

        composeTestRule.onNodeWithContentDescription("Email field")
            .performTextInput("user@example.com")
        composeTestRule.onNodeWithContentDescription("Password field")
            .performTextInput("secret123")

        composeTestRule.onNodeWithText("Sign In")
            .assertIsEnabled()
    }
}
```

### Semantic Matching Best Practice

Prefer `testTag` and `contentDescription` over text matching -- text changes break tests, semantics are stable:

```kotlin
// In Composable
Button(
    onClick = onSubmit,
    modifier = Modifier.semantics { testTag = "submit_button" }
) {
    Text("Submit Order")
}

// In test
composeTestRule.onNodeWithTag("submit_button")
    .assertIsEnabled()
    .performClick()

composeTestRule.onNodeWithTag("confirmation_dialog")
    .assertIsDisplayed()
```

### Navigation Testing

```kotlin
@Test
fun `clicking product navigates to detail screen`() {
    val navController = TestNavHostController(
        ApplicationProvider.getApplicationContext()
    )

    composeTestRule.setContent {
        AppNavHost(navController = navController)
    }

    composeTestRule.onNodeWithTag("product_item_42").performClick()

    composeTestRule.runOnIdle {
        assertThat(navController.currentBackStackEntry?.destination?.route)
            .isEqualTo("product_detail/{id}")
    }
}
```

### Accessibility Testing via Semantics

```kotlin
@Test
fun `product image has content description for screen readers`() {
    composeTestRule.setContent {
        ProductCard(product = sampleProduct)
    }

    composeTestRule
        .onNodeWithContentDescription("Product image: ${sampleProduct.name}")
        .assertExists()
}

@Test
fun `all interactive elements are focusable`() {
    composeTestRule.setContent { CheckoutSummary(order = sampleOrder) }

    // Print semantic tree to logs for inspection
    composeTestRule.onRoot().printToLog("A11Y_TREE")

    composeTestRule.onNodeWithContentDescription("Total price")
        .assertIsDisplayed()
    composeTestRule.onNodeWithText("Confirm Purchase")
        .assertHasClickAction()
}
```

### Screenshot Testing

Three tools -- choose based on speed vs fidelity requirements:

| Tool | Renderer | Speed | CI Friendly | KMP Support |
|---|---|---|---|---|
| **Roborazzi** | Robolectric | Fast (JVM) | Yes | Partial |
| **Paparazzi** | LayoutLib | Fast (JVM) | Yes | No |
| **Compose Preview Screenshot** | AGP plugin | Medium | Yes | No |

#### Roborazzi (recommended for Compose)

```kotlin
// build.gradle.kts
testImplementation("io.github.takahirom.roborazzi:roborazzi:1.13.0")
testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.13.0")
testImplementation("org.robolectric:robolectric:4.13")

android {
    testOptions {
        unitTests { isIncludeAndroidResources = true }
    }
}
```

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ProductCardScreenshotTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `product card matches snapshot`() {
        composeTestRule.setContent {
            MaterialTheme {
                ProductCard(product = Product("Widget", 9.99, inStock = true))
            }
        }

        composeTestRule.onRoot()
            .captureRoboImage("snapshots/product_card.png")
    }
}
```

#### Paparazzi (View-based / mixed)

```kotlin
@RunWith(JUnit4::class)
class ButtonSnapshotTest {

    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_6,
        theme = "android:Theme.Material3.DayNight"
    )

    @Test
    fun `primary button snapshot`() {
        paparazzi.snapshot {
            PrimaryButton(text = "Buy Now", onClick = {})
        }
    }
}
```

---

## 5. KMP Shared Module Testing

### commonTest Setup

```kotlin
// shared/build.gradle.kts
kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()
    jvm()

    sourceSets {
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation("io.kotest:kotest-assertions-core:5.9.1")
            implementation("app.cash.turbine:turbine:1.2.0")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
        }
        androidUnitTest.dependencies {
            implementation("io.kotest:kotest-runner-junit4:5.9.1")
            implementation("org.robolectric:robolectric:4.13")
        }
    }
}
```

### expect/actual for Test Utilities

```kotlin
// commonTest/TestDispatcherProvider.kt
expect fun createTestDispatcher(): TestCoroutineDispatcher

// androidUnitTest/TestDispatcherProvider.android.kt
actual fun createTestDispatcher(): TestCoroutineDispatcher =
    StandardTestDispatcher()

// iosTest/TestDispatcherProvider.ios.kt
actual fun createTestDispatcher(): TestCoroutineDispatcher =
    StandardTestDispatcher()
```

### Shared Test Fixtures

```kotlin
// commonTest/fixtures/TestFixtures.kt
object TestFixtures {
    val sampleUser = User(
        id = UserId("usr-001"),
        name = "Ada Lovelace",
        email = Email("ada@example.com")
    )

    val sampleProduct = Product(
        id = ProductId("prod-001"),
        name = "Widget Pro",
        price = Money(29.99, Currency.EUR),
        stock = 50
    )
}

// Usage in any target test
class UserRepositoryTest {
    @Test
    fun `find by id returns correct user`() = runTest {
        repo.save(TestFixtures.sampleUser)
        val found = repo.findById(UserId("usr-001"))
        found shouldBe TestFixtures.sampleUser
    }
}
```

---

## 6. Flow & Coroutine Testing

### runTest and TestDispatcher

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*

@OptIn(ExperimentalCoroutinesApi::class)
class OrderServiceTest {

    private val testDispatcher = UnconfinedTestDispatcher()

    @BeforeEach
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @AfterEach
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `place order returns success result`() = runTest {
        val service = OrderService(
            repo = fakeRepo,
            dispatcher = testDispatcher
        )
        val result = service.placeOrder(TestFixtures.sampleOrder)
        result shouldBe OrderResult.Success
    }
}
```

### Reusable MainDispatcherRule

```kotlin
// Reusable rule for JUnit 4 / JUnit 5 compatible via TestWatcher
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Turbine for Flow Testing

Turbine is the standard library for testing `Flow` emissions:

```kotlin
import app.cash.turbine.test
import app.cash.turbine.turbineScope

// Testing a single flow
@Test
fun `search emits loading then results`() = runTest {
    val viewModel = SearchViewModel(searchUseCase = fakeUseCase)

    viewModel.uiState.test {
        awaitItem() shouldBe SearchState.Idle

        viewModel.search("kotlin")

        awaitItem() shouldBe SearchState.Loading
        val results = awaitItem()
        results.shouldBeInstanceOf<SearchState.Success>()
        (results as SearchState.Success).items.size shouldBe 3

        cancelAndIgnoreRemainingEvents()
    }
}

// Testing multiple flows simultaneously
@Test
fun `cart updates propagate to checkout readiness`() = runTest {
    turbineScope {
        val cartFlow = cart.items.testIn(this)
        val checkoutFlow = checkout.isReady.testIn(this)

        cartFlow.awaitItem()  // initial empty state
        cart.add(TestFixtures.sampleProduct)
        cartFlow.awaitItem().size shouldBe 1
        checkoutFlow.awaitItem() shouldBe true
    }
}
```

### ViewModel StateFlow Testing

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class ProductListViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: ProductListViewModel

    @Before
    fun setup() {
        viewModel = ProductListViewModel(fakeProductRepository)
    }

    @Test
    fun `initial load transitions from Loading to Success`() = runTest {
        viewModel.uiState.test {
            awaitItem() shouldBe ProductListState.Loading
            val loaded = awaitItem()
            loaded.shouldBeInstanceOf<ProductListState.Success>()
            (loaded as ProductListState.Success).products.isNotEmpty() shouldBe true
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Forgetting `Dispatchers.setMain` | Tests hang or miss emissions | Use `MainDispatcherRule` |
| `StandardTestDispatcher` without `advanceUntilIdle()` | Emissions never arrive | Call `testScheduler.advanceUntilIdle()` |
| Not cancelling Turbine | Test timeouts on subsequent emissions | Always `cancelAndIgnoreRemainingEvents()` |
| `runBlocking` in coroutine tests | Deadlocks with `Dispatchers.Main` | Use `runTest` instead |
| Testing `SharedFlow` without subscribers | Emissions silently dropped | Use `SharingStarted.Eagerly` in tests |
| `UnconfinedTestDispatcher` for time-sensitive tests | Time not controlled | Switch to `StandardTestDispatcher` |

---

## 7. Integration Testing

### Robolectric vs Instrumented Tests

| Dimension | Robolectric | Instrumented (Device/Emulator) |
|---|---|---|
| Speed | ~100-500 ms/test | 2-10 s/test + emulator boot |
| Fidelity | Good (shadows) | Exact Android behavior |
| CI cost | Low (JVM only) | High (emulator required) |
| Compose support | Yes (via Roborazzi) | Full |
| Hardware access | No | Yes |
| Best for | Unit + shallow integration | Compose UI, real device behavior |

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34], application = TestApplication::class)
class UserDaoRobolectricTest {

    private lateinit var db: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        userDao = db.userDao()
    }

    @After
    fun tearDown() = db.close()

    @Test
    fun `insert and retrieve user by id`() = runTest {
        val user = UserEntity(id = 1, name = "Test User", email = "test@example.com")
        userDao.insert(user)
        val found = userDao.findById(1)
        assertThat(found).isEqualTo(user)
    }
}
```

### Koin Test Modules

```kotlin
// test/di/TestModules.kt
val testNetworkModule = module {
    single<HttpClient> { createMockHttpClient() }
}

val testDatabaseModule = module {
    single<SqlDriver> {
        JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also { driver ->
            AppDatabase.Schema.create(driver)
        }
    }
}

// In test class
@RunWith(AndroidJUnit4::class)
class CartIntegrationTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(testDatabaseModule, testNetworkModule, cartModule)
    }

    private val cartRepository: CartRepository by inject()

    @Test
    fun `add item persists correctly`() = runTest {
        cartRepository.addItem(TestFixtures.sampleProduct, quantity = 2)
        val items = cartRepository.getItems()
        items.size shouldBe 1
        items.first().quantity shouldBe 2
    }
}
```

---

## 8. Database Testing

### In-Memory SQLDelight (JVM Driver)

For KMP projects sharing SQL schemas, the JDBC driver enables fast in-memory tests without Android:

```kotlin
// build.gradle.kts (shared module, jvmTest / androidUnitTest)
testImplementation("app.cash.sqldelight:sqlite-driver:2.0.2")

// Factory function
fun createInMemoryDriver(): SqlDriver =
    JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also { driver ->
        AppDatabase.Schema.create(driver)
    }
```

```kotlin
class ProductDatabaseTest {

    private val driver = createInMemoryDriver()
    private val db = AppDatabase(driver)
    private val queries = db.productQueries

    @AfterTest
    fun tearDown() = driver.close()

    @Test
    fun `insert and select product by id`() {
        queries.insertProduct(id = "p1", name = "Widget", price = 9.99, stock = 100)
        val product = queries.selectById("p1").executeAsOne()

        product.name shouldBe "Widget"
        product.price shouldBe 9.99
        product.stock shouldBe 100
    }

    @Test
    fun `delete product removes from results`() {
        queries.insertProduct("p1", "Widget", 9.99, 100)
        queries.deleteProduct("p1")
        val result = queries.selectById("p1").executeAsOneOrNull()
        result shouldBe null
    }

    @Test
    fun `transaction rolls back on failure`() {
        assertFailsWith<Exception> {
            db.transaction {
                queries.insertProduct("p2", "Gadget", 19.99, 10)
                throw RuntimeException("Simulated failure")
            }
        }
        queries.selectById("p2").executeAsOneOrNull() shouldBe null
    }
}
```

### Room In-Memory Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class OrderDaoTest {

    private lateinit var db: OrderDatabase
    private lateinit var orderDao: OrderDao

    @Before
    fun setup() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            OrderDatabase::class.java
        ).build()
        orderDao = db.orderDao()
    }

    @After
    fun tearDown() = db.close()

    @Test
    fun `insert order and observe via flow`() = runTest {
        val order = OrderEntity(id = 1, total = 99.50, status = "PENDING")
        orderDao.insert(order)

        val orders = orderDao.getAll().first()
        orders shouldContain order
    }
}
```

### Migration Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class DatabaseMigrationTest {

    private val TEST_DB = "migration_test"

    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun `migrate from version 1 to 2 preserves data`() {
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO orders VALUES (1, 50.0, 'PENDING')")
            close()
        }

        val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        db.query("SELECT status FROM orders WHERE id = 1").use { cursor ->
            cursor.moveToFirst()
            assertThat(cursor.getString(0)).isEqualTo("PENDING")
        }
    }
}
```

---

## 9. Network Testing

### Ktor MockEngine (KMP-friendly)

`MockEngine` intercepts all Ktor client calls and works in `commonTest` / `jvmTest`:

```kotlin
// commonTest or androidUnitTest
class ProductApiClientTest {

    @Test
    fun `getProduct returns parsed product on 200`() = runTest {
        val mockEngine = MockEngine { request ->
            when (request.url.encodedPath) {
                "/api/products/p1" -> respond(
                    content = """{"id":"p1","name":"Widget","price":9.99}""",
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
                else -> respondError(HttpStatusCode.NotFound)
            }
        }

        val client = ProductApiClient(
            HttpClient(mockEngine) {
                install(ContentNegotiation) { json() }
            }
        )

        val product = client.getProduct("p1")
        product.name shouldBe "Widget"
        product.price shouldBe 9.99
    }

    @Test
    fun `getProduct throws domain exception on 404`() = runTest {
        val mockEngine = MockEngine { respondError(HttpStatusCode.NotFound) }
        val client = ProductApiClient(HttpClient(mockEngine))

        assertFailsWith<ProductNotFoundException> {
            client.getProduct("missing")
        }
    }
}
```

### OkHttp MockWebServer (OkHttp/Retrofit projects)

```kotlin
class RetrofitOrderApiTest {

    private val mockWebServer = MockWebServer()

    @Before fun start() = mockWebServer.start()
    @After fun shutdown() = mockWebServer.shutdown()

    @Test
    fun `fetch orders returns deserialized list`() = runTest {
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody("""[{"id":1,"status":"PENDING"},{"id":2,"status":"SHIPPED"}]""")
                .addHeader("Content-Type", "application/json")
        )

        val api = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(OrderApi::class.java)

        val orders = api.getOrders()
        orders.size shouldBe 2
        orders.first().status shouldBe "PENDING"

        val recorded = mockWebServer.takeRequest()
        recorded.path shouldBe "/orders"
        recorded.method shouldBe "GET"
    }
}
```

### WireMock for Complex Stubbing

```kotlin
@RunWith(AndroidJUnit4::class)
class PaymentGatewayIntegrationTest {

    @get:Rule
    val wireMock = WireMockRule(wireMockConfig().dynamicPort())

    @Test
    fun `charge returns transaction id on success`() {
        wireMock.stubFor(
            post(urlEqualTo("/payments/charge"))
                .withRequestBody(matchingJsonPath("$.amount", equalTo("50.00")))
                .willReturn(
                    okJson("""{"transactionId":"txn-123","status":"APPROVED"}""")
                )
        )

        val gateway = PaymentGateway(baseUrl = "http://localhost:${wireMock.port()}")
        val result = gateway.charge(amount = "50.00")

        result.transactionId shouldBe "txn-123"
        wireMock.verify(postRequestedFor(urlEqualTo("/payments/charge")))
    }
}
```

### Pact Consumer-Driven Contract Testing

For microservice integrations where both consumer (app) and provider (API) are tested:

```kotlin
// Consumer side -- Android app
@ExtendWith(PactConsumerTestExt::class)
@PactTestFor(providerName = "ProductService", port = "8080")
class ProductContractTest {

    @Pact(consumer = "AndroidApp")
    fun getProductPact(builder: PactDslWithProvider): RequestResponsePact =
        builder
            .given("product p1 exists")
            .uponReceiving("GET /products/p1")
            .path("/products/p1")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(
                PactDslJsonBody()
                    .stringType("id", "p1")
                    .stringType("name", "Widget")
                    .numberType("price", 9.99)
            )
            .toPact()

    @Test
    @PactTestFor(pactMethod = "getProductPact")
    fun `consumer can parse product response`(mockServer: MockServer) = runTest {
        val client = ProductApiClient(baseUrl = mockServer.getUrl())
        val product = client.getProduct("p1")
        product.id shouldBe "p1"
        product.name shouldBe "Widget"
    }
}
```

---

## 10. Advanced Patterns

### Property-Based Testing with Kotest

```kotlin
import io.kotest.core.spec.style.StringSpec
import io.kotest.property.Arb
import io.kotest.property.arbitrary.*
import io.kotest.property.checkAll
import io.kotest.matchers.doubles.between

class MoneyPropertyTest : StringSpec({

    "adding money is commutative" {
        checkAll(
            Arb.double(0.01, 1000.0),
            Arb.double(0.01, 1000.0)
        ) { a, b ->
            val moneyA = Money(a, Currency.EUR)
            val moneyB = Money(b, Currency.EUR)
            (moneyA + moneyB) shouldBe (moneyB + moneyA)
        }
    }

    "discount result is between zero and original price" {
        checkAll(
            Arb.double(1.0, 1000.0),
            Arb.double(0.0, 1.0)
        ) { price, discount ->
            val result = Money(price, Currency.EUR).applyDiscount(discount)
            result.amount shouldBe between(0.0, price)
        }
    }

    "custom arbitrary for domain objects" {
        val arbProduct = Arb.bind(
            Arb.string(3..50),
            Arb.double(0.01, 9999.99),
            Arb.int(0..1000)
        ) { name, price, stock ->
            Product(name, price, stock)
        }

        checkAll(arbProduct) { product ->
            product.isAvailable() shouldBe (product.stock > 0)
        }
    }
})
```

### Mutation Testing with Pitest

Applies to Android JVM unit tests only (not instrumented):

```kotlin
// build.gradle.kts
plugins {
    id("info.solidsoft.pitest") version "1.15.0"
}

pitest {
    targetClasses.set(setOf("com.example.app.domain.*"))
    excludedClasses.set(setOf("com.example.app.domain.*Test*"))
    mutators.set(setOf("STRONGER"))
    outputFormats.set(setOf("HTML", "XML"))
    failWhenNoMutations.set(false)
    junit5PluginVersion.set("1.2.1")
    mutationThreshold.set(80)  // Fail build if < 80% mutations killed
    coverageThreshold.set(70)
}
```

Run with `./gradlew pitest` -- reports generated at `build/reports/pitest/`.

### Test Coverage with Kover

```kotlin
// root build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.8.3"
}

kover {
    reports {
        filters {
            excludes {
                classes("*.*_Impl", "*.di.*", "*.*Activity", "*.*Fragment")
                packages("com.example.generated")
            }
        }
        verify {
            rule("Line coverage threshold") {
                bound {
                    minValue = 70
                    metric = CoverageUnit.LINE
                }
            }
        }
    }
}
```

```bash
# Generate HTML report
./gradlew koverHtmlReport

# CI gate -- fails if coverage drops below threshold
./gradlew koverVerify
```

### Flaky Test Detection in CI

```yaml
# .github/workflows/android-test.yml
- name: Run unit tests with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: ./gradlew testDebugUnitTest

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: "**/build/test-results/**/*.xml"
```

### Recommended CI Job Structure

```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew testDebugUnitTest koverXmlReport
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  screenshot-tests:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew verifyRoborazziDebug   # or paparazziTest

  instrumented-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          script: ./gradlew connectedDebugAndroidTest
```

---

## 11. cabo-verde-pos Reference Setup

Configuration extracted from a real KMP project using JUnit 4, Kotest 5.9.1, Turbine 1.2.0, and in-memory SQLDelight:

```kotlin
// shared/build.gradle.kts -- version catalog excerpt
val kotestVersion = "5.9.1"
val turbineVersion = "1.2.0"
val coroutinesVersion = "1.8.1"
val sqlDelightVersion = "2.0.2"

sourceSets {
    commonTest.dependencies {
        implementation(kotlin("test"))
        implementation("io.kotest:kotest-assertions-core:$kotestVersion")
        implementation("app.cash.turbine:turbine:$turbineVersion")
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:$coroutinesVersion")
    }
    androidUnitTest.dependencies {
        implementation("io.kotest:kotest-runner-junit4:$kotestVersion")
        implementation("org.robolectric:robolectric:4.13")
        implementation("app.cash.sqldelight:sqlite-driver:$sqlDelightVersion")
    }
}
```

In-memory SQLDelight JVM driver pattern used across the project:

```kotlin
// androidUnitTest/helpers/DatabaseTestHelper.kt
fun createInMemoryPosDatabase(): Pair<SqlDriver, PosDatabase> {
    val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    PosDatabase.Schema.create(driver)
    return driver to PosDatabase(driver)
}

// Example usage in a POS transaction test
class PosTransactionRepositoryTest {

    private val (driver, db) = createInMemoryPosDatabase()
    private val repo = TransactionRepository(db.transactionQueries)

    @AfterTest
    fun tearDown() = driver.close()

    @Test
    fun `record sale creates transaction with correct total`() = runTest {
        val saleItems = listOf(
            SaleItem("prod-1", qty = 2, unitPrice = 5.0),
            SaleItem("prod-2", qty = 1, unitPrice = 10.0)
        )
        repo.recordSale(saleItems, paymentMethod = PaymentMethod.CASH)

        val txns = repo.getAll()
        txns.size shouldBe 1
        txns.first().total shouldBe 20.0
        txns.first().paymentMethod shouldBe PaymentMethod.CASH
    }

    @Test
    fun `void transaction marks as cancelled`() = runTest {
        repo.recordSale(
            listOf(SaleItem("prod-1", qty = 1, unitPrice = 15.0)),
            PaymentMethod.CARD
        )
        val txnId = repo.getAll().first().id
        repo.voidTransaction(txnId)

        repo.findById(txnId)!!.status shouldBe TransactionStatus.CANCELLED
    }
}
```

Turbine pattern for POS state machine testing:

```kotlin
class PosSessionViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val viewModel = PosSessionViewModel(fakeTransactionRepo, fakeProductRepo)

    @Test
    fun `scanning product adds to active sale`() = runTest {
        viewModel.saleState.test {
            awaitItem() shouldBe SaleState.Empty

            viewModel.scanBarcode("prod-001")

            val updated = awaitItem()
            updated.shouldBeInstanceOf<SaleState.Active>()
            (updated as SaleState.Active).items.size shouldBe 1

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## Trade-offs & Considerations

### Tool Selection Guide

| Scenario | Recommended Tool |
|---|---|
| Pure Kotlin logic, no Android deps | `kotlin.test` in `commonTest` |
| Domain layer with rich assertions | Kotest assertions + `assertSoftly` |
| Testing Flows / StateFlow / SharedFlow | Turbine + `runTest` |
| Compose UI interaction | ComposeTestRule + Espresso |
| Compose snapshot regression | Roborazzi |
| View-based snapshot regression | Paparazzi |
| KMP API client testing | Ktor MockEngine |
| OkHttp/Retrofit client testing | MockWebServer |
| Advanced stub + verification | WireMock |
| Microservice contract testing | Pact |
| Database (KMP/shared) | SQLDelight JVM in-memory driver |
| Database (Android Room) | Room in-memory builder |
| Property-based testing | Kotest Property Testing |
| Mutation testing | Pitest (unit tests only) |
| Coverage gating | Kover |

### When NOT to Use

- **Espresso on CI without emulator**: Use Robolectric for non-hardware UI tests.
- **Pitest on instrumented tests**: Pitest works on JVM unit tests only.
- **Paparazzi for Compose-only apps**: Roborazzi is more actively maintained and Compose-native.
- **WireMock in commonTest**: Use Ktor MockEngine (JVM/native compatible) instead.
- **`runBlocking` in coroutine tests**: Use `runTest` to avoid deadlocks with `Dispatchers.Main`.
- **`UnconfinedTestDispatcher` when testing time**: Use `StandardTestDispatcher` + `advanceUntilIdle()`.

---

## References

1. [Android Testing Documentation](https://developer.android.com/training/testing) -- Official guide covering Espresso, JUnit, AndroidX Test
2. [Compose Testing Guide](https://developer.android.com/jetpack/compose/testing) -- Semantic matching, ComposeTestRule, accessibility
3. [Kotlin Multiplatform Testing](https://kotlinlang.org/docs/multiplatform-run-tests.html) -- commonTest, expect/actual, target configuration
4. [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/) -- Jupiter API, extensions, parameterized tests
5. [android-junit5 Plugin](https://github.com/mannodermaus/android-junit5) -- JUnit 5 for Android unit tests by Marcel Bro
6. [Kotest Documentation](https://kotest.io/docs/framework/testing-styles.html) -- Testing styles, property testing, assertion matchers
7. [Turbine GitHub](https://github.com/cashapp/turbine) -- Flow testing library by Cash App
8. [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) -- TestDispatcher, runTest, advanceUntilIdle
9. [Robolectric](https://robolectric.org/) -- JVM-based Android unit testing with device simulation via shadows
10. [Roborazzi](https://github.com/takahirom/roborazzi) -- JVM screenshot testing for Compose and View
11. [Paparazzi](https://github.com/cashapp/paparazzi) -- Offline screenshot testing by Cash App
12. [Compose Preview Screenshot Testing](https://developer.android.com/studio/preview/compose-screenshot-testing) -- AGP-integrated screenshot testing tool
13. [OkHttp MockWebServer](https://github.com/square/okhttp/tree/master/mockwebserver) -- HTTP server for testing OkHttp/Retrofit clients
14. [Ktor Client Testing](https://ktor.io/docs/client-testing.html) -- MockEngine for KMP HTTP client testing
15. [WireMock for Android](https://wiremock.org/docs/android/) -- Advanced HTTP stubbing and request verification
16. [SQLDelight Testing](https://cashapp.github.io/sqldelight/2.x/android_sqlite/) -- JVM driver, in-memory databases, schema management
17. [Kover](https://github.com/Kotlin/kotlinx-kover) -- Kotlin code coverage with Gradle integration and verification rules
18. [Pitest](https://pitest.org/) -- Mutation testing for JVM languages
19. [Pact](https://docs.pact.io/) -- Consumer-driven contract testing framework
20. [Kotest Property Testing](https://kotest.io/docs/proptest/property-based-testing.html) -- Arb generators, checkAll, automatic shrinking
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
