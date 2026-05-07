# Troubleshooting: Tilt Setup

## Installation Issues

### `tilt: command not found` after install

**Symptom**: Running `tilt version` returns "command not found".

**Causes**:
- macOS: Homebrew tap not added before install
- Linux: `~/.local/bin` not on `PATH`

**Fix**:
```bash
# macOS — re-add tap
brew install tilt-dev/tap/tilt

# Linux — add to PATH in ~/.zshrc or ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc

# Verify
tilt version
```

### `tilt up` fails with "no such cluster"

**Symptom**: `kubectl config current-context` returns empty or an unknown context.

**Cause**: No local Kubernetes cluster is running.

**Fix** (pick one):
```bash
# Docker Desktop — enable Kubernetes in Settings
# OrbStack — enable Kubernetes in app preferences
# kind
kind create cluster --name dev

# k3d
k3d cluster create dev
```

Then verify: `kubectl get nodes` should list at least one node.

### Tilt installed but version too old (< 0.30)

**Symptom**: `Tilt version 0.20.x is missing required features`.

**Fix**: Upgrade.
```bash
# macOS
brew upgrade tilt

# Linux
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
```

Required features (`docker_build_with_restart`, `helm_resource`, native OrbStack support) need Tilt 0.34+.

---

## Detection Issues

### Detector reports `kubectl_context.is_production_pattern: true` for safe context

**Symptom**: A custom local cluster name (e.g., `mycompany-dev`) gets flagged as production.

**Cause**: The substring matcher catches generic words like `prod` or `staging` even in non-prod contexts.

**Fix**: Rename the cluster, OR after scaffolding, edit the `validate_cluster_safety()` function in `Tiltfile` to remove the offending pattern from `blocked` list.

**Important**: Be deliberate — don't weaken the guard for convenience. If you're unsure whether a context is safe, it's safer to add it to a `safe` whitelist than to remove blocks.

### Ecosystems not detected

**Symptom**: Java/Spring Boot project shows `ecosystems: []`.

**Causes**:
- Service is nested deeper than 2 levels (detector checks root + 1 level + monorepo subdirs `apps/`, `services/`, `backend/`, `frontend/`)
- Build file is in unusual location (e.g., `cmd/api/build.gradle`)

**Fix**: Run the detector from a parent directory, or restructure to put build files in conventional monorepo locations.

### `is_spring_boot: false` for Spring Boot project

**Symptom**: Project clearly uses Spring Boot but detector says no.

**Cause**: Detector greps build files for `spring-boot` or `springframework.boot`. If dependencies are managed in a parent `build.gradle.kts` or BOM, the per-service file may not contain the marker.

**Fix**: Add a comment like `// spring-boot project` to the service's `build.gradle.kts`, OR manually treat the service as `java-gradle` with Spring Boot patterns when scaffolding.

---

## Audit False Positives

### TILT011 fires on a modular Tiltfile

**Symptom**: `k8s_yaml() used without any k8s_resource() calls` even though `k8s_resource` is called in `services.star`.

**Cause**: The audit only parses the root `Tiltfile`, not loaded sub-modules.

**Fix**: Skip this violation when the project uses a modular layout (`tilt_layout.is_modular: true`). The detector flags these for awareness but the warning is informational in modular projects.

### TILT016 fires when `fall_back_on` is in a sub-module

**Symptom**: Same root cause as TILT011 — fall_back_on calls in `services.star` aren't counted.

**Fix**: Skip when `tilt_layout.is_modular: true`. To remove false positives entirely, move at least one `fall_back_on` to the root Tiltfile.

---

## Scaffold Issues

### `load('ext://...')` fails with "module not found"

**Symptom**: Tilt errors with `Error parsing Tiltfile: cannot load 'ext://...': module not found`.

**Causes**:
1. First run — Tilt needs to download the extension. Re-run `tilt up`.
2. Trying to `load('ext://...')` from a sub-`.star` file (this is not allowed).

**Fix**: Move all `load('ext://...')` calls to the **root** `Tiltfile`. Then pass extension symbols as arguments to your sub-module functions:

```python
# Tiltfile (root)
load('ext://restart_process', 'docker_build_with_restart')
load('.tilt/services.star', 'deploy_service')

deploy_service('myapp', cfg, namespace, _build_with_restart=docker_build_with_restart)
```

### `live_update` doesn't trigger on file changes

**Symptom**: Editing source files doesn't update the container.

**Causes**:
1. File path in `sync(local, remote)` doesn't match build context.
2. File is excluded by `.tiltignore` or `watch_settings(ignore=)`.
3. Container uses a tool that can't detect filesystem changes via inotify (common in Next.js/webpack).

**Fix**:
1. Verify `local` path is inside `docker_build` context. Tilt prints a clear error if not.
2. Check `.tiltignore` patterns — add a comment to the file you're editing and watch the Tilt UI.
3. For Next.js / webpack: set `WATCHPACK_POLLING=true` in the Dockerfile or env vars.
4. For Java with DevTools: ensure `spring-boot-devtools` is in `developmentOnly` deps and `spring.devtools.restart.poll-interval=2s` is set.

### `tilt up` hangs at "Waiting for K8s resource"

**Symptom**: A pod is stuck in `Pending` or `ImagePullBackOff`.

**Causes**:
1. PVC requests storage size larger than the StorageClass allows.
2. Image push to in-cluster registry failed (kind/k3d).
3. Resource requests exceed cluster capacity.

**Fix**:
```bash
# Diagnose
kubectl get pods -n <namespace>
kubectl describe pod -n <namespace> <pod-name>

# Common fixes
kubectl get storageclass     # confirm a default exists
kubectl top nodes            # check resource pressure
```

### Custom_build with Gradle is slow on every save

**Symptom**: Saving a Java file triggers a 2+ minute rebuild.

**Cause**: `custom_build` re-runs the entire `gradle build` instead of incremental compile.

**Fix**: Pair `custom_build` with `local_resource` for compile, then `live_update` syncs only the compiled `.class` files (sellabella pattern):

```python
# Compile incrementally on host
local_resource('api-compile',
    cmd='./gradlew :api:classes -x test',
    deps=['apps/api/src/main/java'],
    labels=['build'],
    allow_parallel=True,
)

# Build image once; live_update syncs class files
custom_build('myapp/api',
    './gradlew :api:bootJar && docker build -t $EXPECTED_REF -f Dockerfile.dev .',
    deps=['apps/api/build/libs'],
    live_update=[
        sync('apps/api/build/classes/java/main', '/workspace/application/BOOT-INF/classes'),
        sync('apps/api/build/resources/main', '/workspace/application/BOOT-INF/classes'),
    ],
)
```

---

## Runtime Issues

### Production safety guard fires on local context

**Symptom**: `validate_cluster_safety()` blocks `colima` or a custom local context name.

**Cause**: Your context name contains a substring in `blocked` (e.g., `prod` in `prodigy-dev`).

**Fix**: Rename the kubectl context:
```bash
kubectl config rename-context prodigy-dev local-dev
```

Or refine the `blocked` patterns in the guard to be more specific:
```python
blocked = [
    "arn:aws:eks:",     # ARN format
    "gke_prod-",        # specific GKE prod prefix
    "-prod-cluster",    # word-boundary match
    "-production",
]
```

### Port forward conflicts

**Symptom**: `Error: bind: address already in use` for port 5432, 8080, etc.

**Causes**:
- Local Postgres/Redis/etc. already running on the host.
- Another `tilt up` session is active.

**Fix**:
```bash
# Find what's using the port
lsof -i :5432

# Kill the old Tilt session
pkill -f tilt

# Or remap the port in your service-config.yaml
postgres:
  ports: [5433]   # was 5432
```

### `tilt up` deletes my PostgreSQL data on `tilt down`

**Symptom**: Database state is lost between Tilt sessions.

**Cause**: PVC is managed by Tilt → deleted with `tilt down`.

**Fix**: Use the PVC persistence pattern (created via `local("kubectl apply")` outside Tilt's lifecycle):

```python
def create_persistent_pvc(name, namespace, size):
    manifest = """apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {name}-pvc
  namespace: {ns}
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: {size}
""".format(name=name, ns=namespace, size=size)
    local("echo '{}' | kubectl apply -f -".format(manifest))

create_persistent_pvc("postgres", "myapp", "1Gi")
```

To explicitly reset: `kubectl delete pvc postgres-pvc -n myapp`.

### `helm_resource` fails with "context deadline exceeded"

**Symptom**: Helm install times out, Prometheus/Grafana don't deploy.

**Causes**:
- First-time chart download is slow.
- Cluster doesn't have enough resources.

**Fix**:
```python
update_settings(
    max_parallel_updates=2,
    k8s_upsert_timeout_secs=120,    # Default is 30 — increase for Helm
)
```

---

## Modular `.tilt/` Issues

### `read_yaml` fails with "no such file"

**Symptom**: `read_yaml(".tilt/service-config.yaml")` errors.

**Cause**: Path is relative to the **root Tiltfile location**, not the loading `.star` file.

**Fix**: Always use paths relative to the Tiltfile root:
```python
# In .tilt/config.star
def load_service_config():
    return read_yaml(".tilt/service-config.yaml")    # Correct
    # NOT: return read_yaml("./service-config.yaml")
```

### Sub-module functions can't see top-level extension symbols

**Symptom**: `name 'docker_build_with_restart' is not defined` in a sub-module.

**Cause**: Starlark `load()` of `ext://` from sub-files is not supported.

**Fix**: Pass the symbol as a function argument:
```python
# Tiltfile (root)
load('ext://restart_process', 'docker_build_with_restart')
load('.tilt/services.star', 'deploy_with_restart')

deploy_with_restart('myapp', _build=docker_build_with_restart)
```

```python
# .tilt/services.star
def deploy_with_restart(name, _build):
    _build(name, '.', entrypoint=['./app'], live_update=[...])
```

---

## Tilt UI Issues

### Tilt UI shows "Tiltfile errored"

**Symptom**: The Tilt UI loads but shows a parse error banner.

**Fix**: Validate the Tiltfile syntax:
```bash
tilt alpha tiltfile-result
```

This prints the parse result and any errors. Most common causes:
- Indentation error (Starlark requires consistent indentation)
- Missing import (`load(...)` for a builtin extension)
- Type error (e.g., passing `None` where a string is expected)

### Resources stuck in "Pending"

**Symptom**: All resources show "Pending" forever.

**Causes**:
1. `resource_deps` cycle — a depends on b depends on a.
2. A dependency is never marked ready (e.g., a stateful service without a readiness probe).

**Fix**:
```bash
# Check resource graph
tilt get k8sresource

# For services without proper readiness probes, use:
k8s_resource('myservice', pod_readiness='ignore')
```

But prefer adding proper readiness probes to manifests over `pod_readiness='ignore'`.
