# Actuator Endpoints

Endpoint configuration, security, and custom endpoints.

## Table of Contents

- [Endpoint Exposure Configuration](#endpoint-exposure-configuration)
  - [Development Profile](#development-profile)
  - [Production Profile](#production-profile)
- [Health Indicators](#health-indicators)
  - [Built-in Health Indicators](#built-in-health-indicators)
  - [Custom Health Indicator](#custom-health-indicator)
  - [Kotlin Health Indicator](#kotlin-health-indicator)
  - [Reactive Health Indicator](#reactive-health-indicator)
- [Health Groups (Kubernetes Probes)](#health-groups-kubernetes-probes)
- [Info Endpoint](#info-endpoint)
  - [Custom Info Contributor](#custom-info-contributor)
- [Custom Actuator Endpoint](#custom-actuator-endpoint)
- [Actuator Security](#actuator-security)
  - [Separate Security Filter Chain](#separate-security-filter-chain)
  - [Users for Actuator](#users-for-actuator)
- [Prometheus Integration](#prometheus-integration)
  - [Dependencies](#dependencies)
  - [Configuration](#configuration)
  - [Prometheus Scrape Config](#prometheus-scrape-config)
- [Graceful Shutdown](#graceful-shutdown)
- [Environment and Loggers Endpoints](#environment-and-loggers-endpoints)

## Endpoint Exposure Configuration

### Development Profile

```yaml
# application-dev.yml
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
```

### Production Profile

```yaml
# application-prod.yml
management:
  server:
    port: 8081
    address: 127.0.0.1  # Only localhost
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
    access:
      default: none
  endpoint:
    health:
      show-details: when-authorized
      access: unrestricted  # Health always accessible
    prometheus:
      access: read-only
    info:
      access: read-only
```

## Health Indicators

### Built-in Health Indicators

| Indicator | Auto-configured When |
|-----------|---------------------|
| `db` | DataSource present |
| `diskSpace` | Always |
| `redis` | RedisConnectionFactory present |
| `mongo` | MongoClient present |
| `elasticsearch` | RestClient present |
| `rabbit` | RabbitMQ connection present |
| `kafka` | KafkaAdmin present |

### Custom Health Indicator

```java
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class PaymentGatewayHealthIndicator implements HealthIndicator {

    private final PaymentGatewayClient client;
    private final CircuitBreaker circuitBreaker;

    @Override
    public Health health() {
        if (circuitBreaker.getState() == CircuitBreaker.State.OPEN) {
            return Health.down()
                .withDetail("circuit_breaker", "OPEN")
                .withDetail("reason", "Too many failures")
                .build();
        }

        try {
            PaymentGatewayStatus status = client.getStatus();

            if (!status.isOperational()) {
                return Health.outOfService()
                    .withDetail("gateway_status", status.getMessage())
                    .build();
            }

            return Health.up()
                .withDetail("gateway_version", status.getVersion())
                .withDetail("response_time_ms", status.getLatency())
                .build();

        } catch (Exception e) {
            return Health.down()
                .withException(e)
                .build();
        }
    }
}
```

### Kotlin Health Indicator

```kotlin
@Component
class PaymentGatewayHealthIndicator(
    private val client: PaymentGatewayClient,
    private val circuitBreaker: CircuitBreaker
) : HealthIndicator {

    override fun health(): Health {
        if (circuitBreaker.state == CircuitBreaker.State.OPEN) {
            return Health.down()
                .withDetail("circuit_breaker", "OPEN")
                .build()
        }

        return runCatching { client.getStatus() }
            .fold(
                onSuccess = { status ->
                    if (status.isOperational) {
                        Health.up()
                            .withDetail("gateway_version", status.version)
                            .withDetail("response_time_ms", status.latency)
                            .build()
                    } else {
                        Health.outOfService()
                            .withDetail("gateway_status", status.message)
                            .build()
                    }
                },
                onFailure = { Health.down().withException(it).build() }
            )
    }
}
```

### Reactive Health Indicator

```java
@Component
public class ReactiveExternalServiceHealthIndicator implements ReactiveHealthIndicator {

    private final WebClient webClient;

    @Override
    public Mono<Health> health() {
        return webClient.get()
            .uri("/health")
            .retrieve()
            .bodyToMono(HealthStatus.class)
            .map(status -> Health.up()
                .withDetail("service", status.name())
                .build())
            .timeout(Duration.ofSeconds(5))
            .onErrorResume(e -> Mono.just(
                Health.down()
                    .withException(e)
                    .build()
            ));
    }
}
```

## Health Groups (Kubernetes Probes)

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
        add-additional-paths: true  # Exposes /livez and /readyz
      group:
        liveness:
          include: livenessState,ping
          show-details: never
        readiness:
          include: readinessState,db,redis,kafka,customService
          show-details: when-authorized
        startup:
          include: livenessState
```

Kubernetes deployment:

```yaml
spec:
  containers:
    - name: app
      livenessProbe:
        httpGet:
          path: /actuator/health/liveness
          port: 8081
        initialDelaySeconds: 10
        periodSeconds: 10
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /actuator/health/readiness
          port: 8081
        initialDelaySeconds: 5
        periodSeconds: 5
        failureThreshold: 3
      startupProbe:
        httpGet:
          path: /actuator/health/liveness
          port: 8081
        initialDelaySeconds: 0
        periodSeconds: 5
        failureThreshold: 30  # 30 * 5 = 150s max startup time
```

## Info Endpoint

```yaml
management:
  info:
    env:
      enabled: true
    git:
      enabled: true
      mode: full
    build:
      enabled: true
    java:
      enabled: true
    os:
      enabled: true

info:
  app:
    name: "@project.name@"
    version: "@project.version@"
    description: "@project.description@"
  contact:
    team: platform-team
    slack: "#platform-support"
```

### Custom Info Contributor

```java
@Component
public class FeatureFlagsInfoContributor implements InfoContributor {

    private final FeatureFlagService featureFlags;

    @Override
    public void contribute(Info.Builder builder) {
        Map<String, Boolean> flags = featureFlags.getAllFlags();
        builder.withDetail("features", flags);
    }
}
```

## Custom Actuator Endpoint

```java
@Component
@Endpoint(id = "cache")
public class CacheEndpoint {

    private final CacheManager cacheManager;

    @ReadOperation
    public Map<String, CacheStats> caches() {
        return cacheManager.getCacheNames().stream()
            .collect(Collectors.toMap(
                name -> name,
                name -> getCacheStats(cacheManager.getCache(name))
            ));
    }

    @ReadOperation
    public CacheStats cache(@Selector String name) {
        Cache cache = cacheManager.getCache(name);
        if (cache == null) {
            throw new IllegalArgumentException("Cache not found: " + name);
        }
        return getCacheStats(cache);
    }

    @DeleteOperation
    public void clearCache(@Selector String name) {
        Cache cache = cacheManager.getCache(name);
        if (cache != null) {
            cache.clear();
        }
    }

    @WriteOperation
    public void clearAllCaches() {
        cacheManager.getCacheNames().forEach(name ->
            cacheManager.getCache(name).clear()
        );
    }

    private CacheStats getCacheStats(Cache cache) {
        // Implementation depends on cache provider
    }
}
```

## Actuator Security

### Separate Security Filter Chain

```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurity(HttpSecurity http) throws Exception {
        http
            .securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                .requestMatchers(EndpointRequest.to("prometheus")).hasRole("METRICS")
                .requestMatchers(EndpointRequest.to("loggers", "env")).hasRole("ADMIN")
                .anyRequest().hasRole("ACTUATOR")
            )
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```

### Users for Actuator

```yaml
spring:
  security:
    user:
      name: actuator
      password: ${ACTUATOR_PASSWORD}
      roles: ACTUATOR,METRICS
```

## Prometheus Integration

### Dependencies

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

### Configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
  prometheus:
    metrics:
      export:
        enabled: true
```

### Prometheus Scrape Config

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['app:8081']
    basic_auth:
      username: actuator
      password: secret
```

## Graceful Shutdown

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s

management:
  endpoint:
    health:
      probes:
        enabled: true
```

Application responds to SIGTERM:
1. Health readiness → DOWN (stops receiving traffic)
2. Waits for in-flight requests (up to 30s)
3. Closes connections
4. Shuts down

## Environment and Loggers Endpoints

```yaml
management:
  endpoint:
    env:
      show-values: when-authorized  # or 'always', 'never'
    loggers:
      enabled: true
```

Change log level at runtime:

```bash
curl -X POST http://localhost:8081/actuator/loggers/com.example \
  -H 'Content-Type: application/json' \
  -d '{"configuredLevel": "DEBUG"}'
```
