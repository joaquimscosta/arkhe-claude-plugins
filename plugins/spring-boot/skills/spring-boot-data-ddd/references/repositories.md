# Repositories & Query Patterns

Spring Data repository patterns for aggregate persistence.

## Table of Contents

- [Repository Hierarchy](#repository-hierarchy)
- [Complete Repository Example](#complete-repository-example)
  - [Java](#java)
  - [Kotlin](#kotlin)
- [Projections](#projections)
  - [Interface-Based Projection](#interface-based-projection)
  - [Class-Based Projection (Record)](#class-based-projection-record)
  - [Kotlin Data Class Projection](#kotlin-data-class-projection)
- [Specifications (Dynamic Queries)](#specifications-dynamic-queries)
  - [Java](#java-1)
  - [Kotlin](#kotlin-1)
- [EntityGraph Strategies](#entitygraph-strategies)
  - [Annotation-Based](#annotation-based)
  - [Programmatic EntityGraph](#programmatic-entitygraph)
- [Batch Operations](#batch-operations)
- [Pagination](#pagination)
- [Custom Repository Implementation](#custom-repository-implementation)

## Repository Hierarchy

| Interface | Use When |
|-----------|----------|
| `Repository<T, ID>` | Marker only, define all methods yourself |
| `CrudRepository<T, ID>` | Basic CRUD, returns `Iterable` |
| `ListCrudRepository<T, ID>` | CRUD with `List` returns |
| `PagingAndSortingRepository<T, ID>` | Add pagination/sorting |
| `JpaRepository<T, ID>` | Full JPA features: flush, batch, examples |

## Complete Repository Example

### Java

```java
public interface OrderRepository extends JpaRepository<Order, Long>,
                                        JpaSpecificationExecutor<Order> {
    
    // Derived query
    List<Order> findByStatus(OrderStatus status);
    
    // With sorting
    List<Order> findByStatusOrderByCreatedAtDesc(OrderStatus status);
    
    // Pagination
    Page<Order> findByCustomerIdValue(String customerId, Pageable pageable);
    
    // Optional for single results
    Optional<Order> findByIdAndStatus(Long id, OrderStatus status);
    
    // EntityGraph - solve N+1
    @EntityGraph(attributePaths = {"lines", "lines.product"})
    Optional<Order> findWithLinesById(Long id);
    
    // JPQL query
    @Query("SELECT o FROM Order o WHERE o.customerId.value = :customerId AND o.status = :status")
    List<Order> findByCustomerAndStatus(
        @Param("customerId") String customerId,
        @Param("status") OrderStatus status
    );
    
    // Native query
    @Query(value = "SELECT * FROM orders WHERE total_amount > :amount", nativeQuery = true)
    List<Order> findHighValueOrders(@Param("amount") BigDecimal amount);
    
    // Modifying query
    @Modifying
    @Query("UPDATE Order o SET o.status = :status WHERE o.createdAt < :before")
    int archiveOldOrders(@Param("status") OrderStatus status, @Param("before") Instant before);
    
    // Projection
    List<OrderSummary> findSummaryByStatus(OrderStatus status);
    
    // Dynamic projection
    <T> List<T> findByStatus(OrderStatus status, Class<T> type);
    
    // Exists check (efficient)
    boolean existsByCustomerIdValueAndStatus(String customerId, OrderStatus status);
    
    // Count
    long countByStatus(OrderStatus status);
    
    // Delete
    void deleteByStatusAndCreatedAtBefore(OrderStatus status, Instant before);
}
```

### Kotlin

```kotlin
interface OrderRepository : JpaRepository<Order, Long>,
                           JpaSpecificationExecutor<Order> {
    
    fun findByStatus(status: OrderStatus): List<Order>
    
    @EntityGraph(attributePaths = ["lines", "lines.product"])
    fun findWithLinesById(id: Long): Order?
    
    @Query("SELECT o FROM Order o WHERE o.customerId.value = :customerId")
    fun findByCustomerId(@Param("customerId") customerId: String): List<Order>
    
    fun findSummaryByStatus(status: OrderStatus): List<OrderSummary>
    
    fun <T> findByStatus(status: OrderStatus, type: Class<T>): List<T>
}
```

## Projections

### Interface-Based Projection

```java
public interface OrderSummary {
    Long getId();
    OrderStatus getStatus();
    Money getTotal();
    Instant getCreatedAt();
    
    // Nested projection
    CustomerInfo getCustomer();
    
    interface CustomerInfo {
        String getName();
        String getEmail();
    }
    
    // Computed value (SpEL)
    @Value("#{target.total.amount.multiply(1.1)}")
    BigDecimal getTotalWithTax();
}
```

### Class-Based Projection (Record)

Better performance - no proxy overhead:

```java
public record OrderDto(
    Long id,
    String status,
    BigDecimal totalAmount,
    Instant createdAt
) {
    // Constructor must match SELECT order
    public static OrderDto from(Order order) {
        return new OrderDto(
            order.getId(),
            order.getStatus().name(),
            order.getTotal().amount(),
            order.getCreatedAt()
        );
    }
}

// In repository
@Query("SELECT new com.example.OrderDto(o.id, o.status, o.total.amount, o.createdAt) " +
       "FROM Order o WHERE o.status = :status")
List<OrderDto> findDtoByStatus(@Param("status") OrderStatus status);
```

### Kotlin Data Class Projection

```kotlin
data class OrderDto(
    val id: Long,
    val status: String,
    val totalAmount: BigDecimal,
    val createdAt: Instant
) {
    companion object {
        fun from(order: Order) = OrderDto(
            id = order.id!!,
            status = order.status.name,
            totalAmount = order.total.amount,
            createdAt = order.createdAt!!
        )
    }
}
```

## Specifications (Dynamic Queries)

### Java

```java
public class OrderSpecifications {
    
    public static Specification<Order> hasStatus(OrderStatus status) {
        return (root, query, cb) -> cb.equal(root.get("status"), status);
    }
    
    public static Specification<Order> belongsToCustomer(CustomerId customerId) {
        return (root, query, cb) -> cb.equal(root.get("customerId"), customerId);
    }
    
    public static Specification<Order> createdAfter(Instant date) {
        return (root, query, cb) -> cb.greaterThan(root.get("createdAt"), date);
    }
    
    public static Specification<Order> totalGreaterThan(Money amount) {
        return (root, query, cb) -> cb.greaterThan(
            root.get("total").get("amount"), 
            amount.amount()
        );
    }
}

// Usage
List<Order> orders = orderRepository.findAll(
    hasStatus(SUBMITTED)
        .and(belongsToCustomer(customerId))
        .and(createdAfter(lastWeek))
);
```

### Kotlin

```kotlin
object OrderSpecifications {
    
    fun hasStatus(status: OrderStatus) = Specification<Order> { root, _, cb ->
        cb.equal(root.get<OrderStatus>("status"), status)
    }
    
    fun belongsToCustomer(customerId: CustomerId) = Specification<Order> { root, _, cb ->
        cb.equal(root.get<CustomerId>("customerId"), customerId)
    }
    
    fun createdAfter(date: Instant) = Specification<Order> { root, _, cb ->
        cb.greaterThan(root.get("createdAt"), date)
    }
}

// Usage with Kotlin and()
val orders = orderRepository.findAll(
    hasStatus(SUBMITTED) and belongsToCustomer(customerId) and createdAfter(lastWeek)
)
```

## EntityGraph Strategies

### Annotation-Based

```java
@EntityGraph(attributePaths = {"lines", "lines.product"})
Optional<Order> findWithLinesById(Long id);

// Named graph defined on entity
@NamedEntityGraph(
    name = "Order.withLines",
    attributeNodes = @NamedAttributeNode(value = "lines", subgraph = "lines-product"),
    subgraphs = @NamedSubgraph(name = "lines-product", attributeNodes = @NamedAttributeNode("product"))
)
@Entity
public class Order { ... }

// Usage
@EntityGraph(value = "Order.withLines")
Optional<Order> findWithGraphById(Long id);
```

### Programmatic EntityGraph

```java
@Repository
public class OrderRepositoryCustomImpl implements OrderRepositoryCustom {
    
    @PersistenceContext
    private EntityManager em;
    
    @Override
    public Optional<Order> findWithDynamicGraph(Long id, String... attributePaths) {
        EntityGraph<Order> graph = em.createEntityGraph(Order.class);
        for (String path : attributePaths) {
            graph.addAttributeNodes(path);
        }
        
        Map<String, Object> hints = Map.of("jakarta.persistence.fetchgraph", graph);
        return Optional.ofNullable(em.find(Order.class, id, hints));
    }
}
```

## Batch Operations

```java
// Batch insert - configure in properties
// spring.jpa.properties.hibernate.jdbc.batch_size=50
// spring.jpa.properties.hibernate.order_inserts=true

@Transactional
public void createOrders(List<Order> orders) {
    for (int i = 0; i < orders.size(); i++) {
        repository.save(orders.get(i));
        if (i % 50 == 0) {
            repository.flush();
            entityManager.clear();
        }
    }
}

// Bulk update (bypasses entity lifecycle)
@Modifying(clearAutomatically = true)
@Query("UPDATE Order o SET o.status = :status WHERE o.id IN :ids")
int bulkUpdateStatus(@Param("ids") List<Long> ids, @Param("status") OrderStatus status);
```

## Pagination

```java
// Controller
@GetMapping
public Page<OrderSummary> list(
    @RequestParam(defaultValue = "SUBMITTED") OrderStatus status,
    @PageableDefault(size = 20, sort = "createdAt", direction = DESC) Pageable pageable
) {
    return orderRepository.findSummaryByStatus(status, pageable);
}

// Custom pageable
Pageable pageable = PageRequest.of(0, 20, Sort.by(DESC, "createdAt", "id"));

// Slice (no count query - more efficient for infinite scroll)
Slice<Order> findSliceByStatus(OrderStatus status, Pageable pageable);
```

## Custom Repository Implementation

```java
// Custom interface
public interface OrderRepositoryCustom {
    List<Order> findWithComplexCriteria(OrderSearchCriteria criteria);
}

// Implementation (naming convention: {RepositoryName}Impl)
@Repository
public class OrderRepositoryImpl implements OrderRepositoryCustom {
    
    @PersistenceContext
    private EntityManager em;
    
    @Override
    public List<Order> findWithComplexCriteria(OrderSearchCriteria criteria) {
        CriteriaBuilder cb = em.getCriteriaBuilder();
        CriteriaQuery<Order> query = cb.createQuery(Order.class);
        Root<Order> root = query.from(Order.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.status() != null) {
            predicates.add(cb.equal(root.get("status"), criteria.status()));
        }
        if (criteria.minTotal() != null) {
            predicates.add(cb.ge(root.get("total").get("amount"), criteria.minTotal()));
        }
        
        query.where(predicates.toArray(new Predicate[0]));
        query.orderBy(cb.desc(root.get("createdAt")));
        
        return em.createQuery(query)
            .setMaxResults(criteria.limit())
            .getResultList();
    }
}

// Main repository extends custom
public interface OrderRepository extends JpaRepository<Order, Long>, OrderRepositoryCustom {
    // ...
}
```
