---
title: "Offline-First Mobile Architecture: Patterns & Implementation"
version: "1.0.0"
status: Published
created: 2026-04-04
last_updated: 2026-04-04
slug: offline-first-mobile-architecture
aliases: ["offline-first", "local-first-mobile", "sync-patterns", "outbox-pattern-mobile"]
tags: ["offline-first", "mobile", "sync", "conflict-resolution", "workmanager", "sqldelight", "outbox-pattern", "kmp", "android", "kotlin"]
promoted_at: 2026-04-04T14:52:54.576861Z
last_refreshed: 2026-04-04T14:52:28.163874+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->

# Offline-First Mobile Architecture: Patterns & Implementation

## Overview

Offline-first mobile architecture treats the network as an enhancement, not a requirement. Rather than trying to handle connectivity loss as an exception, the local database is the source of truth and all reads and writes happen locally first. The network is used purely to synchronise state with a backend when convenient.

This approach is essential for mobile applications deployed in environments with unreliable connectivity — rural areas, underground transit, developing-market networks, point-of-sale terminals — and is becoming the preferred model even for well-connected apps because it produces faster, more resilient user experiences.

This document covers the full spectrum: terminology, architecture patterns, sync strategies, conflict resolution, background processing, outbox pattern, idempotency, queue management, and a POS case study, with practical Kotlin/KMP examples throughout.

---

## 1. Terminology: Local-First vs Offline-First vs Offline-Capable

These terms are often used interchangeably but carry distinct meanings:

| Term | Definition | Network model | Data ownership |
|---|---|---|---|
| **Offline-capable** | App works without network but degrades gracefully | Network preferred, fallback to cache | Server owns data |
| **Offline-first** | App works identically offline; sync is async background process | Network optional; local state always consistent | Shared ownership |
| **Local-first** | Data lives on device permanently; sync is a replication mechanism | Network is one peer among many | User/device owns data |

**Offline-capable** is the legacy model: fetch data, cache it, show stale on error. Write operations queue and retry. The local copy is derivative, not authoritative.

**Offline-first** (this document's focus) inverts this. Every write goes local first. The local database is always consistent. The sync engine propagates changes to the server asynchronously and resolves conflicts. The app never blocks on network.

**Local-first** (Kleppmann et al., 2019) goes further: data belongs to the user's devices and a server is just another peer. CRDTs and peer-to-peer replication are central. This is appropriate for collaborative editors (Figma, Linear) but over-engineered for most mobile apps.

**For most mobile applications, offline-first is the right target.** Local-first adds significant complexity (CRDT design, peer discovery) that only pays off for real-time collaborative use cases.

---

## 2. Core Architecture

### 2.1 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mobile Device                            │
│                                                                 │
│  UI Layer (Compose/Views)                                       │
│       │  reads from StateFlow/LiveData                         │
│       ▼                                                         │
│  ViewModel / Presenter                                          │
│       │  calls repository                                       │
│       ▼                                                         │
│  Repository (single API surface)                                │
│       │                          │                             │
│       ▼                          ▼                             │
│  LocalDataSource            RemoteDataSource                   │
│  (SQLDelight / Room)        (Retrofit / Ktor)                  │
│       │                          │                             │
│       ▼                          ▼                             │
│  Local SQLite DB ──── Sync ──── Outbox Table                   │
│                       Engine         │                         │
│                          │           ▼                         │
│                          │    WorkManager                      │
└──────────────────────────┼──────────┼──────────────────────────┘
                           │          │  (when online)
                           ▼          ▼
                    ┌─────────────────────┐
                    │   Backend API /     │
                    │   Sync Service      │
                    └─────────────────────┘
```

**Key invariants:**
1. The UI **never** reads directly from the network — only from the local DB.
2. All writes go to the local DB **first**, then to the outbox.
3. The sync engine processes the outbox independently of the UI.
4. Reads are always fast (local I/O); perceived latency comes only from sync lag.

### 2.2 Trust Boundaries

| Layer | Trusts | Does not trust |
|---|---|---|
| UI | Local DB state | Network availability |
| Repository | Local DB as truth | Remote API response timing |
| Sync engine | Idempotency keys | Duplicate delivery from server |
| Backend | Server state as canonical | Client clocks, client-generated IDs for sensitive fields |

The local DB is trusted for **read operations** and **user intent** (pending writes). The server is trusted as the **canonical reconciled state** after sync. Client clocks are never trusted for ordering across devices — use server timestamps or HLC.

### 2.3 Optimistic UI Pattern

Optimistic UI renders the local pending state immediately, before the server confirms the write:

```kotlin
// ViewModel
fun submitTransaction(tx: Transaction) {
    viewModelScope.launch {
        // 1. Write locally with PENDING status — UI updates instantly
        repository.saveLocal(tx.copy(syncStatus = SyncStatus.PENDING))
        // 2. Outbox receives the write; WorkManager schedules sync
        outbox.enqueue(OutboxEntry(entityId = tx.id, operation = Operation.CREATE))
    }
}
```

The UI shows the item immediately with a "pending" badge. On sync success the badge disappears. On permanent failure the item is marked with an error state and the user is notified.

**When NOT to use optimistic UI:** fiscal documents (tax receipts must be server-confirmed before display), payment authorisations, or any operation where the server may reject the write for business-logic reasons.

---

## 3. Local-First Architecture with SQLDelight

### 3.1 SQLDelight as Source of Truth

SQLDelight generates type-safe Kotlin from `.sq` files. It integrates with coroutines Flow, making it natural to observe live queries.

```sql
-- src/main/sqldelight/com/pos/Transaction.sq

CREATE TABLE Transaction (
  id              TEXT NOT NULL PRIMARY KEY,   -- client UUID/ULID
  receipt_number  TEXT NOT NULL,               -- M-{DEVICE4}-{YYYYMMDD}-{NNN}
  device_id       TEXT NOT NULL,
  total_amount    REAL NOT NULL,
  currency        TEXT NOT NULL DEFAULT 'CVE',
  status          TEXT NOT NULL DEFAULT 'PENDING_SYNC', -- PENDING_SYNC | SYNCED | SYNC_ERROR
  created_at      INTEGER NOT NULL,            -- epoch millis, set by device
  synced_at       INTEGER,                     -- null until confirmed by server
  server_id       TEXT,                        -- server-assigned ID, null until synced
  version         INTEGER NOT NULL DEFAULT 1,  -- optimistic lock version
  is_deleted      INTEGER NOT NULL DEFAULT 0   -- soft delete for sync
);

-- Queries
getAll:
SELECT * FROM Transaction WHERE is_deleted = 0 ORDER BY created_at DESC;

getPendingSync:
SELECT * FROM Transaction WHERE status = 'PENDING_SYNC' AND is_deleted = 0;

upsert:
INSERT OR REPLACE INTO Transaction VALUES ?;

markSynced:
UPDATE Transaction SET status = 'SYNCED', synced_at = ?, server_id = ? WHERE id = ?;
```

```kotlin
// Repository
class TransactionRepository(
    private val db: AppDatabase,
    private val api: SyncApi,
) {
    // Reads always from local DB — returns Flow for live updates
    fun observeAll(): Flow<List<Transaction>> =
        db.transactionQueries.getAll().asFlow().mapToList(Dispatchers.IO)

    // Writes: local first, then outbox
    suspend fun save(tx: Transaction) {
        db.transaction {  // SQLDelight DB transaction
            db.transactionQueries.upsert(tx)
            db.outboxQueries.enqueue(tx.id, Operation.UPSERT, Clock.System.now())
        }
    }
}
```

### 3.2 Schema Design for Offline

Every synced entity needs:

| Column | Purpose |
|---|---|
| `id` (client UUID/ULID) | Stable identity before server confirmation |
| `server_id` | Populated after first successful sync |
| `sync_status` | PENDING_SYNC / SYNCED / SYNC_ERROR / CONFLICT |
| `created_at` | Device clock (epoch ms); used for ordering within device |
| `updated_at` | Last local modification time |
| `synced_at` | Last confirmed sync time |
| `version` | Optimistic lock counter, incremented on each write |
| `is_deleted` | Soft-delete flag (never hard-delete before sync) |
| `checksum` / `etag` | Optional: for delta sync validation |

### 3.3 Cache Invalidation Strategies

| Strategy | When to use | Trade-off |
|---|---|---|
| **TTL-based** | Catalog, pricing data | Simple; stale data possible |
| **Version-based** | Inventory, config | Requires server version endpoint |
| **Event-driven** | Push notification triggers re-sync | Real-time but needs push infrastructure |
| **Pull-on-foreground** | Any entity | Simple; adds latency on app open |
| **Dirty-flag** | User-modified entities | Fine-grained; requires tracking |

For POS applications, a hybrid approach works well: TTL for catalog (1 hour), event-driven for price changes, dirty-flag for inventory adjustments.

---

## 4. Sync Strategies

### 4.1 Strategy Comparison

```
┌────────────────────┬────────────────┬───────────────────┬──────────────────────┐
│ Strategy           │ Direction      │ Data volume       │ Conflict risk        │
├────────────────────┼────────────────┼───────────────────┼──────────────────────┤
│ Push-only          │ Client→Server  │ Low (mutations)   │ Low (server wins)    │
│ Pull-only          │ Server→Client  │ Medium (catalog)  │ None (read-only)     │
│ Bi-directional     │ Both           │ Medium-High       │ Medium-High          │
│ Delta sync         │ Both           │ Low (diffs only)  │ Low-Medium           │
│ Batch sync         │ Both           │ High (bulk)       │ Medium               │
│ Incremental cursor │ Server→Client  │ Low (since cursor)│ None (append-only)   │
└────────────────────┴────────────────┴───────────────────┴──────────────────────┘
```

### 4.2 Push-Only Sync (Outbox → Server)

Simplest model: client writes go into the outbox, a background worker drains the outbox by calling the server API. Server always accepts (idempotent) or rejects with a conflict error.

```kotlin
class OutboxSyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val pending = db.outboxQueries.getPending().executeAsList()
        if (pending.isEmpty()) return Result.success()

        return try {
            val chunks = pending.chunked(BATCH_SIZE)
            for (chunk in chunks) {
                val response = api.pushChanges(chunk.toSyncPayload())
                db.transaction {
                    response.accepted.forEach { db.outboxQueries.markProcessed(it.localId) }
                    response.conflicts.forEach { db.outboxQueries.markConflict(it.localId, it.reason) }
                }
            }
            Result.success()
        } catch (e: IOException) {
            if (runAttemptCount < MAX_RETRIES) Result.retry() else Result.failure()
        }
    }

    companion object {
        const val BATCH_SIZE = 50
        const val MAX_RETRIES = 5
    }
}
```

### 4.3 Pull-Only Sync (Server → Client)

Used for read-only datasets: product catalog, price lists, tax rates, configuration. The server owns the data; the device caches a copy.

```kotlin
class CatalogSyncWorker(...) : CoroutineWorker(...) {
    override suspend fun doWork(): Result {
        val lastSync = prefs.getLastCatalogSync()
        val delta = api.getCatalogDelta(since = lastSync)  // delta endpoint
        db.transaction {
            delta.products.forEach { db.productQueries.upsert(it) }
            delta.deletedIds.forEach { db.productQueries.softDelete(it) }
        }
        prefs.setLastCatalogSync(delta.serverTimestamp)
        return Result.success()
    }
}
```

### 4.4 Delta Sync with Cursors

The server returns only records changed since a cursor (timestamp or sequence number). The client stores the cursor and sends it on the next request.

```
GET /sync/catalog?since=1712000000000&limit=500
→ { items: [...], next_cursor: "1712010000000", has_more: false }
```

Cursor design considerations:
- **Timestamp cursors**: simple but vulnerable to clock skew; use server-assigned timestamps.
- **Sequence cursors**: monotonic, reliable, but require global sequence or per-entity sequences.
- **Opaque tokens**: server encodes cursor type internally; clients treat as opaque string.

### 4.5 Priority-Based Sync

Not all data is equally urgent. A priority queue ensures critical operations reach the server first:

```kotlin
enum class SyncPriority(val value: Int) {
    CRITICAL(0),   // Cash transactions, fiscal documents
    HIGH(1),       // Inventory adjustments
    NORMAL(2),     // Catalog pulls, config updates
    LOW(3)         // Analytics, audit logs
}

// Outbox table
CREATE TABLE Outbox (
  id          TEXT PRIMARY KEY,
  entity_id   TEXT NOT NULL,
  operation   TEXT NOT NULL,
  priority    INTEGER NOT NULL DEFAULT 2,
  payload     TEXT NOT NULL,       -- JSON
  idempotency_key TEXT NOT NULL,
  attempts    INTEGER NOT NULL DEFAULT 0,
  created_at  INTEGER NOT NULL,
  process_after INTEGER,           -- NULL = process immediately
  processed_at  INTEGER            -- NULL = pending
);

-- Process by priority, then by creation time
getPending:
SELECT * FROM Outbox
WHERE processed_at IS NULL AND (process_after IS NULL OR process_after <= :now)
ORDER BY priority ASC, created_at ASC
LIMIT :batchSize;
```

---

## 5. Conflict Resolution Patterns

### 5.1 Strategy Overview

```
┌──────────────────────────┬──────────────────────────────┬────────────────────────────┐
│ Strategy                 │ Best for                     │ Trade-off                  │
├──────────────────────────┼──────────────────────────────┼────────────────────────────┤
│ Last-Write-Wins (LWW)    │ Profile data, settings       │ Silent data loss possible  │
│ Server-authoritative     │ Prices, tax rates, inventory │ Client changes rejected    │
│ Client-authoritative     │ Notes, drafts, offline forms │ Server state overwritten   │
│ Hybrid Logical Clocks    │ Distributed ordering         │ Requires HLC library       │
│ CRDTs                    │ Collaborative real-time      │ High design complexity     │
│ Merge functions          │ Inventory counters           │ Domain-specific code       │
│ Domain-specific rules    │ POS transactions             │ Most correct for business  │
└──────────────────────────┴──────────────────────────────┴────────────────────────────┘
```

### 5.2 Last-Write-Wins (LWW)

The record with the highest timestamp wins. Simple and widely used. Relies on monotonic clocks or NTP-synchronized device clocks.

```kotlin
data class ConflictResolution(
    val winner: SyncRecord,
    val loser: SyncRecord,
    val strategy: String
)

fun resolveWithLWW(local: SyncRecord, remote: SyncRecord): ConflictResolution {
    return if (local.updatedAt >= remote.updatedAt) {
        ConflictResolution(winner = local, loser = remote, strategy = "LWW_LOCAL")
    } else {
        ConflictResolution(winner = remote, loser = local, strategy = "LWW_REMOTE")
    }
}
```

**Risk:** Two devices writing at nearly the same millisecond will lose one update silently. Use HLC to avoid this.

### 5.3 Hybrid Logical Clocks (HLC)

HLCs combine physical time with a logical counter. They guarantee: if event A happened before event B causally, A's HLC < B's HLC. Solves the "same millisecond" problem.

```kotlin
data class HLC(val wallTime: Long, val logical: Int) : Comparable<HLC> {
    override fun compareTo(other: HLC): Int {
        val timeCmp = wallTime.compareTo(other.wallTime)
        return if (timeCmp != 0) timeCmp else logical.compareTo(other.logical)
    }

    fun tick(receivedHLC: HLC? = null): HLC {
        val now = System.currentTimeMillis()
        return when {
            receivedHLC == null -> {
                if (now > wallTime) HLC(now, 0)
                else HLC(wallTime, logical + 1)
            }
            now > wallTime && now > receivedHLC.wallTime ->
                HLC(now, 0)
            receivedHLC.wallTime > wallTime ->
                HLC(receivedHLC.wallTime, receivedHLC.logical + 1)
            else ->
                HLC(wallTime, maxOf(logical, receivedHLC.logical) + 1)
        }
    }
}
```

Store the HLC alongside each record; use it for both ordering and LWW comparison.

### 5.4 CRDTs (Conflict-free Replicated Data Types)

CRDTs are data structures that can be merged automatically without conflicts. Operations must be commutative, associative, and idempotent.

**Appropriate for mobile offline-first when:**
- Multiple devices edit the same record concurrently.
- Network partitions are frequent and long.
- Data types map naturally to CRDT semantics.

**Common CRDT types:**

| CRDT | Use case | Mobile example |
|---|---|---|
| G-Counter | Increment-only counter | View counts, like counts |
| PN-Counter | Increment/decrement counter | Inventory adjustments |
| LWW-Register | Single mutable value | User profile field |
| OR-Set (Observed-Remove) | Add/remove set | Shopping cart, tag list |
| RGA (Replicated Growable Array) | Ordered list with insert/delete | Document editing |

```kotlin
// PN-Counter CRDT for inventory
data class PNCounter(
    val increments: Map<String, Long> = emptyMap(),  // deviceId → count
    val decrements: Map<String, Long> = emptyMap()   // deviceId → count
) {
    fun increment(deviceId: String, amount: Long = 1): PNCounter =
        copy(increments = increments + (deviceId to (increments[deviceId] ?: 0) + amount))

    fun decrement(deviceId: String, amount: Long = 1): PNCounter =
        copy(decrements = decrements + (deviceId to (decrements[decrements] ?: 0) + amount))

    fun value(): Long =
        increments.values.sum() - decrements.values.sum()

    fun merge(other: PNCounter): PNCounter = PNCounter(
        increments = (increments.keys + other.increments.keys).associateWith { k ->
            maxOf(increments[k] ?: 0, other.increments[k] ?: 0)
        },
        decrements = (decrements.keys + other.decrements.keys).associateWith { k ->
            maxOf(decrements[k] ?: 0, other.decrements[k] ?: 0)
        }
    )
}
```

**CRDTs are over-engineered for most mobile apps.** Use them selectively for counters and sets where concurrent mutation is expected. Avoid for complex business entities where domain rules are simpler and more maintainable.

### 5.5 Domain-Specific Rules (POS Example)

POS transactions are the best example of domain-specific conflict resolution. The rules are:

1. **Transactions are immutable once created.** No conflict is possible because no update path exists.
2. **Prices are server-authoritative.** Client-side price changes are rejected; a catalog sync re-fetches correct prices.
3. **Inventory is server-reconciled.** Clients submit adjustments (PN-Counter semantics); server computes final stock.
4. **Transaction numbering is device-scoped.** `M-{DEVICE4}-{YYYYMMDD}-{NNN}` ensures global uniqueness without coordination.

```kotlin
// Immutable transaction — conflict resolution is trivial: never conflict
@Immutable
data class POSTransaction(
    val id: String,                    // ULID, client-generated
    val receiptNumber: String,         // M-{DEVICE4}-{YYYYMMDD}-{NNN}
    val deviceId: String,
    val lines: List<TransactionLine>,  // immutable list
    val totalAmount: Long,             // in minor currency units (centavos)
    val currency: String,
    val paymentMethod: PaymentMethod,
    val createdAt: Long,               // device HLC wall time
    val syncStatus: SyncStatus
) {
    init {
        // Enforce immutability at construction time
        require(totalAmount >= 0) { "Transaction total cannot be negative" }
        require(lines.isNotEmpty()) { "Transaction must have at least one line" }
    }
}
```

---

## 6. Background Processing (Android)

### 6.1 WorkManager — The Right Tool

WorkManager is the canonical solution for deferrable, guaranteed background work on Android. It survives app restarts and device reboots, respects battery optimization, and integrates with Doze mode.

```kotlin
// Scheduling a sync worker
fun scheduleSyncWork(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)  // only when online
        .setRequiresBatteryNotLow(false)                // don't block on battery
        .build()

    // Periodic sync — every 15 minutes (WorkManager minimum)
    val periodicSync = PeriodicWorkRequestBuilder<OutboxSyncWorker>(
        repeatInterval = 15,
        repeatIntervalTimeUnit = TimeUnit.MINUTES
    )
        .setConstraints(constraints)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
        .addTag("outbox-sync")
        .build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "outbox-sync",
        ExistingPeriodicWorkPolicy.KEEP,  // don't replace if already scheduled
        periodicSync
    )
}

// Immediate one-shot sync — triggered by network reconnect
fun triggerImmediateSync(context: Context) {
    val immediateSync = OneTimeWorkRequestBuilder<OutboxSyncWorker>()
        .setConstraints(
            Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
        )
        .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "outbox-sync-immediate",
        ExistingWorkPolicy.REPLACE,
        immediateSync
    )
}
```

### 6.2 Exponential Backoff

WorkManager's built-in backoff handles transient failures. For custom retry logic:

```kotlin
class OutboxSyncWorker(...) : CoroutineWorker(...) {
    override suspend fun doWork(): Result {
        return try {
            performSync()
            Result.success()
        } catch (e: HttpException) {
            when (e.code()) {
                429, 503 -> Result.retry()  // rate-limited or server overloaded
                400, 422 -> {
                    // Unrecoverable: mark entry as permanently failed
                    recordPermanentFailure(e)
                    Result.failure()
                }
                else -> if (runAttemptCount < MAX_RETRIES) Result.retry() else Result.failure()
            }
        } catch (e: IOException) {
            Result.retry()  // Network error — always retry
        }
    }
    // Backoff schedule: 30s, 1m, 2m, 4m, 8m (WorkManager doubles each time)
}
```

### 6.3 Doze Mode and Battery Optimization

Android's Doze mode defers background work when the device is idle and unplugged. WorkManager handles this transparently: work is queued and executed in maintenance windows.

**Implications for POS apps:**
- Don't rely on exact timing for sync. Use event-driven triggers (network reconnect) instead.
- For truly critical operations (fiscal document submission), use a **Foreground Service** with a persistent notification — Doze mode does not affect foreground services.

```kotlin
// Foreground service for fiscal document submission
class FiscalDocumentSyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildSyncNotification())
        serviceScope.launch {
            try {
                submitPendingFiscalDocuments()
            } finally {
                stopSelf()
            }
        }
        return START_NOT_STICKY
    }
}
```

### 6.4 Connectivity-Triggered Sync

Register a `NetworkCallback` to trigger immediate sync when connectivity is restored:

```kotlin
class NetworkAwareSyncTrigger(private val context: Context) {

    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    private val callback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            // Network restored: schedule immediate outbox drain
            triggerImmediateSync(context)
        }
    }

    fun register() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        connectivityManager.registerNetworkCallback(request, callback)
    }

    fun unregister() {
        connectivityManager.unregisterNetworkCallback(callback)
    }
}
```

---

## 7. Outbox Pattern

### 7.1 Transactional Outbox

The outbox guarantees that a business write (e.g., save a transaction) and its sync intent are committed atomically. Without the outbox, a crash between "write entity" and "queue sync" would leave data unsynced silently.

```
Write Transaction + Enqueue Outbox Entry
─────────────────────────────────────────
           │
    SQLite BEGIN TRANSACTION
           │
    INSERT INTO transactions (...)
    INSERT INTO outbox (entity_id, op, ...)
           │
    COMMIT
           │
    (if crash here, both writes survive)
```

```kotlin
// Atomic write + outbox enqueue
suspend fun saveTransaction(tx: POSTransaction) {
    db.transaction {  // single SQLite transaction
        db.transactionQueries.insert(tx.toEntity())
        db.outboxQueries.enqueue(
            OutboxEntry(
                id = ULID.generate(),
                entityId = tx.id,
                entityType = "TRANSACTION",
                operation = "CREATE",
                payload = json.encodeToString(tx),
                idempotencyKey = tx.id,  // tx.id is stable; safe to use as idempotency key
                priority = SyncPriority.CRITICAL.value,
                createdAt = System.currentTimeMillis()
            )
        )
    }
}
```

### 7.2 Outbox Processing Pipeline

```
┌──────────────┐    poll    ┌──────────────┐    HTTP    ┌──────────────┐
│   Outbox     │──────────►│  Sync Worker  │──────────►│  Backend API │
│   Table      │           │  (WorkManager)│           │              │
└──────────────┘           └──────┬────────┘           └──────┬───────┘
                                  │                           │
                             ┌────▼────┐                 ┌───▼──────┐
                             │ Mark    │                 │ Idempotent│
                             │Processed│                 │ upsert    │
                             └─────────┘                 └──────────┘
```

### 7.3 Idempotency in the Outbox

Each outbox entry carries an `idempotency_key`. The server uses this key to deduplicate re-submitted requests (caused by retry after network timeout where the server actually processed the request).

```kotlin
// Server-side idempotency (conceptual)
// POST /api/transactions
// Header: Idempotency-Key: 01HV7QXXXXXX
// → Server checks: has this key been processed?
//   YES → return cached response (201 or 200)
//   NO  → process and store result keyed by idempotency_key

data class OutboxEntry(
    val id: String,            // outbox entry ID (ULID)
    val entityId: String,      // ID of the entity being synced
    val idempotencyKey: String, // = entityId for creates; entityId+version for updates
    val payload: String,        // serialised entity or delta
    val attempts: Int = 0,
    val maxAttempts: Int = 10,
    val processAfter: Long? = null,  // for scheduled retries
    val processedAt: Long? = null,   // null = pending
    val failedAt: Long? = null,
    val failureReason: String? = null
)
```

### 7.4 Compaction

When an entity is updated multiple times before sync, the outbox accumulates redundant entries. Compaction merges them:

```kotlin
// Compaction: if multiple updates to the same entity exist, keep only the latest
fun compactOutbox() {
    db.transaction {
        // Find entities with multiple pending entries
        val duplicates = db.outboxQueries.findDuplicateEntities().executeAsList()
        for (entityId in duplicates) {
            val entries = db.outboxQueries.getPendingForEntity(entityId).executeAsList()
            val latest = entries.maxByOrNull { it.createdAt } ?: continue
            val toDelete = entries.filter { it.id != latest.id }
            toDelete.forEach { db.outboxQueries.delete(it.id) }
        }
    }
}
```

**Compaction is safe only for update operations.** Never compact across CREATE → DELETE (that would silently drop the entity).

---

## 8. Idempotency and Deduplication

### 8.1 Client-Generated IDs

Using client-generated IDs means the entity has a stable identity before server confirmation. This enables optimistic UI and outbox deduplication.

| ID Type | Sortable | Collision-safe | Readable | Use case |
|---|---|---|---|---|
| UUID v4 | No | Yes | No | General purpose |
| ULID | Yes (time-prefixed) | Yes | Better | Recommended for synced entities |
| CUID2 | Partial | Yes | Good | Web APIs |
| Device-scoped seq | Yes | Yes (per device) | Excellent | Receipt numbers |

```kotlin
// ULID generation (no third-party library needed)
object ULID {
    private val ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    private val random = java.security.SecureRandom()

    fun generate(): String {
        val timestamp = System.currentTimeMillis()
        val sb = StringBuilder(26)
        // 10 chars timestamp
        var t = timestamp
        for (i in 9 downTo 0) {
            sb.insert(0, ENCODING[(t % 32).toInt()])
            t /= 32
        }
        // 16 chars randomness
        repeat(16) { sb.append(ENCODING[random.nextInt(32)]) }
        return sb.toString()
    }
}
```

### 8.2 Device-Based Transaction Numbering (POS)

Receipt numbers must be human-readable, sequential within a device, and unique globally. The pattern `M-{DEVICE4}-{YYYYMMDD}-{NNN}` achieves this:

- `M` — merchant/mode prefix
- `{DEVICE4}` — last 4 chars of device ID
- `{YYYYMMDD}` — date for daily reset
- `{NNN}` — zero-padded daily sequence starting at 001

```kotlin
class ReceiptNumberGenerator(
    private val deviceId: String,
    private val db: AppDatabase
) {
    suspend fun next(date: LocalDate): String {
        return db.transaction(noEnclosing = false) {
            val device4 = deviceId.takeLast(4).uppercase()
            val dateStr = date.format(DateTimeFormatter.BASIC_ISO_DATE)  // YYYYMMDD
            val lastSeq = db.sequenceQueries.getLastSequence(device4, dateStr)
                .executeAsOneOrNull() ?: 0
            val nextSeq = lastSeq + 1
            db.sequenceQueries.upsertSequence(device4, dateStr, nextSeq)
            "M-$device4-$dateStr-${nextSeq.toString().padStart(3, '0')}"
        }
    }
}
```

This sequence is stored in SQLite and is durable across app restarts. No server coordination required.

---

## 9. Connectivity-Aware UX

### 9.1 Network State Detection

```kotlin
// Expose network state as Flow
fun observeNetworkState(context: Context): Flow<NetworkState> = callbackFlow {
    val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    val callback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) { trySend(NetworkState.CONNECTED) }
        override fun onLost(network: Network) { trySend(NetworkState.DISCONNECTED) }
        override fun onCapabilitiesChanged(n: Network, caps: NetworkCapabilities) {
            val state = when {
                caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> NetworkState.WIFI
                caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> NetworkState.CELLULAR
                else -> NetworkState.CONNECTED
            }
            trySend(state)
        }
    }

    val request = NetworkRequest.Builder()
        .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        .build()
    cm.registerNetworkCallback(request, callback)
    awaitClose { cm.unregisterNetworkCallback(callback) }
}

enum class NetworkState { WIFI, CELLULAR, DISCONNECTED, CONNECTED }
```

### 9.2 Offline Indicator and Sync Status UX

```
┌─────────────────────────────────────────────────────────────────┐
│  [☁ Syncing... 3 pending]        [⚠ Offline — 12 pending]     │
│                                                                 │
│  Transaction #M-A3F2-20260404-001   ● PENDING          [retry] │
│  Transaction #M-A3F2-20260404-002   ✓ SYNCED                   │
│  Transaction #M-A3F2-20260404-003   ✗ SYNC ERROR      [retry]  │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
// Compose UI for sync status indicator
@Composable
fun SyncStatusBar(syncState: SyncState, pendingCount: Int) {
    when {
        syncState == SyncState.SYNCING ->
            SyncBanner(text = "Syncing... $pendingCount pending", color = MaterialTheme.colorScheme.tertiary)
        pendingCount > 0 && syncState == SyncState.OFFLINE ->
            SyncBanner(text = "Offline — $pendingCount pending", color = MaterialTheme.colorScheme.error)
        pendingCount == 0 ->
            Unit  // All synced, no banner needed
    }
}
```

### 9.3 Graceful Degradation Patterns

| Scenario | Graceful behaviour |
|---|---|
| Network unavailable | Hide sync-dependent features (e.g., real-time inventory), show cached data |
| Partial sync failure | Show error badge on specific items; allow manual retry |
| Stale catalog detected | Prompt user: "Prices may be outdated. Sync now?" |
| Auth token expired | Queue changes locally, trigger re-auth flow, resume sync |
| Conflicting edit | Show diff to user with accept/reject options (for non-POS apps) |

---

## 10. Case Study: POS Offline Transaction Flow

### 10.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  POS Device (Android tablet)                                    │
│                                                                 │
│  [Cashier UI]                                                   │
│       │                                                         │
│  ┌────▼────────────────────────────────────┐                   │
│  │  Local SQLite (SQLDelight)               │                   │
│  │  ┌──────────────┐  ┌────────────────┐   │                   │
│  │  │ transactions  │  │    outbox      │   │                   │
│  │  │ (immutable)   │  │  (queue)       │   │                   │
│  │  └──────────────┘  ├────────────────┤   │                   │
│  │  ┌──────────────┐  │ fiscal_docs    │   │                   │
│  │  │   catalog    │  │ (queue, prio 0)│   │                   │
│  │  │ (cached)     │  └────────────────┘   │                   │
│  │  └──────────────┘                       │                   │
│  └─────────────────────────────────────────┘                   │
│       │                                                         │
│  [WorkManager]                                                  │
│  ├─ OutboxSyncWorker (15min periodic + on-connect immediate)    │
│  ├─ CatalogSyncWorker (1hr periodic)                            │
│  └─ FiscalDocumentService (foreground, when online)             │
└─────────────────────────────────────────────────────────────────┘
                     │   (when network available)
                     ▼
            ┌────────────────┐
            │  Backend API   │
            │  (cloud)       │
            └────────────────┘
```

### 10.2 Cash Transaction Flow (Fully Offline)

```
1. Cashier scans items → lines built from local catalog
2. Customer pays cash → amount computed locally
3. Receipt generated locally with number M-A3F2-20260404-001
4. Transaction written to SQLite (status=PENDING_SYNC)
5. Outbox entry created atomically (priority=CRITICAL)
6. Receipt printed immediately from local printer
   ────────────────────────────────────────────────────
   [at this point the customer leaves — receipt is final]
   ────────────────────────────────────────────────────
7. WorkManager OutboxSyncWorker fires (online or deferred)
8. Transaction POSTed to server with idempotency key = tx.id
9. Server confirms → tx.status = SYNCED
10. If fiscal document required: FiscalDocumentService enqueues
    to tax authority API (priority=CRITICAL, foreground service)
```

### 10.3 Catalog Sync (Server → Device)

Prices and products are server-authoritative. The device refreshes the catalog every hour or on demand:

```
Server sends delta:
{ products: [updated/new], deletedIds: ["p123"], serverTimestamp: 1712000000000 }

Device:
1. Upsert received products (SQLDelight INSERT OR REPLACE)
2. Soft-delete removed products (is_deleted = 1)
3. Store serverTimestamp as cursor for next delta pull
4. UI re-queries local DB → catalog refreshed without network dependency
```

### 10.4 Inventory Reconciliation

Inventory is complex: multiple devices sell from the same stock. The pattern used:

1. **Device tracks adjustments, not absolute quantities** (PN-Counter semantics).
2. On sync, device submits `{ productId, adjustment: -2, deviceId, timestamp }` — not absolute stock.
3. Server aggregates all device adjustments and computes current stock.
4. Server pushes canonical stock back to all devices on next pull.

This avoids read-modify-write conflicts between devices and works correctly when devices are offline for extended periods.

### 10.5 Fiscal Document Queue

Many jurisdictions require real-time fiscal document submission to a tax authority API. When offline, documents are queued locally and submitted as soon as connectivity is available:

```kotlin
// Fiscal documents get highest priority and use a foreground service
// to ensure they are submitted even if the app is in the background.

data class FiscalDocument(
    val id: String,            // ULID
    val transactionId: String,
    val fiscalCode: String?,   // assigned by tax authority after submission
    val status: FiscalStatus,  // PENDING / SUBMITTED / ACCEPTED / REJECTED
    val payload: String,       // serialised XML/JSON for tax authority
    val submittedAt: Long?,
    val receiptNumber: String  // M-{DEVICE4}-{YYYYMMDD}-{NNN}
)

enum class FiscalStatus { PENDING, SUBMITTED, ACCEPTED, REJECTED, PERMANENT_FAILURE }
```

**Fiscal document conflict resolution:** There is none. Transactions are immutable; documents are append-only. The only "conflict" is a rejection by the tax authority API (malformed document or business-rule violation), which triggers a human-review workflow.

### 10.6 Multi-Device Scenarios

| Scenario | Handling |
|---|---|
| Two devices sell same item simultaneously | PN-Counter inventory tracking; server reconciles |
| Device A has stale catalog, device B has fresh catalog | Each device syncs independently; stale catalog triggers re-pull |
| Receipt number collision (both reset on same day) | Impossible by design: DEVICE4 scopes sequence per device |
| One device offline for 3 days | Outbox accumulates; bulk push on reconnect; compaction reduces payload size |
| Manager voids transaction on device A, cashier re-sells on device B | Voids are server-confirmed (not optimistic); device B won't see the item as available until sync |

---

## 11. KMP (Kotlin Multiplatform) Considerations

When targeting both Android and iOS with KMP, the sync layer can be shared but platform-specific background processing is required:

```kotlin
// Shared (commonMain) — sync logic, outbox, DB queries
expect class BackgroundSyncScheduler {
    fun schedulePeriodicSync()
    fun scheduleImmediateSync()
    fun cancel()
}

// Android (androidMain)
actual class BackgroundSyncScheduler(private val context: Context) {
    actual fun schedulePeriodicSync() { /* WorkManager */ }
    actual fun scheduleImmediateSync() { /* OneTimeWorkRequest expedited */ }
    actual fun cancel() { WorkManager.getInstance(context).cancelAllWorkByTag("sync") }
}

// iOS (iosMain)
actual class BackgroundSyncScheduler {
    actual fun schedulePeriodicSync() {
        // BGTaskScheduler.shared.register(forTaskWithIdentifier:...)
        // BGProcessingTaskRequest for catalog sync
    }
    actual fun scheduleImmediateSync() {
        // URLSession background transfer or BGAppRefreshTask
    }
    actual fun cancel() { /* BGTaskScheduler cancel */ }
}
```

**iOS background modes** relevant to offline-first:
- `fetch` (BGAppRefreshTask) — periodic background refresh, 30 seconds budget.
- `processing` (BGProcessingTask) — longer operations (catalog sync), requires charging or sufficient battery.
- `remote-notifications` — push-triggered sync (most reliable for time-sensitive sync).
- URLSession background download/upload — for large payload sync, survives app termination.

---

## 12. Summary: Decision Guide

```
Is your app's core workflow usable without network?
├─ NO  → Offline-capable with graceful degradation
└─ YES → Offline-first (this document)
         │
         ├─ Does data need real-time multi-user collaboration?
         │   ├─ YES → Consider local-first + CRDTs (high complexity)
         │   └─ NO  → Offline-first with outbox + sync
         │
         ├─ What sync direction do you need?
         │   ├─ Client→Server only → Push outbox
         │   ├─ Server→Client only → Pull with cursor
         │   └─ Bi-directional     → Outbox + delta pull + conflict resolution
         │
         ├─ What conflict resolution?
         │   ├─ Simple user data    → LWW or server-authoritative
         │   ├─ Counters (inventory)→ PN-Counter or server-merge
         │   ├─ Transactions (POS)  → Immutable → no conflict possible
         │   └─ Collaborative data  → CRDTs or OT
         │
         └─ Background processing
             ├─ Android → WorkManager (deferrable) + Foreground Service (critical)
             └─ iOS     → BGTaskScheduler + URLSession background
```

---

## References

1. Kleppmann, M. et al. (2019). **Local-first software: You own your data, in spite of the cloud.** Ink & Switch. https://www.inkandswitch.com/local-first/

2. Kleppmann, M. (2017). **Designing Data-Intensive Applications.** O'Reilly. https://dataintensive.net/

3. Richardson, C. **Transactional Outbox Pattern.** microservices.io. https://microservices.io/patterns/data/transactional-outbox.html

4. Kulkarni, S. et al. (2014). **Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases.** SUNY Buffalo. https://cse.buffalo.edu/tech-reports/2014-04.pdf

5. Shapiro, M. et al. (2011). **A Comprehensive Study of Convergent and Commutative Replicated Data Types.** INRIA. https://inria.hal.science/inria-00555588

6. Google. **WorkManager — Schedule tasks with WorkManager.** Android Developers. https://developer.android.com/topic/libraries/architecture/workmanager

7. Google. **Optimize for Doze and App Standby.** Android Developers. https://developer.android.com/training/monitoring-device-state/doze-standby

8. Google. **ConnectivityManager NetworkCallback.** Android Developers. https://developer.android.com/reference/android/net/ConnectivityManager.NetworkCallback

9. Cash App. **SQLDelight Documentation.** https://cashapp.github.io/sqldelight/

10. ULID Community. **Universally Unique Lexicographically Sortable Identifier.** https://github.com/ulid/spec

11. Acolyer, A. (2015). **A comprehensive study of CRDTs.** The Morning Paper. https://blog.acolyer.org/2015/03/18/a-comprehensive-study-of-convergent-and-commutative-replicated-data-types/

12. Apple. **BGTaskScheduler — Background Tasks.** Apple Developer Documentation. https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler

13. JetBrains. **Kotlin Multiplatform — Background work.** https://kotlinlang.org/docs/multiplatform.html

14. Google I/O 2022. **Build apps that work offline.** https://www.youtube.com/watch?v=C35tIblzlzc

15. Caboz, S. (2023). **Delta sync with cursors — engineering patterns.** Notion Engineering. https://www.notion.so/blog/how-we-built-notions-real-time-collaboration

16. Perron, M. & Jiang, L. (2021). **Operational Transformation FAQ.** https://operational-transformation.github.io/

17. **cabo-verde-pos** (internal). Offline-first POS for Cabo Verde: SQLDelight, outbox pattern, WorkManager, device-based receipt numbering `M-{DEVICE4}-{YYYYMMDD}-{NNN}`.
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

_Add project-specific notes, implementation references, and team knowledge here._

<!-- TEAM-NOTES: End -->
