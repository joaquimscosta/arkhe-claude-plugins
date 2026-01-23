# WebFlux Reactive Patterns

Spring WebFlux for non-blocking reactive APIs.

## Table of Contents

- [When to Use WebFlux](#when-to-use-webflux)
- [Annotated Controllers](#annotated-controllers)
  - [Java](#java)
  - [Kotlin with Coroutines](#kotlin-with-coroutines)
- [Functional Router](#functional-router)
  - [Java](#java-1)
  - [Kotlin coRouter DSL](#kotlin-corouter-dsl)
- [Reactive Operators Patterns](#reactive-operators-patterns)
- [WebTestClient](#webtestclient)
- [Server-Sent Events (SSE)](#server-sent-events-sse)
- [WebSocket](#websocket)
- [Critical WebFlux Rules](#critical-webflux-rules)

## When to Use WebFlux

| Use WebFlux | Use MVC (with Virtual Threads) |
|-------------|--------------------------------|
| 10k+ concurrent connections | Standard REST APIs |
| Streaming real-time data | JPA/JDBC databases |
| Reactive databases (R2DBC, MongoDB Reactive) | Team unfamiliar with reactive |
| Microservices with many remote calls | Simpler debugging needed |
| Event-driven architectures | Blocking libraries in stack |

**Spring Boot 4 recommendation:** With Virtual Threads (`spring.threads.virtual.enabled=true`), MVC handles high concurrency without WebFlux complexity.

## Annotated Controllers

### Java

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    private final OrderService orderService;
    
    @GetMapping("/{id}")
    public Mono<OrderDto> getById(@PathVariable Long id) {
        return orderService.findById(id)
            .map(OrderDto::from)
            .switchIfEmpty(Mono.error(new OrderNotFoundException(id)));
    }
    
    @GetMapping
    public Flux<OrderDto> list(@RequestParam(required = false) OrderStatus status) {
        return orderService.findByStatus(status)
            .map(OrderDto::from);
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<OrderDto> create(@Valid @RequestBody Mono<CreateOrderRequest> request) {
        return request
            .flatMap(orderService::create)
            .map(OrderDto::from);
    }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@PathVariable Long id) {
        return orderService.delete(id);
    }
    
    // Streaming response
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<OrderDto> streamOrders() {
        return orderService.streamNewOrders()
            .map(OrderDto::from);
    }
}
```

### Kotlin with Coroutines

```kotlin
@RestController
@RequestMapping("/api/orders")
class OrderController(private val orderService: OrderService) {
    
    @GetMapping("/{id}")
    suspend fun getById(@PathVariable id: Long): OrderDto =
        orderService.findById(id)?.let { OrderDto.from(it) }
            ?: throw OrderNotFoundException(id)
    
    @GetMapping
    fun list(@RequestParam status: OrderStatus?): Flow<OrderDto> =
        orderService.findByStatus(status).map { OrderDto.from(it) }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    suspend fun create(@Valid @RequestBody request: CreateOrderRequest): OrderDto =
        OrderDto.from(orderService.create(request))
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    suspend fun delete(@PathVariable id: Long) = orderService.delete(id)
}
```

## Functional Router

### Java

```java
@Configuration
public class OrderRouter {
    
    @Bean
    public RouterFunction<ServerResponse> orderRoutes(OrderHandler handler) {
        return RouterFunctions.route()
            .path("/api/orders", builder -> builder
                .GET("/{id}", accept(APPLICATION_JSON), handler::getById)
                .GET("", accept(APPLICATION_JSON), handler::list)
                .POST("", contentType(APPLICATION_JSON), handler::create)
                .DELETE("/{id}", handler::delete)
            )
            .filter(this::errorHandler)
            .build();
    }
    
    private Mono<ServerResponse> errorHandler(
            ServerRequest request,
            HandlerFunction<ServerResponse> next
    ) {
        return next.handle(request)
            .onErrorResume(OrderNotFoundException.class, e ->
                ServerResponse.notFound().build())
            .onErrorResume(IllegalArgumentException.class, e ->
                ServerResponse.badRequest()
                    .bodyValue(ProblemDetail.forStatusAndDetail(
                        HttpStatus.BAD_REQUEST, e.getMessage())));
    }
}

@Component
public class OrderHandler {
    
    private final OrderService orderService;
    
    public Mono<ServerResponse> getById(ServerRequest request) {
        Long id = Long.valueOf(request.pathVariable("id"));
        return orderService.findById(id)
            .flatMap(order -> ServerResponse.ok().bodyValue(OrderDto.from(order)))
            .switchIfEmpty(ServerResponse.notFound().build());
    }
    
    public Mono<ServerResponse> list(ServerRequest request) {
        Optional<OrderStatus> status = request.queryParam("status")
            .map(OrderStatus::valueOf);
        
        Flux<OrderDto> orders = orderService.findByStatus(status.orElse(null))
            .map(OrderDto::from);
        
        return ServerResponse.ok().body(orders, OrderDto.class);
    }
    
    public Mono<ServerResponse> create(ServerRequest request) {
        return request.bodyToMono(CreateOrderRequest.class)
            .flatMap(orderService::create)
            .flatMap(order -> ServerResponse
                .created(URI.create("/api/orders/" + order.getId()))
                .bodyValue(OrderDto.from(order)));
    }
    
    public Mono<ServerResponse> delete(ServerRequest request) {
        Long id = Long.valueOf(request.pathVariable("id"));
        return orderService.delete(id)
            .then(ServerResponse.noContent().build());
    }
}
```

### Kotlin coRouter DSL

```kotlin
@Configuration
class OrderRouter(private val handler: OrderHandler) {
    
    @Bean
    fun routes() = coRouter {
        "/api/orders".nest {
            accept(APPLICATION_JSON).nest {
                GET("/{id}", handler::getById)
                GET("", handler::list)
            }
            contentType(APPLICATION_JSON).nest {
                POST("", handler::create)
            }
            DELETE("/{id}", handler::delete)
        }
        
        onError<OrderNotFoundException> { _, _ ->
            ServerResponse.notFound().buildAndAwait()
        }
    }
}

@Component
class OrderHandler(private val orderService: OrderService) {
    
    suspend fun getById(request: ServerRequest): ServerResponse {
        val id = request.pathVariable("id").toLong()
        return orderService.findById(id)
            ?.let { ServerResponse.ok().bodyValueAndAwait(OrderDto.from(it)) }
            ?: ServerResponse.notFound().buildAndAwait()
    }
    
    suspend fun list(request: ServerRequest): ServerResponse {
        val status = request.queryParamOrNull("status")?.let { OrderStatus.valueOf(it) }
        val orders = orderService.findByStatus(status).map { OrderDto.from(it) }
        return ServerResponse.ok().bodyAndAwait(orders)
    }
    
    suspend fun create(request: ServerRequest): ServerResponse {
        val body = request.awaitBody<CreateOrderRequest>()
        val order = orderService.create(body)
        return ServerResponse
            .created(URI.create("/api/orders/${order.id}"))
            .bodyValueAndAwait(OrderDto.from(order))
    }
    
    suspend fun delete(request: ServerRequest): ServerResponse {
        val id = request.pathVariable("id").toLong()
        orderService.delete(id)
        return ServerResponse.noContent().buildAndAwait()
    }
}
```

## Reactive Operators Patterns

```java
// Chain operations
public Mono<OrderDto> processOrder(Long orderId) {
    return orderRepository.findById(orderId)
        .switchIfEmpty(Mono.error(new OrderNotFoundException(orderId)))
        .flatMap(order -> {
            order.process();
            return orderRepository.save(order);
        })
        .doOnSuccess(order -> log.info("Processed order {}", order.getId()))
        .map(OrderDto::from);
}

// Parallel execution
public Mono<OrderSummary> getOrderWithDetails(Long orderId) {
    Mono<Order> orderMono = orderRepository.findById(orderId);
    Mono<Customer> customerMono = orderMono
        .flatMap(o -> customerService.findById(o.getCustomerId()));
    Mono<List<Product>> productsMono = orderMono
        .flatMapMany(o -> productService.findByIds(o.getProductIds()))
        .collectList();
    
    return Mono.zip(orderMono, customerMono, productsMono)
        .map(tuple -> new OrderSummary(tuple.getT1(), tuple.getT2(), tuple.getT3()));
}

// Error handling
public Mono<OrderDto> createWithFallback(CreateOrderRequest request) {
    return orderService.create(request)
        .map(OrderDto::from)
        .onErrorResume(ServiceUnavailableException.class, e -> {
            log.warn("Service unavailable, using fallback");
            return Mono.just(OrderDto.pending());
        })
        .timeout(Duration.ofSeconds(5))
        .onErrorMap(TimeoutException.class, e -> 
            new ServiceUnavailableException("Order service timeout"));
}

// Retry with backoff
public Mono<Order> createWithRetry(CreateOrderRequest request) {
    return orderService.create(request)
        .retryWhen(Retry.backoff(3, Duration.ofMillis(100))
            .filter(e -> e instanceof TransientException)
            .onRetryExhaustedThrow((spec, signal) -> signal.failure()));
}
```

## WebTestClient

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OrderApiTest {
    
    @Autowired
    private WebTestClient webClient;
    
    @Test
    void createOrder_ValidInput_ReturnsCreated() {
        var request = new CreateOrderRequest(
            CustomerId.generate(),
            List.of(new OrderLineRequest(ProductId.generate(), 2, BigDecimal.TEN))
        );
        
        webClient.post()
            .uri("/api/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue(request)
            .exchange()
            .expectStatus().isCreated()
            .expectHeader().exists("Location")
            .expectBody()
            .jsonPath("$.id").isNotEmpty()
            .jsonPath("$.status").isEqualTo("DRAFT");
    }
    
    @Test
    void getOrder_NotFound_ReturnsProblemDetail() {
        webClient.get()
            .uri("/api/orders/99999")
            .exchange()
            .expectStatus().isNotFound()
            .expectBody()
            .jsonPath("$.type").value(containsString("not-found"))
            .jsonPath("$.status").isEqualTo(404);
    }
    
    @Test
    void streamOrders_ReturnsServerSentEvents() {
        webClient.get()
            .uri("/api/orders/stream")
            .accept(MediaType.TEXT_EVENT_STREAM)
            .exchange()
            .expectStatus().isOk()
            .expectHeader().contentTypeCompatibleWith(MediaType.TEXT_EVENT_STREAM)
            .returnResult(OrderDto.class)
            .getResponseBody()
            .take(3)
            .collectList()
            .block();
    }
}
```

## Server-Sent Events (SSE)

```java
@GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<OrderEvent>> streamEvents() {
    return orderEventPublisher.getEvents()
        .map(event -> ServerSentEvent.<OrderEvent>builder()
            .id(event.getId().toString())
            .event(event.getType().name())
            .data(event)
            .retry(Duration.ofSeconds(5))
            .build());
}

// Client consumption
WebClient.create("http://localhost:8080")
    .get()
    .uri("/api/orders/events")
    .accept(MediaType.TEXT_EVENT_STREAM)
    .retrieve()
    .bodyToFlux(new ParameterizedTypeReference<ServerSentEvent<OrderEvent>>() {})
    .subscribe(event -> {
        log.info("Received event: {}", event.data());
    });
```

## WebSocket

```java
@Configuration
@EnableWebFlux
public class WebSocketConfig {
    
    @Bean
    public HandlerMapping handlerMapping(OrderWebSocketHandler handler) {
        Map<String, WebSocketHandler> map = Map.of("/ws/orders", handler);
        SimpleUrlHandlerMapping mapping = new SimpleUrlHandlerMapping();
        mapping.setUrlMap(map);
        mapping.setOrder(-1);
        return mapping;
    }
}

@Component
public class OrderWebSocketHandler implements WebSocketHandler {
    
    private final OrderEventPublisher publisher;
    
    @Override
    public Mono<Void> handle(WebSocketSession session) {
        Flux<WebSocketMessage> messages = publisher.getEvents()
            .map(event -> session.textMessage(toJson(event)));
        
        return session.send(messages);
    }
}
```

## Critical WebFlux Rules

1. **Never block** — No `.block()`, `Thread.sleep()`, or blocking I/O
2. **Use reactive all the way** — One blocking call blocks the event loop
3. **Subscribe carefully** — Missing subscription = nothing happens
4. **Handle errors** — Use `onErrorResume`, `onErrorMap`, not try-catch
5. **Backpressure** — Use `limitRate()`, `buffer()` for fast producers
6. **Context propagation** — Use `contextWrite()` for MDC, security context
