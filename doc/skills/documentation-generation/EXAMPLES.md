# Documentation Examples

Complete templates and examples for common documentation types.

## Example 1: Complete README

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

## Example 2: OpenAPI Specification

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

## Example 3: Module Documentation

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

## Example 4: Configuration Documentation

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

## Example 5: Function/Method Documentation

### Python (Google Style)

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

### TypeScript (TSDoc)

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
