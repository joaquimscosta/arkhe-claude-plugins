# Controllers & Validation

Detailed patterns for REST controllers and Bean Validation 3.1.

## Table of Contents

- [Controller Structure](#controller-structure)
  - [Complete CRUD Controller (Java)](#complete-crud-controller-java)
  - [Kotlin Controller](#kotlin-controller)
- [Bean Validation](#bean-validation)
  - [Request DTOs with Validation](#request-dtos-with-validation)
  - [Kotlin Request DTOs](#kotlin-request-dtos)
  - [Validation Groups](#validation-groups)
  - [Custom Validator](#custom-validator)
  - [Cross-Field Validation](#cross-field-validation)
- [Content Negotiation](#content-negotiation)
- [Response Patterns](#response-patterns)
  - [ResponseEntity Usage](#responseentity-usage)
- [Path Variables & Query Parameters](#path-variables--query-parameters)
- [File Upload](#file-upload)
- [Async Controller Methods](#async-controller-methods)

## Controller Structure

### Complete CRUD Controller (Java)

```java
@RestController
@RequestMapping("/api/v1/orders")
@Validated
@Tag(name = "Orders", description = "Order management endpoints")
public class OrderController {
    
    private final OrderService orderService;
    private final OrderAssembler assembler;
    
    public OrderController(OrderService orderService, OrderAssembler assembler) {
        this.orderService = orderService;
        this.assembler = assembler;
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "Get order by ID")
    public ResponseEntity<OrderDto> getById(@PathVariable Long id) {
        return orderService.findById(id)
            .map(assembler::toDto)
            .map(ResponseEntity::ok)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }
    
    @GetMapping
    @Operation(summary = "List orders with pagination")
    public Page<OrderSummary> list(
        @RequestParam(required = false) OrderStatus status,
        @RequestParam(required = false) @DateTimeFormat(iso = ISO.DATE) LocalDate from,
        @RequestParam(required = false) @DateTimeFormat(iso = ISO.DATE) LocalDate to,
        @PageableDefault(size = 20, sort = "createdAt", direction = DESC) Pageable pageable
    ) {
        return orderService.search(new OrderSearchCriteria(status, from, to), pageable);
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create new order")
    public ResponseEntity<OrderDto> create(
        @Valid @RequestBody CreateOrderRequest request,
        UriComponentsBuilder uriBuilder
    ) {
        Order order = orderService.create(request);
        URI location = uriBuilder.path("/api/v1/orders/{id}").buildAndExpand(order.getId()).toUri();
        return ResponseEntity.created(location).body(assembler.toDto(order));
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update order")
    public OrderDto update(
        @PathVariable Long id,
        @Valid @RequestBody UpdateOrderRequest request
    ) {
        return assembler.toDto(orderService.update(id, request));
    }
    
    @PatchMapping("/{id}/status")
    @Operation(summary = "Update order status")
    public OrderDto updateStatus(
        @PathVariable Long id,
        @Valid @RequestBody UpdateStatusRequest request
    ) {
        return assembler.toDto(orderService.updateStatus(id, request.status()));
    }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "Delete order")
    public void delete(@PathVariable Long id) {
        orderService.delete(id);
    }
    
    @PostMapping("/{id}/submit")
    @Operation(summary = "Submit order for processing")
    public OrderDto submit(@PathVariable Long id) {
        return assembler.toDto(orderService.submit(id));
    }
}
```

### Kotlin Controller

```kotlin
@RestController
@RequestMapping("/api/v1/orders")
@Validated
class OrderController(
    private val orderService: OrderService,
    private val assembler: OrderAssembler
) {
    @GetMapping("/{id}")
    fun getById(@PathVariable id: Long): ResponseEntity<OrderDto> =
        orderService.findById(id)
            ?.let { assembler.toDto(it) }
            ?.let { ResponseEntity.ok(it) }
            ?: throw OrderNotFoundException(id)
    
    @PostMapping
    fun create(
        @Valid @RequestBody request: CreateOrderRequest,
        uriBuilder: UriComponentsBuilder
    ): ResponseEntity<OrderDto> {
        val order = orderService.create(request)
        val location = uriBuilder.path("/api/v1/orders/{id}").buildAndExpand(order.id).toUri()
        return ResponseEntity.created(location).body(assembler.toDto(order))
    }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    fun delete(@PathVariable id: Long) = orderService.delete(id)
}
```

## Bean Validation

### Request DTOs with Validation

```java
public record CreateOrderRequest(
    @NotNull(message = "Customer ID is required")
    CustomerId customerId,
    
    @NotEmpty(message = "Order must have at least one line")
    @Size(max = 100, message = "Maximum 100 lines per order")
    List<@Valid OrderLineRequest> lines,
    
    @Size(max = 500, message = "Notes must be under 500 characters")
    String notes
) {}

public record OrderLineRequest(
    @NotNull(message = "Product ID is required")
    ProductId productId,
    
    @Min(value = 1, message = "Quantity must be at least 1")
    @Max(value = 1000, message = "Quantity cannot exceed 1000")
    int quantity,
    
    @DecimalMin(value = "0.01", message = "Price must be positive")
    BigDecimal unitPrice
) {}
```

### Kotlin Request DTOs

```kotlin
data class CreateOrderRequest(
    @field:NotNull(message = "Customer ID is required")
    val customerId: CustomerId,
    
    @field:NotEmpty(message = "Order must have at least one line")
    @field:Size(max = 100)
    val lines: List<@Valid OrderLineRequest>,
    
    @field:Size(max = 500)
    val notes: String? = null
)

data class OrderLineRequest(
    @field:NotNull
    val productId: ProductId,
    
    @field:Min(1) @field:Max(1000)
    val quantity: Int,
    
    @field:DecimalMin("0.01")
    val unitPrice: BigDecimal
)
```

**Note:** Kotlin requires `@field:` prefix for annotations to target the backing field.

### Validation Groups

```java
// Define groups
public interface OnCreate {}
public interface OnUpdate {}

// Use in DTO
public record OrderRequest(
    @Null(groups = OnCreate.class, message = "ID must be null on create")
    @NotNull(groups = OnUpdate.class, message = "ID required on update")
    Long id,
    
    @NotNull(groups = {OnCreate.class, OnUpdate.class})
    String name
) {}

// Apply in controller
@PostMapping
public OrderDto create(@Validated(OnCreate.class) @RequestBody OrderRequest request) { }

@PutMapping("/{id}")
public OrderDto update(@Validated(OnUpdate.class) @RequestBody OrderRequest request) { }
```

### Custom Validator

```java
// Annotation
@Target({FIELD, PARAMETER})
@Retention(RUNTIME)
@Constraint(validatedBy = ValidOrderStatusTransitionValidator.class)
public @interface ValidOrderStatusTransition {
    String message() default "Invalid status transition";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
    OrderStatus from();
}

// Validator
public class ValidOrderStatusTransitionValidator 
    implements ConstraintValidator<ValidOrderStatusTransition, OrderStatus> {
    
    private OrderStatus fromStatus;
    
    @Override
    public void initialize(ValidOrderStatusTransition annotation) {
        this.fromStatus = annotation.from();
    }
    
    @Override
    public boolean isValid(OrderStatus toStatus, ConstraintValidatorContext context) {
        if (toStatus == null) return true;
        return fromStatus.canTransitionTo(toStatus);
    }
}
```

### Cross-Field Validation

```java
@Target(TYPE)
@Retention(RUNTIME)
@Constraint(validatedBy = DateRangeValidator.class)
public @interface ValidDateRange {
    String message() default "End date must be after start date";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class DateRangeValidator implements ConstraintValidator<ValidDateRange, DateRangeRequest> {
    @Override
    public boolean isValid(DateRangeRequest request, ConstraintValidatorContext context) {
        if (request.startDate() == null || request.endDate() == null) return true;
        return request.endDate().isAfter(request.startDate());
    }
}

@ValidDateRange
public record DateRangeRequest(
    @NotNull LocalDate startDate,
    @NotNull LocalDate endDate
) {}
```

## Content Negotiation

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    // Multiple representations
    @GetMapping(value = "/{id}", produces = {APPLICATION_JSON_VALUE, APPLICATION_XML_VALUE})
    public OrderDto getById(@PathVariable Long id) {
        return orderService.findById(id);
    }
    
    // Specific format endpoint
    @GetMapping(value = "/{id}/pdf", produces = APPLICATION_PDF_VALUE)
    public ResponseEntity<byte[]> getAsPdf(@PathVariable Long id) {
        byte[] pdf = orderService.generatePdf(id);
        return ResponseEntity.ok()
            .header(CONTENT_DISPOSITION, "attachment; filename=order-" + id + ".pdf")
            .body(pdf);
    }
    
    // Accept specific content type
    @PostMapping(consumes = APPLICATION_JSON_VALUE)
    public OrderDto createFromJson(@Valid @RequestBody CreateOrderRequest request) { }
    
    @PostMapping(consumes = "text/csv")
    public List<OrderDto> createFromCsv(@RequestBody String csvContent) { }
}
```

## Response Patterns

### ResponseEntity Usage

```java
// Created with location header
@PostMapping
public ResponseEntity<OrderDto> create(@Valid @RequestBody CreateOrderRequest request) {
    Order order = orderService.create(request);
    return ResponseEntity
        .created(URI.create("/api/orders/" + order.getId()))
        .body(OrderDto.from(order));
}

// No content
@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable Long id) {
    orderService.delete(id);
    return ResponseEntity.noContent().build();
}

// Conditional response
@GetMapping("/{id}")
public ResponseEntity<OrderDto> getById(
    @PathVariable Long id,
    @RequestHeader(value = IF_NONE_MATCH, required = false) String ifNoneMatch
) {
    Order order = orderService.findById(id);
    String etag = "\"" + order.getVersion() + "\"";
    
    if (etag.equals(ifNoneMatch)) {
        return ResponseEntity.status(NOT_MODIFIED).build();
    }
    
    return ResponseEntity.ok()
        .eTag(etag)
        .body(OrderDto.from(order));
}
```

## Path Variables & Query Parameters

```java
@GetMapping("/{orderId}/lines/{lineId}")
public OrderLineDto getLine(
    @PathVariable Long orderId,
    @PathVariable Long lineId
) { }

// Matrix variables (rare)
@GetMapping("/filter/{criteria}")
public List<OrderDto> filter(
    @MatrixVariable Map<String, String> criteria
) { }
// URL: /filter/status=SUBMITTED;minAmount=100

// Optional query params
@GetMapping
public Page<OrderDto> search(
    @RequestParam(required = false) String query,
    @RequestParam(defaultValue = "createdAt") String sortBy,
    @RequestParam(defaultValue = "DESC") Sort.Direction direction,
    Pageable pageable
) { }
```

## File Upload

```java
@PostMapping(value = "/{id}/attachments", consumes = MULTIPART_FORM_DATA_VALUE)
public AttachmentDto uploadAttachment(
    @PathVariable Long id,
    @RequestParam("file") MultipartFile file,
    @RequestParam(required = false) String description
) {
    if (file.isEmpty()) {
        throw new BadRequestException("File is empty");
    }
    if (file.getSize() > 10_000_000) {
        throw new BadRequestException("File too large (max 10MB)");
    }
    return attachmentService.store(id, file, description);
}

// Multiple files
@PostMapping(value = "/{id}/attachments/batch", consumes = MULTIPART_FORM_DATA_VALUE)
public List<AttachmentDto> uploadMultiple(
    @PathVariable Long id,
    @RequestParam("files") List<MultipartFile> files
) {
    return files.stream()
        .map(f -> attachmentService.store(id, f, null))
        .toList();
}
```

## Async Controller Methods

```java
@GetMapping("/{id}/report")
public CompletableFuture<ReportDto> generateReport(@PathVariable Long id) {
    return CompletableFuture.supplyAsync(() -> reportService.generate(id));
}

// Streaming response
@GetMapping(value = "/{id}/events", produces = TEXT_EVENT_STREAM_VALUE)
public SseEmitter streamEvents(@PathVariable Long id) {
    SseEmitter emitter = new SseEmitter(30_000L);
    eventService.subscribe(id, event -> {
        try {
            emitter.send(event);
        } catch (IOException e) {
            emitter.completeWithError(e);
        }
    });
    return emitter;
}
```
