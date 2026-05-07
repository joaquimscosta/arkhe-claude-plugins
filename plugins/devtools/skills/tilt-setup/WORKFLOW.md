# Workflow: Tilt Setup

## Decision Flow

```
USER invokes /devtools:tilt-setup
    |
    v
Run detect_tilt.py on project root
    |
    ├── tilt_binary.installed = false?
    │   └── Go to "Install Tilt"
    |
    ├── kubectl_context.is_production_pattern = true?
    │   └── STOP — show error, refuse to proceed until safe context
    |
    ├── tiltfile.exists = true?
    │   └── Go to "Phase 1: Audit"
    │
    └── tiltfile.exists = false?
        └── Go to "Phase 2: Scaffold"
```

---

## Install Tilt

Show commands based on `os` field from detector:

| OS | Command |
|----|---------|
| macOS | `brew install tilt-dev/tap/tilt` |
| Linux | `curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh \| bash` |
| Windows | `iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.ps1'))` |

After install, verify:
```bash
tilt version
```

Re-run detector to confirm installation.

**Also recommend** (if missing):
- `kubectl` — `brew install kubernetes-cli` (macOS)
- A local cluster — see "Local Cluster Choice" below

---

## Local Cluster Choice (when none detected)

If `kubectl_context.cluster_type == "unknown"` AND no production pattern matched, ask user via `AskUserQuestion`:

| Option | When to choose |
|--------|----------------|
| **OrbStack** (macOS) | Apple Silicon, lowest overhead, native ClusterIP. Install: `brew install orbstack`. |
| **k3d** (cross-platform) | Fastest cross-platform, built-in registry, Traefik default. Install: `brew install k3d`. |
| **kind** (cross-platform) | Best for CI parity, multi-node testing. Install: `brew install kind`. |
| **Docker Desktop** | If already installed and team standardized. Built-in K8s in preferences. |

After install, verify the kubectl context is safe:
```bash
kubectl config current-context
```

---

## Phase 1: Audit

### Step 1: Present Status Table

Display detection results as a formatted table:

```
| Component        | Status      | Detail                                         |
|------------------|-------------|------------------------------------------------|
| tilt binary      | installed   | v0.37.0 at /opt/homebrew/bin/tilt              |
| kubectl context  | safe        | docker-desktop                                 |
| Tiltfile         | found       | ./Tiltfile (320 lines)                         |
| Modular layout   | yes         | .tilt/ (config.star, services.star, *.yaml)    |
| Ecosystems       | 3 detected  | java-gradle (Spring Boot), nextjs, infra       |
| Service count    | 12 services | k8s_resource calls in Tiltfile                 |
| Safety guard     | yes         | manual validate_cluster_safety()               |
| .tiltignore      | yes         | ./.tiltignore                                  |
```

### Step 2: Present Violations

Group by severity (ERROR first, then WARNING, then INFO, then SUGGESTION):

```
## Audit Results — N violations

### ERRORS
| Rule    | Message                              | Fix                                  |
|---------|--------------------------------------|--------------------------------------|
| TILT001 | No production safety guard           | Add validate_cluster_safety() guard  |

### WARNINGS
| Rule    | Message                              | Fix                                  |
|---------|--------------------------------------|--------------------------------------|
| TILT004 | docker_build without live_update     | Add live_update= to docker_build     |
| TILT023 | Deprecated restart_container() used  | Use ext://restart_process            |

### INFO
| Rule    | Message                              | Fix                                  |
|---------|--------------------------------------|--------------------------------------|
| TILT010 | No .tiltignore file                  | Create .tiltignore with ignore patterns |
```

### Step 3: Offer Fixes

Use `AskUserQuestion` (multiSelect: true) listing each violation with its fix. User selects which to apply.

### Step 4: Per-Rule Fix Strategies

#### TILT001 — No production safety guard

Add at the **top** of the Tiltfile (before any deploys):

```python
def validate_cluster_safety():
    """Fail-fast guard against production deployments."""
    context = str(local("kubectl config current-context", quiet=True)).strip()

    blocked = [
        "arn:aws:eks:",   # AWS EKS ARN
        "gke_",           # GKE format
        "akscluster",     # AKS naming
        "prod",
        "production",
        "staging",
    ]
    for pattern in blocked:
        if pattern in context:
            fail("PRODUCTION SAFETY CHECK FAILED! Context: {}\n"
                 "Switch to a local context first.".format(context))

    safe = ["docker-desktop", "minikube", "kind-", "k3d-",
            "colima", "orbstack", "rancher-desktop", "localhost"]
    if not any(s in context.lower() for s in safe):
        print("WARNING: Unrecognized context '{}'. Proceeding.".format(context))

    print("Kubernetes context validated: " + context)

validate_cluster_safety()
```

Combine with `allow_k8s_contexts` for redundant safety:
```python
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-dev', 'k3d-local', 'orbstack'])
```

#### TILT002 — Manual guard missing patterns

Extend the `blocked` list:
```python
blocked = [
    "arn:aws:eks:", "gke_", "akscluster", ":aks/",
    "prod", "production", "staging",
]
```

#### TILT004 / TILT005 — `docker_build` / `custom_build` without `live_update`

Add `live_update=[...]` appropriate to the ecosystem (see "Ecosystem Templates" below).

#### TILT007 / TILT010 — Missing `watch_settings` / `.tiltignore`

Create `.tiltignore` next to the Tiltfile:
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

And add `watch_settings` in the Tiltfile:
```python
watch_settings(ignore=[
    '**/build/**', '**/.gradle/**', '**/node_modules/**',
    '**/__pycache__/**', '**/*.log', '**/.idea/**',
])
```

#### TILT008 — `live_update` with only `run()`, no `sync()`

Add `sync()` steps before `run()`:
```python
live_update=[
    fall_back_on(['Dockerfile', 'requirements.txt']),
    sync('./src/', '/app/src/'),         # ADD THIS
    run('pip install -r /app/requirements.txt',
        trigger=['./requirements.txt']),
]
```

#### TILT011 — `k8s_yaml` without `k8s_resource`

For each workload deployed via `k8s_yaml`, add a `k8s_resource()`:
```python
k8s_yaml('k8s/deployment.yaml')
k8s_resource(
    'myapp',
    port_forwards='8080:8080',
    resource_deps=['postgres'],
    labels=['services'],
)
```

#### TILT012 — No `update_settings` parallelism cap

Add near the top of Tiltfile:
```python
update_settings(max_parallel_updates=2)
```

Use `2` for laptops with 4–8 cores, `3` for desktops, default `3` is rarely the right answer for 4+ services.

#### TILT013 — Missing resource labels

Add `labels=` to each `k8s_resource()`:
- `labels=['infrastructure']` — postgres, redis, kafka, opensearch
- `labels=['services']` — application services
- `labels=['frontend']` — UI services
- `labels=['monitoring']` — prometheus, grafana
- `labels=['gateway']` — traefik, nginx

#### TILT016 — `live_update` missing `fall_back_on`

Add `fall_back_on()` as the **first** step:
```python
live_update=[
    fall_back_on(['Dockerfile', 'package.json', 'requirements.txt', 'build.gradle']),
    sync(...),
    run(...),
]
```

#### TILT020 — Tiltfile > 300 lines, no modularization

Extract to `.tilt/`:
```
.tilt/
  config.star          # CLI parsing, env loading
  services.star        # deploy_service() helper
  service-config.yaml  # service definitions
  environments.yaml    # presets
```

Then in Tiltfile:
```python
load('ext://namespace', 'namespace_create')         # Extensions: root only
load('ext://restart_process', 'docker_build_with_restart')

load('.tilt/config.star', 'parse_config', 'load_service_config')
load('.tilt/services.star', 'deploy_service')

cfg = parse_config()
svcs = load_service_config()
for name in cfg.get("services", []):
    deploy_service(name, svcs["services"][name], cfg)
```

#### TILT022 — Hardcoded service list

Move services to `.tilt/service-config.yaml`:
```yaml
services:
  postgres:
    type: external
    image: postgres:17
    ports: [5432]
  api:
    type: java-gradle
    build_context: ./api
    ports: [8080]
    dependencies: [postgres]
```

Load via `read_yaml(".tilt/service-config.yaml")`.

#### TILT023 — Deprecated `restart_container()`

Replace:
```python
# OLD (deprecated)
docker_build('myapp', '.', live_update=[
    sync('./src/', '/app/'),
    restart_container(),    # DEPRECATED
])

# NEW
load('ext://restart_process', 'docker_build_with_restart')

docker_build_with_restart(
    'myapp', '.',
    entrypoint=['./app'],
    live_update=[sync('./src/', '/app/')],
)
```

#### TILT025 — `config.parse()` without `tilt_config.json`

Create `tilt_config.json` in project root with sensible defaults:
```json
{
  "environment": "minimal",
  "debug": false
}
```

Tilt auto-reads this file; users can override with `tilt up -- --environment=full-stack`.

### Step 5: Verify

After fixes, re-run the detector and run:
```bash
tilt alpha tiltfile-result
```

This validates Tiltfile syntax without launching Tilt.

---

## Phase 2: Scaffold

### Step 1: Choose Pattern

Use `AskUserQuestion` to present options:

**Single-file** (1–3 services, 1 ecosystem):
- All logic in one `Tiltfile`
- Easy to discover all configuration at a glance
- Recommended threshold: < 200 lines

**Modular** (4+ services, 2+ ecosystems, or 2+ environment presets):
- Root `Tiltfile` + `.tilt/config.star` + `.tilt/services.star`
- `.tilt/service-config.yaml` (service definitions) + `.tilt/environments.yaml` (presets)
- Better separation of concerns; team-friendly

### Step 2: Choose Features (multiSelect)

| Feature | What it adds |
|---------|--------------|
| Manual context guard | `validate_cluster_safety()` function blocking prod patterns |
| PVC persistence toggle | Helper to create persistent PVCs outside Tilt's lifecycle |
| JDWP debug ports | Per-Java-service debug port forwards (5005–501x), env-controlled |
| Monitoring stack | Prometheus + Grafana via `helm_resource` (kube-prometheus-stack) |
| Traefik gateway | Traefik IngressRoute scaffolds with CRDs |

### Step 3: Generate Files

Use the templates below. Replace `myproject`, image names, and paths to match the detected ecosystems.

---

## Single-File Template

**`Tiltfile`**:
```python
"""
Single-file Tiltfile — minimal-viable starting point.
"""

# ----- Safety -----
def validate_cluster_safety():
    context = str(local("kubectl config current-context", quiet=True)).strip()
    blocked = ["arn:aws:eks:", "gke_", "akscluster", "prod", "production", "staging"]
    for p in blocked:
        if p in context:
            fail("PRODUCTION SAFETY CHECK FAILED! Context: " + context)
    print("Context: " + context)

validate_cluster_safety()
allow_k8s_contexts(['docker-desktop', 'minikube', 'kind-dev', 'k3d-local', 'orbstack'])

# ----- File watch performance -----
watch_settings(ignore=[
    '**/build/**', '**/dist/**', '**/.gradle/**',
    '**/node_modules/**', '**/__pycache__/**', '**/*.log',
])

# ----- Parallelism cap -----
update_settings(max_parallel_updates=2)

# ----- Build & deploy (replace per ecosystem) -----
docker_build(
    'myapp',
    context='.',
    only=['./src/'],
    live_update=[
        fall_back_on(['Dockerfile', 'package.json']),
        sync('./src/', '/app/src/'),
    ],
)

k8s_yaml(['k8s/deployment.yaml', 'k8s/service.yaml'])

k8s_resource(
    'myapp',
    port_forwards='8080:8080',
    labels=['services'],
)
```

**`.tiltignore`** (alongside Tiltfile):
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

---

## Modular Template

### Layout
```
project/
├── Tiltfile
├── .tiltignore
├── tilt_config.json
├── .tilt/
│   ├── config.star
│   ├── services.star
│   ├── service-config.yaml
│   └── environments.yaml
└── k8s/                     # Optional: raw manifests for special services
```

### `Tiltfile` (root orchestrator)

```python
"""
Modular Tiltfile — multi-service orchestrator.
"""

# Extensions MUST load from root (Starlark constraint)
load('ext://namespace', 'namespace_create')
load('ext://restart_process', 'docker_build_with_restart')

# Sub-modules
load('.tilt/config.star', 'parse_config', 'load_service_config', 'load_environments')
load('.tilt/services.star', 'deploy_service')

# ----- Safety -----
def validate_cluster_safety():
    context = str(local("kubectl config current-context", quiet=True)).strip()
    blocked = ["arn:aws:eks:", "gke_", "akscluster", ":aks/",
               "prod", "production", "staging"]
    for p in blocked:
        if p in context:
            fail("PRODUCTION SAFETY CHECK FAILED! Context: " + context)
    print("Context validated: " + context)

validate_cluster_safety()

# ----- Performance -----
watch_settings(ignore=[
    '**/build/**', '**/.gradle/**', '**/node_modules/**',
    '**/__pycache__/**', '**/*.log', '**/.idea/**',
])
update_settings(max_parallel_updates=2)

# ----- Main -----
def main():
    cfg = parse_config()
    svc_configs = load_service_config()
    environments = load_environments()
    namespace = cfg.get("namespace", "myproject")

    namespace_create(namespace)

    # Resolve which services to deploy
    env_name = cfg.get("environment", "")
    if env_name and env_name in environments:
        services = environments[env_name].get("services", [])
        print("Deploying environment '{}': {}".format(
            env_name, environments[env_name].get("description", "")
        ))
    else:
        services = cfg.get("services", [])
        if not services:
            print("Available environments: " + ", ".join(environments.keys()))
            print("Usage: tilt up -- --environment=<name>")
            return

    for svc_name in services:
        if svc_name not in svc_configs.get("services", {}):
            fail("Service '{}' not in service-config.yaml".format(svc_name))
        deploy_service(
            svc_name,
            svc_configs["services"][svc_name],
            namespace,
            debug=cfg.get("debug", False),
        )

main()
```

### `.tilt/config.star`

```python
def parse_config():
    config.define_string_list("services", usage="Services to deploy")
    config.define_string("environment", usage="Environment preset")
    config.define_string("namespace", usage="Kubernetes namespace")
    config.define_bool("debug", usage="Enable JDWP debug ports")
    cfg = config.parse()
    return {
        "services": cfg.get("services", []),
        "environment": cfg.get("environment", ""),
        "namespace": cfg.get("namespace", "myproject"),
        "debug": cfg.get("debug", False),
    }


def load_service_config():
    return read_yaml(".tilt/service-config.yaml")


def load_environments():
    data = read_yaml(".tilt/environments.yaml")
    return data.get("environments", {})
```

### `.tilt/services.star`

```python
def deploy_service(name, cfg, namespace, debug=False):
    """Deploy a service based on its type."""
    svc_type = cfg.get("type", "external")

    if svc_type == "external":
        _deploy_external(name, cfg, namespace)
    elif svc_type == "java-gradle":
        _deploy_java_gradle(name, cfg, namespace, debug)
    elif svc_type == "nextjs":
        _deploy_nextjs(name, cfg, namespace)
    elif svc_type == "python":
        _deploy_python(name, cfg, namespace)
    else:
        fail("Unknown service type: " + svc_type)


def _deploy_external(name, cfg, namespace):
    manifest = _generate_manifest(name, cfg, namespace, image=cfg["image"])
    k8s_yaml(blob(manifest))
    k8s_resource(
        name,
        port_forwards=["{}:{}".format(p, p) for p in cfg.get("ports", [])],
        resource_deps=cfg.get("dependencies", []),
        labels=[cfg.get("label", "infrastructure")],
    )


def _deploy_java_gradle(name, cfg, namespace, debug):
    image = "myproject-" + name
    build_ctx = cfg["build_context"]

    # Compile on host (fast iteration)
    local_resource(
        name + "-compile",
        cmd="./gradlew :{}:classes -x test".format(name),
        deps=[build_ctx + "/src/main/java"],
        labels=["build"],
        allow_parallel=True,
    )

    # Build image with live update of compiled classes
    custom_build(
        image,
        "./gradlew :{}:bootJar && docker build -t $EXPECTED_REF "
        "--build-arg SERVICE_NAME={} -f Dockerfile.dev .".format(name, name),
        deps=[build_ctx + "/build/libs"],
        live_update=[
            sync(build_ctx + "/build/classes/java/main",
                 "/workspace/application/BOOT-INF/classes"),
            sync(build_ctx + "/build/resources/main",
                 "/workspace/application/BOOT-INF/classes"),
        ],
    )

    manifest = _generate_manifest(name, cfg, namespace, image=image, debug=debug)
    k8s_yaml(blob(manifest))

    pf = ["{}:{}".format(p, p) for p in cfg.get("ports", [])]
    if debug:
        # JDWP debug port — assign per service from cfg
        pf.append("{}:5005".format(cfg.get("debug_port", 5005)))

    k8s_resource(
        name,
        port_forwards=pf,
        resource_deps=cfg.get("dependencies", []),
        labels=[cfg.get("label", "services")],
    )


def _deploy_nextjs(name, cfg, namespace):
    # Preferred: run as local_resource (native HMR)
    local_resource(
        name,
        serve_cmd="cd {} && pnpm dev".format(cfg["build_context"]),
        deps=[cfg["build_context"] + "/src"],
        labels=[cfg.get("label", "frontend")],
        links=["http://localhost:{}".format(cfg["ports"][0])] if cfg.get("ports") else [],
    )


def _deploy_python(name, cfg, namespace):
    image = "myproject-" + name
    build_ctx = cfg["build_context"]
    docker_build(
        image,
        build_ctx,
        dockerfile=build_ctx + "/Dockerfile.dev",
        live_update=[
            fall_back_on([build_ctx + "/pyproject.toml",
                          build_ctx + "/uv.lock"]),
            sync(build_ctx + "/", "/app/"),
            run("uv sync --frozen",
                trigger=[build_ctx + "/pyproject.toml",
                         build_ctx + "/uv.lock"]),
        ],
    )
    manifest = _generate_manifest(name, cfg, namespace, image=image)
    k8s_yaml(blob(manifest))
    k8s_resource(
        name,
        port_forwards=["{}:{}".format(p, p) for p in cfg.get("ports", [])],
        resource_deps=cfg.get("dependencies", []),
        labels=[cfg.get("label", "services")],
    )


def _generate_manifest(name, cfg, namespace, image, debug=False):
    """Generate Deployment + Service YAML inline."""
    ports = cfg.get("ports", [])
    port_yaml = "\n".join([
        "        - containerPort: {}".format(p) for p in ports
    ])
    svc_port_yaml = "\n".join([
        "    - port: {}\n      targetPort: {}".format(p, p) for p in ports
    ])
    env_yaml = ""
    for ev in cfg.get("env_vars", []):
        env_yaml += "        - name: {}\n          value: \"{}\"\n".format(
            ev["name"], ev["value"]
        )

    resources = cfg.get("resources", {})
    resource_yaml = ""
    if resources:
        resource_yaml = """        resources:
          requests:
            memory: "{mem}"
            cpu: "{cpu}"
          limits:
            memory: "{mem_l}"
            cpu: "{cpu_l}"
""".format(
            mem=resources.get("memory", "256Mi"),
            cpu=resources.get("cpu", "100m"),
            mem_l=resources.get("memory_limit", resources.get("memory", "512Mi")),
            cpu_l=resources.get("cpu_limit", resources.get("cpu", "500m")),
        )

    return """---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {ns}
  labels:
    app: {name}
    managed-by: tilt
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
        managed-by: tilt
    spec:
      containers:
      - name: {name}
        image: {image}
        ports:
{ports}
        env:
{env}
{resources}---
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {ns}
spec:
  selector:
    app: {name}
  ports:
{svc_ports}
""".format(
        name=name, ns=namespace, image=image,
        ports=port_yaml, svc_ports=svc_port_yaml,
        env=env_yaml, resources=resource_yaml,
    )
```

### `.tilt/service-config.yaml`

```yaml
services:
  postgres:
    type: external
    image: postgres:17
    ports: [5432]
    label: infrastructure
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
    type: java-gradle
    build_context: ./apps/api
    ports: [8080]
    debug_port: 5013
    dependencies: [postgres]
    label: services
    env_vars:
      - name: SPRING_PROFILES_ACTIVE
        value: dev
    resources:
      memory: "512Mi"
      cpu: "250m"
      memory_limit: "1Gi"
      cpu_limit: "1000m"

  web:
    type: nextjs
    build_context: ./apps/web
    ports: [3000]
    label: frontend
```

### `.tilt/environments.yaml`

```yaml
environments:
  minimal:
    description: "Database only — fastest startup"
    services: [postgres]

  backend:
    description: "Database + API"
    services: [postgres, api]

  full-stack:
    description: "Full stack — DB + API + Web"
    services: [postgres, api, web]
```

### `tilt_config.json` (defaults)

```json
{
  "environment": "minimal",
  "debug": false
}
```

---

## Ecosystem Templates

### Spring Boot (Java/Gradle)

**`Dockerfile.dev`** (layertools pattern for fast live_update):
```dockerfile
FROM eclipse-temurin:21-jre AS base
WORKDIR /workspace
ARG SERVICE_NAME
COPY ${SERVICE_NAME}/build/libs/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre
WORKDIR /workspace/application
COPY --from=base /workspace/dependencies/ ./
COPY --from=base /workspace/spring-boot-loader/ ./
COPY --from=base /workspace/snapshot-dependencies/ ./
COPY --from=base /workspace/application/ ./
ENV DEBUG_PORT=5005
ENV SUSPEND_MODE=n
ENTRYPOINT ["sh", "-c", "java \
  -agentlib:jdwp=transport=dt_socket,server=y,suspend=${SUSPEND_MODE},address=*:${DEBUG_PORT} \
  org.springframework.boot.loader.launch.JarLauncher"]
```

Add Spring Boot DevTools to the service's `build.gradle`:
```groovy
dependencies {
    developmentOnly 'org.springframework.boot:spring-boot-devtools'
}
```

### Next.js

**Approach A — local_resource (preferred, native HMR)**:
```python
local_resource(
    'web',
    serve_cmd='cd apps/web && pnpm dev',
    deps=['apps/web/src'],
    links=['http://localhost:3000'],
    labels=['frontend'],
)
```

**Approach B — container with HMR** (when team requires K8s parity):

`Dockerfile.dev`:
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install
COPY . .
ENV WATCHPACK_POLLING=true
CMD ["pnpm", "dev"]
```

```python
docker_build('web', './apps/web',
    dockerfile='./apps/web/Dockerfile.dev',
    live_update=[
        fall_back_on(['apps/web/package.json', 'apps/web/next.config.js']),
        sync('./apps/web/src/', '/app/src/'),
        run('pnpm install', trigger=['./apps/web/package.json']),
    ]
)
k8s_resource('web', port_forwards='3000:3000', labels=['frontend'])
```

### Python (FastAPI / uvicorn with uv)

**`Dockerfile.dev`**:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["uv", "run", "uvicorn", "main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--reload"]
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
k8s_resource('python-api', port_forwards='8000:8000', labels=['services'])
```

### External (Postgres / Redis / Kafka)

```yaml
# In service-config.yaml
postgres:
  type: external
  image: postgres:17
  ports: [5432]
```

The `_deploy_external()` helper generates a Deployment + Service. For stateful services, also create a PVC (see "PVC Persistence" below).

---

## Optional Features

### PVC Persistence Toggle

Add to `services.star`:
```python
def create_persistent_pvc(name, namespace, storage_size, persist):
    """Create a PVC. When persist=True, create outside Tilt's lifecycle
    so it survives `tilt down`."""
    pvc_manifest = """apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {name}-pvc
  namespace: {ns}
  labels:
    app: {name}
    managed-by: tilt
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: {size}
""".format(name=name, ns=namespace, size=storage_size)

    if persist:
        local("kubectl get namespace {} 2>/dev/null || kubectl create namespace {}"
              .format(namespace, namespace))
        local("echo '{}' | kubectl apply -f -".format(pvc_manifest))
        print("PVC for {} persisted (survives tilt down)".format(name))
    else:
        k8s_yaml(blob(pvc_manifest))
```

Toggle via `.env` or `tilt_config.json`:
```json
{"postgres_persist": true}
```

### JDWP Debug Ports (Java)

Already wired into `_deploy_java_gradle()` above. Per-service ports defined in `service-config.yaml`:
```yaml
api:
  type: java-gradle
  debug_port: 5013   # IntelliJ remote JVM debug → localhost:5013
```

User triggers with: `tilt up -- --debug`

### Monitoring Stack (Prometheus + Grafana)

Add to root Tiltfile (after main services):
```python
load('ext://helm_resource', 'helm_resource', 'helm_repo')

if config.tilt_subcommand != "down":
    helm_repo('prometheus-community',
        'https://prometheus-community.github.io/helm-charts',
        labels=['monitoring'])

    helm_resource('kube-prometheus-stack',
        chart='prometheus-community/kube-prometheus-stack',
        namespace='monitoring',
        flags=['--create-namespace',
               '--set', 'grafana.adminPassword=admin'],
        port_forwards=['9090:9090', '3001:3000'],
        labels=['monitoring'],
        auto_init=False,    # opt-in only
    )
```

User triggers via Tilt UI (sidebar) or `tilt enable kube-prometheus-stack`.

### Traefik Gateway

Apply CRDs synchronously before Tilt manages anything:
```python
local("kubectl apply -f traefik/crds.yaml 2>/dev/null || true")
local("kubectl wait --for=condition=Established "
      "crd/ingressroutes.traefik.io --timeout=30s 2>/dev/null || true")

k8s_yaml(['traefik/deployment.yaml', 'traefik/service.yaml'])
k8s_resource('traefik',
    port_forwards=['8000:8000', '8180:8080'],   # gateway, dashboard
    labels=['gateway'],
)
```

---

## Verification

After scaffold or audit fixes:

1. **Validate Tiltfile syntax**:
   ```bash
   tilt alpha tiltfile-result
   ```

2. **Re-run detector**:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/detect_tilt.py <project-root>
   ```

3. **Show confirmation summary**:
   ```
   | Step          | Action                          | Result      |
   |---------------|---------------------------------|-------------|
   | Tool          | tilt v0.37.0                    | installed   |
   | Tiltfile      | scaffolded (modular)            | created     |
   | Files         | .tilt/{config,services}.star   | created     |
   | Files         | .tilt/{service-config,environments}.yaml | created |
   | Safety        | manual context guard            | enabled     |
   | .tiltignore   | created                         | yes         |
   ```

4. **Suggest next steps**:
   - `tilt up` to start the development environment
   - `tilt up -- --environment=minimal` for the lightest preset
   - Open the Tilt UI at http://localhost:10350
   - Commit `Tiltfile`, `.tilt/`, `.tiltignore`, `tilt_config.json` to git
