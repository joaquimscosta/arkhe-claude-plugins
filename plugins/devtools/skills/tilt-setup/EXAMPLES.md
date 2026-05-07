# Examples: Tilt Setup

## Example 1: Greenfield Single-Service (Python API)

### Detection Output

```json
{
  "tilt_binary": {"installed": true, "version": "0.37.0"},
  "kubectl_binary": {"installed": true, "version": "1.30.0"},
  "kubectl_context": {
    "context": "docker-desktop",
    "is_production_pattern": false,
    "is_safe_pattern": true,
    "cluster_type": "docker-desktop"
  },
  "tiltfile": {"exists": false},
  "tilt_layout": {"exists": false},
  "tiltignore": {"exists": false},
  "ecosystems": [
    {"ecosystem": "python", "package_manager": "uv", "root": "."},
    {"ecosystem": "infra", "has_dockerfile": true, "has_compose": false, "has_k8s_manifests": true, "root": "."}
  ],
  "os": "macos"
}
```

### Scaffold Session

**Status**: tilt installed, no Tiltfile, single Python service.

**User chooses**: Single-file pattern, features = [Manual context guard, PVC persistence].

### Generated `Tiltfile`

```python
"""
Tiltfile — Python API single-service setup.
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

# ----- Performance -----
watch_settings(ignore=[
    '**/__pycache__/**', '**/*.pyc', '**/*.log',
    '**/.pytest_cache/**', '**/.mypy_cache/**',
])
update_settings(max_parallel_updates=2)

# ----- Build -----
docker_build(
    'myapp/python-api',
    context='.',
    dockerfile='Dockerfile.dev',
    only=['./src/', './pyproject.toml', './uv.lock', './main.py'],
    live_update=[
        fall_back_on(['pyproject.toml', 'uv.lock']),
        sync('./src/', '/app/src/'),
        sync('./main.py', '/app/main.py'),
        run('uv sync --frozen', trigger=['./pyproject.toml', './uv.lock']),
    ],
)

# ----- Deploy -----
k8s_yaml(['k8s/postgres.yaml', 'k8s/api.yaml'])

k8s_resource('postgres',
    port_forwards='5432:5432',
    labels=['infrastructure'],
)
k8s_resource('python-api',
    port_forwards='8000:8000',
    resource_deps=['postgres'],
    labels=['services'],
    links=['http://localhost:8000/docs'],
)
```

### Generated `Dockerfile.dev`

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

### Generated `.tiltignore`

```
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
*.log
.idea/
.vscode/
*.md
```

---

## Example 2: Modular Multi-Service (Spring Boot + Next.js + Postgres)

### Detection Output

```json
{
  "tilt_binary": {"installed": true, "version": "0.37.0"},
  "kubectl_context": {
    "context": "orbstack",
    "is_production_pattern": false,
    "is_safe_pattern": true,
    "cluster_type": "orbstack"
  },
  "tiltfile": {"exists": false},
  "tilt_layout": {"exists": false},
  "ecosystems": [
    {"ecosystem": "java-gradle", "build_file": "build.gradle.kts", "is_spring_boot": true, "root": "apps/api"},
    {"ecosystem": "nextjs", "root": "apps/web"},
    {"ecosystem": "infra", "has_dockerfile": true, "has_k8s_manifests": false, "root": "."}
  ],
  "os": "macos"
}
```

### Scaffold Session

**Status**: 2 ecosystems (java-gradle Spring Boot + nextjs), no Tiltfile.

**User chooses**: Modular pattern, features = [Manual context guard, PVC persistence, JDWP debug, Monitoring].

### Generated Files

**`Tiltfile`** (root): see WORKFLOW.md "Modular Template → Tiltfile" — same content.

**`tilt/service-config.yaml`**:

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
    persistent: true
    storage_size: 1Gi
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
      - name: SPRING_DATASOURCE_URL
        value: jdbc:postgresql://postgres:5432/myapp
    health_check:
      path: /actuator/health
      port: 8080
      initialDelaySeconds: 30
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
    dependencies: [api]
```

**`tilt/environments.yaml`**:

```yaml
environments:
  minimal:
    description: "Database only"
    services: [postgres]

  backend:
    description: "Database + API"
    services: [postgres, api]

  full-stack:
    description: "Full stack"
    services: [postgres, api, web]
```

**`tilt_config.json`**:

```json
{
  "environment": "minimal",
  "debug": false,
  "namespace": "myapp"
}
```

### Usage

```bash
# Smallest startup
tilt up -- --environment=minimal

# Backend dev
tilt up -- --environment=backend --debug    # JDWP on 5013

# Full stack
tilt up -- --environment=full-stack
```

---

## Example 3: Audit Existing Tiltfile (Sellabella-style)

### Detection Output

```json
{
  "tiltfile": {
    "exists": true,
    "path": "Tiltfile",
    "line_count": 521,
    "docker_build_count": 0,
    "custom_build_count": 0,
    "k8s_yaml_count": 3,
    "k8s_resource_count": 0,
    "live_update_count": 0,
    "deprecated_restart_container_count": 0,
    "has_allow_k8s_contexts": false,
    "has_watch_settings": true,
    "has_update_settings": true,
    "has_manual_context_guard": true,
    "guard_blocks_eks": true,
    "guard_blocks_gke": false,
    "loads_local_starfiles": true,
    "loads_extensions": true,
    "max_parallel_updates": 2
  },
  "tilt_layout": {
    "exists": true,
    "path": ".tilt",
    "star_files": ["config.star", "services.star"],
    "yaml_files": ["environments.yaml", "service-config.yaml"],
    "is_modular": true
  },
  "tiltignore": {"exists": true},
  "audit": {
    "violations": [
      {"rule": "TILT002", "severity": "ERROR",
       "message": "Manual context guard missing dangerous patterns: GKE prefix ('gke_')",
       "fix_hint": "Add the missing patterns to the blocklist in validate_cluster_safety()"},
      {"rule": "TILT011", "severity": "INFO",
       "message": "k8s_yaml() used without any k8s_resource() calls",
       "fix_hint": "Add k8s_resource() to wire up port_forwards, labels, and resource_deps"}
    ],
    "summary": {"total": 2, "errors": 1, "warnings": 0, "info": 1, "suggestions": 0}
  }
}
```

### Audit Report

```
## Audit Results — 2 violations (1 error, 1 info)

### ERRORS
| Rule    | Message                                                          | Fix                                       |
|---------|------------------------------------------------------------------|-------------------------------------------|
| TILT002 | Manual context guard missing GKE prefix ('gke_')                 | Add 'gke_' to blocklist                   |

### INFO
| Rule    | Message                                                          | Fix                                       |
|---------|------------------------------------------------------------------|-------------------------------------------|
| TILT011 | k8s_yaml() without k8s_resource() (note: may be in services.star)| Verify k8s_resource calls in sub-modules  |

Note: This Tiltfile uses the legacy `.tilt/` directory (sellabella convention; the
detector recognizes both `tilt/` and `.tilt/`). The detector parses only the root
Tiltfile, so k8s_resource calls in services.star are not counted.
```

**User selects**: TILT002 to fix. Skips TILT011 (false positive — modular layout).

### After Fix

The `validate_cluster_safety()` function in `Tiltfile` is updated to add `gke_`:

```python
production_contexts = [
    "arn:aws:eks:us-east-1:390403866510:cluster/sellabella-eks",
    "sellabella-eks",
    "sellabella-prod",
    "sellabella-production",
    "gke_",          # ADDED
    "akscluster",    # ADDED
    "prod",
    "production",
]
```

Re-running the detector shows 0 errors remaining.

---

## Example 4: Production Context Detected — Refuse to Proceed

### Detection Output

```json
{
  "tilt_binary": {"installed": true, "version": "0.37.0"},
  "kubectl_context": {
    "context": "arn:aws:eks:us-east-1:123456789:cluster/myapp-prod",
    "is_production_pattern": true,
    "is_safe_pattern": false,
    "cluster_type": "unknown"
  },
  "tiltfile": {"exists": false}
}
```

### Skill Response

```
🚨 PRODUCTION CONTEXT DETECTED 🚨

Current kubectl context: arn:aws:eks:us-east-1:123456789:cluster/myapp-prod

This appears to be an AWS EKS production cluster. Tilt is designed for
LOCAL DEVELOPMENT ONLY.

To proceed:
  1. Switch to a local context:
       kubectl config use-context docker-desktop
       OR
       kubectl config use-context orbstack
       OR
       kubectl config use-context kind-dev

  2. Verify the switch:
       kubectl config current-context

  3. Re-run /devtools:tilt-setup

I will NOT scaffold or modify Tilt configuration while a production
context is active.
```

The skill stops here. No files are created or modified.

---

## Example 5: Already-Compliant Tiltfile

### Detection Output

```json
{
  "tiltfile": {
    "exists": true,
    "line_count": 180,
    "docker_build_count": 2,
    "live_update_count": 2,
    "fall_back_on_count": 2,
    "sync_count": 4,
    "k8s_yaml_count": 1,
    "k8s_resource_count": 3,
    "has_allow_k8s_contexts": true,
    "has_manual_context_guard": true,
    "guard_blocks_eks": true,
    "guard_blocks_gke": true,
    "has_watch_settings": true,
    "has_update_settings": true,
    "deprecated_restart_container_count": 0,
    "max_parallel_updates": 2
  },
  "tiltignore": {"exists": true},
  "audit": {
    "violations": [],
    "summary": {"total": 0, "errors": 0, "warnings": 0, "info": 0, "suggestions": 0}
  }
}
```

### Result

```
Tilt audit complete — no violations found.

Your Tiltfile follows best practices:
  - Manual context guard blocks all dangerous patterns (EKS, GKE, prod, staging)
  - allow_k8s_contexts is also configured (defense in depth)
  - All docker_build calls have live_update with fall_back_on + sync
  - watch_settings and update_settings configured
  - .tiltignore present
  - 3 k8s_resource calls match 3 deployed workloads
  - max_parallel_updates=2 (laptop-friendly)

No changes needed. Run `tilt up` to start the dev environment.
```
