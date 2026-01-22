# Spring Boot Scanner Workflow

Detailed step-by-step detection and routing workflow.

## Complete Detection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIGGER: User Activity                        │
│  - Editing Java or Kotlin file                                   │
│  - Discussing Spring Boot                                        │
│  - Working with build files                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 1: Spring Boot Project Detection              │
│                                                                  │
│  1. Glob for build files:                                        │
│     - **/pom.xml                                                │
│     - **/build.gradle*                                          │
│                                                                  │
│  2. Grep for Spring Boot indicators:                             │
│     - spring-boot-starter                                       │
│     - org.springframework.boot                                  │
│                                                                  │
│  Result: IS_SPRING_BOOT = true/false                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
         IS_SPRING_BOOT                     NOT SPRING_BOOT
              │                                   │
              ▼                                   ▼
    Continue to Phase 2                    EXIT (no action)
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 2: Annotation Pattern Scanning                │
│                                                                  │
│  Target: Current file being edited OR recently changed files    │
│                                                                  │
│  Scan for annotation categories:                                │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ WEB PATTERNS     │  │ DATA PATTERNS    │                     │
│  │ @RestController  │  │ @Entity          │                     │
│  │ @GetMapping      │  │ @Repository      │                     │
│  │ @PostMapping     │  │ @Aggregate       │                     │
│  │ @RequestMapping  │  │ @MappedSuperclass│                     │
│  │ @ResponseBody    │  │ @EmbeddedId      │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ SECURITY         │  │ TESTING          │                     │
│  │ @EnableWebSec    │  │ @SpringBootTest  │                     │
│  │ @PreAuthorize    │  │ @WebMvcTest      │                     │
│  │ @Secured         │  │ @DataJpaTest     │                     │
│  │ SecurityFilter   │  │ @MockitoBean     │                     │
│  │ Chain            │  │ @MockBean (dep)  │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ MODULITH         │  │ OBSERVABILITY    │                     │
│  │ @ApplicationMod  │  │ @Timed           │                     │
│  │ @ApplicationMod  │  │ @Counted         │                     │
│  │   uleListener    │  │ HealthIndicator  │                     │
│  │ @NamedInterface  │  │ MeterRegistry    │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ DDD PATTERNS     │                                           │
│  │ @Service in      │                                           │
│  │   domain/**      │                                           │
│  │ @DomainService   │                                           │
│  │ @ValueObject     │                                           │
│  │ @AggregateRoot   │                                           │
│  └──────────────────┘                                           │
│                                                                  │
│  Result: detected_patterns = [{skill, risk_level, patterns[]}]  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 3: Risk Classification                        │
│                                                                  │
│  Categorize detected skills by risk:                            │
│                                                                  │
│  LOW_RISK = [                                                   │
│    spring-boot-web-api,                                         │
│    spring-boot-data-ddd,                                        │
│    domain-driven-design,                                        │
│    spring-boot-modulith,                                        │
│    spring-boot-observability                                    │
│  ]                                                               │
│                                                                  │
│  HIGH_RISK = [                                                  │
│    spring-boot-security,                                        │
│    spring-boot-testing,                                         │
│    spring-boot-verify                                           │
│  ]                                                               │
│                                                                  │
│  ESCALATION_TRIGGERS = [                                        │
│    @MockBean → deprecated warning                               │
│    @EnableGlobalMethodSecurity → deprecated warning             │
│    .and() in security → removed warning                         │
│    com.fasterxml.jackson → migration warning                    │
│    version < 3.0 → major migration warning                      │
│  ]                                                               │
│                                                                  │
│  Separate patterns into:                                        │
│    - low_risk_patterns[]                                        │
│    - high_risk_patterns[]                                       │
│    - escalation_patterns[]                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 4: Routing & Response                         │
│                                                                  │
│  CASE 1: Only LOW_RISK patterns                                 │
│  ────────────────────────────                                   │
│  → Auto-invoke relevant skill guidance                          │
│  → Format: "Working with [pattern]. Here's guidance:"           │
│  → Load skill Quick Reference inline                            │
│                                                                  │
│  CASE 2: Only HIGH_RISK patterns                                │
│  ────────────────────────────                                   │
│  → Use AskUserQuestion to confirm                               │
│  → Options:                                                     │
│    - "Load [skill] for detailed guidance"                       │
│    - "Run verification scan"                                    │
│    - "Continue without guidance"                                │
│  → Wait for user selection                                      │
│  → Route based on choice                                        │
│                                                                  │
│  CASE 3: Mixed LOW + HIGH risk                                  │
│  ────────────────────────────                                   │
│  → Auto-invoke LOW_RISK guidance                                │
│  → Separately ask about HIGH_RISK                               │
│  → Format: "Loaded [low] guidance. For [high], would you like?" │
│                                                                  │
│  CASE 4: ESCALATION triggers present                            │
│  ────────────────────────────                                   │
│  → Always show warning first                                    │
│  → Format: "⚠️ Detected deprecated pattern: [pattern]"          │
│  → Recommend specific action                                    │
│  → Then proceed with normal routing                             │
│                                                                  │
│  CASE 5: Many files / comprehensive request                     │
│  ────────────────────────────                                   │
│  → Delegate to spring-boot-reviewer agent                       │
│  → Format: "This requires comprehensive review. Launching..."   │
│  → Use Task tool to invoke agent                                │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Detect Spring Boot Project

```python
# Using Glob + Grep
1. files = Glob("**/pom.xml") + Glob("**/build.gradle*")
2. for file in files:
     content = Read(file)
     if "spring-boot-starter" in content or "org.springframework.boot" in content:
       return IS_SPRING_BOOT = True
3. return IS_SPRING_BOOT = False
```

### Step 2: Scan for Annotations

```python
# Using Grep with patterns
PATTERNS = {
    "web-api": r"@RestController|@GetMapping|@PostMapping|@RequestMapping",
    "data-ddd": r"@Entity|@Repository|@Aggregate|@MappedSuperclass",
    "security": r"@EnableWebSecurity|@PreAuthorize|@Secured|SecurityFilterChain",
    "testing": r"@SpringBootTest|@WebMvcTest|@DataJpaTest|@MockitoBean|@MockBean",
    "modulith": r"@ApplicationModule|@ApplicationModuleListener|@NamedInterface",
    "observability": r"@Timed|@Counted|HealthIndicator|MeterRegistry",
    "ddd": r"@DomainService|@ValueObject|@AggregateRoot"
}

detected = []
for skill, pattern in PATTERNS.items():
    matches = Grep(pattern, target_file)
    if matches:
        detected.append({"skill": skill, "matches": matches})
```

### Step 3: Classify and Route

```python
LOW_RISK = ["web-api", "data-ddd", "ddd", "modulith", "observability"]
HIGH_RISK = ["security", "testing", "verify"]

low_risk_detected = [d for d in detected if d["skill"] in LOW_RISK]
high_risk_detected = [d for d in detected if d["skill"] in HIGH_RISK]

# Check for escalation triggers
escalations = check_escalation_triggers(target_file)

# Route based on classification
if escalations:
    show_warnings(escalations)

if low_risk_detected:
    auto_invoke_guidance(low_risk_detected)

if high_risk_detected:
    ask_user_confirmation(high_risk_detected)
```

## Grep Patterns Reference

> **Note**: All patterns work with both Java (`*.java`) and Kotlin (`*.kt`) files.

### Web API Patterns
```bash
grep -E "@RestController|@GetMapping|@PostMapping|@PutMapping|@DeleteMapping|@PatchMapping|@RequestMapping|@ResponseBody|@RequestBody|@PathVariable|@RequestParam" **/*.java **/*.kt
```

### Data/Repository Patterns
```bash
grep -E "@Entity|@Repository|@Aggregate|@MappedSuperclass|@EmbeddedId|@Embeddable|@OneToMany|@ManyToOne|@JoinColumn" **/*.java **/*.kt
```

### Security Patterns
```bash
grep -E "@EnableWebSecurity|@EnableMethodSecurity|@PreAuthorize|@PostAuthorize|@Secured|@RolesAllowed|SecurityFilterChain|AuthenticationManager|UserDetailsService" **/*.java **/*.kt
```

### Testing Patterns
```bash
grep -E "@SpringBootTest|@WebMvcTest|@DataJpaTest|@DataJdbcTest|@JsonTest|@MockitoBean|@MockBean|@SpyBean|@ServiceConnection|Testcontainers" **/*.java **/*.kt
```

### Modulith Patterns
```bash
grep -E "@ApplicationModule|@ApplicationModuleListener|@NamedInterface|@Externalized|ApplicationModuleTest" **/*.java **/*.kt
```

### Observability Patterns
```bash
grep -E "@Timed|@Counted|@Observed|HealthIndicator|MeterRegistry|Tracer|Span|ObservationRegistry" **/*.java **/*.kt
```

### Escalation Triggers
```bash
# Deprecated patterns requiring immediate attention
grep -E "@MockBean|@EnableGlobalMethodSecurity|\.and\(\)|antMatchers|authorizeRequests|com\.fasterxml\.jackson" **/*.java **/*.kt
```

## Response Templates

### Low Risk Auto-Invoke Template
```
I notice you're working with {patterns}. Here's relevant guidance:

**From spring-boot-{skill}:**
- {quick reference point 1}
- {quick reference point 2}
- {quick reference point 3}

For detailed patterns, I can load the full skill guidance.
```

### High Risk Confirmation Template
```
I detected {patterns} in your code. This involves {security/testing/migration} considerations.

Would you like me to:
1. Load spring-boot-{skill} for detailed guidance
2. Run a comprehensive verification scan
3. Continue without additional guidance

[AskUserQuestion with these options]
```

### Escalation Warning Template
```
⚠️ **Deprecated Pattern Detected**

Found `{pattern}` which is {reason}.

**Recommended action:** {action}

**Migration:**
```java
// Before (deprecated)
{old_code}

// After (current)
{new_code}
```

Would you like me to help migrate this pattern?
```

### Delegation to Agent Template
```
This analysis requires reviewing multiple files. I'll delegate to the spring-boot-reviewer agent for a comprehensive scan.

**Scope:** {scope}
**Skills to check:** {relevant_skills}

Launching review...

[Task tool to invoke spring-boot-reviewer agent]
```
