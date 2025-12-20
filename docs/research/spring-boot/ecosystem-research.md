# **Spring Boot 4 and Spring Framework 7: A Comprehensive Ecosystem Research Dossier**

## **Executive Summary**

The transition to Spring Boot 4 and Spring Framework 7 represents the most significant architectural inflection point in the Java ecosystem since the release of Spring Boot 2.0. This generation of the framework is not merely an iterative update; it is a fundamental re-platforming designed to leverage the modern capabilities of the Java Virtual Machine (JVM), specifically targeting Java 17 as a strict baseline while optimizing for Java 21 and the forthcoming Java 25\.1

The architectural philosophy of Spring Boot 4 is defined by three primary forcing functions: the adoption of Project Loom (Virtual Threads) as a first-class citizen, which challenges the decade-long necessity of Reactive programming for standard I/O-bound workloads; the rigorous standardization of null-safety via JSpecify, which bridges the interoperability gap between Java and Kotlin 3; and the complete alignment with Jakarta EE 11, necessitating upgrades to Servlet 6.1, JPA 3.2, and Hibernate 7\.1

Furthermore, this release cycle institutionalizes the "modular monolith" as a default architectural pattern through the deep integration of Spring Modulith 2.0. This signals a strategic move away from the premature optimization of microservices toward verifyable, structured monoliths that can be decomposed only when necessary.6 The ecosystem also embraces a major breaking change in JSON processing by adopting Jackson 3, which introduces a new package namespace (tools.jackson), signaling a clear break from legacy technical debt.7

This dossier provides an exhaustive analysis of these changes, dissecting the subsystems of Web, Data, Security, Observability, and Testing. It provides evidence-based guidance for backend architects to navigate migration, leverage new paradigms, and avoid significant pitfalls associated with this transition.

## ---

**1\. Ecosystem Baseline and Compatibility Map**

Understanding the dependency matrix is critical for platform engineering teams preparing for the upgrade. Spring Boot 4.0 functions as a strict bill-of-materials (BOM) orchestrator for a wide array of upgraded transitive dependencies. The shift requires a synchronized upgrade of the underlying JDK, build tools, and container runtime environments.

### **1.1 Core Dependency Matrix**

| Component | Spring Boot 3.x Baseline | Spring Boot 4.0 Baseline | Architectural Implication |
| :---- | :---- | :---- | :---- |
| **Java SDK** | Java 17 | **Java 17 (Min), Java 25 (Rec)** | Enables access to Foreign Function & Memory APIs and strict encapsulation.1 |
| **Spring Framework** | 6.x | **7.0** | Native Virtual Thread integration, JSpecify Null-safety, and Reflection-free AOT optimizations.9 |
| **Kotlin** | 1.9+ | **2.2 (K2 Compiler)** | Strict null-safety translation, faster compilation, and removal of "platform type" ambiguity.10 |
| **Jakarta EE** | EE 10 | **EE 11** | Mandatory upgrade to Servlet 6.1, Concurrency 3.1, and Bean Validation 3.1.1 |
| **Persistence** | Hibernate 6.x | **Hibernate 7.0 / JPA 3.2** | Introduction of Jakarta Data integration and Stateless Session improvements.5 |
| **JSON Processing** | Jackson 2.x (com.fasterxml) | **Jackson 3.x (tools.jackson)** | **Breaking Change:** Namespace migration required; immutable configuration via JsonMapper.8 |
| **Security** | Spring Security 6.x | **Spring Security 7.0** | Complete removal of legacy chain APIs; mandatory Lambda DSL for configuration.11 |
| **Testing** | JUnit 5 / Mockito 5 | **JUnit 6 / Mockito 5+** | Deprecation of @MockBean in favor of @MockitoBean to prevent context caching issues.12 |
| **Build Tools** | Gradle 7.x / Maven 3.6 | **Gradle 8.14+ / Maven 3.6.3+** | Required for Kotlin 2.2 support and enhanced metadata processing.13 |

### **1.2 The Release Cadence and Adoption Window**

The roadmap for Spring Boot 4 indicates a General Availability (GA) target around late November 2025, aligning with the release of Spring Framework 7\.14 Organizations should treat the current Milestone (M1-M3) and Release Candidate (RC) phases as the critical window for library compatibility verification. The most significant friction points will likely be the Jackson 3 migration (due to the package rename) and the Jakarta EE 11 upgrades, which require compatible servlet containers like Tomcat 11 or Jetty 12\.15

## ---

**2\. Deep Dive: Core Framework and Language Support**

The core of Spring Framework 7 is re-engineered to solve two persistent sources of complexity in Java development: the cognitive load of asynchronous programming and the runtime risks of null references.

### **2.1 Sub-Project: Spring Core (Concurrency & Null Safety)**

**Purpose:** To provide the fundamental dependency injection container and lifecycle management, now augmented with native support for Virtual Threads (Project Loom) and comprehensive null-safety enforcement.

Best Practices:  
The defining best practice for Spring Boot 4 is to enable Virtual Threads by default for I/O-bound workloads. This decouples the Java Thread from the operating system thread, allowing the JVM to handle massive concurrency with imperative, blocking code syntax. This effectively deprecates the "Reactive First" mindset for standard REST APIs.16 Architects should configure spring.threads.virtual.enabled=true and revert to standard blocking I/O patterns.  
Simultaneously, development teams must adopt JSpecify annotations. Spring Framework 7 annotates its entire codebase with @NullMarked and @Nullable. For Kotlin consumers, this transforms what were previously flexible "platform types" into strict nullable or non-nullable types. Java developers should adopt the same rigor to prevent NullPointerExceptions at runtime.4

Pitfalls:  
A critical pitfall in the adoption of Virtual Threads is "pinning." If a virtual thread executes code inside a synchronized block or calls a native method, the carrier thread (the OS thread) is pinned, blocking other virtual threads. While recent JDKs have mitigated this in some areas, legacy third-party libraries may still exhibit this behavior, degrading performance. Furthermore, the migration to JSpecify is a breaking change for Kotlin codebases that were lax with null checks; code that previously compiled with warnings will now fail to compile.10  
Performance:  
Virtual Threads offer near-linear scalability for I/O-intensive tasks, matching the throughput of Reactive stacks without the complexity. However, for CPU-bound tasks, platform threads remain superior.  
Testing:  
Testing must now account for null-safety. Tests that explicitly pass null to non-nullable Spring APIs (e.g., in MockMvc) will now trigger compile-time errors or immediate runtime failures before logic execution.

#### **Minimal Code Example**

**Java: Null-Safe Service with Virtual Threads**

Java

package com.example.demo.core;

import org.jspecify.annotations.NullMarked;  
import org.jspecify.annotations.Nullable;  
import org.springframework.stereotype.Service;

// @NullMarked implies all parameters and return types are non-null by default  
@NullMarked  
@Service  
public class UserService {

    // Explicitly nullable return type  
    @Nullable  
    public User findUser(String id) {  
        // Virtual threads handle blocking DB calls efficiently  
        return null; // Simulated not found  
    }

    public void processUser(User user) {  
        // No null check needed; compiler enforces 'user' is not null  
        System.out.println(user.name());   
    }  
}

**Kotlin: Strict Interoperability**

Kotlin

@Service  
class UserFacade(private val userService: UserService) {  
      
    fun execute(id: String) {  
        // Compiler Error in Boot 4: Type mismatch.   
        // Java's findUser returns @Nullable, so Kotlin infers User?  
        // val user: User \= userService.findUser(id) 

        // Correct usage required:  
        val user: User? \= userService.findUser(id)  
        if (user\!= null) {  
            userService.processUser(user)  
        }  
    }  
}

## ---

**3\. Deep Dive: Spring Web (MVC & Clients)**

The Web layer in Spring Boot 4 focuses on standardizing API evolution and simplifying client-side interactions through declarative interfaces.

### **3.1 Sub-Project: Spring MVC**

**Purpose:** To serve as the primary web stack, leveraging the synchronous nature of Virtual Threads to provide high throughput with a simple programming model.

Best Practices:  
The industry is moving away from manual URL path versioning toward built-in support. Spring Boot 4 introduces the spring.mvc.apiversion configuration namespace. Architects should select a strategy early—Path Segment (/v1/) is recommended for pragmatic browseability, while Media Type (Accept: application/vnd.v1+json) is preferred for strict REST compliance. Additionally, the new @HttpExchange annotation should replace RestTemplate for all service-to-service communication.19  
Pitfalls:  
The migration to Jackson 3 is the most dangerous aspect of the web layer upgrade. The package rename from com.fasterxml.jackson to tools.jackson is binary incompatible. Any custom Serializer, Deserializer, or Module implementation must be rewritten. Furthermore, the ObjectMapper is often replaced by JsonMapper and is now immutable, requiring the use of Builders for all configurations.8  
Performance:  
With Virtual Threads enabled, Spring MVC on Tomcat 11 (Servlet 6.1) shows throughput comparable to WebFlux on Netty for I/O-bound payloads, eliminating the need for the complexity of reactive chains.17  
Testing:  
Use RestTestClient for integration testing. This client is designed to test @HttpExchange interfaces and MVC endpoints without the overhead of a full server start in some contexts, or as a full integration tool.1

#### **Minimal Code Example**

**Java: API Versioning and Declarative Client**

Java

// 1\. Controller with Built-in Versioning  
@RestController  
@RequestMapping("/api/orders")  
public class OrderController {

    // Maps to /api/v1/orders automatically via properties config  
    @GetMapping(version \= "1")   
    public List\<Order\> getOrdersV1() {   
        return List.of(new Order("123"));   
    }  
}

// 2\. Declarative Client Definition  
@HttpExchange("/external/inventory")  
public interface InventoryClient {  
      
    @PostExchange("/check")  
    boolean checkStock(@RequestBody StockRequest request);  
}

// 3\. Client Registration  
@Configuration  
@ImportHttpServices(classes \= InventoryClient.class)  
public class ClientConfig {}

**Kotlin: Client Usage**

Kotlin

@Service  
class OrderService(private val inventoryClient: InventoryClient) {  
      
    fun placeOrder(req: StockRequest) {  
        // Calls external service declaratively  
        if (inventoryClient.checkStock(req)) {  
            // Logic  
        }  
    }  
}

## ---

**4\. Deep Dive: Spring Data & Persistence**

Spring Boot 4 realigns the persistence layer with Jakarta Persistence 3.2 and Hibernate 7, focusing on performance optimizations for high-throughput batch operations.

### **4.1 Sub-Project: Spring Data JPA**

**Purpose:** To abstract data access while exposing the advanced capabilities of the underlying Hibernate 7 ORM, specifically addressing the overhead of the persistence context in batch scenarios.

Best Practices:  
For bulk processing or high-volume read-only transactions, developers should leverage the new StatelessSession integration. Standard JPA repositories utilize an EntityManager which maintains a stateful first-level cache. This cache introduces overhead (dirty checking, memory consumption) that is unnecessary for simple reads or massive inserts. Hibernate 7's Stateless Session bypasses this context, offering near-JDBC performance.22  
Additionally, the adoption of ListCrudRepository is now standard. This interface returns List\<T\> instead of Iterable\<T\>, removing the boilerplate stream/collection conversions required in previous versions.24

Pitfalls:  
When using StatelessSession, developers must remember that there is no dirty checking. Changes to entity objects will not be automatically flushed to the database upon transaction commit. Explicit update() or insert() calls are required. Furthermore, lazy loading does not work in a stateless context; all associations must be fetched eagerly or via explicit join queries.25  
Performance:  
Hibernate 7 on Java 25 (via Boot 4\) shows significant improvements in startup time and query generation efficiency. The StatelessSession can reduce memory footprint by orders of magnitude during large batch jobs.22  
Testing:  
Integration tests should utilize @ServiceConnection (discussed in Section 7\) to spin up ephemeral databases, ensuring that Hibernate 7 dialect features are tested against real database engines rather than H2 in-memory approximations.

#### **Minimal Code Example**

**Java: Stateless Repository Usage**

Java

@Repository  
public interface ProductRepository extends ListCrudRepository\<Product, Long\> {  
      
    // Standard JPA Query  
    List\<Product\> findByCategory(String category);  
}

@Service  
public class BatchService {  
      
    // Injecting Hibernate StatelessSession directly for batch ops  
    private final StatelessSession statelessSession;

    public BatchService(SessionFactory sessionFactory) {  
        this.statelessSession \= sessionFactory.openStatelessSession();  
    }

    public void bulkInsert(List\<Product\> products) {  
        Transaction tx \= statelessSession.beginTransaction();  
        for (Product p : products) {  
            statelessSession.insert(p); // Direct insert, no cache overhead  
        }  
        tx.commit();  
    }  
}

**Kotlin: Repository Definition**

Kotlin

interface ProductRepository : ListCrudRepository\<Product, Long\> {  
    fun findByName(name: String): List\<Product\>  
}

## ---

**5\. Deep Dive: Spring Security**

Spring Security 7 enforces a strict "secure-by-default" philosophy and removes years of accumulated API redundancy, resulting in a cleaner but strictly enforced configuration style.

### **5.1 Sub-Project: Spring Security**

**Purpose:** To provide authentication, authorization, and protection against common exploits, now configured exclusively via a Lambda DSL that improves readability and consistency.

Best Practices:  
The configuration chaining style (.and()) is removed. Architects must adopt the Lambda DSL, which uses nested blocks to visually represent the configuration hierarchy. This is not a stylistic choice but a compilation requirement.26  
Security configuration should be modular. Instead of a single monolithic SecurityConfig, applications should define multiple SecurityFilterChain beans with distinct @Order priorities (e.g., one chain for API endpoints with stateless JWT auth, another for internal actuator endpoints with Basic auth).27

Pitfalls:  
The removal of WebSecurityConfigurerAdapter (begun in version 5.7) is complete. Legacy documentation referencing this class is now obsolete. A common error during migration is attempting to use the deprecated .and() method to chain configuration blocks, which will cause compilation failures. Additionally, the default behavior of authorizeHttpRequests is "deny all" unless explicitly configured, which may cause seemingly "broken" endpoints upon upgrade.29  
Performance:  
The new filter chain mechanism in Spring Security 7 is optimized for virtual threads, reducing the overhead of context switching during authentication filters.  
Testing:  
Testing security rules requires the new @MockitoBean (replacing @MockBean) to mock dependencies within the security context without triggering context reloads.

#### **Minimal Code Example**

**Java: Modern Lambda DSL**

Java

@Configuration  
@EnableWebSecurity  
public class SecurityConfig {

    @Bean  
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {  
        http  
            // Mandatory Lambda DSL  
           .authorizeHttpRequests(auth \-\> auth  
               .requestMatchers("/public/\*\*").permitAll()  
               .requestMatchers("/admin/\*\*").hasRole("ADMIN")  
               .anyRequest().authenticated()  
            )  
           .httpBasic(basic \-\> basic.realmName("AppRealm"))  
           .sessionManagement(session \-\> session  
               .sessionCreationPolicy(SessionCreationPolicy.STATELESS)  
            )  
           .csrf(csrf \-\> csrf.disable()); // Explicit disable required for APIs

        return http.build();  
    }  
}

**Kotlin: DSL**

Kotlin

@Bean  
fun filterChain(http: HttpSecurity): SecurityFilterChain {  
    http {  
        authorizeHttpRequests {  
            authorize("/public/\*\*", permitAll)  
            authorize(anyRequest, authenticated)  
        }  
        formLogin {   
            disable()   
        }  
        csrf {   
            disable()   
        }  
    }  
    return http.build()  
}

## ---

**6\. Deep Dive: Spring Modulith**

Spring Modulith 2.0 transforms the logical architecture of Spring Boot applications, providing tooling to enforce modular boundaries within a single deployment artifact.

### **6.1 Sub-Project: Spring Modulith**

**Purpose:** To enable the creation of "Modular Monoliths" by verifying that code in one package (module) does not improperly access internal classes of another package, preventing the "Big Ball of Mud" anti-pattern.6

Best Practices:  
Architects should structure applications such that the root package contains the main application class, and sub-packages represent business modules (e.g., com.acme.app.inventory, com.acme.app.order). Using ApplicationModules.verify() in a test ensures that no module accesses the internal sub-package of another module and that no cyclic dependencies exist.6  
A key capability is **Event Externalization**. Instead of tightly coupling modules via service calls, modules should publish domain events. Spring Modulith 2.0 can automatically intercept these events and persist them to an event publication log (Outbox Pattern), ensuring they are eventually delivered to external brokers (Kafka/RabbitMQ) even if the transaction fails.31

Pitfalls:  
Modulith verification is strict. It will fail the build if a developer creates a cyclic dependency (Module A depends on B, B depends on A). This often requires refactoring shared logic into a third "kernel" or "shared" module.  
Performance:  
Modulith has zero runtime overhead for the application itself. The verification runs strictly during the test phase. However, the event externalization feature does introduce a database write for the event log, which must be accounted for in transaction sizing.

#### **Minimal Code Example**

**Java: Module Verification Test**

Java

class ArchitectureTest {  
    @Test  
    void verifyModularity() {  
        // Scans the classpath for @ApplicationModule structures  
        ApplicationModules modules \= ApplicationModules.of(Application.class);  
          
        // Throws exception if architectural rules (cycles, internal access) are violated  
        modules.verify();   
          
        // Generates documentation (PlantUML C4 diagrams)  
        new Documenter(modules).writeDocumentation();  
    }  
}

## ---

**7\. Deep Dive: Observability**

Spring Boot 4 completes the transition from vendor-specific agents to a unified, open-standard observability stack based on OpenTelemetry (OTLP).

### **7.1 Sub-Project: Spring Boot Actuator & Micrometer**

**Purpose:** To provide production-grade insights (metrics, logs, traces) using a unified API that abstracts the underlying backend (Prometheus, Grafana Tempo, etc.).

Best Practices:  
The recommendation for Spring Boot 4 is to use spring-boot-starter-opentelemetry. This starter configures Micrometer Tracing to export data in the OTLP format by default. This eliminates the need for sidecar agents in many Kubernetes deployments. "Zero-code" instrumentation means that RestClient and JdbcTemplate automatically propagate W3C trace context headers.32  
Pitfalls:  
A common confusion arises between "Micrometer" (the facade) and "OpenTelemetry" (the standard). In Boot 4, you use Micrometer APIs in your code (ObservationRegistry), but the data is exported via OpenTelemetry protocols. Do not mix legacy Sleuth configurations with the new OTLP setup.  
**Code Example: Configuration**

Properties

\# Enable OTLP export for tracing  
management.opentelemetry.tracing.export.otlp.endpoint\=http://otel-collector:4318  
\# Sample all requests (dev/test only)  
management.tracing.sampling.probability\=1.0  
\# Correlate logs with trace IDs  
logging.pattern.level\=%5p \[${spring.application.name:},%X{traceId:-},%X{spanId:-}\]

## ---

**8\. Deep Dive: Testing Strategy**

Testing sees significant quality-of-life improvements with the deeper integration of Testcontainers and the cleanup of mocking annotations.

### **8.1 Sub-Project: Spring Test & Testcontainers**

**Purpose:** To provide reliable integration testing environments that mirror production infrastructure using ephemeral Docker containers.

Best Practices:  
Use @ServiceConnection to simplify Testcontainers configuration. In Spring Boot 3.1+, developers had to manually register dynamic properties or use DynamicPropertyRegistry. Boot 4 standardizes @ServiceConnection, which automatically injects connection details (URL, user, password) from the container into the Spring context.34  
Replace @MockBean with @MockitoBean. The legacy @MockBean caused the Spring TestContext framework to cache a unique context for every test class that used a different set of mocks. This led to "Context Thrashing," where the application would restart dozens of times during a test suite run. @MockitoBean is implemented to allow context reuse more aggressively.12

Pitfalls:  
Mixing @MockBean and @MockitoBean in the same suite can lead to unpredictable application context behavior. A full migration to @MockitoBean is required.

#### **Minimal Code Example**

**Java: Integration Test with Testcontainers**

Java

@SpringBootTest  
@Testcontainers  
class OrderIntegrationTest {

    // Automatically finds the container and injects spring.datasource.\* properties  
    @Container  
    @ServiceConnection  
    static PostgreSQLContainer\<?\> postgres \= new PostgreSQLContainer\<\>("postgres:16");

    // Replaces @MockBean  
    @MockitoBean  
    private PaymentGateway paymentGateway;

    @Autowired  
    private OrderService orderService;

    @Test  
    void testOrderFlow() {  
        given(paymentGateway.charge(any())).willReturn(true);  
        // Execute logic against real Postgres and mocked Payment gateway  
        orderService.processOrder(new Order());  
    }  
}

## ---

**9\. Cross-Cutting Best Practices**

1. **Concurrency Strategy:** Adopt Virtual Threads (spring.threads.virtual.enabled=true) for all standard REST and MVC applications. Reserve WebFlux strictly for streaming endpoints or scenarios requiring functional routing.17  
2. **Strict Nullity:** Configure the IDE and build tools to treat JSpecify violations as errors. This is the only way to ensure robustness, particularly in mixed Java/Kotlin environments.4  
3. **Immutable Configuration:** With the changes in Jackson 3 and internal Spring optimizations, move away from mutable JavaBean-style configuration properties. Use Java Records (record) annotated with @ConfigurationProperties.  
4. **AOT Readiness:** Even if not compiling to Native Image immediately, write code that is AOT-friendly. Avoid unrestricted reflection and prefer the RuntimeHints API for dynamic capabilities. This ensures the application is future-proofed for serverless deployments where startup time is critical.

## ---

**10\. Starter Blueprint: The Spring Boot 4 Reference Architecture**

To accelerate development, the following project structure represents the "Gold Standard" for a Spring Boot 4 application, integrating Modulith, Docker, and best practices.

**Project Structure:**

src/main/java/com/company/app  
├── Application.java (The main class)  
├── package-info.java (@NullMarked)  
├── shared (Shared kernel, DTOs, utils \- verifiable by Modulith)  
│ └── package-info.java  
├── inventory (Business Module 1\)  
│ ├── package-info.java (@ApplicationModule)  
│ ├── InventoryController.java (Package-private implementation)  
│ ├── InventoryService.java (Public Interface)  
│ └── internal (Hidden implementation details)  
└── order (Business Module 2\)  
├── package-info.java  
└── OrderService.java  
**build.gradle.kts (Kotlin DSL):**

Kotlin

plugins {  
    java  
    id("org.springframework.boot") version "4.0.0"  
    id("io.spring.dependency-management") version "1.1.7"  
    kotlin("jvm") version "2.2.0"   
    kotlin("plugin.spring") version "2.2.0"  
}

java {  
    toolchain {  
        languageVersion.set(JavaLanguageVersion.of(25)) // Recommended   
    }  
}

dependencies {  
    // Web & Data  
    implementation("org.springframework.boot:spring-boot-starter-web")  
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")  
      
    // Ops & Security  
    implementation("org.springframework.boot:spring-boot-starter-actuator")  
    implementation("org.springframework.boot:spring-boot-starter-security")  
      
    // Architecture  
    implementation("org.springframework.modulith:spring-modulith-starter-core")  
      
    // JSON (Jackson 3 implicit in starter-web, but ensure no legacy overrides)  
      
    // Observability (OTLP Native)  
    implementation("io.micrometer:micrometer-tracing-bridge-otel")  
    implementation("io.opentelemetry:opentelemetry-exporter-otlp")

    // Testing  
    testImplementation("org.springframework.boot:spring-boot-starter-test")  
    testImplementation("org.springframework.boot:spring-boot-testcontainers")  
    testImplementation("org.testcontainers:postgresql")  
    testImplementation("org.springframework.modulith:spring-modulith-starter-test")  
}

**application.properties (Sensible Defaults):**

Properties

\# Concurrency: The Virtual Thread Switch  
spring.threads.virtual.enabled\=true

\# API Architecture  
spring.mvc.apiversion.type\=path

\# Lifecycle & Shutdown (Critical for Kubernetes)  
server.shutdown\=graceful  
spring.lifecycle.timeout-per-shutdown-phase\=20s

\# Observability  
management.endpoints.web.exposure.include\=health,metrics,prometheus,info  
management.tracing.sampling.probability\=1.0

\# Database (Docker Compose / Testcontainers support active)  
spring.docker.compose.enabled\=true

## **Conclusion**

Spring Boot 4 is a rigorous modernization of the Java enterprise landscape. By enforcing strict boundaries through Modulith, strict typing through JSpecify, and simplified concurrency through Virtual Threads, it reduces the cognitive load required to build scalable systems. The migration cost—particularly regarding the Jackson 3 package rename and the Spring Security 7 Lambda DSL—is non-trivial and will require significant refactoring of legacy codebases. However, the resulting platform provides a stable, high-performance foundation optimized for the next decade of JVM innovation.

#### **Works cited**

1. Spring Boot 4 and Spring Framework 7: Key Features and Changes \- Loiane Groner, accessed December 18, 2025, [https://loiane.com/2025/08/spring-boot-4-spring-framework-7-key-features/](https://loiane.com/2025/08/spring-boot-4-spring-framework-7-key-features/)  
2. Spring Framework 7.0 Release Notes \- GitHub, accessed December 18, 2025, [https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes)  
3. Spring Boot 4.0.0 available now, accessed December 18, 2025, [https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/)  
4. ⛔ Stop NullPointerExceptions Before Production in Spring Boot 4 with Null Safety, accessed December 18, 2025, [https://www.youtube.com/watch?v=QlGnaRoujL8](https://www.youtube.com/watch?v=QlGnaRoujL8)  
5. Spring Framework 7 & Spring Boot 4: Baseline Updates, Deprecations, and New API Versioning Features \- RBA Consulting, accessed December 18, 2025, [https://www.rbaconsulting.com/blog/spring-framework-7-spring-boot-4/](https://www.rbaconsulting.com/blog/spring-framework-7-spring-boot-4/)  
6. Spring Modulith, accessed December 18, 2025, [https://spring.io/projects/spring-modulith/](https://spring.io/projects/spring-modulith/)  
7. Jackson 3 Support is HERE: What's New in Spring Framework 7 & Spring Boot 4 \- YouTube, accessed December 18, 2025, [https://www.youtube.com/watch?v=4cvP\_qroLH4](https://www.youtube.com/watch?v=4cvP_qroLH4)  
8. Introducing Jackson 3 support in Spring, accessed December 18, 2025, [https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/](https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/)  
9. accessed December 18, 2025, [https://endoflife.date/spring-framework](https://endoflife.date/spring-framework)  
10. Next level Kotlin support in Spring Boot 4, accessed December 18, 2025, [https://spring.io/blog/2025/12/18/next-level-kotlin-support-in-spring-boot-4/](https://spring.io/blog/2025/12/18/next-level-kotlin-support-in-spring-boot-4/)  
11. Spring News Roundup: GA Releases of Boot, Security, GraphQL, Integration, Modulith, Batch \- InfoQ, accessed December 18, 2025, [https://www.infoq.com/news/2025/11/spring-news-roundup-nov17-2025/](https://www.infoq.com/news/2025/11/spring-news-roundup-nov17-2025/)  
12. Spring Boot @MockBean and @SpyBean Are Saying Goodbye \- Alexis SEGURA, accessed December 18, 2025, [https://www.alexis-segura.com/notes/spring-boot-mockbean-and-spybean-are-saying-goodbye/](https://www.alexis-segura.com/notes/spring-boot-mockbean-and-spybean-are-saying-goodbye/)  
13. System Requirements :: Spring Boot, accessed December 18, 2025, [https://docs.spring.io/spring-boot/system-requirements.html](https://docs.spring.io/spring-boot/system-requirements.html)  
14. The Road to GA \- Introduction \- Spring, accessed December 18, 2025, [https://spring.io/blog/2025/09/02/road\_to\_ga\_introduction/](https://spring.io/blog/2025/09/02/road_to_ga_introduction/)  
15. Spring Boot version history \- what is the latest Spring Boot version? \- CodeJava.net, accessed December 18, 2025, [https://www.codejava.net/frameworks/spring-boot/spring-boot-version-history](https://www.codejava.net/frameworks/spring-boot/spring-boot-version-history)  
16. Spring Boot 4: The New Architecture — No Async, No WebFlux, No Thread Pools \- Medium, accessed December 18, 2025, [https://medium.com/@gangoladeepa/spring-boot-4-the-new-architecture-no-async-no-webflux-no-thread-pools-2b8cdda346f5](https://medium.com/@gangoladeepa/spring-boot-4-the-new-architecture-no-async-no-webflux-no-thread-pools-2b8cdda346f5)  
17. Virtual Threads vs Reactive WebFlux: Which One Should You Use in 2025? | by MEsfandiari, accessed December 18, 2025, [https://medium.com/@mesfandiari77/virtual-threads-vs-reactive-webflux-which-one-should-you-use-in-2025-9720996b57e3](https://medium.com/@mesfandiari77/virtual-threads-vs-reactive-webflux-which-one-should-you-use-in-2025-9720996b57e3)  
18. Null-safe applications with Spring Boot 4, accessed December 18, 2025, [https://spring.io/blog/2025/11/12/null-safe-applications-with-spring-boot-4/](https://spring.io/blog/2025/11/12/null-safe-applications-with-spring-boot-4/)  
19. API Versioning in Spring | Baeldung, accessed December 18, 2025, [https://www.baeldung.com/spring-api-versioning](https://www.baeldung.com/spring-api-versioning)  
20. HTTP Interfaces in Spring Boot 4: Say Goodbye to Boilerplate \- Dan Vega, accessed December 18, 2025, [https://www.danvega.dev/blog/2025/11/06/http-interfaces-spring-boot-4](https://www.danvega.dev/blog/2025/11/06/http-interfaces-spring-boot-4)  
21. ️ Virtual Threads vs WebFlux — Real Benchmarks (2025) | by dolly \- Medium, accessed December 18, 2025, [https://medium.com/@gangoladeepa/%EF%B8%8F-virtual-threads-vs-webflux-real-benchmarks-2025-8a621e3f1b30](https://medium.com/@gangoladeepa/%EF%B8%8F-virtual-threads-vs-webflux-real-benchmarks-2025-8a621e3f1b30)  
22. Hibernate ORM 7 on Quarkus: each new version brings a better database experience, accessed December 18, 2025, [https://quarkus.io/blog/hibernate7-on-quarkus/](https://quarkus.io/blog/hibernate7-on-quarkus/)  
23. How to use StatelessSession with Spring Data JPA and Hibernate? \- Stack Overflow, accessed December 18, 2025, [https://stackoverflow.com/questions/15460601/how-to-use-statelesssession-with-spring-data-jpa-and-hibernate](https://stackoverflow.com/questions/15460601/how-to-use-statelesssession-with-spring-data-jpa-and-hibernate)  
24. New CRUD Repository Interfaces in Spring Data 3 | Baeldung, accessed December 18, 2025, [https://www.baeldung.com/spring-data-3-crud-repository-interfaces](https://www.baeldung.com/spring-data-3-crud-repository-interfaces)  
25. Hibernate StatelessSession JDBC Batching \- Vlad Mihalcea, accessed December 18, 2025, [https://vladmihalcea.com/hibernate-statelesssession-jdbc-batching/](https://vladmihalcea.com/hibernate-statelesssession-jdbc-batching/)  
26. What's New in Spring Security 7.0, accessed December 18, 2025, [https://docs.spring.io/spring-security/reference/whats-new.html](https://docs.spring.io/spring-security/reference/whats-new.html)  
27. Spring Security \- Filter Chain with Example \- GeeksforGeeks, accessed December 18, 2025, [https://www.geeksforgeeks.org/java/spring-security-filter-chain-with-example/](https://www.geeksforgeeks.org/java/spring-security-filter-chain-with-example/)  
28. Spring boot security \- how to use SecurityFilterChain for authentification? \- Stack Overflow, accessed December 18, 2025, [https://stackoverflow.com/questions/72499313/spring-boot-security-how-to-use-securityfilterchain-for-authentification](https://stackoverflow.com/questions/72499313/spring-boot-security-how-to-use-securityfilterchain-for-authentification)  
29. Spring Security :: Spring Boot, accessed December 18, 2025, [https://docs.spring.io/spring-boot/reference/web/spring-security.html](https://docs.spring.io/spring-boot/reference/web/spring-security.html)  
30. Build a modular monolith with Spring Modulith \- BellSoft, accessed December 18, 2025, [https://bell-sw.com/blog/how-to-build-a-modular-application-with-spring-modulith/](https://bell-sw.com/blog/how-to-build-a-modular-application-with-spring-modulith/)  
31. Spring Modulith 2.0 GA, 1.4.5, and 1.3.11 released, accessed December 18, 2025, [https://spring.io/blog/2025/11/21/spring-modulith-2-0-ga-1-4-5-and-1-3-11-released](https://spring.io/blog/2025/11/21/spring-modulith-2-0-ga-1-4-5-and-1-3-11-released)  
32. OpenTelemetry with Spring Boot, accessed December 18, 2025, [https://spring.io/blog/2025/11/18/opentelemetry-with-spring-boot/](https://spring.io/blog/2025/11/18/opentelemetry-with-spring-boot/)  
33. Spring Boot 4 \- OpenTelemetry Guide \- Foojay.io, accessed December 18, 2025, [https://foojay.io/today/spring-boot-4-opentelemetry-explained/](https://foojay.io/today/spring-boot-4-opentelemetry-explained/)  
34. Spring Boot @ServiceConnection Example \- Mkyong.com, accessed December 18, 2025, [https://mkyong.com/spring-boot/spring-boot-serviceconnection-example/](https://mkyong.com/spring-boot/spring-boot-serviceconnection-example/)  
35. Cannot find MockBean in Spring Boot 4.0.0 \- Stack Overflow, accessed December 18, 2025, [https://stackoverflow.com/questions/79828472/cannot-find-mockbean-in-spring-boot-4-0-0](https://stackoverflow.com/questions/79828472/cannot-find-mockbean-in-spring-boot-4-0-0)