# Module Maturity Scale

Shared vocabulary for rating module implementation maturity across all roadmap plugin skills and agents.

## Scale

| Level | Description | Evidence |
|-------|-------------|----------|
| **Stub** | Directory/package exists, maybe a placeholder | Empty or minimal files, no business logic |
| **Domain Started** | Entities/models/types defined | Model classes, type definitions, value objects exist |
| **Service Layer** | Business logic implemented | Services, use cases, or handlers process domain operations |
| **API Ready** | Endpoints/routes exposed | Controllers, handlers, or route definitions expose functionality |
| **Tested** | Tests covering key paths | Test files exist and cover core operations (happy path + key edge cases) |
| **Production Ready** | Fully tested, documented, monitoring-ready | Comprehensive tests, user-facing docs, health checks, logging, error handling |

## Evidence Checklist

For each module, gather:

- Count source files vs test files
- Check for TODOs, FIXMEs, stubs, placeholder implementations
- Verify tests actually run (not just exist)
- Check for documentation
- Look for monitoring/observability integration
- Assess error handling completeness
