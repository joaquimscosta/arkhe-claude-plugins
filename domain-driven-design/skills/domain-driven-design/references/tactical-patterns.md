# Tactical DDD Patterns

Tactical patterns implement domain logic within bounded context boundaries. **Apply selectively in core domains only.**

## Table of Contents
1. [Entities](#entities)
2. [Value Objects](#value-objects)
3. [Aggregates](#aggregates)
4. [Domain Services](#domain-services)
5. [Application Services](#application-services)
6. [Repositories](#repositories)
7. [Factories](#factories)
8. [Domain Events](#domain-events)

---

## Entities

Objects defined by unique identity maintained throughout their lifecycle.

### Characteristics
- Identity-based equality (same ID = same entity)
- Mutable state
- Trackable history
- Lifecycle (created, modified, archived)

### Examples
- `Customer` (ID=123 remains same customer as name changes)
- `Order` (tracked from creation to fulfillment)
- `Account` (balance changes, identity persists)
- `Employee` (role changes, same person)

### Entity Design Guidelines
1. Identity should be immutable after creation
2. Use strongly-typed IDs (`CustomerId` not `long`)
3. Encapsulate state changes in behavior methods
4. Validate invariants on state changes

### When to Use Entity
- Need to track object through time
- Domain experts reference it as uniquely identifiable
- Object has a lifecycle with state transitions
- Equality based on identity, not attributes

---

## Value Objects

Objects defined entirely by their attributes—no conceptual identity.

### Characteristics
- Structural equality (same attributes = equal objects)
- Immutable (changes create new instances)
- No identity
- Freely interchangeable

### Examples
- `Money` ($100 USD is identical to any other $100 USD)
- `Address` (123 Main St is the same address everywhere)
- `DateRange` (Jan 1-15 is equal to another Jan 1-15)
- `Email` (encapsulates format validation)
- `Coordinates` (lat/long pair)

### Value Object Design Guidelines
1. Make immutable—no setters
2. Implement structural equality
3. Use for attributes that describe entities
4. Encapsulate validation in constructor
5. Provide behavior methods that return new instances

### Common Mistake: Primitive Obsession
```
// Bad: Primitives leak validation everywhere
String email = customer.getEmail();

// Good: Value object encapsulates rules
Email email = customer.getEmail();
// Email class validates format, provides behavior
```

### When to Use Value Object
- Only attribute values matter
- Objects with same values are interchangeable
- Concept represents descriptive aspect
- No need to track through time
- **Default choice**—use entities only when identity required

---

## Aggregates

Cluster of domain objects treated as single unit for data changes.

### Core Concepts
- **Aggregate Root**: Single entry point, only externally referenceable object
- **Boundary**: Defines transactional consistency scope
- **Invariants**: Business rules enforced within boundary

### Vaughn Vernon's Design Rules

**Rule 1: Model true invariants in consistency boundaries**
- Only include objects that must be immediately consistent
- If consistency can be eventual, separate aggregates

**Rule 2: Design small aggregates**
- Large aggregates never perform or scale well
- ~70% should be just root entity + value objects
- ~30% should have 2-3 total entities maximum

**Rule 3: Reference other aggregates by ID only**
```
// Bad: Direct object reference
class Order {
    Customer customer; // Creates coupling
}

// Good: ID reference
class Order {
    CustomerId customerId; // Decoupled
}
```

**Rule 4: Use eventual consistency outside boundary**
- One transaction = one aggregate modification
- Cross-aggregate consistency via domain events

### Aggregate Design Process
1. Identify cluster of related objects
2. Determine which invariants must be immediately consistent
3. Choose aggregate root (commands go through root)
4. Draw minimal boundary around true invariants
5. Everything else becomes separate aggregate with ID reference

### Common Aggregate Mistakes
- **Too large**: Modeling relationships instead of rules
- **Wrong root**: Choosing based on data, not invariants
- **Cross-aggregate transactions**: Trying to update multiple in one transaction
- **Direct references**: Object links instead of ID references

### Aggregate Size Heuristic
If aggregate contains more than 3 entities, question whether all invariants truly require immediate consistency.

---

## Domain Services

Stateless operations implementing domain logic that doesn't belong in entities or value objects.

### Characteristics
- Contain business logic
- Operate on domain objects
- Use ubiquitous language
- Live in domain layer
- No state

### When to Use Domain Service
- Operation involves multiple aggregates
- Logic doesn't naturally fit in single entity
- Business concept is a process, not a thing

### Examples
```
// Transfer between accounts requires both accounts
TransferService.transfer(fromAccount, toAccount, amount)

// Pricing involves product, customer tier, promotions
PricingService.calculatePrice(product, customer, promotions)

// Shipping calculation requires address, items, carrier
ShippingService.calculateCost(address, items, carrier)
```

### Domain Service Guidelines
1. Name using ubiquitous language
2. Keep stateless
3. Operate on domain objects, not DTOs
4. Don't put CRUD operations here

---

## Application Services

Orchestrate use cases without containing domain logic.

### Characteristics
- Orchestration only, no business rules
- Work with DTOs and commands
- Manage transaction boundaries
- Entry point from presentation layer
- Fetch entities, delegate to domain, persist changes

### Responsibilities
1. Receive command/request
2. Fetch required aggregates from repositories
3. Execute domain operations
4. Persist changes
5. Publish integration events
6. Return result

### Example Structure
```
class PlaceOrderService {
    execute(PlaceOrderCommand command) {
        // 1. Fetch aggregates
        customer = customerRepository.findById(command.customerId);
        product = productRepository.findById(command.productId);
        
        // 2. Execute domain logic (in domain, not here)
        order = customer.placeOrder(product, command.quantity);
        
        // 3. Persist
        orderRepository.save(order);
        
        // 4. Publish events
        eventPublisher.publish(order.getDomainEvents());
        
        // 5. Return result
        return OrderDto.from(order);
    }
}
```

### Domain Service vs Application Service

| Aspect | Domain Service | Application Service |
|--------|---------------|---------------------|
| Contains | Business logic | Orchestration |
| Language | Ubiquitous | Use cases |
| Layer | Domain | Application |
| State | Stateless | Stateless |
| Works with | Domain objects | DTOs, Commands |

**Rule**: If business rules appear in application service, move them to domain service or entity.

---

## Repositories

Collection-oriented interfaces for accessing aggregates.

### Characteristics
- Abstract persistence details
- Interface in domain layer
- Implementation in infrastructure
- Work with aggregates, not tables
- Use ubiquitous language

### Interface Design
```
interface OrderRepository {
    Order findById(OrderId id);
    List<Order> findPendingOrders();          // Business language
    List<Order> findByCustomer(CustomerId id);
    void save(Order order);
    void delete(Order order);
}
```

### Repository vs DAO

| Aspect | Repository | DAO |
|--------|-----------|-----|
| Scope | Aggregate | Table/Entity |
| Language | Business terms | Technical terms |
| Returns | Domain objects | Data objects |
| Interface location | Domain layer | Infrastructure |

### Repository Guidelines
1. One repository per aggregate root
2. Interface uses ubiquitous language
3. Return domain objects, not entities
4. Abstract query details from domain
5. Handle aggregate reconstitution

---

## Factories

Encapsulate complex aggregate creation.

### When to Use Factory
- Construction requires multiple steps
- Business rules apply during creation
- Structure varies based on input
- Creation logic is complex

### When Constructor Suffices
- Simple aggregates
- No special creation logic
- Few required parameters

### Factory Patterns

**Factory Method** (on aggregate or separate class)
```
class Order {
    static Order createWithDiscount(Customer customer, DiscountCode code) {
        // Apply discount rules during creation
        order = new Order(customer);
        order.applyDiscount(code);
        return order;
    }
}
```

**Factory Service** (when creation needs external data)
```
class OrderFactory {
    Order create(CustomerId customerId, List<ProductId> productIds) {
        customer = customerRepo.findById(customerId);
        products = productRepo.findByIds(productIds);
        // Complex assembly with validation
        return new Order(customer, products);
    }
}
```

---

## Domain Events

Significant occurrences that happened in the past.

### Characteristics
- Named in past tense: `OrderPlaced`, `PaymentProcessed`
- Immutable record of what happened
- Contain relevant data at time of occurrence
- Enable loose coupling between aggregates

### Domain Event Structure
```
class OrderPlaced {
    OrderId orderId;
    CustomerId customerId;
    Money totalAmount;
    Instant occurredAt;
    // All data needed by handlers
}
```

### Domain Events vs Integration Events

| Aspect | Domain Event | Integration Event |
|--------|-------------|-------------------|
| Scope | Within bounded context | Across contexts |
| Transport | In-memory | Message broker |
| Timing | Often synchronous | Asynchronous |
| Coupling | Loose within context | Cross-context |

### Event Publishing Pattern
1. Aggregate records event during operation
2. Application service retrieves events after save
3. Events dispatched to handlers
4. Handlers update other aggregates or projections

### Domain Event Guidelines
1. Name using ubiquitous language
2. Include all data handlers need
3. Make immutable
4. Record timestamp
5. Consider versioning for evolution
