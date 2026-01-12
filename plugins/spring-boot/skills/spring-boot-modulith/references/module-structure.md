# Module Structure & Boundaries

Package conventions and dependency rules for Spring Modulith.

## Package Layout

### Standard Structure

```
com.example/
├── Application.java                    ← Main class
│
├── order/                              ← Module: order
│   ├── OrderService.java               ← API: public service
│   ├── Order.java                      ← API: public type (if exposed)
│   ├── OrderCreated.java               ← API: public event
│   ├── package-info.java               ← Module configuration
│   │
│   ├── internal/                       ← Implementation details
│   │   ├── OrderRepository.java
│   │   ├── OrderEntity.java
│   │   └── OrderMapper.java
│   │
│   └── web/                            ← Still internal (sub-package)
│       └── OrderController.java
│
├── inventory/                          ← Module: inventory
│   ├── InventoryService.java
│   └── internal/
│
└── shared/                             ← Shared kernel (use sparingly)
    └── Money.java
```

### What Goes Where

| Location | Contains | Visibility |
|----------|----------|------------|
| `order/` (base) | Services, events, DTOs for API | Public to all modules |
| `order/internal/` | Repositories, entities, mappers | Hidden |
| `order/web/` | Controllers | Hidden (sub-package) |
| `shared/` | Value objects used across modules | Public (minimize this) |

## Module Configuration

### @ApplicationModule

```java
// package-info.java
@ApplicationModule(
    displayName = "Order Management",
    allowedDependencies = {
        "inventory :: api",     // Only inventory's API, not internals
        "customer",             // All of customer module
        "shared"                // Shared kernel
    },
    type = Type.CLOSED          // Strict encapsulation
)
package com.example.order;
```

### Module Types

| Type | Behavior |
|------|----------|
| `OPEN` (default) | All modules can depend on this |
| `CLOSED` | Only explicitly allowed dependencies |

### Named Interfaces

Expose subsets of a module:

```java
// package-info.java in com.example.order
@ApplicationModule
@NamedInterface("api")
package com.example.order;

// package-info.java in com.example.order.spi
@NamedInterface("spi")
package com.example.order.spi;
```

Now other modules can depend on specific interfaces:

```java
// In shipping module
@ApplicationModule(
    allowedDependencies = {"order :: api"}  // Only order's API, not SPI
)
package com.example.shipping;
```

## Dependency Rules

### Allowed Patterns

```
order → shared          ✓ (shared kernel)
order → inventory       ✓ (if declared)
order.internal → order  ✓ (internal uses own API)
```

### Forbidden Patterns (fail verification)

```
order → inventory.internal    ✗ (accessing internals)
order → shipping              ✗ (if not declared)
inventory → order             ✗ (circular, if order → inventory)
```

## Module Detection

Modulith automatically detects modules as direct sub-packages of the main application class package.

```java
@SpringBootApplication
public class Application { }  // In com.example

// Detected modules:
// - com.example.order
// - com.example.inventory
// - com.example.shipping
```

### Explicit Module Definition

For non-standard layouts:

```java
@SpringBootApplication
@Modulithic(
    sharedModules = "shared",
    additionalPackages = "com.example.legacy"
)
public class Application { }
```

## Module Verification

### Basic Verification

```java
class ModularityTests {
    
    @Test
    void verifyModuleStructure() {
        ApplicationModules.of(Application.class).verify();
    }
}
```

### Verification Checks

1. **No cycles** — Module A → B → A forbidden
2. **No internal access** — Can't use `.internal` types from other modules
3. **Declared dependencies only** — For `CLOSED` modules
4. **Event types are public** — Events must be in module's API package

### Verification Output

```
# Successful
Verifying module structure...
✓ order
✓ inventory
✓ shipping
All modules verified successfully!

# Failed
Verifying module structure...
✗ order
  - Uses internal type: inventory.internal.StockEntity
  - Undeclared dependency: shipping
```

## Documentation Generation

```java
@Test
void generateDocs() {
    ApplicationModules modules = ApplicationModules.of(Application.class);
    
    new Documenter(modules)
        .writeModulesAsPlantUml()           // Overview diagram
        .writeIndividualModulesAsPlantUml() // Per-module diagrams
        .writeModuleCanvases();             // Module canvases
}
```

Generates:
- `target/modulith-docs/components.puml` — Module overview
- `target/modulith-docs/module-order.puml` — Order module detail
- `target/modulith-docs/module-order.adoc` — Order module canvas

## Cross-Cutting Concerns

### Shared Configuration

```java
// In shared module or main package
@Configuration
public class SharedConfig {
    @Bean
    public Clock clock() {
        return Clock.systemUTC();
    }
}
```

### Module-Specific Configuration

```java
// In order/internal/
@Configuration
class OrderConfig {
    @Bean
    OrderService orderService(OrderRepository repo, ApplicationEventPublisher events) {
        return new OrderService(repo, events);
    }
}
```

## Integration with DDD Layers

```
com.example.order/                    ← Bounded Context
├── OrderFacade.java                  ← Application Service (API)
├── OrderSubmitted.java               ← Domain Event (API)
│
├── domain/                           ← Domain Layer (internal)
│   ├── Order.java                    ← Aggregate Root
│   ├── OrderLine.java                ← Entity
│   ├── Money.java                    ← Value Object
│   └── OrderRepository.java          ← Repository Interface
│
├── application/                      ← Application Layer (internal)
│   ├── SubmitOrderHandler.java
│   └── OrderQueryService.java
│
└── infrastructure/                   ← Infrastructure Layer (internal)
    ├── JpaOrderRepository.java
    └── OrderController.java
```

**Note:** Even with DDD layers, only `OrderFacade` and `OrderSubmitted` are in the base package (API). Everything else is internal.

## Testing Module Boundaries

```java
@ApplicationModuleTest(mode = BootstrapMode.DIRECT_DEPENDENCIES)
class OrderModuleTest {
    
    @Autowired
    OrderService orderService;  // From this module
    
    @Autowired
    InventoryService inventoryService;  // Direct dependency
    
    // ShippingService NOT available - not a direct dependency
}
```

### Bootstrap Modes

| Mode | Loads |
|------|-------|
| `STANDALONE` | Current module only |
| `DIRECT_DEPENDENCIES` | Module + direct dependencies |
| `ALL_DEPENDENCIES` | Module + full dependency tree |
