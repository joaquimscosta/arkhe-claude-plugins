# Tutorial Creation Examples

This document provides three complete examples demonstrating the create-tutorial skill in action, covering all three modes: Quick Start, Deep Dive, and Workshop Series.

---

## Example A: Quick Start Mode

### User Request

> "Quick intro to Docker for Python developers. Show them how to containerize a simple FastAPI app in 5 minutes."

### Mode Selection Reasoning

**Detected:**
- Keywords: "quick intro", "5 minutes"
- Short request (~20 words)
- Narrow scope: single task (containerize one app)

**Selected Mode:** Quick Start
**Estimated Time:** 5-10 minutes

### Generated Files

#### 1. article.md (Excerpt)

````markdown
# Dockerize Your Python FastAPI App in 5 Minutes

**Audience:** Beginner
**Language:** Python
**Topic:** Docker
**Time:** 5 minutes
**Prerequisites:** Python 3.8+, Docker Desktop installed

---

## 1. What You'll Build

- A Dockerfile for a FastAPI application
- A running containerized API accessible on localhost
- Understanding of basic Docker concepts

**End Result:** Your FastAPI app running in a Docker container.

---

## 2. Why Docker?

Docker packages your application with all its dependencies into a container—a lightweight, portable unit that runs consistently anywhere.

**Benefits:**
- **Consistency:** Same environment in development, testing, and production
- **Isolation:** No conflicts with other projects
- **Portability:** Share and deploy easily

---

## 3. Minimal Example

We'll containerize this simple FastAPI app:

**main.py:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Docker!"}
```

**requirements.txt:**
```
fastapi
uvicorn
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

**Expected Output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit: `http://localhost:8000`

**Response:**
```json
{"message": "Hello from Docker!"}
```

> 💡 **Tip:** The `FROM python:3.12-slim` base image is lightweight and perfect for production.

---

## 4. Challenge

Add a new endpoint `/health` that returns `{"status": "ok"}` and verify it works in your container.

<details><summary>Solution</summary>

Update **main.py:**
```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

Rebuild and run:
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

Test: `http://localhost:8000/health`

</details>

---

## 5. Summary

✅ You created a Dockerfile for Python FastAPI
✅ Built and ran a container
✅ Accessed your containerized app

**Next Steps:**
- Learn Docker Compose for multi-container apps
- Explore multi-stage builds for smaller images
- Deploy to cloud (AWS, GCP, Azure)
````

---

#### 2. video_script.md (Excerpt)

```markdown
# Video Script: Dockerize FastAPI in 5 Minutes

**Duration:** 5 minutes
**Audience:** Beginner

---

### [00:00-00:15] HOOK

**On-Screen Text:** Docker + FastAPI

**Script:**
"In the next 5 minutes, you'll containerize a Python FastAPI app and have it running in Docker. Let's go!"

---

### [00:15-00:30] AGENDA

**On-Screen List:**
1. Create a simple FastAPI app
2. Write a Dockerfile
3. Build and run the container

---

### [00:30-01:30] WHY DOCKER?

**Script:**
"Docker packages your app with all dependencies. Same environment everywhere—dev, testing, production. No more 'it works on my machine!'"

**Visual:** Diagram showing app + dependencies → container

---

### [01:30-02:30] DEMO: FastAPI APP

**Script:**
"Here's our simple FastAPI app. Just one endpoint returning a JSON message."

**Visual:** Show main.py and requirements.txt side by side

---

### [02:30-04:00] DEMO: DOCKERFILE

**Script:**
"Now let's write the Dockerfile. We start from Python 3.12 slim image, copy our files, install dependencies, and run uvicorn."

**Visual:** Type Dockerfile line by line, explain each line

**Callouts:**
- "FROM sets the base image"
- "WORKDIR creates our app directory"
- "CMD runs when container starts"

---

### [04:00-04:30] BUILD & RUN

**Script:**
"Build with docker build, run with docker run, and... there it is! Our API is live in a container."

**Visual:** Terminal showing build logs, then browser hitting localhost:8000

---

### [04:30-04:50] CTA

**Script:**
"That's it! You just containerized a Python app. Like and subscribe for more Docker tutorials. Try adding more endpoints and let me know in the comments!"

---
```

---

#### 3. chapters.json

```json
[
  {"time": "00:00", "title": "Hook & What We're Building"},
  {"time": "00:15", "title": "Agenda"},
  {"time": "00:30", "title": "Why Docker Matters"},
  {"time": "01:30", "title": "Creating the FastAPI App"},
  {"time": "02:30", "title": "Writing the Dockerfile"},
  {"time": "04:00", "title": "Build & Run Demo"},
  {"time": "04:30", "title": "Challenge & Next Steps"}
]
```

---

#### 4. seo.yaml

```yaml
title: "Dockerize Python FastAPI App in 5 Minutes"
slug: "dockerize-python-fastapi-5-minutes"
description: "Learn to containerize a Python FastAPI application with Docker. Beginner-friendly tutorial with a runnable Dockerfile and step-by-step guide."
keywords:
  - "docker python"
  - "fastapi docker"
  - "containerize python app"
  - "docker tutorial"
tags:
  - "python"
  - "fastapi"
  - "docker"
  - "beginner"
  - "tutorial"
  - "containerization"
  - "devops"
reading_time_min: 5
target_audience: "beginner developers"
difficulty: "beginner"
code_languages:
  - "python"
  - "dockerfile"
technologies:
  - "Docker"
  - "FastAPI"
  - "Python"
```

---

#### 5. thumb_brief.md (Excerpt)

```markdown
# Thumbnail Design Brief: Docker + FastAPI

### Visual Concept
**Core Visual:** Split screen - Left: Python/FastAPI logo, Right: Docker whale logo, with an arrow connecting them

### Text Overlay
**Primary:** "Docker in 5 Min"
**Secondary:** "FastAPI"

### Color Palette
- Primary: #0DB7ED (Docker blue)
- Secondary: #009688 (FastAPI teal)
- Accent: #FFFFFF (white text)
- Background: Dark gradient (#1A1A2E to #16213E)

### Composition
- Logos centered with connection arrow
- Text in top-right corner (bold sans-serif)
- High contrast for mobile readability
```

---

## Example B: Deep Dive Mode

### User Request

> "I want a comprehensive tutorial on Kubernetes Ingress for Java Spring Boot developers. Cover Service, Deployment, Ingress controller setup, and how to test locally with minikube. Include troubleshooting common issues."

### Mode Selection Reasoning

**Detected:**
- Keywords: "comprehensive tutorial", "cover"
- Medium-length request (~30 words)
- Multiple topics: Service, Deployment, Ingress, testing
- Troubleshooting requested

**Selected Mode:** Deep Dive
**Estimated Time:** 45-60 minutes

### Generated Files

#### 1. article.md (Excerpt)

````markdown
# Kubernetes Ingress for Spring Boot: Complete Guide

**Audience:** Intermediate
**Language:** Java
**Topic:** Kubernetes
**Time:** 45 minutes
**Prerequisites:** Java 11+, Kubernetes basics, minikube installed, kubectl

---

## 1. What You'll Build

- A Spring Boot REST API deployed to Kubernetes
- Kubernetes Service and Deployment manifests
- Ingress resource with path-based routing
- Local testing environment with minikube

**End Result:** A production-ready Ingress setup routing external traffic to your Spring Boot service.

**Repository:** [github.com/example/k8s-ingress-springboot](https://github.com)

---

## 2. Concept Overview: What is Ingress?

Kubernetes Ingress is an API object that manages external HTTP/HTTPS access to services in a cluster.

**Why Ingress vs NodePort/LoadBalancer?**
- **Single entry point** - One external IP for multiple services
- **Path/host-based routing** - Route by URL path or domain
- **TLS termination** - Handle HTTPS at the edge
- **Cost-effective** - No need for multiple LoadBalancers

**Architecture:**
```
Internet → Ingress → Service → Pod(s)
```

**Ingress Controller** (e.g., NGINX, Traefik) implements the Ingress rules.

---

## 3. Minimal Spring Boot Example

Simple REST API we'll deploy:

**HelloController.java:**
```java
@RestController
public class HelloController {

    @GetMapping("/api/hello")
    public Map<String, String> hello() {
        return Map.of("message", "Hello from Spring Boot on Kubernetes!");
    }

    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }
}
```

**application.properties:**
```properties
server.port=8080
spring.application.name=spring-k8s-demo
```

**Dockerfile:**
```dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY target/demo-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Build and push:**
```bash
./mvnw clean package
docker build -t myregistry/spring-k8s-demo:1.0 .
docker push myregistry/spring-k8s-demo:1.0
```

---

## 4. Guided Steps

### Step 1: Create Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-app
  labels:
    app: spring-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: spring-app
  template:
    metadata:
      labels:
        app: spring-app
    spec:
      containers:
      - name: spring-app
        image: myregistry/spring-k8s-demo:1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Apply:**
```bash
kubectl apply -f deployment.yaml
```

**Verify:**
```bash
kubectl get pods
```

**Expected output:**
```
NAME                          READY   STATUS    RESTARTS   AGE
spring-app-7d4f8c6b9d-4xk2p   1/1     Running   0          15s
spring-app-7d4f8c6b9d-9ghjk   1/1     Running   0          15s
```

> 💡 **Tip:** Setting resource requests/limits ensures reliable scheduling and prevents resource starvation.

---

### Step 2: Create Kubernetes Service

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: spring-app-service
spec:
  selector:
    app: spring-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

**Apply:**
```bash
kubectl apply -f service.yaml
```

**Verify:**
```bash
kubectl get svc spring-app-service
```

**Test internally:**
```bash
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl http://spring-app-service/api/hello
```

**Expected:**
```json
{"message": "Hello from Spring Boot on Kubernetes!"}
```

> ⚠️ **Warning:** `ClusterIP` services are only accessible within the cluster. We'll expose via Ingress next.

---

### Step 3: Install Ingress Controller (minikube)

**Enable NGINX Ingress addon:**
```bash
minikube addons enable ingress
```

**Verify Ingress controller pods:**
```bash
kubectl get pods -n ingress-nginx
```

**Expected:**
```
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-5d88495688-abc12   1/1     Running   0          2m
```

> 💡 **Production note:** For cloud deployments, use Helm to install the NGINX Ingress controller.

---

### Step 4: Create Ingress Resource

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spring-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: spring.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: spring-app-service
            port:
              number: 80
```

**Apply:**
```bash
kubectl apply -f ingress.yaml
```

**Verify:**
```bash
kubectl get ingress spring-app-ingress
```

**Expected:**
```
NAME                 CLASS   HOSTS          ADDRESS        PORTS   AGE
spring-app-ingress   nginx   spring.local   192.168.49.2   80      30s
```

---

### Step 5: Test Ingress Locally

**Get minikube IP:**
```bash
minikube ip
```

**Add to /etc/hosts:**
```
192.168.49.2  spring.local
```

**Test with curl:**
```bash
curl http://spring.local/api/hello
```

**Expected response:**
```json
{"message": "Hello from Spring Boot on Kubernetes!"}
```

**Test in browser:**
Navigate to `http://spring.local/api/hello`

--- Progress Check ---

You should now have:
- ✅ Spring Boot app deployed with 2 replicas
- ✅ Service routing traffic to pods
- ✅ Ingress controller running
- ✅ Ingress resource configured
- ✅ External access working via spring.local

---

## 5. Variations

### Variation A: Path-Based Routing (Multiple Services)

```yaml
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /api/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
      - path: /api/orders
        pathType: Prefix
        backend:
          service:
            name: order-service
            port:
              number: 80
```

### Variation B: TLS/HTTPS

```yaml
spec:
  tls:
  - hosts:
    - spring.local
    secretName: tls-secret
  rules:
  - host: spring.local
    # ... rest of config
```

**Create TLS secret:**
```bash
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

---

## 6. Challenge

Add a second endpoint `/api/version` that returns `{"version": "1.0.0"}`. Update your Deployment and verify it's accessible via Ingress.

<details><summary>Solution</summary>

**Update HelloController.java:**
```java
@GetMapping("/api/version")
public Map<String, String> version() {
    return Map.of("version", "1.0.0");
}
```

**Rebuild and push:**
```bash
./mvnw clean package
docker build -t myregistry/spring-k8s-demo:1.1 .
docker push myregistry/spring-k8s-demo:1.1
```

**Update deployment.yaml:**
```yaml
# Change image tag
image: myregistry/spring-k8s-demo:1.1
```

**Apply:**
```bash
kubectl apply -f deployment.yaml
```

**Wait for rollout:**
```bash
kubectl rollout status deployment/spring-app
```

**Test:**
```bash
curl http://spring.local/api/version
```

**Expected:**
```json
{"version": "1.0.0"}
```

</details>

---

## 7. Troubleshooting & Common Pitfalls

### Error: "503 Service Temporarily Unavailable"

**Cause:** Ingress can't reach the backend Service

**Fix checklist:**
1. Verify Service exists: `kubectl get svc spring-app-service`
2. Check Service selector matches Pod labels
3. Verify Service port matches Ingress backend port
4. Check Pod status: `kubectl get pods`

**Debug:**
```bash
kubectl describe ingress spring-app-ingress
# Look for backend endpoints
```

---

### Error: "Connection refused" when curling Ingress

**Cause:** Ingress controller not running or wrong host

**Fix:**
1. Check Ingress controller: `kubectl get pods -n ingress-nginx`
2. Verify /etc/hosts entry matches Ingress host
3. Ensure minikube IP is correct: `minikube ip`

---

### Error: "404 Not Found" for valid paths

**Cause:** Path or pathType misconfiguration

**Fix:**
- For `/api/*` paths, use `pathType: Prefix`
- Check `rewrite-target` annotation if paths don't match app routes
- Verify Spring Boot context path in application.properties

**Example rewrite:**
```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2
# Then use path: /api(/|$)(.*)
```

---

### Pods not starting

**Cause:** Image pull error or resource constraints

**Fix:**
```bash
kubectl describe pod <pod-name>
```

Look for:
- `ImagePullBackOff`: Check image name/tag and registry access
- `CrashLoopBackOff`: Check application logs: `kubectl logs <pod-name>`
- `Pending`: Check resource availability

---

## 8. Summary & Next Steps

### What You Learned

✅ Deployed a Spring Boot app to Kubernetes
✅ Created Service and Deployment manifests
✅ Installed and configured NGINX Ingress controller
✅ Set up path-based routing with Ingress
✅ Tested locally with minikube
✅ Troubleshot common Ingress issues

### Quick Reference

**Apply all manifests:**
```bash
kubectl apply -f deployment.yaml -f service.yaml -f ingress.yaml
```

**Check everything:**
```bash
kubectl get all,ingress
```

### Next Steps

1. **Production deployment:**
   - Deploy to cloud Kubernetes (EKS, GKE, AKS)
   - Set up TLS certificates (cert-manager)
   - Configure autoscaling (HPA)

2. **Advanced Ingress:**
   - Learn rate limiting and authentication
   - Explore Istio or Linkerd for service mesh
   - Implement blue-green deployments

3. **Monitoring:**
   - Add Prometheus and Grafana
   - Implement distributed tracing
   - Set up alerts for Ingress errors

**Resources:**
- [Kubernetes Ingress Docs](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Spring Boot on Kubernetes](https://spring.io/guides/gs/spring-boot-kubernetes/)

---

## Production Checklist

Before deploying to production:

- [ ] TLS/HTTPS enabled
- [ ] Resource limits set on all containers
- [ ] Liveness and readiness probes configured
- [ ] Horizontal Pod Autoscaler (HPA) configured
- [ ] Ingress rate limiting configured
- [ ] Monitoring and logging set up
- [ ] Backup and disaster recovery plan
- [ ] Security: NetworkPolicies, RBAC configured
````

---

#### 2. video_script.md (Excerpt)

```markdown
# Video Script: Kubernetes Ingress for Spring Boot

**Duration:** 12 minutes
**Audience:** Intermediate

---

### [00:00-00:20] HOOK

**On-Screen:** Kubernetes + Spring Boot logos

**Script:**
"Kubernetes Ingress can be confusing. In this tutorial, I'll show you exactly how to expose your Spring Boot API to the internet using Ingress with path-based routing. By the end, you'll have a working setup running on minikube."

---

### [00:20-00:45] AGENDA

1. What is Ingress and why use it?
2. Deploy Spring Boot app to Kubernetes
3. Create Service and Ingress resources
4. Test locally with minikube
5. Troubleshoot common issues

---

### [00:45-02:00] WHAT IS INGRESS?

**Visual:** Architecture diagram animation

**Script:**
"Ingress is a Kubernetes API object that manages external access to your services. Instead of using multiple LoadBalancers—which costs money—you use one Ingress controller that routes based on URL paths or hostnames."

**On-Screen Diagram:**
```
Internet → Ingress Controller → Ingress Rules → Services → Pods
```

---

### [02:00-04:30] DEMO: DEPLOY SPRING BOOT

**Visual:** Split screen - code editor + terminal

**Script:**
"Let's start with a simple Spring Boot REST API. I've got a Hello endpoint here. Now let's containerize it and create our Deployment manifest..."

*Type deployment.yaml*

"Notice I'm setting resource requests and limits—this is important for reliable scheduling. Let's apply this..."

```bash
kubectl apply -f deployment.yaml
kubectl get pods
```

**On-Screen:** Highlight READY 1/1, Running status

---

### [04:30-06:00] CREATE SERVICE

**Script:**
"Now we need a Service to route traffic to our pods. This is a ClusterIP service—internal only. The Ingress will expose it externally."

*Show service.yaml*

"The key here is the selector matching our pod labels, and the port mapping—port 80 to targetPort 8080."

---

### [06:00-08:00] SETUP INGRESS

**Script:**
"First, we need an Ingress controller. On minikube, it's one command..."

```bash
minikube addons enable ingress
```

"Now let's create our Ingress resource..."

*Show ingress.yaml*

**Callouts:**
- "host: spring.local - we'll add this to /etc/hosts"
- "path: /api - routes all /api/* requests"
- "backend points to our Service"

---

### [08:00-10:00] TEST IT

**Script:**
"Add the minikube IP to /etc/hosts, and let's test..."

```bash
curl http://spring.local/api/hello
```

**On-Screen:** JSON response appears

"There we go! External access to our Spring Boot app via Ingress."

---

### [10:00-11:30] TROUBLESHOOTING

**Script:**
"If you get a 503, check your Service selector. If 404, verify your path configuration..."

**Visual:** Show kubectl describe ingress, point out Endpoints section

---

### [11:30-12:00] RECAP & CTA

**Script:**
"You just deployed a Spring Boot app to Kubernetes with Ingress. Subscribe for more Kubernetes content, and try adding TLS next!"
```

---

#### 3. chapters.json

```json
[
  {"time": "00:00", "title": "Introduction & Hook"},
  {"time": "00:20", "title": "What We'll Cover"},
  {"time": "00:45", "title": "What is Kubernetes Ingress?"},
  {"time": "02:00", "title": "Deploy Spring Boot to K8s"},
  {"time": "04:30", "title": "Create Service"},
  {"time": "06:00", "title": "Setup Ingress Controller"},
  {"time": "06:45", "title": "Create Ingress Resource"},
  {"time": "08:00", "title": "Test with Minikube"},
  {"time": "10:00", "title": "Troubleshooting Tips"},
  {"time": "11:30", "title": "Recap & Next Steps"}
]
```

---

#### 4. seo.yaml

```yaml
title: "Kubernetes Ingress for Spring Boot: Complete Guide"
slug: "kubernetes-ingress-spring-boot-guide"
description: "Learn to expose Spring Boot apps with Kubernetes Ingress. Covers Service, Deployment, path-based routing, and troubleshooting. Includes minikube setup."
keywords:
  - "kubernetes ingress"
  - "spring boot kubernetes"
  - "k8s ingress tutorial"
  - "java kubernetes"
  - "ingress controller"
tags:
  - "java"
  - "spring-boot"
  - "kubernetes"
  - "ingress"
  - "intermediate"
  - "tutorial"
  - "devops"
  - "cloud-native"
  - "minikube"
  - "deployment"
reading_time_min: 45
target_audience: "intermediate developers"
difficulty: "intermediate"
code_languages:
  - "java"
  - "yaml"
  - "bash"
technologies:
  - "Kubernetes"
  - "Spring Boot"
  - "NGINX Ingress"
  - "Docker"
  - "minikube"
```

---

## Example C: Workshop Series Mode

### User Request

> "I want to create a comprehensive series on React state management. Start with useState basics, then cover lifting state up, Context API, and finally useReducer and custom hooks. Each part should build on the previous one. Target intermediate React developers who want to master state management patterns."

### Mode Selection Reasoning

**Detected:**
- Keywords: "series", "start with... then... finally" (sequential structure), "comprehensive"
- Long request (50+ words)
- Multiple related topics that build on each other
- Explicit multi-part structure mentioned

**Selected Mode:** Workshop Series
**Estimated Time:** 90 minutes total (4 parts)

### Series Structure

**Part 1:** useState Fundamentals (20 min)
**Part 2:** Lifting State Up (25 min)
**Part 3:** Context API (25 min)
**Part 4:** useReducer & Custom Hooks (20 min)

### Generated Files (Part 1 shown, Parts 2-4 follow same pattern)

#### 1. article.md (Part 1 - Excerpt)

````markdown
# Mastering React State Management Part 1: useState Fundamentals

**Audience:** Intermediate
**Language:** JavaScript (React)
**Topic:** State Management
**Time:** 20 minutes
**Series:** Part 1 of 4
**Prerequisites:** React basics (components, JSX), JavaScript ES6+

---

## Series Overview

This 4-part workshop covers React state management from fundamentals to advanced patterns:

1. **Part 1 (You are here):** useState Fundamentals
2. **Part 2:** Lifting State Up
3. **Part 3:** Context API
4. **Part 4:** useReducer & Custom Hooks

By the end, you'll know exactly which pattern to use for any state management scenario.

---

## 1. What You'll Learn

- How `useState` creates local component state
- Updating state correctly (and common mistakes)
- Multiple state variables vs. state objects
- Functional updates for dependent state changes

**End Result:** Solid foundation in useState patterns used in every React app.

---

## 2. Concept Overview: Local Component State

**State** is data that changes over time in your component. When state changes, React re-renders the component with the new data.

**useState** is React's hook for adding state to functional components.

**Basic pattern:**
```jsx
const [value, setValue] = useState(initialValue);
```

- `value`: Current state
- `setValue`: Function to update state
- `initialValue`: Starting value

**Key principle:** Never mutate state directly. Always use the setter function.

---

## 3. Minimal Example

**Counter component:**

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

**What happens:**
1. Component renders with `count = 0`
2. User clicks button
3. `setCount(count + 1)` called
4. React re-renders with new `count`

> 💡 **Tip:** Each call to `useState` creates independent state. You can use it multiple times in one component.

---

## 4. Guided Steps

### Step 1: Multiple State Variables

```jsx
function UserProfile() {
  const [name, setName] = useState('');
  const [age, setAge] = useState(0);
  const [email, setEmail] = useState('');

  return (
    <form>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <input value={age} onChange={(e) => setAge(Number(e.target.value))} />
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
    </form>
  );
}
```

**When to use:** Independent state variables that don't change together.

---

### Step 2: State as an Object

```jsx
function UserProfile() {
  const [user, setUser] = useState({
    name: '',
    age: 0,
    email: ''
  });

  const updateField = (field, value) => {
    setUser({
      ...user,
      [field]: value
    });
  };

  return (
    <form>
      <input
        value={user.name}
        onChange={(e) => updateField('name', e.target.value)}
      />
      <input
        value={user.age}
        onChange={(e) => updateField('age', Number(e.target.value))}
      />
      <input
        value={user.email}
        onChange={(e) => updateField('email', e.target.value)}
      />
    </form>
  );
}
```

**When to use:** Related values that logically belong together.

> ⚠️ **Warning:** Always spread the previous object (`...user`) to avoid losing other fields!

---

### Step 3: Functional Updates

**Problem:** State updates based on previous state can be stale.

**Wrong way:**
```jsx
<button onClick={() => setCount(count + 1)}>Increment</button>
<button onClick={() => setCount(count + 1)}>Increment</button>
// Clicking both fast may only increment by 1!
```

**Right way:**
```jsx
<button onClick={() => setCount(prev => prev + 1)}>Increment</button>
```

**Functional update** ensures you're working with the latest state.

---

### Step 4: Complex Example

**Todo list with multiple operations:**

```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  const addTodo = () => {
    setTodos(prev => [...prev, { id: Date.now(), text: input, done: false }]);
    setInput('');
  };

  const toggleTodo = (id) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  return (
    <div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={addTodo}>Add</button>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

--- Progress Check ---

You should now understand:
- ✅ How to create state with useState
- ✅ Multiple state variables vs. state objects
- ✅ Why and when to use functional updates
- ✅ Updating arrays and objects immutably

---

## 5. Challenge

Extend the TodoList to include a filter showing "All", "Active", or "Completed" todos.

**Requirements:**
- Add a filter state variable
- Add three buttons to change the filter
- Filter the displayed todos based on the selected filter

<details><summary>Solution</summary>

```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  const [filter, setFilter] = useState('all'); // 'all' | 'active' | 'completed'

  const addTodo = () => {
    setTodos(prev => [...prev, { id: Date.now(), text: input, done: false }]);
    setInput('');
  };

  const toggleTodo = (id) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.done;
    if (filter === 'completed') return todo.done;
    return true; // 'all'
  });

  return (
    <div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={addTodo}>Add</button>

      <div>
        <button onClick={() => setFilter('all')}>All</button>
        <button onClick={() => setFilter('active')}>Active</button>
        <button onClick={() => setFilter('completed')}>Completed</button>
      </div>

      <ul>
        {filteredTodos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

</details>

---

## 6. Troubleshooting & Common Pitfalls

### Pitfall 1: Mutating State Directly

**Wrong:**
```jsx
const [items, setItems] = useState([1, 2, 3]);
items.push(4); // ❌ Mutates state!
```

**Right:**
```jsx
setItems(prev => [...prev, 4]); // ✓ Creates new array
```

---

### Pitfall 2: Stale Closures

**Problem:** State inside callbacks might be stale.

**Solution:** Use functional updates or useEffect with dependencies.

---

### Pitfall 3: Unnecessary Re-renders

**Problem:** Every state update triggers a re-render.

**Solution:**
- Only update state when value actually changes
- Consider `useMemo` or `useCallback` for expensive computations
- Split state into smaller pieces

---

## 7. Summary & Next Steps

### What You Mastered

✅ Creating state with `useState`
✅ Multiple state variables vs. state objects
✅ Functional updates for dependent changes
✅ Immutable updates for arrays and objects
✅ Common useState pitfalls

### Quick Reference

```jsx
// Basic state
const [value, setValue] = useState(initial);

// Functional update
setValue(prev => prev + 1);

// Object update
setUser(prev => ({ ...prev, name: 'New Name' }));

// Array updates
setItems(prev => [...prev, newItem]); // Add
setItems(prev => prev.filter(item => item.id !== id)); // Remove
setItems(prev => prev.map(item =>
  item.id === id ? { ...item, updated: true } : item
)); // Update
```

### Up Next: Part 2 - Lifting State Up

In the next part, you'll learn:
- When and how to lift state to parent components
- Sharing state between sibling components
- Avoiding prop drilling (preview of Context API in Part 3)

**Continue to [Part 2: Lifting State Up](link)**

---

**Series Navigation:**
- **Part 1 (Current):** useState Fundamentals
- [Part 2](link): Lifting State Up
- [Part 3](link): Context API
- [Part 4](link): useReducer & Custom Hooks
````

---

#### 2. video_script.md (Part 1 - Excerpt)

```markdown
# Video Script: React State Management Part 1

**Series:** Mastering React State Management
**Part:** 1 of 4
**Duration:** 8 minutes

---

### [00:00-00:20] SERIES HOOK

**On-Screen:** Series title + "Part 1/4"

**Script:**
"State management confuses most React developers. In this 4-part series, I'll show you every pattern from useState to custom hooks. By the end, you'll know exactly which to use and when. Let's start with the fundamentals."

---

### [00:20-00:40] PART 1 AGENDA

1. useState basics
2. Multiple state variables
3. State objects
4. Functional updates

**Script:**
"Today we're mastering useState—the foundation of React state."

---

### [00:40-02:00] WHAT IS USESTATE?

**Visual:** Code example with animations

**Script:**
"useState adds state to functional components. You get the current value and a setter function. When you call the setter, React re-renders with the new value."

---

### [02:00-06:00] LIVE CODING: TODO LIST

**Script:**
"Let's build a real todo list to see useState in action..."

*Build incrementally, explaining each pattern*

---

### [06:00-07:30] COMMON MISTAKES

**Visual:** Side-by-side wrong vs. right

**Script:**
"Three pitfalls to avoid: direct mutations, stale closures, and unnecessary re-renders..."

---

### [07:30-08:00] SERIES CTA

**Script:**
"You just mastered useState! In Part 2, we'll lift state between components. Subscribe and click the bell so you don't miss it. See you in the next one!"

**End Card:**
- Part 2 thumbnail (clickable)
- Series playlist
```

---

#### 3. chapters.json (Part 1)

```json
[
  {"time": "00:00", "title": "Series Introduction"},
  {"time": "00:20", "title": "Part 1 Agenda"},
  {"time": "00:40", "title": "What is useState?"},
  {"time": "02:00", "title": "Live Coding: Todo List"},
  {"time": "03:30", "title": "Multiple State Variables"},
  {"time": "04:30", "title": "State as Objects"},
  {"time": "05:15", "title": "Functional Updates"},
  {"time": "06:00", "title": "Common Pitfalls"},
  {"time": "07:30", "title": "Recap & Part 2 Preview"}
]
```

---

#### 4. seo.yaml (Part 1)

```yaml
title: "React State Management Part 1: useState Fundamentals"
slug: "react-state-management-part-1-usestate"
description: "Master React useState hook in this comprehensive tutorial. Learn multiple state patterns, functional updates, and common pitfalls. Part 1 of 4-part series."
keywords:
  - "react usestate"
  - "react state management"
  - "react hooks tutorial"
  - "usestate examples"
tags:
  - "react"
  - "javascript"
  - "hooks"
  - "state-management"
  - "intermediate"
  - "tutorial"
  - "series"
  - "frontend"
reading_time_min: 20
target_audience: "intermediate React developers"
difficulty: "intermediate"
series:
  name: "Mastering React State Management"
  part: 1
  total_parts: 4
code_languages:
  - "javascript"
  - "jsx"
technologies:
  - "React"
  - "React Hooks"
```

---

#### 5. thumb_brief.md (Series)

```markdown
# Thumbnail Brief: React State Management Series

### Series Branding Strategy

Consistent visual identity across all 4 parts with color progression.

---

### Part 1: useState Fundamentals

**Visual Concept:** React logo with "useState" text, surrounded by state bubbles

**Text Overlay:**
- Primary: "useState"
- Secondary: "Part 1/4"

**Color:** #61DAFB (React blue)

---

### Part 2: Lifting State Up

**Text Overlay:**
- Primary: "Lift State"
- Secondary: "Part 2/4"

**Color:** #4CAF50 (Green - progression)

---

### Part 3: Context API

**Text Overlay:**
- Primary: "Context API"
- Secondary: "Part 3/4"

**Color:** #9C27B0 (Purple - advanced)

---

### Part 4: useReducer & Hooks

**Text Overlay:**
- Primary: "useReducer"
- Secondary: "Part 4/4"

**Color:** #FF9800 (Orange - mastery)

---

### Series Consistency

- Same layout template across all parts
- Part number always visible (X/4)
- Color coding shows progression
- React logo placement consistent
```

---

## Summary

These three examples demonstrate:

1. **Quick Start** - Concise, practical, fast introduction (Docker + FastAPI)
2. **Deep Dive** - Comprehensive, thorough explanation with troubleshooting (K8s Ingress + Spring Boot)
3. **Workshop Series** - Multi-part progressive learning with cross-references (React State Management)

Each mode produces:
- Complete article.md with pedagogical structure
- video_script.md with timing and stage directions
- chapters.json for video navigation
- seo.yaml for discoverability
- thumb_brief.md for visual consistency

All examples follow the templates and workflow documented in this skill.
