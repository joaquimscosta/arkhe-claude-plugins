---
title: "Sync Engine Landscape for Kotlin/KMP Mobile"
version: "1.0.0"
status: Published
created: 2026-07-28
last_updated: 2026-07-28
slug: sync-engine-landscape
aliases: ["sync engines", "offline sync backend", "powersync kotlin", "local-first backend comparison", "mobile sync engine landscape", "ditto vs powersync"]
tags: ["sync-engine", "offline-first", "kotlin", "kmp", "android", "powersync", "firebase", "electricsql", "ditto", "crdt", "cr-sqlite", "store5", "pos", "local-first"]
promoted_at: 2026-07-28T00:00:00Z
last_refreshed: 2026-07-28T00:00:00Z
sources: []
---

# Sync Engine Landscape for Kotlin/KMP Mobile

## Executive Summary

**Decision, up front: for a new Kotlin/KMP offline-first mobile project in 2026, adopt PowerSync as the default sync engine. Hand-roll the outbox/repository layer (as documented in `offline-first-mobile-architecture.md`) only if you have a hard requirement PowerSync can't meet — most commonly true peer-to-peer/no-server sync, in which case Ditto is the correct choice.** Everything else in this landscape is either dead (Atlas Device Sync/Realm Sync, effectively cr-sqlite), not actually a Kotlin/KMP option (ElectricSQL, Zero, Triplit, InstantDB, Jazz), a different category entirely (Store5, Turso/libSQL), or too immature to bet production data on (Automerge-kmp, Yjs/ykt).

Key findings:

- **PowerSync** (Kotlin SDK v1.13.0, 2026-06-08) is the most production-ready off-the-shelf sync engine for Kotlin/KMP today. It has official SQLDelight (beta since v1.6.0) and Room (beta since v1.13.0) integrations, self-hosting via an Apache-2.0/FSL-licensed Docker service, and a documented conflict-resolution model. Use it unless P2P/no-server is a hard requirement.
- **Firebase SQL Connect** (the 2026-04-29 rebrand of Firebase Data Connect) just shipped native offline caching and realtime subscriptions, and does have a Kotlin Android SDK — but it is Android-only (not KMP), the offline story is brand new and unproven, and it's a fully managed Google product with no self-host option. Firestore's decade-old offline persistence remains Google's more battle-tested offline story; SQL Connect's is worth watching, not betting a POS system on, yet.
- **ElectricSQL** pivoted its entire public positioning to "the agent platform built on sync" on 2026-04-29. Its Postgres Sync (formerly "Electric") engine is real, maintained, and Apache-2.0, but there is no Kotlin client — its client library list is TypeScript-native plus Java/Swift/Go/Rust/etc. for its newer Durable Streams product, with Kotlin conspicuously absent. **Not viable for Kotlin/KMP.**
- **Ditto** is the only genuinely production-ready, mature P2P mesh sync engine with a real Kotlin/Android SDK (SDK v5, `minSdk 24`). It syncs device-to-device over BLE/Wi-Fi Direct/LAN with no server required, and opportunistically to the cloud when available. This is the correct default for POS/kiosk fleets that must sync register-to-register when the internet, or even the store's own router, is down. It is a paid, license-token-gated product.
- **CR-SQLite** has had no tagged release since **v0.16.3 on 2024-01-17** — 18+ months with an open "is this project dead?" GitHub issue. It also has no Android/Kotlin binding path (it's a native SQLite loadable extension; Android doesn't support arbitrary loadable extensions without a custom SQLite build). **Effectively dead for new Kotlin/KMP adoption**, full stop.
- **Store5** is not a sync engine — it's the off-the-shelf alternative to hand-rolling the *repository/caching layer* (fetcher + source-of-truth + memory cache) that `offline-first-mobile-architecture.md` §2–3 describes. It has no server component and does not solve multi-device conflict resolution. Adopt it to save repository boilerplate; still build (or adopt) an outbox+sync layer on top.
- **Automerge** and **Yjs** Kotlin/KMP bindings are pre-1.0 and community-maintained (`automerge-kmp` v0.1.1, single maintainer; `ykt`/`y-crdt-jni` fragmented and JVM-only). Neither is production-viable for Kotlin/KMP today. Reach for a CRDT library only when you have genuinely collaborative, multi-writer, field-level-merge data (rich text, shared documents) — a POS transaction ledger does not need this.
- **Atlas Device Sync (MongoDB Realm) is dead.** Deprecated September 2024, reached end-of-life **September 30, 2025** — already past as of this writing. Do not build new sync architecture on Realm Sync. The local (unsynced) Realm database survives as a community OSS project with reduced investment.
- **Couchbase Lite** (v4.1.0 adds full idiomatic Kotlin support) is a mature, dual-mode (P2P *and* client-server via Sync Gateway/Capella) alternative to Ditto, with a longer track record but a commercial Enterprise Edition for some features.
- **Supabase** by itself is a BaaS (Postgres + Auth + Realtime), not an offline sync engine — its official Kotlin SDK (`supabase-kt`, KMP-native) has no built-in offline cache/outbox. PowerSync's own blog explicitly recommends **Supabase + PowerSync** as the stack, not Supabase alone.
- **Turso/libSQL embedded replicas** are a different category again: a local *read* replica with periodic pull-sync, not a bidirectional offline-write engine with conflict resolution. Good for read-heavy reference data (catalogs, price lists); the Android SDK is a technical preview.
- **Zero, Triplit, InstantDB, Jazz** are all real, interesting local-first/sync products — and all TypeScript/JS-first with explicit statements (Zero) or de facto reality (Triplit, InstantDB, Jazz) that native mobile/Kotlin is not a supported target. Not viable for this stack.

---

## 1. Decision Framework: Hand-Roll vs. Adopt a Sync Engine

See `offline-first-mobile-architecture.md` §2–§9, which teaches you how to build the repository + outbox + WorkManager + conflict-resolution stack yourself. That remains the right choice in some cases. This section is the decision gate for when to instead adopt one of the engines evaluated in §2.

### 1.1 When to hand-roll (stick with the offline-first-mobile-architecture.md patterns)

- **Your sync surface is narrow and asymmetric.** A handful of entity types, mostly push-only or pull-only (see the strategy table in `offline-first-mobile-architecture.md` §4.1) — an outbox + WorkManager worker is genuinely less code than integrating a general-purpose sync engine's schema/bucket/rules DSL.
- **Your backend is not Postgres/MySQL/MongoDB/SQL Server.** Every viable full sync engine below (PowerSync, Ditto's cloud connector, Couchbase's Sync Gateway) assumes a specific backend shape or requires you to run its server component. If your backend is a bespoke REST API you don't control the schema of, hand-rolling the client side against that API is usually less friction than forcing it through a sync engine's replication model.
- **Conflict resolution is domain-specific and simple.** If your domain rules collapse to "transactions are immutable, no conflict is possible" (the POS case in `offline-first-mobile-architecture.md` §5.5 and §10) or straightforward LWW, you don't need a product that ships general-purpose conflict machinery you won't use.
- **You need tight control over payload shape and battery/network budget** on a fleet of low-spec Android Go devices, and can't accept a vendor SDK's footprint or its background service model.
- **Team already owns WorkManager/SQLDelight expertise** and the marginal cost of a new dependency (learning curve, upgrade cadence, vendor risk) exceeds the boilerplate it would save.

### 1.2 When to adopt a sync engine

- **Multi-device, bi-directional, conflict-prone sync is a core, ongoing requirement** — not a one-off feature. Engines amortize the hard 20% (checkpointing, partial replication, delta protocols, retry/backoff, schema migration under sync) across every entity, not just the one you hand-rolled for.
- **You need P2P/no-server operation.** This is not something you can reasonably hand-roll (BLE mesh discovery, multi-hop relay, transport arbitration). This is Ditto's or Couchbase Lite's entire reason to exist — see §5.
- **Your backend is already Postgres (or MongoDB/MySQL/SQL Server) and mostly CRUD-shaped.** PowerSync's sync-rules model (SQL-like bucket definitions) maps directly onto this and gets you partial/filtered sync (per-user, per-store data slices) essentially for free.
- **You want compile-time-safe local queries without owning the sync plumbing.** PowerSync's Room/SQLDelight integrations give you the exact same generated-Kotlin ergonomics as a hand-rolled SQLDelight repository, but the sync/outbox/conflict layer underneath is someone else's on-call rotation.
- **Time-to-first-sync matters more than long-term flexibility.** A sync engine gets a team to "offline-first works" in days; hand-rolling the full stack in `offline-first-mobile-architecture.md` is a multi-sprint investment even for experienced teams.

### 1.3 The cross-cutting rule of thumb

> If you can draw your sync requirement as "keep this SQL view up to date on the device, push writes back through my existing API," adopt PowerSync. If you can draw it as "these devices must talk to each other with no infrastructure between them," adopt Ditto (or Couchbase Lite for a P2P/client-server hybrid with a longer track record). Everything else on this list is either not ready, not for Kotlin, or solving a different problem than "sync engine."

---

## 2. Per-Engine Evaluation

### 2.1 PowerSync — VIABLE (recommended default)

| | |
|---|---|
| **Current version** | Kotlin SDK v1.13.0 (2026-06-08); Room integration beta as of this release; SQLDelight integration beta since v1.6.0 (2025-09-18) |
| **License** | Client SDKs: Apache-2.0 (open source). PowerSync Service (self-hosted "Open Edition"): Functional Source License (source-available, not OSI-approved open source). PowerSync Cloud & Enterprise Self-Hosted: Commercial License & Services Agreement |
| **Hosting** | PowerSync Cloud (managed) or self-hosted via Docker (`journeyapps/powersync-service`, Open Edition) |
| **Backend support** | Postgres, MongoDB, MySQL, SQL Server, Convex |
| **Kotlin/KMP status** | Native KMP artifact (`com.powersync:core`), targets Android/iOS/JVM/macOS/watchOS/tvOS. As of v1.12.0, the SQLite core extension is statically linked for Apple targets, matching Android/JVM. |

PowerSync syncs a subset of a backend Postgres/MongoDB/MySQL/SQL Server database into an embedded SQLite database on-device, using "sync rules" (SQL-like bucket definitions) to define per-user/per-store partial replication. Writes go through a client-side upload queue that your backend API applies to the source database — PowerSync does not write to your backend directly, keeping your existing REST/GraphQL API as the write path.

**SQLDelight/Room integration** — the detail this research was asked to verify:

```toml
# libs.versions.toml
[versions]
powersync = "1.13.0"

[libraries]
powersync-core = { module = "com.powersync:core", version.ref = "powersync" }
powersync-integration-sqldelight = { module = "com.powersync:integration-sqldelight", version.ref = "powersync" }
powersync-integration-room = { module = "com.powersync:integration-room", version.ref = "powersync" }
```

```kotlin
// commonMain — SQLDelight driver backed by an open PowerSync database
val driver: SqlDriver = PowerSyncSqlDelightDriver(powerSyncDatabase)
val appDatabase = AppDatabase(driver)

// Reads flow naturally through SQLDelight's generated Flow-returning queries,
// while PowerSync's sync engine keeps the underlying SQLite tables current.
appDatabase.transactionQueries.getPendingSync().asFlow().mapToList(Dispatchers.IO)
```

Per PowerSync's own docs guidance: prefer **SQLDelight** when starting fresh on a PowerSync schema; prefer **Room** only if you have an existing Room database and are retrofitting sync onto it (Room requires "raw tables" and custom trigger wiring to feed PowerSync's `ps_crud` upload queue — meaningfully more setup than SQLDelight).

**Conflict handling**: default is **last-write-wins per field** (not per-row) — concurrent edits to *different* fields on the same record don't conflict. The server processes the client's upload queue in order; PowerSync's own docs describe five documented custom-conflict-resolution strategies (sequence-number versioning, field-level LWW, business-rule validation, and a "record the conflict, let a human resolve it" dead-letter pattern) for cases where LWW isn't sufficient. Consistency model is causal+ (verified with Jepsen-style testing per PowerSync's own published test suite).

**Pricing**: Free tier ($0/mo: 500 MB hosted data, 50 peak concurrent connections, 2 GB synced/mo), Pro (from $49/mo), Team (from $599/mo), Enterprise (custom). Self-hosted Open Edition is free (FSL-licensed); Enterprise Self-Hosted adds custom write checkpoints, SOC 2 support, and dedicated support at custom pricing.

**Verdict: VIABLE, recommended default.** Officially recommended pairing is Supabase (Postgres+Auth+Realtime) + PowerSync (offline sync layer) — see §6 and PowerSync's own "Offline-First Apps Made Simple" post. The only real caveats are (a) Room integration is still beta as of v1.13.0, so prefer SQLDelight for new schemas, and (b) the self-hosted server is source-available (FSL), not OSI open-source — read the license terms if that distinction matters to your organization.

### 2.2 Firebase SQL Connect (formerly Firebase Data Connect) — CONDITIONALLY VIABLE, Android-only, unproven

Rebranded from "Firebase Data Connect" to **"Firebase SQL Connect"** at Cloud Next, announced **2026-04-29** in Firebase's own blog post ("Realtime PostgreSQL: From Data Connect to SQL Connect"). The same announcement post shipped, simultaneously:

- **Realtime Query Updates** — subscribe to a query via the new `@refresh` directive; the #1 most-requested Firebase feature per their own UserVoice tracker, which shows it going fully live around **2026-06-12**.
- **Offline Caching** — client SDKs now natively support query-level and entity-level ("normalized") caching, configured per-connector in `connector.yaml`:

```yaml
# connector.yaml
clientCache:
  maxAge: 10s
  maxSize: 50MB
  storage: memory   # or persistent (persists across app restarts; web only supports memory)
```

- **Native SQL support** — you can now write raw SQL alongside GraphQL operations, plus a local emulator for fully offline testing of the relational backend.

**What it is, concretely**: a Cloud SQL for PostgreSQL-backed service where queries/mutations are pre-registered server-side (compiled like Cloud Functions, not ad-hoc client SQL by default), consumed via generated, type-safe SDKs. Official SDK support: **Kotlin Android, iOS (Swift), Flutter (Dart), and web** — Android has a real first-party Kotlin SDK, but there is **no shared-Kotlin-Multiplatform artifact**: it's four separate native SDKs, not one `commonMain` KMP module usable across Android+iOS from shared Kotlin code. If your app is Android-only Kotlin, this is usable; if you need a genuine KMP sync layer shared between Android and iOS, this doesn't provide one the way PowerSync's single KMP core does.

**Relationship to Firestore**: Firestore has had native offline persistence (local cache, offline queries, automatic reconnect/resync) since roughly its 2017 GA — a decade of production hardening. SQL Connect's offline caching, by contrast, is **brand new as of 2026-04-29** and its own realtime feature only fully shipped mid-2026. Firestore also received a major overhaul at the same Cloud Next 2026 event (native full-text search, geospatial queries, relational-style joins/subqueries/DML) explicitly to reduce the need for external sync tooling. For an app that needs mature, battle-tested Firebase-native offline behavior today, **Firestore remains the safer choice over SQL Connect** — SQL Connect's offline story should be evaluated as an early adopter, not assumed production-hardened.

**Hosting**: fully managed only (Cloud SQL under the hood is a normal Postgres instance you technically own/can export, but the SQL Connect layer itself — schema deployment, caching, realtime fan-out — has no self-hosted option).

**Verdict: CONDITIONALLY VIABLE.** Reasonable if you are Android-only (not KMP), already fully committed to Firebase/GCP, and can tolerate adopting a feature set that is roughly three months old as of this writing. Not recommended as the offline engine for a KMP app, and not recommended over PowerSync/Ditto for a POS system where offline-write correctness under real network chaos is the whole point — this feature set hasn't had time to be proven under that kind of load.

### 2.3 ElectricSQL — NOT VIABLE for Kotlin/KMP (confirmed pivot)

ElectricSQL's public positioning changed dramatically in 2026. The company's own blog, **"Introducing Electric Agents — the agent platform built on sync"** (2026-04-29 — the same day as the Firebase SQL Connect rebrand), and the current electric.ax homepage both now lead with: *"Electric is the first agent platform built on sync... Agents are not compute. Agents are data."* The underlying Postgres replication technology didn't disappear — it was reframed as infrastructure for durable AI agent state (via "Electric Streams" / "Durable Streams") rather than marketed as a general mobile/web offline-sync product.

The original product still exists and is maintained under the "Postgres Sync" name: an Apache-2.0, HTTP-based, CDN-friendly read-path sync engine for Postgres using "Shapes" for partial replication (`@electric-sql/client` on npm, actively released — v1.5.23 on 2026-07-02). It is genuinely good technology. But:

- **There is no Kotlin client.** Electric's own client library matrix (for the newer Durable Streams product) explicitly lists **TypeScript, Python, Go, Rust, Java, Swift, PHP, Ruby, Elixir, and .NET** — ten languages, and Kotlin is not one of them. Java exists (usable from Kotlin with friction, no coroutines/Flow idioms, no Android-specific packaging), but that is a materially worse starting point than PowerSync's or Ditto's native Kotlin SDKs.
- **No official Android/mobile packaging, examples, or docs** exist for consuming Postgres Sync/Shapes from a mobile client at all — every quickstart and integration guide targets web frameworks (React, TanStack DB).

**Verdict: NOT VIABLE.** Even setting the agent-platform pivot aside, there was never a first-party Kotlin/KMP SDK, and the current product focus makes one unlikely to appear. Do not plan a Kotlin/KMP offline architecture around ElectricSQL.

### 2.4 Ditto — VIABLE (best-in-class for true P2P/no-server)

| | |
|---|---|
| **Current version** | Ditto Kotlin SDK v5 ("Built for Speed and Developer Experience" — SDK v5), Android install docs reference `minSdk 24`, `compileSdk 36`, JDK 17 |
| **License** | Proprietary/commercial; requires an activated license token (`setOfflineOnlyLicenseToken` for fully offline activation) |
| **Hosting** | Ditto-hosted cloud, BYOC, or fully self-managed (Enterprise tier) |
| **P2P** | Yes — the core differentiator: BLE, Wi-Fi Peer-to-Peer/Wi-Fi Aware, LAN, with automatic transport selection and **multi-hop relay** (data can hop across multiple offline devices to reach a device that does have connectivity, up to ~130m/425ft per hop and further via multihop) |
| **Kotlin/KMP status** | Native Kotlin SDK (Android), coroutine/Flow-friendly APIs, Jetpack Compose examples in official docs. Android-only — no shared-Kotlin iOS target; iOS gets its own Swift SDK. |

Ditto is a document database with automatic, CRDT-based conflict-free merge built in — devices sync via **subscription queries** (declarative "sync me all documents matching this filter") rather than a manual outbox/upload-queue model. Sync is peer-to-peer by default: devices discover each other and form mesh networks with **no server, WiFi access point, or cloud dependency required**. When any device in the mesh has internet access, changes propagate to Ditto's cloud (or your self-hosted/BYOC deployment) and back out to the rest of the mesh — this is exactly the "one register has a hotspot, the rest sync through it" pattern a POS fleet needs.

```kotlin
// Kotlin/Android — minimal Ditto setup
val config = DittoConfig(
    databaseId = BuildConfig.DITTO_DATABASE_ID,
    connect = DittoConfig.Connect.Server(url = BuildConfig.DITTO_URL),
)
val ditto = Ditto(applicationContext, config)
ditto.setOfflineOnlyLicenseToken(BuildConfig.DITTO_OFFLINE_TOKEN) // works with zero network
ditto.startSync()

// Subscription query — declares what this device should sync
ditto.sync.registerSubscription("SELECT * FROM transactions WHERE storeId = :storeId", mapOf("storeId" to storeId))
```

**Pricing**: Free tier (10 concurrent cloud device connections, 2 GB storage, 5 GB data transfer, no SLA), Pro (from custom pricing: 1,000+ concurrent connections, 50GB+ storage, 99% SLA), Enterprise (custom, BYOC/self-managed, 99.95% SLA). Startup/nonprofit discounts available. Note: the P2P mesh sync itself (device-to-device, no cloud involved) is not metered the same way as cloud connections — the pricing tiers above gate cloud-side scale, not local mesh capability.

**Verdict: VIABLE — the correct choice specifically for true offline, no-server, P2P sync.** This is not a "PowerSync alternative" in the general case; it solves a different, narrower, harder problem that PowerSync fundamentally cannot (PowerSync always requires a reachable PowerSync Service to sync). If your requirement is genuinely "these devices must sync directly with each other, with no infrastructure in between," Ditto is production-ready and the clear leader. The cost is a commercial license and BLE/Wi-Fi permission overhead (manifest permissions merged automatically, but runtime permission prompts and a foreground service are required to keep syncing while backgrounded).

### 2.5 CR-SQLite — DEAD, do not adopt

**Confirmed stagnant.** The last tagged release is **v0.16.3, dated 2024-01-17** — over 18 months ago as of this writing (2026-07-28), with zero releases since. GitHub issue [vlcn-io/cr-sqlite#444](https://github.com/vlcn-io/cr-sqlite/issues/444), titled *"Is this project dead?"* (opened 2024-10-11, last comment 2025-08-18), has the maintainer confirming the creator moved to a full-time job elsewhere and releases slowed to a stop, while insisting "software either works or it doesn't" — a fair point for existing deployments, but not a basis for new adoption. The most credible evidence of continued life is Fly.io's internal fork ("corrosion," at `superfly/cr-sqlite`), which diverged meaningfully (repurposed `db_version` semantics) and is optimized for Fly's own distributed-machine use case, not general mobile sync.

Separately from the maintenance question: cr-sqlite is a native SQLite **loadable extension** (Rust-compiled). Android does not support loading arbitrary SQLite extensions through the standard Android SQLite APIs without shipping a custom SQLite build — there is no official or community Kotlin/Android packaging of cr-sqlite at all. Even at peak activity, this was never a mobile-first project; it targets server/edge SQLite (Fly.io's use case) and browser/WASM SQLite, not Android.

**Verdict: DEAD for the purposes of this landscape.** No release in 18+ months, no path to Android/Kotlin integration, no community mobile bindings. Do not build new Kotlin/KMP architecture on cr-sqlite.

### 2.6 Store5 — different category, not a sync engine, VIABLE as a caching layer

`org.mobilenativefoundation.store:store5` — stable major release **5.0.0 (2023-09-14)**, current pre-release channel is **5.1.0-alpha09 (2026-06-10)** per the project's own changelog (5.1.0-alpha08 landed 2026-01-12 on Maven Central). Apache-2.0, genuinely Kotlin Multiplatform, maintained by the Mobile Native Foundation (originally spun out of Dropbox's internal Store library).

```toml
[versions]
store = "5.1.0"
[libraries]
store = { module = "org.mobilenativefoundation.store:store5", version.ref = "store" }
```

Store5 solves the **"fetcher + source-of-truth + memory cache" repository pattern** — the same box labeled "Repository" in `offline-first-mobile-architecture.md`'s §2.1 data-flow diagram — as a reusable, tested library instead of hand-rolled `Flow`/coroutine plumbing. Its `MutableStore` (added in 5.0) adds a `Validator`/`Updater`/`Bookkeeper` pipeline for write operations, including single-writer conflict handling (e.g., "is this locally cached write still valid before I show it?") — but this is fundamentally different from **multi-device sync conflict resolution**. Store5 has no server component, no wire protocol, no concept of "another device's concurrent write" — it manages one device's view of one backend, with layered caching in front.

**Verdict: VIABLE, but as the answer to a different question.** Adopt Store5 to stop hand-rolling the repository/caching layer that sits *above* your local database in the offline-first-mobile-architecture.md diagram. It is not a substitute for PowerSync/Ditto/an outbox+WorkManager pipeline if you need actual cross-device offline sync with conflict resolution — those remain necessary underneath or alongside it.

### 2.7 Automerge (Kotlin/KMP bindings) — NOT YET VIABLE

The core Automerge Rust crate is healthy and active: `automerge` v0.10.0 released 2026-06-05 (MSRV 1.89.0), with releases roughly monthly through 2026. `automerge-java` (the official JVM binding project under the `automerge` GitHub org) merged a **"kotlin helper library"** PR (#51) on 2026-04-21 — so idiomatic Kotlin ergonomics are landing, but only as helpers on top of the Java/JNI binding, not a standalone KMP artifact, and there is still no official multiplatform (Android+iOS+shared) release from the Automerge org itself.

The only genuine KMP wrapper is **community-maintained**: `com.yeh35:automerge-kmp:0.1.1` (released 2026-03-17, MIT license, single listed developer "aspect," wraps Automerge via Rust + UniFFI), targeting Android/JVM/iOS/Linux. This is a real, buildable artifact on Maven Central — but a 0.1.1 release from a single-maintainer community project is not a foundation to build production POS or financial-transaction sync on.

```kotlin
// com.yeh35:automerge-kmp:0.1.1 — illustrative, unofficial community wrapper
implementation("com.yeh35:automerge-kmp:0.1.1")
```

**Verdict: NOT YET VIABLE for production.** Reach for Automerge conceptually only when your data is genuinely document-shaped and multi-writer-collaborative (rich text, nested structures edited concurrently by multiple users) — not for POS transaction/inventory data, which doesn't need CRDT-grade merge semantics (see `offline-first-mobile-architecture.md` §5.4–5.5 on when CRDTs are and aren't warranted). Revisit once either the official `automerge-java` project ships a real multiplatform artifact, or the community `automerge-kmp` project reaches a 1.x with more than one maintainer.

### 2.8 Yjs / y-crdt Kotlin bindings — NOT VIABLE

Yjs itself (JS) is mature and widely used. Its Rust reimplementation, **y-crdt (yrs)**, has bindings for Python, Ruby, R, .NET, Swift, Elixir — and Kotlin is explicitly on the list, but every concrete Kotlin binding effort is either inactive or incomplete:

- **`y-crdt/ykt`** (the org's own repo): README states plainly, **"this repository is currently not active. Consult y-uniffi for details."**
- **`planerist/ykt`** (community continuation): actively developed, but JVM-only today — its own checklist shows "Multiplatform + tests" as an unchecked TODO — and only `YText` is described as "solid"; other Y-CRDT types (YArray, YMap, XML types) are partial.
- **`edpaget/y-crdt-jni`** (`net.carcdr:ycrdt-jni`): a genuine, actively updated JVM binding (JNI and Panama/FFM variants) — but it targets server-side JVM use cases (a ProseMirror/Tiptap collaborative-editing backend, Java 21+/22+), not Android or KMP.

**Verdict: NOT VIABLE.** No official, complete, multiplatform Kotlin binding exists for Yjs/y-crdt as of 2026-07-28. Three separate unofficial efforts are fragmented across JVM-only and incomplete-API states. Do not plan a Kotlin/KMP architecture around Yjs.

### 2.9 Realm / Atlas Device Sync — DEAD (confirmed EOL)

MongoDB announced deprecation of Atlas Device SDKs (formerly "Realm") and Atlas Device Sync in **September 2024**. Per MongoDB's own deprecation page, Atlas Device SDKs and Device Sync **reached end-of-life and were removed on September 30, 2025** — already past as of this document's date (2026-07-28). MongoDB's own App Services Admin API v3 docs carry an explicit **"END-OF-LIFE (EOL) NOTICE"** banner confirming Device Sync, SDKs, Data API, GraphQL, static hosting, and HTTPS endpoints all reached EOL on that date (database triggers are the one App Service capability that remains).

MongoDB's own blog frames this as "doubling down" on the core database and explicitly names its own migration partner (WeKan) steering existing customers toward **Ditto, PowerSync, and ObjectBox** as replacement sync solutions. The client-side (unsynced) Realm database continues as an OSS project, but MongoDB engineering has stepped back to "keep the lights on" mode per public maintainer statements — no active feature development.

**Verdict: DEAD.** Do not build new sync architecture on Realm/Atlas Device Sync under any circumstances. If migrating an existing Realm Sync app, treat this as a forced migration to PowerSync, Ditto, or a hand-rolled stack — not an optional modernization.

### 2.10 Couchbase Lite — VIABLE (mature P2P + client-server hybrid)

Couchbase Lite for Android reached **v4.1.0**, which "introduces full idiomatic support for Kotlin apps, out-of-the-box," including Kotlin Flows for change notifications and configuration-factory builders (`ReplicatorConfigurationFactory`, etc.) — full API parity with the existing Java API plus Kotlin-specific ergonomics. Current stable install docs reference **v4.0.3** for the Community/Enterprise Maven artifacts (`couchbase-lite-android-ktx` / `couchbase-lite-android-ee-ktx`).

Couchbase Mobile supports **both** modes: traditional client-server sync via Sync Gateway (self-hosted) or Couchbase Capella App Services (managed), *and* genuine peer-to-peer sync directly between Couchbase Lite instances with no server — making it a longer-track-record alternative to Ditto for teams that want both options from one product. Couchbase's own migration-marketing post (published the day Atlas Device Sync went EOL) explicitly pitches P2P support and customizable conflict resolvers as differentiators versus what Realm Sync offered.

**Verdict: VIABLE.** A credible alternative to Ditto specifically because it supports both P2P and client-server sync from a single SDK, with a decade-plus production track record (Couchbase Mobile predates Ditto). The tradeoff is licensing: some capabilities (e.g., Vector Search) are Enterprise-only, and running your own Sync Gateway is real infrastructure to operate (see the `tilt-setup`/`taskfile-setup` skills in this repo's devtools plugin if self-hosting Sync Gateway locally for dev).

### 2.11 Turso / libSQL Embedded Replicas — NICHE VIABLE (different category)

Turso's Android SDK (`tech.turso.libsql:libsql`, v0.1.0) is explicitly marked **"technical preview"** and states it currently "will only work with the Android Gradle Plugin" (full general Kotlin/KMP support is described as "coming," not present). Embedded Replicas keep a local SQLite file that reads instantly from disk and periodically (or on-demand via `db.sync()`) pulls changes from a remote Turso primary; writes are delegated to the remote primary rather than queued and conflict-resolved locally.

```kotlin
val db = Libsql.open(
    path = "./local.db",
    url = "TURSO_DATABASE_URL",
    authToken = "TURSO_AUTH_TOKEN",
    syncInterval = 1000, // ms — background pull-sync cadence
)
val conn = db.connect()
db.sync() // manual pull; call periodically or on app foreground
```

**Verdict: NICHE VIABLE.** This is a *read-replica* pattern, not an offline-write sync engine — good for reference/catalog data (product catalog, price lists, config) that changes centrally and rarely needs offline writes, but not a substitute for PowerSync/Ditto if your app needs to accept writes while fully offline and reconcile them later. Track its maturity; the Android SDK is not production-hardened yet.

### 2.12 Other BaaS/local-first products — NOT VIABLE for Kotlin/KMP (surveyed for completeness)

- **Supabase**: the official Kotlin SDK (`supabase-kt`, KMP-native, modules for `postgrest-kt`/`auth-kt`/`realtime-kt`) is solid and genuinely multiplatform — but it is a BaaS client, not an offline sync engine; there is no built-in local cache/outbox from Supabase itself. A third-party wrapper (`androidpoet/supabase-kmp`) bolts on `supabase-sync`/`supabase-sync-core`/`supabase-sync-sqldelight` modules providing pull/merge/push and conflict resolution over SQLDelight — a community effort, not an official Supabase product. PowerSync's own blog explicitly positions **Supabase + PowerSync** as the recommended combination (see §6). **Verdict: not a sync engine by itself; pair with PowerSync.**
- **Zero (Rocicorp)**: reached v1.0 on 2026-06-08. Its own "When To Use Zero" docs state outright: *"You are building a native mobile app [→ not a fit]. Zero is written in TypeScript and only supports TypeScript clients."* It further explicitly says it is **not local-first** — it's a client-server system with an authoritative server and only limited offline read support. **Verdict: NOT VIABLE for Kotlin/mobile**, by the vendor's own documentation.
- **Triplit**: TypeScript-only client/server, targets browser/Node/React Native — no native Kotlin/Android SDK exists or is planned in public materials. **Verdict: NOT VIABLE.**
- **InstantDB**: SDKs limited to JavaScript/React/React Native; explicitly "no official server-side SDK, no REST API for non-JS consumers" per third-party technical review. **Verdict: NOT VIABLE.**
- **Jazz**: a genuinely interesting local-first relational database (2.0 alpha as of this research), but its supported client list is React/Vue/Svelte/Solid/Expo(React Native)/plain TypeScript/Rust — no native Kotlin/Android client is documented. (Unverified as of 2026-07-28: whether any deeper native-Android integration exists beyond what Expo/React Native provides — nothing in official docs suggests one.) **Verdict: NOT VIABLE for native Kotlin.**

---

## 3. Comparison Matrix

| Engine | Kotlin/KMP SDK | Self-hostable | Conflict strategy | P2P | Cost model | Production verdict |
|---|---|---|---|---|---|---|
| **PowerSync** | Yes — native KMP, Room (beta) + SQLDelight (beta) integrations | Yes (Open Edition, FSL license, Docker) | Server-authoritative; default LWW-per-field, 5 documented custom strategies | No | Free tier → $49/mo Pro → $599/mo Team → custom Enterprise | **VIABLE — recommended default** |
| **Firebase SQL Connect** | Kotlin Android only (no KMP) | No (Google-managed only; Cloud SQL itself is portable) | Not documented in depth (new feature, 2026-04-29) | No | Firebase pricing (Cloud SQL + Firebase usage) | **CONDITIONALLY VIABLE** — Android-only, unproven offline story |
| **ElectricSQL** | None | Yes (Apache-2.0 core) | Not applicable (no mobile client) | No | Open protocol + Electric Cloud managed option | **NOT VIABLE — no Kotlin client, pivoted to agent platform** |
| **Ditto** | Yes — native Android SDK (v5) | Yes (BYOC/self-managed on Enterprise) | Automatic CRDT merge | **Yes — core feature (BLE/Wi-Fi/LAN mesh, multi-hop)** | Free tier → paid Pro/Enterprise, license-token gated | **VIABLE — best-in-class for P2P/no-server** |
| **CR-SQLite** | None (no Android path at all) | N/A (SQLite extension) | CRDT (Convergent Replicated Relations) | No | Open source (MIT), but unmaintained | **DEAD — no release since 2024-01-17** |
| **Store5** | Yes — native KMP | N/A (client-side library, not a sync engine) | Single-writer validator/updater pipeline only — not multi-device conflict resolution | No | Open source (Apache-2.0) | **VIABLE — different category (caching layer, not sync)** |
| **Automerge (Kotlin)** | Community-only (`automerge-kmp` v0.1.1) | N/A (library, not hosted) | CRDT (rich JSON documents) | Via your own transport | Open source (MIT) | **NOT YET VIABLE — pre-1.0, single maintainer** |
| **Yjs/y-crdt (Kotlin)** | None complete (fragmented, JVM-only efforts) | N/A (library) | CRDT (shared types) | Via your own transport | Open source (MIT) | **NOT VIABLE — no usable Kotlin/Android binding** |
| **Atlas Device Sync (Realm)** | Was native, now dead | N/A | Was server-authoritative | No | N/A | **DEAD — EOL 2025-09-30** |
| **Couchbase Lite** | Yes — native, full idiomatic support since v4.1.0 | Yes (Sync Gateway self-hosted, or Capella managed) | Customizable conflict resolvers | **Yes** (P2P + client-server, dual mode) | Community (free) + Enterprise (paid) editions | **VIABLE — mature P2P/client-server hybrid** |
| **Turso/libSQL embedded replicas** | Yes, but technical preview, AGP-only currently | Yes (libSQL server is self-hostable) | N/A — read replica, writes delegate to primary | No | Turso usage-based pricing | **NICHE VIABLE — read replicas only, not offline-write sync** |
| **Supabase (bare)** | Yes — native KMP (`supabase-kt`) | Yes (Supabase is self-hostable) | N/A — no built-in offline engine | No | Free/Pro/Team/Enterprise | **NOT A SYNC ENGINE — pair with PowerSync** |
| **Zero (Rocicorp)** | None (TS-only by design) | Yes (self-hostable) | Server reconciliation | No | Free (self-hosted) / managed service | **NOT VIABLE for Kotlin/mobile (vendor confirms)** |
| **Triplit** | None | Yes | Not evaluated (no Kotlin path) | No | Open source + hosted | **NOT VIABLE** |
| **InstantDB** | None | No (managed only) | Optimistic + triple-store reconciliation | No | Usage-based | **NOT VIABLE** |
| **Jazz** | None documented | Yes (self-hostable single-tenant server) | Automatic visible-state reconciliation w/ history | No | Free (self-host) / Jazz Cloud | **NOT VIABLE for native Kotlin** |

---

## 4. Category Distinctions

It's easy to conflate four different categories of "thing that helps with offline data." They solve different layers of the stack shown in `offline-first-mobile-architecture.md` §2.1:

1. **Full sync engine** (PowerSync, Ditto, Couchbase Lite, Firebase SQL Connect): owns the entire pipeline — local storage, a wire protocol, conflict resolution, and (for the client-server ones) a server component. Replaces your hand-rolled outbox + WorkManager + conflict-resolution code (`offline-first-mobile-architecture.md` §4, §5, §7).
2. **Caching/repository layer** (Store5): sits between your UI and your local+remote data sources, deduplicating in-flight requests and layering memory/disk caches. Replaces the hand-rolled `Repository` class (`offline-first-mobile-architecture.md` §2.1, §3.1) — but has no concept of multi-device sync and no server component. You still need a sync engine or hand-rolled outbox underneath it if multiple devices write to shared data.
3. **CRDT library** (Automerge, Yjs): a data structure + merge algorithm, not a sync engine. It guarantees that concurrent edits from multiple writers converge to the same value without a coordinator — but you still have to build (or plug in) the transport that moves the CRDT's binary updates between devices. Full sync engines like Ditto use CRDTs *internally* as their conflict-resolution mechanism; a bare CRDT library gives you only that one piece.
4. **BaaS (Backend-as-a-Service)** (Supabase, Firebase/Firestore, InstantDB): a hosted backend with client SDKs for auth, database access, and realtime subscriptions. Some BaaS products (Firestore, InstantDB) bundle a genuine offline cache and optimistic-write reconciliation as part of the platform; others (bare Supabase) leave the offline story to you or a third-party/paired sync engine.

A production Kotlin/KMP offline-first app typically ends up combining **one item from category 4 (or your own backend) + one item from category 1 (or the hand-rolled equivalent) + optionally one item from category 2** for repository ergonomics. Category 3 (CRDT libraries) is usually only needed directly if you're building your *own* sync engine and need its conflict-resolution primitive — most teams should get CRDT semantics for free by picking a category-1 engine that already uses them internally (Ditto), rather than wiring up Automerge/Yjs by hand.

---

## 5. POS / Intermittent-Connectivity Recommendation

For a POS system serving developing-market or intermittent-connectivity deployments (the profile `offline-first-mobile-architecture.md` §10 uses as its case study), the decision comes down to one question: **does connectivity loss ever mean "the store's own local network is also down," or only "the store has no path to the internet, but registers can still see each other on Wi-Fi/LAN"?**

- **If registers must be able to sync with each other even when there is zero local infrastructure** (no router, no shared Wi-Fi, nothing) — for example, food-market or event vendors running fully mobile setups — **adopt Ditto.** Its BLE/Wi-Fi-Direct/LAN mesh with multi-hop relay is purpose-built for exactly this: one register with a cellular hotspot can carry the whole mesh's changes to the cloud and back, and registers keep working and syncing with each other even with that hotspot device turned off. This is not something PowerSync, Firebase, or a hand-rolled outbox can do — none of them operate without a reachable server.
- **If the store always has *some* local network (even a flaky one) and the real problem is intermittent internet, not zero infrastructure** — the far more common case — **adopt PowerSync against a Postgres (or Supabase-hosted Postgres) backend**, self-hosted if data residency matters, PowerSync Cloud if it doesn't. Its causal+-consistent, server-authoritative model with an explicit upload queue is a good match for POS's "transactions are effectively immutable, conflicts are rare and simple" domain shape (`offline-first-mobile-architecture.md` §5.5), and its SQLDelight integration reuses the exact schema/query patterns that document already teaches.
- **If you need both** (registers must mesh with each other locally *and* eventually reconcile with a central backend, and the volume/compliance requirements justify the cost) — **Couchbase Lite** is the one product here that natively supports both P2P and client-server sync from a single SDK, and has the longest production track record of any option on this list for that hybrid shape. Ditto can also reach a central backend (it syncs opportunistically to Ditto Cloud/BYOC when any device has connectivity) — the practical difference is Couchbase's client-server half uses your own Sync Gateway/Capella deployment with more SQL-like query tooling, while Ditto's cloud side is Ditto's own managed/BYOC product.
- **Do not hand-roll a mesh/P2P layer yourself.** BLE mesh discovery, transport arbitration, and multi-hop relay are genuinely hard distributed-systems problems that the vendors above have spent years hardening. This is the one place in this landscape where "just build the outbox pattern from `offline-first-mobile-architecture.md`" is the wrong answer regardless of team skill — that document's outbox pattern assumes a reachable server exists to drain the outbox *to*, which is precisely the assumption P2P deployments can't make.
- **For catalog/price-list data specifically** (read-heavy, centrally authored, rarely conflicting), a lighter-weight **Turso/libSQL embedded replica** can complement whichever primary engine you pick for transactional writes — but treat it as a read-replica addition, not your core sync layer, given its current technical-preview status on Android.

---

## 6. Migration / Adoption Notes

Adopting any sync engine is not free, even when it's the right call. Budget for:

- **Schema/backend coupling.** PowerSync requires your backend to be Postgres, MongoDB, MySQL, SQL Server, or Convex, and requires you to author "sync rules"/bucket definitions describing what data syncs to whom — this is a real modeling exercise, not just a client-side SDK integration, and it changes how you think about per-user/per-store data partitioning. Ditto's subscription-query model is more flexible about backend shape but still requires deciding what each device subscribes to, and your team needs to learn Ditto's document model if your data is currently relational.
- **Wire-protocol and vendor lock-in.** Once your client-side schema and write path are built against a specific engine's upload-queue/subscription semantics, migrating to a different engine (or back to a hand-rolled stack) means rebuilding both the client sync layer and, for server-side engines, the backend write-acceptance logic (PowerSync explicitly requires your API to accept writes synchronously and be idempotent — see its "Writing Client Changes" guidance).
- **Operational overhead of self-hosting.** PowerSync's Open Edition and Couchbase's Sync Gateway both need a running service (Docker/Kubernetes) that you now operate, monitor, and upgrade — this is genuinely comparable in scope to standing up any other stateful service; consider this repo's `tilt-setup` and `taskfile-setup` devtools skills for local dev orchestration of that service alongside your backend.
- **Licensing review.** PowerSync's server (FSL) and Ditto's SDK (proprietary, license-token-gated) both require reading the actual license terms before committing — FSL is not OSI open source (it converts to Apache-2.0 after a time delay per version, but restricts commercial competing use in the interim), and Ditto's free tier caps (10 concurrent cloud connections, 2 GB storage) will not survive a real pilot rollout.
- **Team ramp-up cost.** A sync engine introduces a new conceptual model (sync rules, subscription queries, checkpoints, upload queues) on top of the Kotlin/SQLDelight/Room knowledge your team already has. Budget at least one sprint of spike/prototype time before committing a real feature to it — this is exactly the kind of decision worth prototyping against a throwaway branch first.
- **Reversibility is asymmetric.** Migrating *from* a hand-rolled outbox *to* a sync engine is usually incremental (you can adopt it entity-by-entity). Migrating *away from* a sync engine once your schema and conflict logic are entangled with its bucket/rules model is a much larger rewrite — treat the initial adoption decision as higher-stakes than the "should we hand-roll" decision in §1.

---

## References

1. PowerSync. **Product Updates: PowerSync Kotlin SDK v1.13.0.** https://releases.powersync.com/announcements/powersync-kotlin-sdk
2. PowerSync. **v1.13.0 release notes.** https://github.com/powersync-ja/powersync-kotlin/releases/tag/v1.13.0
3. PowerSync. **CHANGELOG.md (powersync-kotlin).** https://github.com/powersync-ja/powersync-kotlin/blob/main/CHANGELOG.md
4. PowerSync. **Kotlin SQL Libraries (Room & SQLDelight overview).** https://docs.powersync.com/client-sdks/orms/kotlin/overview
5. PowerSync. **Room (Beta) integration guide.** https://docs.powersync.com/client-sdks/orms/kotlin/room
6. PowerSync. **More Robust SQL Queries for Kotlin Apps: Room and SQLDelight Integrations.** https://releases.powersync.com/announcements/more-robust-sql-queries-for-kotlin-apps-room-and-sqldelight-integrations
7. PowerSync. **Pricing.** https://powersync.com/pricing
8. PowerSync. **Licensing & Terms.** https://powersync.com/legal/licensing-terms
9. PowerSync. **Open-Source Packages.** https://powersync.com/open-source
10. PowerSync. **Self-Hosting.** https://powersync.mintlify.app/intro/self-hosting
11. PowerSync. **Custom Conflict Resolution.** https://docs.powersync.com/handling-writes/custom-conflict-resolution
12. PowerSync. **Handling Update Conflicts.** https://docs.powersync.com/handling-writes/handling-update-conflicts
13. PowerSync. **Consistency (causal+, Jepsen testing).** https://docs.powersync.com/architecture/consistency
14. PowerSync. **Offline-First Apps Made Simple: Supabase + PowerSync.** https://powersync.com/blog/offline-first-apps-made-simple-supabase-powersync
15. Firebase. **Realtime PostgreSQL: From Data Connect to SQL Connect.** https://firebase.blog/posts/2026/04/whats-new-sql-connect/
16. Firebase. **What's new from Firebase at Cloud Next 2026.** https://firebase.blog/posts/2026/04/cloud-next-2026-announcements/
17. Firebase. **SQL Connect — Web SDK caching/offline docs.** https://firebase.google.com/docs/sql-connect/web-sdk
18. Firebase. **SQL Connect overview.** https://firebase.google.com/docs/sql-connect
19. Firebase. **Get real-time updates from SQL Connect.** https://firebase.google.cn/docs/sql-connect/realtime
20. Electric. **Introducing Electric Agents — the agent platform built on sync.** https://electric.ax/blog/2026/04/29/introducing-electric-agents
21. Electric. **Electric homepage (current positioning).** https://electricsql.com/
22. Electric. **Postgres Sync overview.** https://electric.ax/sync/postgres-sync
23. Electric. **Announcing Hosted Durable Streams (client library language matrix).** https://electric.ax/blog/2026/01/22/announcing-hosted-durable-streams
24. npm. **@electric-sql/client version history.** https://registry.npmjs.org/@electric-sql/client
25. Ditto. **Kotlin Install Guide.** https://docs.ditto.live/sdk/latest/install-guides/kotlin
26. Ditto. **Pricing.** https://www.ditto.com/pricing
27. Ditto. **Edge SDK (P2P mesh, multi-hop).** https://www.ditto.com/products/edge-sdk
28. Ditto. **Syncing Data (subscription queries).** https://docs.ditto.live/key-concepts/syncing-data
29. vlcn-io/cr-sqlite. **Releases.** https://github.com/vlcn-io/cr-sqlite/releases
30. vlcn-io/cr-sqlite. **Issue #444: "Is this project dead?"** https://github.com/vlcn-io/cr-sqlite/issues/444
31. vlcn-io/cr-sqlite. **Repository (stars, license, activity).** https://github.com/vlcn-io/cr-sqlite
32. Mobile Native Foundation. **Store5 — Maven Central.** https://central.sonatype.com/artifact/org.mobilenativefoundation.store/store5
33. Mobile Native Foundation. **Store5 CHANGELOG.md.** https://github.com/MobileNativeFoundation/Store/blob/main/CHANGELOG.md
34. Mobile Native Foundation. **Store5 Quickstart.** https://store.mobilenativefoundation.org/docs/quickstart
35. Klibs.io. **com.yeh35:automerge-kmp package page.** https://klibs.io/package/com.yeh35/automerge-kmp/0.1.1
36. automerge-java. **"kotlin helper library" PR #51.** https://github.com/automerge/automerge-java/pull/51
37. crates.io. **automerge crate version history.** https://crates.io/crates/automerge
38. y-crdt/y-crdt. **Bindings overview and feature parity.** https://github.com/y-crdt/y-crdt/
39. y-crdt/ykt. **Repository (marked inactive).** https://github.com/y-crdt/ykt
40. planerist/ykt. **Community Kotlin Y-CRDT bindings.** https://github.com/planerist/ykt
41. edpaget/y-crdt-jni. **Java bindings for y-crdt (JVM-only).** https://github.com/edpaget/y-crdt-jni
42. MongoDB. **Atlas Device SDKs Deprecation.** https://www.mongodb.com/docs/atlas/device-sdks/deprecation/
43. MongoDB. **Atlas App Services Admin API v3 — EOL notice.** https://www.mongodb.com/docs/api/doc/atlas-app-services-admin-api-v3/
44. MongoDB. **Future-Proof Your Apps with MongoDB and WeKan (migration partner post).** https://www.mongodb.com/company/blog/innovation/future-proof-your-apps-with-mongodb-wekan
45. Couchbase. **MongoDB Ends Mobile Support Today: Migrate to Couchbase.** https://www.couchbase.com/blog/realm-mongodb-eol-day-2025/
46. Couchbase. **Installing Couchbase Lite on Android (v4.0.3).** https://docs.couchbase.com/couchbase-lite/current/android/gs-install.html
47. Couchbase. **Kotlin support (v4.1.0, full idiomatic support).** https://docs.couchbase.com/couchbase-lite/current/android/kotlin.html
48. Turso. **Kotlin/Android Quickstart (Embedded Replicas).** https://docs.turso.tech/sdk/kotlin/quickstart
49. Turso. **Embedded Replicas feature docs.** https://docs.turso.tech/features/embedded-replicas/introduction
50. tursodatabase/libsql-android. **Repository (technical preview notice).** https://github.com/tursodatabase/libsql-android
51. AndroidPoet. **supabase-kmp (official-style KMP SDK + community offline-sync modules).** https://github.com/androidpoet/supabase-kmp
52. Supabase. **Kotlin SDK installation docs.** https://supabase.com/docs/reference/kotlin/installing
53. Rocicorp. **When To Use Zero (explicitly excludes native mobile).** https://zero.rocicorp.dev/docs/when-to-use
54. Rocicorp. **Zero homepage.** https://zero.rocicorp.dev/
55. InfoQ. **Zero Reaches 1.0.** https://www.infoq.com/news/2026/06/zero-version-1/
56. aspen-cloud/triplit. **README.md.** https://github.com/aspen-cloud/triplit/blob/main/README.md
57. InstantDB. **React Native getting started.** https://www.instantdb.com/docs/start-rn
58. unsubbed.co. **InstantDB technical review (SDK language coverage).** https://unsubbed.co/tools/instant/
59. Jazz. **Homepage.** https://jazz.tools/
60. Jazz. **Docs (supported client frameworks).** https://jazz.tools/docs
61. garden-co/jazz. **Repository README.** https://github.com/garden-co/jazz
