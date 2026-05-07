---
title: "tilt-local-kubernetes-development-setup"
version: "1.0.0"
status: Published
created: 2026-05-07
last_updated: 2026-05-07
slug: tilt-local-kubernetes-development-setup
aliases: ["tilt kubernetes", "tiltfile best practices", "local k8s development", "tilt dev setup"]
tags: ["tilt", "kubernetes", "local-dev", "devtools", "docker", "live-update", "spring-boot", "nextjs", "python"]
promoted_at: 2026-05-07T13:48:26.567697Z
last_refreshed: 2026-05-07T13:02:19.093902+00:00
sources: []
---

<!-- AUTO-GENERATED: Start -->
---
slug: tilt-local-kubernetes-development-setup
title: Tilt Local Kubernetes Development Setup
aliases:
  - tilt kubernetes
  - tiltfile best practices
  - local k8s development
  - tilt dev setup
tags:
  - tilt
  - kubernetes
  - local-dev
  - devtools
  - docker
  - live-update
  - spring-boot
  - nextjs
  - python
researched_at: 2026-05-07T00:00:00Z
expires_at: 2026-06-06T00:00:00Z
sources:
  - url: https://docs.tilt.dev/tiltfile_authoring.html
    title: Writing Your First Tiltfile - Tilt Docs
  - url: https://docs.tilt.dev/api.html
    title: Tiltfile API Reference - Tilt Docs
  - url: https://docs.tilt.dev/live_update_reference.html
    title: Live Update Reference - Tilt Docs
  - url: https://docs.tilt.dev/choosing_clusters.html
    title: Choosing a Local Dev Cluster - Tilt Docs
  - url: https://docs.tilt.dev/tiltfile_config.html
    title: Tiltfile Config - Tilt Docs
  - url: https://docs.tilt.dev/file_changes.html
    title: Debugging File Changes - Tilt Docs
  - url: https://docs.tilt.dev/extensions.html
    title: Extensions - Tilt Docs
  - url: https://docs.tilt.dev/local_resource.html
    title: Local Resources - Tilt Docs
  - url: https://docs.tilt.dev/resource_dependencies.html
    title: Resource Dependencies - Tilt Docs
  - url: https://github.com/tilt-dev/tilt-extensions
    title: tilt-dev/tilt-extensions - Official Extensions Repo
  - url: https://github.com/tilt-dev/tilt-example-java
    title: tilt-dev/tilt-example-java - Official Java Example
  - url: https://github.com/tilt-dev/tilt-example-nodejs
    title: tilt-dev/tilt-example-nodejs - Official Node.js Example
  - url: https://github.com/tilt-dev/tilt-avatars
    title: tilt-dev/tilt-avatars - Official Python/React Demo
---

# Tilt Local Kubernetes Development Setup

## Executive Summary

- **Tilt** is a local Kubernetes development tool that watches source files, builds images, applies YAML, and live-updates running containers — all from a single `Tiltfile` written in Starlark (Python subset).
- **`docker_build`** is the standard choice; use **`custom_build`** when a non-Docker tool (Jib, Bazel, Gradle) produces the image or when you need a shell-level build pipeline.
- **`live_update`** is the core DX accelerator: `sync()` + `run()` + optional `restart_container()` (via `ext://restart_process`) replaces image rebuild + redeploy cycles.
- **Production safety** requires either `allow_k8s_contexts(['docker-desktop', 'kind-...'])` or a manual guard that reads `kubectl config current-context` and calls `fail()` on blocked patterns.
- **Modular layout** (`tilt/config.star`, `tilt/services.star`, external YAML loaded via `read_yaml`) is strongly preferred for projects with 3+ services, 2+ ecosystems, or multiple environment presets.
- **YAML config externalization** (`read_yaml()` / `decode_yaml()` for service definitions and environment presets) is widely adopted in large projects and validated by the sellabella pattern.
- **`k8s_resource`** wires together port forwards, labels, `resource_deps`, and `trigger_mode`; always call it after `k8s_yaml` and `docker_build`.
- **`watch_settings(ignore=[...])`** and `.tiltignore` prevent build churn from `build/`, `.gradle/`, `node_modules/`, and test output directories.
- **Local cluster pick for 2025**: OrbStack (macOS) or k3d (cross-platform) for most teams; kind for CI parity; docker-desktop if tooling mandates it.
- **PVC persistence toggle** (managed by Tilt vs. created via `local("kubectl apply")` outside Tilt's lifecycle) is the standard pattern for stateful services that should survive `tilt down`.

---

## Decision Matrix: Single-File vs. Modular Tiltfile

| Dimension | Single `Tiltfile` | Modular `tilt/*.star` |
|---|---|---|
| Number of services | 1–3 | 4+ |
| Number of ecosystems | 1 | 2+ (e.g., Java + Node + Python) |
| Environment presets | 0–1 | 2+ (minimal, backend-core, full-stack) |
| YAML config | Hardcoded | Externalized YAML files |
| Team size | Solo / small | Multi-person |
| Tiltfile lines | < 200 | > 200 or growing |
| Recommendation | Simple — keep it flat | Modularize immediately |

**Rule of thumb**: When the Tiltfile exceeds ~200 lines or has more than one logical section repeated per service, extract to `tilt/`.

**When NOT to split**: Splitting `.star` files has a key constraint — `load('ext://...')` cannot be called from `load()`-ed or `include()`-ed sub-files (resolved in Tilt >= v0.25 for most cases, but extensions must be loaded from the root `Tiltfile`). Load extensions at the top of `Tiltfile`, then pass imported symbols into sub-modules as function arguments.

---

## Tilt API Reference

### `docker_build`

```python
docker_build(
    ref,           # Image name (must match k8s YAML image field)
    context,       # Build context directory
    dockerfile='Dockerfile',         # Path to Dockerfile
    dockerfile_contents='',          # Inline Dockerfile (alternative)
    only=[],       # Restrict context to these paths (reduces rebuild triggers)
    ignore=[],     # Exclude paths from context AND watch
    live_update=[], # LiveUpdateStep list
    target='',     # Multi-stage target (e.g., 'dev')
    ssh='',        # SSH agent forwarding for private deps
    secret='',     # BuildKit secrets
    build_args={}, # ARG values
    entrypoint=[], # Override container entrypoint
    platform='',   # e.g., 'linux/amd64' for cross-arch builds
)
```

**When to use `docker_build`**: Any service with a standard Dockerfile. Tilt handles image naming, tag injection into YAML, and `pullPolicy: IfNotPresent` injection automatically for local clusters.

**Key patterns**:
- Use `only=['./src/']` in monorepos so unrelated sibling changes don't trigger rebuilds.
- Use `ignore=['./dist/', './node_modules/']` to exclude build artifacts.
- Use `target='dev'` with multi-stage Dockerfiles to stay on the dev stage.
- Use `dockerfile_contents=` for generated or inline Dockerfiles.

### `custom_build`

```python
custom_build(
    ref,           # Image name
    command,       # Shell command — MUST tag image as $EXPECTED_REF
    deps=[],       # Paths that trigger a rebuild when changed
    ignore=[],     # Exclude from deps watch (dockerignore syntax, relative to each dep)
    live_update=[], # Same LiveUpdateStep list as docker_build
    entrypoint=[],
)
```

**When to use `custom_build`**:
- Java/Gradle + Jib: `custom_build('myapp', './gradlew jibDockerBuild --image $EXPECTED_REF', deps=['src'])`
- Any build pipeline requiring shell steps before `docker build`
- Multi-step builds: compile → package → docker build (the sellabella Java pattern)

**Note**: `custom_build` does not auto-inject `pullPolicy: IfNotPresent`. Handle this in YAML if needed. The `$EXPECTED_REF` env var contains the fully-qualified image ref Tilt expects to find after the command runs.

### `k8s_yaml` / `helm` / `kustomize`

```python
# Raw YAML
k8s_yaml('deploy/app.yaml')
k8s_yaml(['svc.yaml', 'deploy.yaml'])

# Kustomize
k8s_yaml(kustomize('./k8s/overlays/dev'))

# Helm
k8s_yaml(helm('./charts/myapp', values=['values-dev.yaml']))

# Inline YAML blob (generated manifests)
k8s_yaml(blob(generated_yaml_string))

# From external command
k8s_yaml(local('./scripts/gen-yaml.sh'))
```

**Tradeoffs**:
- Raw YAML: maximum control, no abstraction overhead, works when manifests are already templated.
- Kustomize: good for overlay-based environments (base + dev/prod patches).
- Helm: best when upstream chart exists; prefer `ext://helm_resource` extension over `helm()` for lifecycle management.
- `blob()`: the sellabella pattern — generate manifests programmatically in Starlark (no external tools needed).

### `k8s_resource`

```python
k8s_resource(
    workload,           # Name must match k8s object name from k8s_yaml
    new_name='',        # Rename in Tilt UI
    port_forwards=[],   # '8080', '8080:80', port_forward(8080, 80, name='web')
    resource_deps=[],   # Wait for these resources to be ready first
    labels=[],          # UI grouping (displayed in sidebar)
    trigger_mode=TRIGGER_MODE_AUTO,  # or TRIGGER_MODE_MANUAL
    auto_init=True,     # False: start disabled
    pod_readiness='',   # 'ignore' to skip pod readiness check
    links=[],           # Clickable links in Tilt UI
    objects=[],         # Extra k8s objects to associate (CRDs, ConfigMaps)
)
```

**Key behaviors**:
- `resource_deps` only applies to the **first** startup after `tilt up`. Once the dependency has been healthy once, the ordering is released for subsequent updates.
- `trigger_mode=TRIGGER_MODE_MANUAL`: resource won't auto-build on file changes. Useful for heavy builds.
- `pod_readiness='ignore'`: resource is "ready" as soon as YAML is applied (no pod health check). Useful for CRDs, Jobs, StatefulSets without readiness probes.
- `labels` group resources visually — use `['infrastructure']` for databases, `['services']` for application services.

### `live_update` Steps

```python
live_update=[
    fall_back_on(['package.json', 'Dockerfile']),  # Full rebuild triggers
    sync('./src/', '/app/src/'),                    # Copy files into container
    run('pip install -r /app/requirements.txt',     # Run command in container
        trigger=['./requirements.txt']),            # Only if trigger files changed
    # restart_container() is DEPRECATED — use ext://restart_process instead
]
```

**`sync(local, remote)`**:
- `local` must be inside `docker_build.context` or `custom_build.deps`.
- Syncs incrementally — only changed files are transferred.
- Deletes are also synced.

**`run(cmd, trigger=[])`**:
- Command runs from `/` in the container — use absolute paths.
- `trigger` files must also be listed in a `sync` step.
- `run` steps must come **after** all `sync` steps.

**`fall_back_on(paths)`**:
- Must be the **first** step in the `live_update` list.
- Triggers full image rebuild + redeploy when these files change.
- Use for: Dockerfile, package.json, requirements.txt, build.gradle, go.mod.

**Restart after live_update**: Use the `ext://restart_process` extension:
```python
load('ext://restart_process', 'docker_build_with_restart')
docker_build_with_restart('myapp', '.', entrypoint=['./app'], live_update=[...])
```

### `watch_settings` and `.tiltignore`

```python
watch_settings(ignore=[
    '**/build/**',
    '**/.gradle/**',
    '**/node_modules/**',
    '**/*.md',
    '**/.idea/**',
    '**/logs/**',
    '**/__pycache__/**',
])
```

`.tiltignore` (same directory as `Tiltfile`, `.dockerignore` syntax):
```
build/
.gradle/
node_modules/
*.md
*.log
.idea/
__pycache__/
```

**Distinction**: `.tiltignore` and `watch_settings(ignore=)` prevent file changes from triggering rebuilds. They do NOT affect which files are included in Docker build contexts — use `.dockerignore` or `docker_build(ignore=[...])` for that.

### `update_settings`

```python
update_settings(
    max_parallel_updates=3,      # Default is 3; cap lower to reduce CPU load
    k8s_upsert_timeout_secs=30,  # Timeout for k8s apply operations
)
```

The sellabella pattern uses `max_parallel_updates=2` for a ~17-service project to prevent CPU saturation on developer laptops.

### `local_resource`

```python
# One-shot build step (e.g., compile on host before live_update)
local_resource(
    'compile',
    cmd='./gradlew :service-name:classes -x test',
    deps=['src/main/java'],
    labels=['build'],
    allow_parallel=True,
    auto_init=True,
)

# Persistent server (alternative to K8s deployment)
local_resource(
    'nextjs-dev',
    serve_cmd='pnpm run dev',
    deps=['src/'],
    labels=['frontend'],
    links=['http://localhost:3000'],
)
```

**Use cases**:
- Compile-on-host for JVM services (host compilation → live_update sync of `.class` files)
- Linters, code generators triggered by file changes
- Running services locally (e.g., Next.js with HMR) instead of in K8s

### `config.parse()` and CLI Args

```python
config.define_string_list("services", usage="Comma-separated services to run")
config.define_string("environment", usage="Preset environment name")
config.define_bool("debug", usage="Enable JDWP debugging")
cfg = config.parse()

# Invocation: tilt up -- --environment=backend-core --debug
```

Store long-lived defaults in `tilt_config.json` (auto-read by Tilt):
```json
{"environment": "minimal", "debug": false}
```

Update without restart: `tilt args -- --environment=full-stack`

### Extensions

Load via `load('ext://ext-name', 'function')`. Extensions are fetched from [`github.com/tilt-dev/tilt-extensions`](https://github.com/tilt-dev/tilt-extensions) and cached in `~/.local/share/tilt-dev/` (XDG data dir).

**Key extensions**:
- `ext://restart_process`: `docker_build_with_restart` — replaces deprecated `restart_container()`
- `ext://namespace`: `namespace_create` — idempotent namespace creation
- `ext://helm_remote`: Deploy remote Helm charts (lifecycle-managed)
- `ext://helm_resource`: Deploy Helm charts with more control (preferred over `helm_remote` for new projects)
- `ext://configmap`: `configmap_create` — create ConfigMaps from files

**Constraint**: Extensions can only be `load()`-ed from the root `Tiltfile`, not from sub-files loaded via `load()`. Pass extension functions as arguments to helper modules.

---

## Project Organization Patterns

### Pattern 1: Single-File Tiltfile (1–3 services)

```
project/
├── Tiltfile
├── .tiltignore
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── src/
└── Dockerfile
```

```python
# Tiltfile (complete)
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-dev'])
watch_settings(ignore=['**/build/**', '**/node_modules/**'])
update_settings(max_parallel_updates=3)

docker_build('myapp', '.', live_update=[
    sync('./src/', '/app/src/'),
])
k8s_yaml('k8s/')
k8s_resource('myapp', port_forwards='8080', labels=['services'])
```

### Pattern 2: Modular `tilt/` Layout (4+ services)

```
project/
├── Tiltfile                      # Root orchestrator
├── .tiltignore                   # Global file watch ignores
├── tilt_config.json              # Default CLI arg values
├── tilt/
│   ├── config.star               # CLI arg parsing, .env loading, env preset merging
│   ├── services.star             # Service deployment logic (build + manifest + k8s_resource)
│   ├── service-config.yaml       # Service definitions (type, ports, deps, env_vars, resources)
│   └── environments.yaml         # Environment presets (groups of services + bundled config)
└── k8s/                          # Optional: manual manifests for special services
    └── traefik/
        └── *.yaml
```

**Key Starlark patterns**:
```python
# In config.star
def load_environments():
    return read_yaml("tilt/environments.yaml").get("environments", {})

# In Tiltfile — load extensions at root, then call sub-modules
load('ext://namespace', 'namespace_create')
load('tilt/config.star', 'parse_config', 'load_service_config')
load('tilt/services.star', 'deploy_service')
```

**`service-config.yaml` schema** (sellabella pattern):
```yaml
services:
  user-service:
    type: java-gradle            # external | java-gradle | nextjs | python | manual-manifest
    build_context: ../backend/user-service
    ports: [8091]
    dependencies: ["postgres", "configuration-service"]
    env_vars:
      - name: SPRING_PROFILES_ACTIVE
        value: "dev"
    health_check:
      path: /actuator/health
      port: 8091
      initialDelaySeconds: 30
    resources:
      memory: "512Mi"
      cpu: "250m"
      memory_limit: "1Gi"
      cpu_limit: "1000m"
```

**`environments.yaml` schema** (sellabella pattern):
```yaml
environments:
  minimal:
    description: "PostgreSQL + Config Service only"
    services: [postgres, configuration-service]
  backend-core:
    description: "Essential backend services"
    services: [postgres, configuration-service, user-service]
    config:
      spring_profiles: dev
      persist_data: false
  full-stack:
    description: "All services"
    services: [postgres, kafka, traefik, prometheus, grafana, user-service, sellabella-ui]
    config:
      persist_data: true
```

### Real-World Examples

**Sellabella (this codebase)**: 17+ service modular pattern. Key characteristics:
- `custom_build` for all Java services (Gradle → JAR → Docker)
- `local_resource` for host compilation (`gradlew :service:classes`)
- `live_update` syncs compiled `.class` files from host to container
- Manual `kubectl apply` via `local()` for CRDs before Tilt manages them
- `namespace_create` from `ext://namespace` for idempotent namespace setup
- PVC persistence toggle: `local("kubectl apply")` vs `k8s_yaml(blob(pvc_manifest))`
- Orphan cleanup: `kubectl get deployments -l managed-by=tilt` + delete unlisted ones

**tilt-dev/pixeltilt**: Multi-language (Go + Next.js). Uses `docker_build_with_restart` for Go services, plain `docker_build` with file sync for Next.js frontend.

**tilt-dev/tilt-avatars**: Python/Flask + React/Vite. Clean example of `fall_back_on` for config files and `sync` for source files.

---

## Ecosystem Live_Update Recipes

### Spring Boot (Java/Gradle)

**Approach**: Compile on host → sync `.class` files → Spring Boot DevTools restarts.

```dockerfile
# Dockerfile.dev (layertools extraction pattern)
FROM eclipse-temurin:21-jre AS base
WORKDIR /workspace
ARG SERVICE_NAME
ARG VERSION
COPY backend/${SERVICE_NAME}/build/libs/${SERVICE_NAME}-${VERSION}.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre
WORKDIR /workspace/application
# Layer ordering: static first, classes last (most volatile)
COPY --from=base /workspace/dependencies/ ./
COPY --from=base /workspace/spring-boot-loader/ ./
COPY --from=base /workspace/snapshot-dependencies/ ./
COPY --from=base /workspace/application/ ./
ENTRYPOINT ["java", \
  "-agentlib:jdwp=transport=dt_socket,server=y,suspend=${SUSPEND_MODE:-n},address=*:${DEBUG_PORT:-5005}", \
  "org.springframework.boot.loader.launch.JarLauncher"]
```

```python
# Tiltfile / services.star
load('ext://restart_process', 'docker_build_with_restart')

# Step 1: Compile on host (fast, avoids rebuild)
local_resource(
    '{}-compile'.format(svc),
    cmd='./gradlew :{}:classes -x test'.format(svc),
    deps=[build_context + '/src/main/java'],
    labels=['build'],
    allow_parallel=True,
)

# Step 2: Full build uses custom_build (Gradle + Docker)
custom_build(
    image_name,
    build_command,    # Shell: gradlew assemble + docker build
    deps=[
        build_context + '/src',
        build_context + '/build/classes',
        build_context + '/build/resources',
    ],
    live_update=[
        sync(build_context + '/build/classes/java/main',
             '/workspace/application/BOOT-INF/classes'),
        sync(build_context + '/build/resources/main',
             '/workspace/application/BOOT-INF/classes'),
    ],
    ignore=[build_context + '/build/tmp/'],
)
```

**JDWP debug port pattern** (sellabella):
- Each service has a unique debug port (5005–5013)
- Port forwarded via `k8s_resource(port_forwards=['5005:5005'])`
- SUSPEND_MODE env var controls whether service waits for debugger

**Alternative (simpler, official)**: Use `docker_build_with_restart` and `local_resource` for compile step:
```python
load('ext://restart_process', 'docker_build_with_restart')

local_resource('compile', './gradlew bootJar && unzip -o build/libs/*.jar -d build/jar',
    deps=['src', 'build.gradle'])

docker_build_with_restart('myapp', './build/jar',
    entrypoint=['java', '-cp', '.:./lib/*', 'com.example.Main'],
    dockerfile='./Dockerfile.dev',
    live_update=[
        sync('./build/jar/BOOT-INF/lib', '/app/lib'),
        sync('./build/jar/BOOT-INF/classes', '/app'),
    ],
)
```

### Next.js (Node.js)

**Approach A: Local process** (preferred — native HMR, no K8s overhead):
```python
local_resource(
    'nextjs',
    serve_cmd='cd frontend && pnpm install && pnpm run dev',
    deps=['frontend/src'],
    labels=['frontend'],
    links=['http://localhost:3000'],
)
```

**Approach B: K8s container with HMR**:
```dockerfile
# Dockerfile.tilt (dev stage)
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ENV WATCHPACK_POLLING=true   # Required in containers
CMD ["npm", "run", "dev"]
```

```python
docker_build('frontend', './frontend',
    dockerfile='./frontend/Dockerfile.tilt',
    live_update=[
        fall_back_on(['package.json', 'next.config.js']),
        sync('./frontend/src/', '/app/src/'),
        run('npm install', trigger=['./frontend/package.json']),
    ]
)
k8s_resource('frontend', port_forwards='3000:3000', labels=['frontend'])
```

**Note**: `WATCHPACK_POLLING=true` is required for Next.js file watching inside containers (volume mounts use polling, not inotify).

### Python (FastAPI / uvicorn)

```dockerfile
# Dockerfile.dev
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY . .
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

```python
docker_build('python-api', '.',
    dockerfile='Dockerfile.dev',
    live_update=[
        fall_back_on(['pyproject.toml', 'uv.lock']),
        sync('./', '/app/'),
        run('uv sync --frozen', trigger=['./pyproject.toml', './uv.lock']),
    ]
)
```

**With pip/requirements.txt**:
```python
docker_build('python-api', '.',
    live_update=[
        fall_back_on(['requirements.txt']),
        sync('.', '/app'),
        run('pip install -r /app/requirements.txt', trigger='./requirements.txt'),
    ]
)
```

The `--reload` flag on uvicorn handles the actual hot-reload after sync. No `restart_container()` needed for interpreted Python.

### Generic Node.js (nodemon / ts-node-dev)

```python
docker_build('node-api', '.',
    build_args={'NODE_ENV': 'development'},
    entrypoint='yarn run nodemon /app/index.js',
    live_update=[
        fall_back_on(['package.json', 'yarn.lock']),
        sync('.', '/app'),
        run('cd /app && yarn install', trigger=['./package.json', './yarn.lock']),
    ]
)
```

**Key**: The `entrypoint` override to nodemon/ts-node-dev is set in `docker_build`, not the Dockerfile — this keeps the Dockerfile prod-clean and adds dev tooling only via Tilt.

---

## Production Safety Guards

### Method 1: `allow_k8s_contexts` (Official, Simple)

```python
# Tilt auto-allows: minikube, docker-desktop, microk8s, kind, k3d, rancher-desktop, orbstack
# Add your team's custom local contexts:
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-dev', 'k3d-local', 'orbstack'])
```

**Limitation**: As of Tilt v0.34.x, there's a known issue ([#6295](https://github.com/tilt-dev/tilt/issues/6295)) where switching kubectl context while Tilt is running may not re-check the allowlist immediately for some resource types.

**Auto-allowed contexts** (no configuration needed): `minikube`, `docker-desktop`, `docker-for-desktop`, `microk8s`, `kind-*`, `k3d-*`, `crc-*`, `krucible`, `orbstack`, `rancher-desktop`.

### Method 2: Manual Context Guard (More Defensive, Sellabella Pattern)

```python
def validate_cluster_safety():
    """Fail-fast guard against production deployments"""
    context = str(local("kubectl config current-context", quiet=True)).strip()

    # Blocklist: known production patterns
    blocked = [
        "arn:aws:eks:",           # Any AWS EKS ARN
        "sellabella-eks",
        "sellabella-prod",
        "gke_",                   # GKE contexts (format: gke_PROJECT_REGION_CLUSTER)
        "akscluster",             # AKS contexts
        "prod",
        "production",
        "staging",
    ]
    for pattern in blocked:
        if pattern in context:
            fail("PRODUCTION SAFETY CHECK FAILED! Context: {}\n"
                 "Switch to a local context first.".format(context))

    # Allowlist: known safe patterns
    safe = ["docker-desktop", "docker-for-desktop", "minikube", "kind-",
            "k3d-", "k3s-", "colima", "orbstack", "rancher-desktop", "localhost"]
    if not any(s in context.lower() for s in safe):
        print("WARNING: Unrecognized context '{}'. Proceeding with caution.".format(context))

    print("Kubernetes context validated: " + context)

validate_cluster_safety()
```

**Why manual over `allow_k8s_contexts`**:
- Custom block patterns (EKS ARN format, GKE prefix) not possible with `allow_k8s_contexts`
- Explicit `fail()` messages guide engineers to the fix
- The guard runs synchronously at Tiltfile parse time — before any K8s operations

**Recommended pattern**: Use `allow_k8s_contexts` for simple projects; use the manual guard for enterprise projects with diverse cluster naming.

---

## Local Cluster Comparison

### Feature Table

| Cluster | Startup | RAM Idle | Multi-node | Built-in Registry | Ingress OOB | Apple Silicon | Windows | CI Ready |
|---|---|---|---|---|---|---|---|---|
| **OrbStack** | ~5s | Low (~150MB) | No | No | Auto wildcard domains | Excellent (native) | No | No |
| **Docker Desktop** | ~30s | High (~1GB) | No | No | NodePort only | Good (Rosetta) | Yes | No |
| **kind** | ~20s | Medium (~580MB) | Yes | Via ctlptl | No (MetalLB needed) | Good | Yes | Excellent |
| **k3d** | ~5s | Low (~520MB) | Yes | Built-in | Traefik (default) | Good | Yes | Excellent |
| **minikube** | ~17–30s | Medium (~600MB) | Via drivers | Via addon | nginx addon | Good | Yes | Moderate |
| **Rancher Desktop** | ~60s | Medium | No | No | Traefik (k3s) | Good | Yes | No |

### Per-Cluster Notes

**OrbStack** (macOS only):
- Fastest startup and lowest resource usage on Apple Silicon
- Full ClusterIP and LoadBalancer IP access (unlike Docker Desktop)
- Auto wildcard `.local.gd` domains for ingress without `/etc/hosts` edits
- Tilt automatically recognizes the `orbstack` context (no `allow_k8s_contexts` needed as of Tilt v0.34.0)
- No Windows support. Closed-source (but free for personal use).

**Docker Desktop**:
- Simplest setup — enable Kubernetes in preferences, no extra tools
- Built images are immediately available in-cluster (no push needed)
- High resource usage, slow with many services
- Tilt auto-allows `docker-desktop` context
- Persistent volumes: `hostPath` via `docker.io/hostpath` StorageClass

**kind**:
- Best for CI/CD parity — same tool used by Kubernetes upstream CI
- Fast cluster creation (~20s), fast teardown
- Local image registry requires `ctlptl` setup (or manual docker registry pod)
- No ingress by default — install MetalLB or `cloud-provider-kind` for LoadBalancer
- Excellent for multi-node testing and CRD-heavy setups
- Persistent volumes: `standard` StorageClass via `kind/local-path-provisioner`

**k3d** (k3s in Docker):
- Fastest non-OrbStack option (<5s startup)
- Built-in local registry (`k3d registry create`) designed for Tilt
- Comes with Traefik ingress controller by default
- Persistent volumes: `local-path` StorageClass
- The Tilt docs recommend k3d for speed-focused workflows

**minikube**:
- Most full-featured: multiple container runtimes, multiple Kubernetes versions
- Better for testing with specific Kubernetes versions or kernel-level requirements
- `minikube addons enable ingress` enables nginx
- `minikube addons enable registry` for local image registry
- Docker driver makes it similar to kind in performance

**Rancher Desktop**:
- User-friendly desktop GUI
- Bundles k3s + Traefik out of the box (including ingress)
- Not suitable for CI; ideal for developers who want GUI management
- Slower startup than k3d/OrbStack

### 2025 Recommendations

- **macOS Apple Silicon**: OrbStack (performance + DX) or k3d (cross-platform parity)
- **Linux**: k3d or kind (both excellent, minimal overhead)
- **Windows**: Docker Desktop or Rancher Desktop
- **CI/CD**: kind (standard) or k3d (speed)
- **Tilt recommendation**: kind (production parity) or k3d (speed) per official docs

---

## Audit Rule Set

The following rules should be detected by the `tilt-setup` skill's audit phase. Severity: `ERROR` = blocks safety/correctness, `WARNING` = degrades DX significantly, `INFO` = best-practice deviation, `SUGGESTION` = optimization opportunity.

| Rule ID | Severity | Name | Detection Heuristic | Fix Hint |
|---|---|---|---|---|
| TILT001 | ERROR | No production safety guard | `Tiltfile` has no `allow_k8s_contexts()` AND no `validate_cluster_safety`-style `local("kubectl config current-context")` + `fail()` pattern | Add `allow_k8s_contexts(['docker-desktop', ...])` or manual context guard at top of Tiltfile |
| TILT002 | ERROR | Blocking dangerous context | Manual context guard exists but does not block EKS ARN pattern (`arn:aws:eks:`) or GKE prefix (`gke_`) | Add `"arn:aws:eks:"` and `"gke_"` to blocklist |
| TILT003 | ERROR | `tilt_config.json` committed with secrets | `tilt_config.json` contains API keys, passwords, or tokens | Move secrets to `.env` (gitignored); use `os.getenv()` in Tiltfile |
| TILT004 | WARNING | `docker_build` without `live_update` | `docker_build()` call with no `live_update` argument for a service type that supports it | Add `live_update=[sync(), ...]` appropriate to ecosystem |
| TILT005 | WARNING | `custom_build` without `live_update` | `custom_build()` call with no `live_update` for an application service | Add live_update; use `local_resource` compile step + class file sync |
| TILT006 | WARNING | Missing `resource_deps` between dependent services | Service declares `dependencies` in config but no `resource_deps` in `k8s_resource()` | Add `resource_deps=['database', 'config-service']` to dependent service |
| TILT007 | WARNING | No `watch_settings(ignore=[...])` for build artifacts | No `watch_settings` call AND no `.tiltignore` with build dir patterns | Add `watch_settings(ignore=['**/build/**', '**/.gradle/**', '**/node_modules/**'])` |
| TILT008 | WARNING | `live_update` with only `run()`, no `sync()` | `live_update=[run(...)]` with no preceding `sync()` step | A `run`-only live_update doesn't transfer changed files; add `sync()` first |
| TILT009 | WARNING | Hardcoded namespace strings repeated | Same namespace string literal appears 3+ times without a variable | Extract to `NAMESPACE = 'my-namespace'` constant |
| TILT010 | WARNING | Missing `.tiltignore` | No `.tiltignore` file in Tiltfile directory | Create `.tiltignore` with ecosystem-appropriate patterns |
| TILT011 | INFO | `k8s_yaml` without `k8s_resource` | `k8s_yaml()` call for a pod-having workload with no matching `k8s_resource()` | Add `k8s_resource()` for port forwards, labels, and resource_deps |
| TILT012 | INFO | No `update_settings` parallelism cap | No `update_settings(max_parallel_updates=N)` with 4+ services | Add `update_settings(max_parallel_updates=3)` (or 2 for laptop use) |
| TILT013 | INFO | Missing resource labels | `k8s_resource()` calls with no `labels=[]` argument | Add `labels=['services']` or `labels=['infrastructure']` for UI grouping |
| TILT014 | INFO | No `port_forwards` on application service | Application service `k8s_resource()` has no `port_forwards` | Add `port_forwards='HOST:CONTAINER'` for local access |
| TILT015 | INFO | `docker_build` context too broad in monorepo | `docker_build` context is `.` with no `only=[]` in a multi-service repo | Add `only=['./service-dir/']` to prevent cross-service rebuilds |
| TILT016 | INFO | `live_update` missing `fall_back_on` for config files | `live_update` present but no `fall_back_on(['Dockerfile', 'package.json'])` | Add `fall_back_on` for files that require full image rebuild |
| TILT017 | INFO | No `links=[]` on services with Web UI | Services like Grafana, Traefik, or app UIs have no `links=` in `k8s_resource` | Add `links=[link('http://localhost:PORT', 'UI')]` |
| TILT018 | INFO | PVC managed by Tilt for stateful service | Stateful services (postgres, kafka) use `k8s_yaml(pvc)` without a persistence toggle | Add persistence toggle: create PVC via `local("kubectl apply")` to survive `tilt down` |
| TILT019 | INFO | Debug port not forwarded when debug enabled | Service has JDWP env vars but no debug port in `k8s_resource(port_forwards=)` | Add debug port forward e.g. `'5005:5005'` when debug mode is active |
| TILT020 | SUGGESTION | Tiltfile > 300 lines with no modularization | Single `Tiltfile` exceeds 300 lines with no `load('tilt/...')` calls | Extract service logic to `tilt/services.star` and config to `tilt/config.star` |
| TILT021 | SUGGESTION | No environment preset system | Project has 4+ services but no `config.define_string("environment")` / preset groups | Add environment presets via `config.parse()` and a service groups dict |
| TILT022 | SUGGESTION | Hardcoded service list | Services are listed inline rather than loaded from YAML | Extract to `tilt/service-config.yaml` + `read_yaml()` |
| TILT023 | SUGGESTION | `restart_container()` used directly | Tiltfile uses deprecated `restart_container()` in `live_update` | Replace with `ext://restart_process` → `docker_build_with_restart()` |
| TILT024 | SUGGESTION | No `auto_init=False` for heavy optional services | Monitoring services (Prometheus, Grafana) start on every `tilt up` with no opt-in | Add `k8s_resource('prometheus', auto_init=False)` for optional-by-default services |
| TILT025 | SUGGESTION | No `tilt_config.json` for team defaults | No `tilt_config.json` in project root with sensible defaults | Create `tilt_config.json` with default environment/feature flags |

---

## Scaffold Templates

### Template 1: Minimal Single-File Tiltfile

```python
"""
Minimal Tiltfile — single service.
Replace: myapp, myregistry/myapp, ./k8s/
"""

# Safety
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-dev', 'k3d-local', 'orbstack'])

# File watch performance
watch_settings(ignore=[
    '**/build/**',
    '**/dist/**',
    '**/node_modules/**',
    '**/.gradle/**',
    '**/*.log',
    '**/__pycache__/**',
])

# Parallelism cap
update_settings(max_parallel_updates=3)

# Build
docker_build(
    'myregistry/myapp',
    context='.',
    dockerfile='Dockerfile',
    only=['./src/', './config/'],
    live_update=[
        fall_back_on(['Dockerfile', 'requirements.txt']),
        sync('./src/', '/app/src/'),
    ],
)

# Deploy
k8s_yaml(['k8s/deployment.yaml', 'k8s/service.yaml'])

# Wire up
k8s_resource(
    'myapp',
    port_forwards='8080:8080',
    labels=['services'],
)
```

### Template 2: Modular `tilt/` Layout (Minimal-Viable)

**`Tiltfile`** (root):
```python
"""
Modular Tiltfile — multi-service project.
"""
# Extensions must load from root Tiltfile
load('ext://namespace', 'namespace_create')
load('ext://restart_process', 'docker_build_with_restart')

# Sub-modules
load('tilt/config.star', 'parse_config', 'load_service_config')
load('tilt/services.star', 'deploy_service')

watch_settings(ignore=[
    '**/build/**', '**/.gradle/**', '**/node_modules/**',
    '**/__pycache__/**', '**/*.log', '**/.idea/**',
])
update_settings(max_parallel_updates=2)

def validate_context():
    ctx = str(local("kubectl config current-context", quiet=True)).strip()
    if any(p in ctx for p in ["arn:aws:eks:", "gke_", "prod", "production"]):
        fail("BLOCKED: Production context detected: " + ctx)
    print("Context OK: " + ctx)

validate_context()

def main():
    cfg = parse_config()
    svc_configs = load_service_config()
    namespace = cfg.get("namespace", "myproject")
    namespace_create(namespace)

    services = cfg.get("services", list(svc_configs.get("services", {}).keys()))
    for svc_name in services:
        svc = svc_configs["services"][svc_name]
        deploy_service(svc_name, svc, namespace, cfg.get("debug", False))

main()
```

**`tilt/config.star`**:
```python
def parse_config():
    config.define_string_list("services", usage="Services to run")
    config.define_string("namespace", usage="Kubernetes namespace")
    config.define_bool("debug", usage="Enable JDWP debug ports")
    cfg = config.parse()
    return {
        "services": cfg.get("services", []),
        "namespace": cfg.get("namespace", "myproject"),
        "debug": cfg.get("debug", False),
    }

def load_service_config():
    return read_yaml("tilt/service-config.yaml")
```

**`tilt/services.star`**:
```python
def deploy_service(name, cfg, namespace, debug=False):
    svc_type = cfg.get("type", "external")
    image_name = "myproject-" + name

    if svc_type == "external":
        image = cfg["image"]
    elif svc_type == "python":
        docker_build(image_name, cfg.get("build_context", "./services/" + name),
            live_update=[sync(cfg.get("build_context", ".") + "/", "/app/")])
        image = image_name
    else:
        docker_build(image_name, cfg.get("build_context", "."))
        image = image_name

    # Generate manifest inline
    manifests = _generate_manifest(name, cfg, namespace, image, debug)
    k8s_yaml(blob(manifests))

    # Port forwards
    ports = cfg.get("ports", [])
    pf = ["{}:{}".format(p, p) for p in ports]
    if debug:
        pf.append("5005:5005")  # JDWP

    k8s_resource(name,
        port_forwards=pf,
        resource_deps=[d for d in cfg.get("dependencies", [])],
        labels=[cfg.get("label", "services")],
    )
```

**`tilt/service-config.yaml`**:
```yaml
services:
  postgres:
    type: external
    image: postgres:17
    ports: [5432]
    env_vars:
      - name: POSTGRES_DB
        value: myapp
      - name: POSTGRES_USER
        value: dev
      - name: POSTGRES_PASSWORD
        value: dev
    resources:
      memory: "256Mi"
      cpu: "250m"

  api:
    type: python
    build_context: ./api
    ports: [8000]
    dependencies: ["postgres"]
    health_check:
      path: /health
      port: 8000
    resources:
      memory: "256Mi"
      cpu: "100m"
```

**`.tiltignore`**:
```
build/
dist/
.gradle/
node_modules/
__pycache__/
*.pyc
*.log
.idea/
.vscode/
*.md
```

**Monitoring addon scaffold** (Prometheus + Grafana via Helm):
```python
# In Tiltfile, after main services:
load('ext://helm_resource', 'helm_resource', 'helm_repo')

helm_repo('prometheus-community',
    'https://prometheus-community.github.io/helm-charts',
    labels=['monitoring'])

helm_resource('kube-prometheus-stack',
    chart='prometheus-community/kube-prometheus-stack',
    namespace='monitoring',
    flags=['--create-namespace'],
    port_forwards=['9090:9090', '3001:3000'],
    labels=['monitoring'],
)
```

---

## References & Further Reading

### Official Documentation
- [Tiltfile API Reference](https://docs.tilt.dev/api.html) — Complete API for all Tiltfile builtins
- [Live Update Reference](https://docs.tilt.dev/live_update_reference.html) — sync, run, fall_back_on, restart
- [Tiltfile Config](https://docs.tilt.dev/tiltfile_config.html) — config.parse(), tilt_config.json, tilt args
- [File Changes & Ignores](https://docs.tilt.dev/file_changes.html) — .tiltignore, watch_settings, only=, ignore=
- [Choosing a Cluster](https://docs.tilt.dev/choosing_clusters.html) — Official cluster comparison
- [Many Tiltfiles & Repos](https://docs.tilt.dev/multiple_repos.html) — load(), include(), monorepo patterns
- [Resource Dependencies](https://docs.tilt.dev/resource_dependencies.html) — resource_deps, update_settings
- [Custom Image Builders](https://docs.tilt.dev/custom_build.html) — custom_build guide
- [Extensions](https://docs.tilt.dev/extensions.html) — ext:// system, extension repos

### Example Repositories
- [tilt-dev/tilt-example-java](https://github.com/tilt-dev/tilt-example-java) — Progression from 0-base to 4-recommended with live_update + Spring Boot layertools
- [tilt-dev/tilt-example-nodejs](https://github.com/tilt-dev/tilt-example-nodejs) — nodemon + live_update sync pattern
- [tilt-dev/tilt-example-python](https://github.com/tilt-dev/tilt-example-python) — Flask + pip install trigger pattern
- [tilt-dev/tilt-avatars](https://github.com/tilt-dev/tilt-avatars) — Python/Flask + React/Vite multi-service reference
- [tilt-dev/pixeltilt](https://github.com/tilt-dev/pixeltilt) — Go + Next.js multi-language pattern
- [tilt-dev/tilt-extensions](https://github.com/tilt-dev/tilt-extensions) — Official extension repository

### Community & Blog
- [OrbStack vs Docker Desktop](https://orbstack.dev/docs/compare/docker-desktop) — 2025 macOS cluster comparison
- [minikube vs kind vs k3d](https://oilbeater.com/en/2024/02/22/minikube-vs-kind-vs-k3d/) — Performance benchmarks
- [Local Kubernetes Dev Clusters Compared](https://www.augmentedmind.de/2022/07/24/kubernetes-development-clusters/) — Detailed feature matrix
- [Tilt Config Blog Post](https://blog.tilt.dev/2020/02/21/add-your-own-options-to-your-tilt-config.html) — config.parse() + service groups pattern
- [tilt-dev/tilt-local-metrics](https://github.com/tilt-dev/tilt-local-metrics/blob/main/Tiltfile) — Prometheus + Grafana monitoring Tiltfile reference

### Starlark/Tiltfile Testing
- `tilt alpha tiltfile-result` — Parse and validate a Tiltfile without running Tilt
- `tilt doctor` — Diagnose cluster compatibility (shows detected cluster type and context)
- `tilt edit` — Live-edit file watches for debugging ignore patterns
<!-- AUTO-GENERATED: End -->

<!-- TEAM-NOTES: Start -->
## Team Context

**Subdirectory naming**: We scaffold the modular layout into `tilt/` (visible directory) rather than `.tilt/`. The Tilt project itself only mandates `Tiltfile`, `.tiltignore`, and `tilt_config.json` filenames — the subdirectory name is project-defined. The `.tilt/` form appears in the sellabella codebase but is not an official or community convention. Visible naming makes the team-editable YAML files (`service-config.yaml`, `environments.yaml`) easier to discover. The `tilt-setup` skill's auditor still recognizes legacy `.tilt/` directories so existing projects audit cleanly.

<!-- TEAM-NOTES: End -->
