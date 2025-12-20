# Validation Report: GCP Secret Manager Analysis Against 2025 Standards

## Critical misconceptions identified

The research reveals several significant misconceptions that need immediate correction in your current implementation approach. Most importantly, the "dual injection" pattern of using both Terraform and GitHub Actions to manage secrets represents a fundamental anti-pattern that violates infrastructure-as-code principles.

### 1. Dual injection pattern is an anti-pattern, not recommended

The practice of using both Terraform and GitHub Actions to manage secrets (dual injection) creates **configuration drift** and state management conflicts. When GitHub Actions deploys using `gcloud run deploy` on Terraform-managed services, it causes the Terraform state to become out of sync. Subsequent `terraform apply` operations fail due to resource conflicts. Google Cloud documentation explicitly warns against mixing imperative gcloud commands with declarative Terraform management.

**Recommended approach**: Choose either Terraform OR gcloud for managing service configurations, not both. If using Terraform for infrastructure, continue using it for all configuration changes. If preferring GitHub Actions deployment, manage the entire service lifecycle through gcloud commands. For organizations wanting separation of concerns, Terraform should manage infrastructure (secrets, IAM, service accounts) while GitHub Actions deploys only container images using the `--no-traffic` flag initially.

### 2. Cloud Run revision behavior contradicts common assumptions

Contrary to potential concerns, secrets defined in Terraform **do not get lost** when GitHub Actions deploys without --set-secrets flags. Cloud Run inherits configuration from previous revisions automatically. Any configuration setting, including secrets, persists across new revisions unless explicitly modified. This means deploying with `gcloud run deploy` without secret flags preserves existing secret configurations.

The relationship between infrastructure-managed and runtime-managed secrets is **additive by default**, not exclusive. This persistence can create confusion about the configuration source of truth but ensures backward compatibility.

### 3. Spring Boot integration requires critical syntax update

A **breaking change** in Spring Boot 3.4+ (released with Spring Cloud 2024.0.0) requires updating from `sm://` to `sm@` syntax for secret references. Applications using the old syntax will fail to resolve secrets:

**Old syntax (deprecated)**: `${sm://database-password}`  
**New syntax (required)**: `${sm@database-password}`

This change results from a complete rewrite of Spring's property placeholder parser. Spring Cloud GCP version 7.3.1 (September 2025) fully supports this new syntax. Organizations still on Spring Boot 3.3.x should plan migration carefully as this represents a breaking change requiring code updates.

### 4. Industry standards favor different solutions by use case

While Google Cloud Secret Manager excels for GCP-native workloads, **HashiCorp Vault remains the enterprise standard** for complex, multi-cloud environments according to CNCF Technology Radar findings. Secret Manager sits in the "assess" tier while Vault occupies the "adopt" tier based on surveys of 140+ organizations.

For GCP-exclusive deployments, Secret Manager provides excellent integration with simplified management. For multi-cloud or hybrid scenarios requiring dynamic secrets, policy-as-code, or advanced rotation capabilities, Vault offers superior functionality despite higher operational complexity.

### 5. Both deployment flags remain actively supported

The analysis of --set-secrets vs --update-secrets flags aligns with current documentation:
- **--set-secrets**: Destructive operation replacing ALL existing secrets
- **--update-secrets**: Additive operation merging with existing configuration

Neither flag is deprecated as of September 2025. Best practice recommends `--update-secrets` for CI/CD pipelines to avoid accidentally removing secrets, while `--set-secrets` suits declarative configuration management where complete control is desired.

### 6. Version pinning strongly recommended for production

Google explicitly advises **always pinning secrets to specific versions in production** rather than using "latest". This recommendation directly contradicts any practice of using "latest" in production environments. The rationale includes preventing outages from problematic new versions, enabling controlled rollouts, and supporting existing rollback procedures.

Production should reference secrets like `projects/PROJECT/secrets/SECRET/versions/42` instead of using the "latest" alias. Development and staging environments may use "latest" for convenience, but production deployments should treat secret updates like application deployments with version control.

### 7. Spring Cloud GCP definitively preferred over environment variables

Research confirms Spring Cloud GCP is **strongly preferred** for production Spring Boot applications despite minor performance overhead (200-500ms startup delay). Security benefits include runtime retrieval preventing plaintext exposure, comprehensive audit logging, fine-grained IAM control, and automatic rotation support.

Environment variables pose significant security risks including process visibility, log exposure potential, and inability to rotate without redeployment. The only valid use cases for environment variables are local development or legacy applications where modification proves difficult.

### 8. Cost optimization aligns with transparent pricing model

Current Secret Manager pricing (2025):
- **Active versions**: $0.06 per version per location per month
- **Access operations**: $0.03 per 10,000 operations
- **Free tier**: 6 active versions and 10,000 operations monthly

Key optimization strategies include deleting obsolete versions, implementing lifecycle policies, caching appropriately to reduce API calls, and using automatic replication unless specific location requirements exist. Regional co-location of Secret Manager with consuming services eliminates network charges.

### 9. Security best practices emphasize least privilege and isolation

Current IAM recommendations mandate:
- **Avoiding default Compute Engine service accounts** for production
- Creating **dedicated service accounts** per Cloud Run service
- Granting permissions at **secret level** rather than project level
- Using **workload identity** instead of service account keys
- Implementing **VPC Service Controls** for network isolation

Anti-patterns to avoid include broad IAM bindings at project level, sharing service accounts across services, and exposing secrets through environment variables for rotating credentials.

### 10. Significant platform updates affecting implementation

Recent changes impacting secret management strategies:
- **Regional secrets** (GA October 2024): Enforce data residency with geographic constraints
- **Parameter Manager** (GA March 2025): Manage non-sensitive configuration separately
- **GKE automatic rotation** (Preview April 2025): Automatically push secret updates to pods
- **Spring syntax change**: Critical breaking change requiring code updates for Spring Boot 3.4+

## Evidence-based recommendations for optimal strategy

Based on comprehensive analysis against 2025 standards, the optimal secret management strategy should:

**Architecture decisions**:
Choose single source of truth - either Terraform manages everything or gcloud manages everything. Mixed approaches cause state drift and operational complexity. For most organizations, Terraform-first provides better auditability and version control.

**Secret reference patterns**:
Pin all production secrets to specific versions. Implement gradual rollout processes testing new versions in staging before production. Use volume mounts for secrets requiring rotation, environment variables only for static values.

**Spring Boot configuration**:
Migrate to Spring Cloud GCP with new `sm@` syntax. Avoid environment variable injection except for local development. Implement proper caching to minimize performance impact while maintaining security.

**Cost and performance**:
Clean up obsolete versions regularly. Co-locate services regionally with Secret Manager. Monitor usage patterns and set billing alerts. Consider Parameter Manager for non-sensitive configuration to reduce Secret Manager costs.

**Security implementation**:
Create dedicated service accounts per service. Implement VPC Service Controls for network isolation. Enable comprehensive audit logging. Use Binary Authorization for container verification. Apply principle of least privilege at secret level, not project level.

The analysis document appears to conflate some recommended practices with anti-patterns, particularly around dual injection and version pinning strategies. The most critical corrections involve abandoning the Terraform + GitHub Actions dual management pattern and implementing proper version pinning for production secrets.