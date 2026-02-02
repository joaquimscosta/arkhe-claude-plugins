# Doc Co-Authoring Examples

Complete templates and examples for different documentation types.

## Table of Contents

1. [Human Documentation Examples](#human-documentation-examples)
   - [Technical Proposal](#example-1-technical-proposal)
   - [Decision Document](#example-2-decision-document)
   - [Technical Spec](#example-3-technical-spec)
2. [Code Documentation Examples](#code-documentation-examples)
   - [Complete README](#example-4-complete-readme)
   - [OpenAPI Specification](#example-5-openapi-specification)
   - [Module Documentation](#example-6-module-documentation)
   - [Configuration Reference](#example-7-configuration-reference)
   - [Function Documentation](#example-8-function-documentation)

---

## Human Documentation Examples

### Example 1: Technical Proposal

```markdown
# Proposal: Migrate Authentication to OAuth2

**Author**: Jane Smith
**Date**: 2025-01-15
**Status**: Draft

## Executive Summary

We propose migrating from our custom JWT-based authentication to OAuth2 with
support for external identity providers (Google, GitHub). This enables SSO
for enterprise customers while reducing our authentication maintenance burden.

## Problem Statement

Our current authentication system has several limitations:
- No SSO support - enterprise customers must create separate credentials
- Custom JWT implementation requires ongoing security maintenance
- Password reset flows create support burden (~50 tickets/month)
- No support for MFA without building it ourselves

## Proposed Solution

Implement OAuth2 authorization server with:
- External IdP support (Google, GitHub, SAML)
- Backward compatibility with existing sessions for 6-month transition
- Self-service MFA enrollment

### Technical Approach

```mermaid
graph LR
    User --> Gateway[API Gateway]
    Gateway --> Auth[Auth Service]
    Auth --> IdP[External IdP]
    Auth --> DB[(User DB)]
```

## Alternatives Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Auth0 | Managed, fast | Cost at scale (~$50k/yr) | Too expensive |
| Keycloak | Self-hosted, free | Operational burden | Considered |
| Custom OAuth2 | Full control | Implementation time | **Selected** |

## Implementation Plan

1. **Phase 1 (4 weeks)**: OAuth2 core implementation
2. **Phase 2 (2 weeks)**: Google/GitHub integration
3. **Phase 3 (3 weeks)**: Migration tooling and dual-auth period
4. **Phase 4 (ongoing)**: User migration with deprecation of old system

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User confusion during migration | Medium | In-app guidance, support documentation |
| Token compatibility issues | High | 6-month dual-auth period |
| External IdP outages | Medium | Fallback to email/password |

## Success Metrics

- 80% of enterprise users on SSO within 6 months
- 50% reduction in auth-related support tickets
- Zero security incidents during migration

## Appendix

- [A. Current Auth Architecture](link)
- [B. OAuth2 RFC Reference](link)
```

---

### Example 2: Decision Document

```markdown
# Decision: Use PostgreSQL for Analytics Data Store

**Decision Date**: 2025-01-10
**Decision Makers**: Data Team, Platform Team
**Status**: Approved

## Context

Our analytics pipeline needs a data store for aggregated metrics. Current
options under consideration: PostgreSQL, ClickHouse, and TimescaleDB.

## Decision

We will use **PostgreSQL with TimescaleDB extension** for analytics data.

## Rationale

### Requirements

1. Store 6 months of aggregated metrics (~500GB)
2. Support time-series queries with <100ms p95 latency
3. Integrate with existing PostgreSQL tooling
4. Handle 10K writes/second during peak

### Evaluation

| Requirement | PostgreSQL | ClickHouse | TimescaleDB |
|-------------|------------|------------|-------------|
| Storage capacity | Yes | Yes | Yes |
| Query latency | Marginal | Yes | Yes |
| Existing tooling | Yes | No | Yes |
| Write throughput | No | Yes | Yes |

### Why TimescaleDB

- Maintains PostgreSQL compatibility (migrations, tooling, team expertise)
- Handles time-series workloads efficiently with hypertables
- Compression reduces storage costs by ~80%
- Single system to maintain vs. separate OLAP cluster

### Why Not ClickHouse

Despite superior raw performance:
- Requires new operational expertise
- Separate system to maintain
- Team would need training
- Our scale doesn't justify the complexity

## Consequences

**Positive:**
- Team can use existing PostgreSQL knowledge
- Single database technology to maintain
- Straightforward backup and recovery

**Negative:**
- May need to revisit if we 10x our data volume
- Some ClickHouse-specific features unavailable

## Implementation Notes

- Enable TimescaleDB extension on analytics database
- Create hypertables for time-series data
- Set up compression policy for data >7 days old
- Configure retention policy for 6-month window
```

---

### Example 3: Technical Spec

```markdown
# Technical Spec: Real-Time Notification System

**Author**: Alex Chen
**Reviewers**: Platform Team
**Status**: In Review

## Overview

Design a real-time notification system supporting push notifications,
email, and in-app messages with guaranteed delivery and user preferences.

## Goals

- Deliver notifications within 5 seconds (p95) for real-time channels
- Support 100K concurrent WebSocket connections
- Respect user notification preferences
- Ensure at-least-once delivery for critical notifications

## Non-Goals

- SMS notifications (future phase)
- Notification analytics dashboard (separate project)
- Message scheduling beyond 24 hours

## System Design

### Architecture

```mermaid
graph TB
    subgraph Producers
        API[API Services]
        Workers[Background Workers]
    end

    subgraph Core
        Queue[Message Queue]
        Router[Notification Router]
        Prefs[Preference Service]
    end

    subgraph Delivery
        Push[Push Gateway]
        Email[Email Service]
        WS[WebSocket Server]
    end

    API --> Queue
    Workers --> Queue
    Queue --> Router
    Router --> Prefs
    Router --> Push
    Router --> Email
    Router --> WS
```

### Components

#### Message Queue (Redis Streams)
- Durable message storage
- Consumer groups for scaling
- Dead letter queue for failures

#### Notification Router
- Reads from queue
- Checks user preferences
- Routes to appropriate channel(s)
- Handles retry logic

#### WebSocket Server
- Maintains persistent connections
- Horizontal scaling with Redis pub/sub
- Heartbeat for connection health

### Data Model

```sql
-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    channel VARCHAR(20)[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    read_at TIMESTAMP
);

-- User Preferences
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY,
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    preferences JSONB DEFAULT '{}'
);
```

### API Endpoints

```
POST /notifications
  - Send notification to user(s)
  - Body: { user_ids, type, payload, priority }

GET /notifications
  - List notifications for current user
  - Query: ?unread=true&limit=50

PATCH /notifications/:id/read
  - Mark notification as read

GET /notifications/preferences
PUT /notifications/preferences
  - Get/update user preferences
```

## Failure Handling

| Failure Mode | Detection | Response |
|--------------|-----------|----------|
| WebSocket disconnect | Heartbeat timeout | Queue messages, retry on reconnect |
| Push delivery failure | Provider callback | Retry 3x, then fallback to email |
| Email bounce | Webhook | Mark channel failed, alert user |
| Queue unavailable | Health check | Circuit breaker, buffer in memory |

## Security Considerations

- WebSocket connections authenticated via JWT
- Notification payload sanitized before display
- User can only access their own notifications
- Rate limiting: 100 notifications/user/hour

## Testing Plan

1. Unit tests for router logic and preference matching
2. Integration tests for each delivery channel
3. Load test: 10K concurrent connections, 1K messages/second
4. Chaos testing: Network partitions, service failures

## Rollout Plan

1. **Week 1**: Deploy to staging, internal testing
2. **Week 2**: 5% of users (opt-in beta)
3. **Week 3**: 25% rollout with monitoring
4. **Week 4**: 100% rollout

## Open Questions

- [ ] Should we support notification batching for high-volume users?
- [ ] What's the retention period for notification history?
```

---

## Code Documentation Examples

### Example 4: Complete README

```markdown
# DataProcessor

Fast, type-safe data transformation library for Node.js.

[![npm version](https://badge.fury.io/js/data-processor.svg)](https://www.npmjs.com/package/data-processor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Type-safe transformations with TypeScript support
- Streaming support for large datasets
- Built-in validation and error handling
- Extensible plugin architecture
- Zero dependencies

## Installation

```bash
npm install data-processor
```

## Quick Start

```typescript
import { DataProcessor } from 'data-processor';

const processor = new DataProcessor();

const result = await processor
  .load('data.csv')
  .transform(row => ({ ...row, total: row.price * row.quantity }))
  .filter(row => row.total > 100)
  .save('output.json');

console.log(`Processed ${result.count} records`);
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `chunkSize` | number | 1000 | Records per batch |
| `validateSchema` | boolean | true | Enable schema validation |
| `onError` | 'skip' \| 'throw' | 'throw' | Error handling mode |

```typescript
const processor = new DataProcessor({
  chunkSize: 5000,
  validateSchema: true,
  onError: 'skip'
});
```

## API Reference

### `DataProcessor`

#### `load(source: string | Stream): DataProcessor`

Load data from file path or stream.

#### `transform(fn: (row: T) => U): DataProcessor`

Apply transformation to each row.

#### `filter(predicate: (row: T) => boolean): DataProcessor`

Filter rows based on predicate.

#### `save(destination: string): Promise<Result>`

Save processed data to file.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.
```

---

### Example 5: OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: User Management API
  description: RESTful API for managing users and authentication
  version: 1.0.0
  contact:
    email: api@example.com

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

security:
  - bearerAuth: []

paths:
  /users:
    get:
      summary: List all users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, pending]
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      summary: Create a new user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'

  /users/{id}:
    get:
      summary: Get user by ID
      operationId: getUser
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - createdAt
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        status:
          type: string
          enum: [active, inactive, pending]
        createdAt:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required:
        - email
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          minLength: 8

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        totalPages:
          type: integer

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Authentication required"

    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
              details:
                type: array
                items:
                  type: string

    NotFound:
      description: Resource not found

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

### Example 6: Module Documentation

```markdown
# Authentication Module

Handles user authentication, session management, and authorization.

## Overview

The authentication module provides:
- JWT-based authentication
- Role-based access control (RBAC)
- Session management with Redis
- OAuth2 integration (Google, GitHub)

## Architecture

```mermaid
graph LR
    Client --> AuthController
    AuthController --> AuthService
    AuthService --> UserRepository
    AuthService --> TokenService
    AuthService --> SessionStore
    SessionStore --> Redis
    UserRepository --> PostgreSQL
```

## Components

### AuthService

Core authentication logic.

**Methods**:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `login` | email, password | TokenPair | Authenticate user |
| `logout` | refreshToken | void | Invalidate session |
| `refresh` | refreshToken | TokenPair | Refresh access token |
| `verify` | accessToken | UserPayload | Verify and decode token |

**Example**:

```typescript
const authService = new AuthService(userRepo, tokenService, sessionStore);

// Login
const { accessToken, refreshToken } = await authService.login(
  'user@example.com',
  'password123'
);

// Verify token
const user = await authService.verify(accessToken);
```

### TokenService

JWT token generation and validation.

**Configuration**:

```typescript
const tokenService = new TokenService({
  accessTokenSecret: process.env.ACCESS_TOKEN_SECRET,
  refreshTokenSecret: process.env.REFRESH_TOKEN_SECRET,
  accessTokenExpiry: '15m',
  refreshTokenExpiry: '7d'
});
```

### SessionStore

Redis-backed session management.

**Operations**:
- `create(userId, metadata)` - Create new session
- `get(sessionId)` - Retrieve session
- `invalidate(sessionId)` - End session
- `invalidateAll(userId)` - End all user sessions

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | Yes | - | Secret for signing tokens |
| `JWT_EXPIRY` | No | 15m | Access token expiry |
| `REDIS_URL` | Yes | - | Redis connection URL |
| `SESSION_TTL` | No | 7d | Session time-to-live |

## Error Handling

| Error | Code | Description |
|-------|------|-------------|
| `InvalidCredentials` | 401 | Wrong email or password |
| `TokenExpired` | 401 | Access token expired |
| `TokenInvalid` | 401 | Malformed or tampered token |
| `SessionNotFound` | 401 | Session invalidated |
| `InsufficientPermissions` | 403 | Missing required role |

## Security Considerations

- Tokens stored in httpOnly cookies
- Refresh tokens rotated on use
- Rate limiting on login endpoint (5/min)
- Passwords hashed with bcrypt (cost=12)
```

---

### Example 7: Configuration Reference

```markdown
# Configuration Reference

Complete configuration options for the application.

## Environment Variables

### Required

| Variable | Type | Description |
|----------|------|-------------|
| `DATABASE_URL` | string | PostgreSQL connection string |
| `REDIS_URL` | string | Redis connection string |
| `JWT_SECRET` | string | Secret for signing JWTs (min 32 chars) |

### Optional

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | number | 3000 | Server port |
| `NODE_ENV` | enum | development | Environment (development, staging, production) |
| `LOG_LEVEL` | enum | info | Logging level (debug, info, warn, error) |
| `CORS_ORIGINS` | string | * | Allowed CORS origins (comma-separated) |

## Configuration File

Create `config.yaml` in the project root:

```yaml
server:
  port: 3000
  host: 0.0.0.0

database:
  pool:
    min: 2
    max: 10
  timeout: 30000

cache:
  ttl: 3600
  prefix: "app:"

features:
  enableMetrics: true
  enableTracing: false
```

## Example .env File

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp

# Redis
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-very-long-secret-key-min-32-chars

# Server
PORT=3000
NODE_ENV=development
LOG_LEVEL=debug

# Features
ENABLE_METRICS=true
```

## Validation

Configuration is validated at startup. Invalid configuration will prevent the application from starting.

```typescript
// Validation schema
const configSchema = z.object({
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  PORT: z.number().default(3000),
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
});
```
```

---

### Example 8: Function Documentation

#### Python (Google Style)

```python
def process_transactions(
    transactions: List[Transaction],
    config: ProcessingConfig,
    *,
    dry_run: bool = False,
    batch_size: int = 100
) -> ProcessingResult:
    """Process a list of transactions according to configuration.

    Validates each transaction, applies business rules, and persists
    results to the database. Supports batch processing for large datasets.

    Args:
        transactions: List of transactions to process. Each transaction
            must have valid account_id and amount fields.
        config: Processing configuration including validation rules
            and persistence settings.
        dry_run: If True, validate without persisting. Defaults to False.
        batch_size: Number of transactions per batch. Defaults to 100.

    Returns:
        ProcessingResult containing:
            - processed_count: Number of successfully processed transactions
            - failed_count: Number of failed transactions
            - errors: List of error details for failed transactions

    Raises:
        ValidationError: If transactions list is empty or config is invalid.
        DatabaseError: If persistence fails (only when dry_run=False).

    Example:
        >>> config = ProcessingConfig(validate_amounts=True)
        >>> transactions = [Transaction(account_id=1, amount=100.00)]
        >>> result = process_transactions(transactions, config)
        >>> print(f"Processed: {result.processed_count}")
        Processed: 1

    Note:
        For transactions over 10,000 items, consider using
        process_transactions_async() for better performance.
    """
```

#### TypeScript (TSDoc)

```typescript
/**
 * Process a list of transactions according to configuration.
 *
 * Validates each transaction, applies business rules, and persists
 * results to the database. Supports batch processing for large datasets.
 *
 * @param transactions - List of transactions to process
 * @param config - Processing configuration
 * @param options - Optional processing options
 * @param options.dryRun - If true, validate without persisting (default: false)
 * @param options.batchSize - Number of transactions per batch (default: 100)
 *
 * @returns Processing result with counts and error details
 *
 * @throws {ValidationError} If transactions list is empty
 * @throws {DatabaseError} If persistence fails (when dryRun=false)
 *
 * @example
 * ```typescript
 * const result = await processTransactions(transactions, config);
 * console.log(`Processed: ${result.processedCount}`);
 * ```
 *
 * @see {@link processTransactionsAsync} for large datasets
 */
async function processTransactions(
  transactions: Transaction[],
  config: ProcessingConfig,
  options?: { dryRun?: boolean; batchSize?: number }
): Promise<ProcessingResult>
```

---

## Conversation Examples

### Workflow Offer Example

**User**: I need to write a design doc for a new caching layer.

**Claude**: I can help you write that design doc. I use a structured workflow that helps ensure the doc works well when others read it:

1. **Context Gathering**: You share all the relevant context while I ask clarifying questions
2. **Refinement & Structure**: We build each section through brainstorming and iterative editing
3. **Reader Testing**: We test the doc with a fresh Claude (no context) to catch blind spots

Would you like to try this workflow, or prefer to work freeform?

### Context Gathering Example

**Claude**: Let's start with some quick questions:

1. Who's the primary audience for this design doc?
2. What's the desired impact - what should readers take away?
3. Do you have a template or specific format to follow?
4. Any constraints I should know about (timeline, tech stack, etc.)?

Feel free to answer in shorthand.

### Brainstorming Example

**Claude**: For the "Technical Approach" section, here are some points we might include:

1. Cache invalidation strategy (TTL vs. event-based)
2. Data structures for cache keys
3. Memory limits and eviction policy
4. Cache warming on startup
5. Metrics and monitoring hooks
6. Fallback behavior when cache is unavailable
7. Serialization format (JSON, Protocol Buffers)
8. Distributed cache vs. local cache trade-offs
9. Cache penetration protection
10. Hot key handling

Which of these should we keep? Any to remove or combine? Anything important I missed?
