# Domain-Driven Design Examples

Scenario walkthroughs demonstrating how to apply DDD thinking to real-world systems.

## Subdomain Identification

An e-commerce company wants to redesign its monolithic platform. The team runs an Event Storming session and identifies these business capabilities:

- **Product catalog** and search
- **Order placement** and fulfillment
- **Pricing** with dynamic rules (loyalty tiers, flash sales, bundle discounts)
- **Inventory** tracking across warehouses
- **Shipping** logistics and carrier integration
- **Customer accounts** and authentication
- **Payment** processing
- **Email/SMS notifications**

### Analysis

Classify each by strategic importance:

| Subdomain | Type | Reasoning |
|-----------|------|-----------|
| **Pricing Engine** | Core | Dynamic pricing is the competitive advantage — competitors use flat pricing. Custom rules that directly drive revenue. |
| **Order Fulfillment** | Core | Orchestrates the end-to-end purchase flow with business-specific rules (partial shipments, backorders, split payments). |
| **Product Catalog** | Supporting | Necessary but not differentiating. Custom enough to need internal development, but quality tradeoffs are acceptable. |
| **Inventory** | Supporting | Important for operations but standard warehouse tracking. Could use simpler patterns. |
| **Shipping** | Supporting | Custom integration with carriers, but the logic itself is standard. |
| **Authentication** | Generic | Use an identity provider (Keycloak, Auth0). No competitive value in building this. |
| **Payments** | Generic | Use Stripe/Adyen. Payment processing is commoditized. |
| **Notifications** | Generic | Use a messaging service (SendGrid, Twilio). Standard integration work. |

**Key points:**
- Invest maximum DDD effort (tactical patterns, domain experts) in Core subdomains
- Supporting subdomains get simpler patterns — possibly CRUD with some domain logic
- Generic subdomains are bought or outsourced, never built from scratch

---

## Bounded Context Definition

The team notices that the word "Order" means different things to different departments:

- **Sales** talks about Orders as shopping carts with line items, discounts, and customer preferences
- **Shipping** talks about Orders as packages with weight, dimensions, destination address, and carrier assignment
- **Accounting** talks about Orders as invoices with tax calculations, payment status, and revenue recognition dates

### Analysis

Each department has its own **ubiquitous language** for "Order." This is the signal to draw bounded context boundaries:

```
Sales Context          Shipping Context        Accounting Context
┌────────────────┐    ┌────────────────┐      ┌────────────────┐
│ Order           │    │ Shipment        │      │ Invoice         │
│  - lineItems    │    │  - packages     │      │  - lineItems    │
│  - discounts    │    │  - weight       │      │  - taxAmount    │
│  - customer     │    │  - destination  │      │  - paymentStatus│
│  - subtotal()   │    │  - carrier      │      │  - revenueDate  │
│                 │    │  - trackingNo   │      │                 │
│ Customer        │    │                 │      │ TaxRule         │
│  - preferences  │    │ Address         │      │  - jurisdiction │
│  - loyaltyTier  │    │  - validated    │      │  - rate         │
└────────────────┘    └────────────────┘      └────────────────┘
```

Notice: the same real-world concept ("Order") becomes three different models — `Order`, `Shipment`, and `Invoice`. Each context only models what it needs. The Sales `Order` has no concept of package weight; the Shipping `Shipment` has no concept of discounts.

**Key points:**
- Draw boundaries where language changes — if stakeholders use the same word differently, that's a context boundary
- Each context has its own model of shared concepts — do not try to create a single unified "Order" model
- Contexts communicate through well-defined integration points, not shared databases

---

## Context Mapping

With three bounded contexts identified, define how they integrate:

```
┌──────────┐  OrderPlaced event   ┌──────────┐
│  Sales   │ ──────────────────▶  │ Shipping │
│ (upstream)│  Published Language  │(downstream)│
└──────────┘                      └──────────┘
      │                                 │
      │ OrderPlaced event               │ ShipmentDispatched event
      │ Published Language              │ Published Language
      ▼                                 ▼
┌──────────────┐              ┌──────────────┐
│  Accounting  │              │ Notification │
│ (downstream) │              │ (downstream) │
└──────────────┘              └──────────────┘
```

### Integration Patterns Applied

**Sales → Shipping: Published Language**
Sales publishes an `OrderPlaced` event with a well-defined schema. Shipping subscribes and translates the event into its own `Shipment` model. Sales does not know or care how Shipping interprets the data.

**Sales → Accounting: Published Language with ACL**
Accounting consumes the same `OrderPlaced` event but applies an Anti-Corruption Layer (ACL) to translate Sales concepts into accounting terms. The ACL maps `Order.lineItems` and `Order.discounts` into `Invoice.lineItems` with proper tax calculations. This protects the Accounting model from changes in the Sales domain.

**Shipping → Notification: Customer-Supplier**
Notification needs specific data from Shipping (tracking numbers, estimated delivery). Shipping agrees to include these fields in its events — a Customer-Supplier relationship where Notification's needs influence Shipping's event schema.

**Key points:**
- Published Language decouples contexts through shared event schemas
- Anti-Corruption Layers protect downstream contexts from upstream model changes
- Customer-Supplier relationships are appropriate when the downstream context has negotiating power
- Avoid Shared Kernel unless contexts are maintained by the same team — shared code creates coupling

---

## Aggregate Design

The Sales context needs an `Order` aggregate. Apply Vaughn Vernon's four rules:

### Rule 1: Model True Invariants

The business rule: "An order cannot be submitted if it has no line items, and the total must not exceed the customer's credit limit."

These invariants must be enforced within a single transaction. The `Order` aggregate protects them:

```
Order (Aggregate Root)
├── orderId: OrderId
├── customerId: CustomerId      ← reference by ID, not embedded Customer
├── status: OrderStatus
├── lines: Set<OrderLine>       ← owned by the aggregate
│   ├── productId: ProductId    ← reference by ID, not embedded Product
│   ├── quantity: Quantity       ← value object
│   └── unitPrice: Money        ← value object
└── submit()                    ← enforces both invariants
```

### Rule 2: Design Small Aggregates

The `Order` aggregate does NOT contain `Customer`, `Product`, or `ShippingAddress` entities. It only references them by ID. The aggregate root plus its value objects and owned entities is the entire boundary.

**Wrong**: Embedding `Customer` inside `Order` so you can check the credit limit. This creates a massive aggregate and contention when multiple orders reference the same customer.

**Right**: The `submit()` method accepts a `CreditLimit` value object (looked up by the application service before calling the aggregate). The aggregate validates against it without owning the Customer.

### Rule 3: Reference Other Aggregates by ID

`customerId: CustomerId` and `productId: ProductId` are typed IDs, not entity references. This means:
- No cascading persistence — Order and Customer have independent lifecycles
- No lock contention — modifying a Customer doesn't lock any Orders
- Clear module boundaries — Order doesn't need Customer's database table

### Rule 4: Use Eventual Consistency Outside the Boundary

When an Order is submitted, the Inventory service must reserve stock. This happens asynchronously:

1. `Order.submit()` registers an `OrderSubmitted` domain event
2. The application service persists the Order (single transaction)
3. An event handler picks up `OrderSubmitted` and calls the Inventory context
4. If Inventory cannot reserve stock, it publishes `ReservationFailed`
5. A compensating handler moves the Order back to `PENDING_REVIEW`

**Key points:**
- Keep aggregates small — most should be a root entity plus value objects
- Reference other aggregates by ID, never by direct object reference
- Enforce invariants within the aggregate boundary in a single transaction
- Use domain events and eventual consistency for cross-aggregate coordination

---

## Modular Monolith vs Microservices Decision

The e-commerce team (12 developers) has identified four bounded contexts. Should they deploy as microservices or a modular monolith?

### Decision Matrix

| Factor | Current State | Favors |
|--------|--------------|--------|
| **Team size** | 12 developers, 2 teams | Modular monolith |
| **Domain boundaries** | Recently identified, not battle-tested | Modular monolith |
| **Scaling needs** | Uniform traffic, no hotspots | Modular monolith |
| **Data consistency** | Several cross-context transactions needed | Modular monolith |
| **Deployment cadence** | Weekly releases, shared schedule | Modular monolith |
| **DevOps maturity** | Basic CI/CD, no service mesh | Modular monolith |
| **Time to market** | Product launch in 3 months | Modular monolith |

### Recommendation: Modular Monolith

Start with a modular monolith using Spring Modulith. Each bounded context becomes a module with:
- Its own package namespace (`com.acme.sales`, `com.acme.shipping`)
- Internal APIs hidden behind a public API surface
- Inter-module communication through application events
- Independent database schemas (logical separation within one database)

This preserves the option to extract microservices later. The bounded context boundaries are the same — only the deployment model changes. If the Pricing Engine eventually needs independent scaling (e.g., Black Friday traffic spikes), it can be extracted as a standalone service because the module boundary already enforces loose coupling.

### When to Reconsider

Extract a microservice when:
- A specific module needs independent scaling (confirmed by metrics, not speculation)
- A team grows large enough to own a full service lifecycle (5+ developers per service)
- Deployment independence is needed (one module deploys daily, others weekly)
- The bounded context boundary has been stable for 6+ months

**Key points:**
- Default to modular monolith unless you have a specific, measurable reason for microservices
- Microservices add operational complexity (networking, observability, data consistency) that must be justified
- Well-defined module boundaries make future extraction straightforward
- Make the decision based on current constraints, not hypothetical future scale
