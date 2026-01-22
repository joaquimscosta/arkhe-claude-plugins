#!/usr/bin/env python3
"""
Spring Boot Pattern Detector

Scans Java and Kotlin files for Spring Boot annotations and returns skill recommendations.
Uses only standard library (no external dependencies).

Usage:
    python3 detect_patterns.py <file_path>
    python3 detect_patterns.py <directory_path> --recursive

Output:
    JSON with detected patterns, skill mappings, and risk levels.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Annotation patterns mapped to skills
SKILL_PATTERNS: Dict[str, List[str]] = {
    "spring-boot-web-api": [
        r"@RestController",
        r"@Controller",
        r"@GetMapping",
        r"@PostMapping",
        r"@PutMapping",
        r"@DeleteMapping",
        r"@PatchMapping",
        r"@RequestMapping",
        r"@ResponseBody",
        r"@RequestBody",
        r"@PathVariable",
        r"@RequestParam",
        r"@ExceptionHandler",
        r"@ControllerAdvice",
        r"@RestControllerAdvice",
    ],
    "spring-boot-data-ddd": [
        r"@Entity",
        r"@Repository",
        r"@MappedSuperclass",
        r"@Embeddable",
        r"@EmbeddedId",
        r"@OneToMany",
        r"@ManyToOne",
        r"@ManyToMany",
        r"@OneToOne",
        r"@JoinColumn",
        r"@JoinTable",
        r"@Query",
        r"@Modifying",
        r"@EntityGraph",
        r"JpaRepository",
        r"CrudRepository",
        r"PagingAndSortingRepository",
    ],
    "spring-boot-security": [
        r"@EnableWebSecurity",
        r"@EnableMethodSecurity",
        r"@PreAuthorize",
        r"@PostAuthorize",
        r"@Secured",
        r"@RolesAllowed",
        r"SecurityFilterChain",
        r"AuthenticationManager",
        r"UserDetailsService",
        r"PasswordEncoder",
        r"JwtDecoder",
        r"OAuth2ResourceServer",
    ],
    "spring-boot-testing": [
        r"@SpringBootTest",
        r"@WebMvcTest",
        r"@DataJpaTest",
        r"@DataJdbcTest",
        r"@JsonTest",
        r"@WebFluxTest",
        r"@MockitoBean",
        r"@SpyBean",
        r"@ServiceConnection",
        r"@Testcontainers",
        r"@Container",
        r"ApplicationModuleTest",
    ],
    "spring-boot-modulith": [
        r"@ApplicationModule",
        r"@ApplicationModuleListener",
        r"@NamedInterface",
        r"@Externalized",
        r"ApplicationModuleTest",
        r"Scenario",
    ],
    "spring-boot-observability": [
        r"@Timed",
        r"@Counted",
        r"@Observed",
        r"HealthIndicator",
        r"MeterRegistry",
        r"Tracer",
        r"Span",
        r"ObservationRegistry",
        r"@Endpoint",
        r"@ReadOperation",
        r"@WriteOperation",
    ],
    "domain-driven-design": [
        r"@DomainService",
        r"@ValueObject",
        r"@AggregateRoot",
        r"@Aggregate",
        r"@DomainEvent",
        r"AbstractAggregateRoot",
    ],
}

# Deprecated/escalation patterns
ESCALATION_PATTERNS: Dict[str, Dict] = {
    "@MockBean": {
        "reason": "Deprecated since Spring Boot 3.4",
        "replacement": "@MockitoBean",
        "severity": "WARNING",
    },
    "@EnableGlobalMethodSecurity": {
        "reason": "Deprecated, use @EnableMethodSecurity",
        "replacement": "@EnableMethodSecurity",
        "severity": "WARNING",
    },
    r"\.and\(\)": {
        "reason": "Removed in Spring Security 7",
        "replacement": "Use Lambda DSL closures",
        "severity": "ERROR",
    },
    "antMatchers": {
        "reason": "Removed in Spring Security 6",
        "replacement": "requestMatchers()",
        "severity": "ERROR",
    },
    "authorizeRequests": {
        "reason": "Deprecated in Spring Security 6",
        "replacement": "authorizeHttpRequests()",
        "severity": "WARNING",
    },
    r"com\.fasterxml\.jackson": {
        "reason": "Namespace changes in Jackson 3 (Spring Boot 4)",
        "replacement": "tools.jackson",
        "severity": "INFO",
    },
}

# Risk classification
LOW_RISK_SKILLS = {
    "spring-boot-web-api",
    "spring-boot-data-ddd",
    "domain-driven-design",
    "spring-boot-modulith",
    "spring-boot-observability",
}

HIGH_RISK_SKILLS = {
    "spring-boot-security",
    "spring-boot-testing",
    "spring-boot-verify",
}


def scan_file(file_path: Path) -> Dict:
    """Scan a single file for patterns."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Could not read file: {e}"}

    result = {
        "file": str(file_path),
        "detected_skills": [],
        "detected_patterns": {},
        "escalations": [],
        "risk_classification": {"low_risk": [], "high_risk": []},
    }

    # Scan for skill patterns
    for skill, patterns in SKILL_PATTERNS.items():
        matched_patterns = []
        for pattern in patterns:
            if re.search(pattern, content):
                matched_patterns.append(pattern.replace("\\", ""))

        if matched_patterns:
            result["detected_skills"].append(skill)
            result["detected_patterns"][skill] = matched_patterns

            # Classify risk
            if skill in LOW_RISK_SKILLS:
                result["risk_classification"]["low_risk"].append(skill)
            elif skill in HIGH_RISK_SKILLS:
                result["risk_classification"]["high_risk"].append(skill)

    # Scan for escalation patterns
    for pattern, info in ESCALATION_PATTERNS.items():
        if re.search(pattern, content):
            result["escalations"].append(
                {
                    "pattern": pattern.replace("\\", ""),
                    "reason": info["reason"],
                    "replacement": info["replacement"],
                    "severity": info["severity"],
                }
            )

    return result


def scan_directory(dir_path: Path, recursive: bool = True) -> Dict:
    """Scan a directory for Java and Kotlin files."""
    results = {
        "directory": str(dir_path),
        "files_scanned": 0,
        "files_with_patterns": [],
        "skill_summary": {},
        "escalation_summary": [],
        "routing_recommendation": {},
    }

    # Find all Java files
    java_pattern = "**/*.java" if recursive else "*.java"
    java_files = list(dir_path.glob(java_pattern))

    # Find all Kotlin files
    kotlin_pattern = "**/*.kt" if recursive else "*.kt"
    kotlin_files = list(dir_path.glob(kotlin_pattern))

    # Combine Java and Kotlin files
    all_files = java_files + kotlin_files

    results["files_scanned"] = len(all_files)

    all_skills: Set[str] = set()
    all_escalations: List[Dict] = []
    files_by_skill: Dict[str, List[str]] = {}

    for source_file in all_files:
        file_result = scan_file(source_file)

        if file_result.get("detected_skills"):
            results["files_with_patterns"].append(
                {
                    "file": str(source_file),
                    "skills": file_result["detected_skills"],
                    "escalations": file_result.get("escalations", []),
                }
            )

            for skill in file_result["detected_skills"]:
                all_skills.add(skill)
                if skill not in files_by_skill:
                    files_by_skill[skill] = []
                files_by_skill[skill].append(str(source_file))

        if file_result.get("escalations"):
            all_escalations.extend(file_result["escalations"])

    # Build summary
    results["skill_summary"] = {
        "detected": list(all_skills),
        "files_by_skill": files_by_skill,
        "low_risk": [s for s in all_skills if s in LOW_RISK_SKILLS],
        "high_risk": [s for s in all_skills if s in HIGH_RISK_SKILLS],
    }

    # Deduplicate escalations
    seen_patterns = set()
    unique_escalations = []
    for esc in all_escalations:
        if esc["pattern"] not in seen_patterns:
            seen_patterns.add(esc["pattern"])
            unique_escalations.append(esc)
    results["escalation_summary"] = unique_escalations

    # Generate routing recommendation
    results["routing_recommendation"] = generate_routing(
        results["skill_summary"], results["escalation_summary"]
    )

    return results


def generate_routing(skill_summary: Dict, escalations: List) -> Dict:
    """Generate routing recommendation based on detected patterns."""
    routing = {
        "auto_invoke": [],
        "require_confirmation": [],
        "warnings": [],
        "delegate_to_agent": False,
        "recommended_action": "",
    }

    low_risk = skill_summary.get("low_risk", [])
    high_risk = skill_summary.get("high_risk", [])

    routing["auto_invoke"] = low_risk
    routing["require_confirmation"] = high_risk

    # Add warnings for escalations
    for esc in escalations:
        routing["warnings"].append(
            f"{esc['severity']}: {esc['pattern']} - {esc['reason']}. Use {esc['replacement']}"
        )

    # Determine if agent delegation is needed
    total_files = len(skill_summary.get("files_by_skill", {}).values())
    if total_files > 10 or len(high_risk) > 2:
        routing["delegate_to_agent"] = True
        routing["recommended_action"] = (
            "Delegate to spring-boot-reviewer agent for comprehensive analysis"
        )
    elif high_risk:
        routing["recommended_action"] = (
            f"Request confirmation before loading: {', '.join(high_risk)}"
        )
    elif low_risk:
        routing["recommended_action"] = (
            f"Auto-invoke guidance for: {', '.join(low_risk)}"
        )
    else:
        routing["recommended_action"] = "No Spring Boot patterns detected"

    return routing


def check_spring_boot_project(dir_path: Path) -> Dict:
    """Check if directory is a Spring Boot project."""
    result = {"is_spring_boot": False, "build_system": None, "spring_boot_version": None}

    # Check for pom.xml
    pom_file = dir_path / "pom.xml"
    if pom_file.exists():
        content = pom_file.read_text(encoding="utf-8")
        if "spring-boot-starter" in content or "org.springframework.boot" in content:
            result["is_spring_boot"] = True
            result["build_system"] = "maven"

            # Try to extract version
            version_match = re.search(
                r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>([^<]+)</version>",
                content,
            )
            if version_match:
                result["spring_boot_version"] = version_match.group(1)

    # Check for build.gradle
    for gradle_file in ["build.gradle", "build.gradle.kts"]:
        gradle_path = dir_path / gradle_file
        if gradle_path.exists():
            content = gradle_path.read_text(encoding="utf-8")
            if "spring-boot" in content.lower():
                result["is_spring_boot"] = True
                result["build_system"] = "gradle"

                # Try to extract version
                version_match = re.search(
                    r"org\.springframework\.boot['\"]?\s*version\s*['\"]?([^'\"]+)",
                    content,
                )
                if version_match:
                    result["spring_boot_version"] = version_match.group(1)

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 detect_patterns.py <file_or_directory> [--recursive]")
        sys.exit(1)

    target = Path(sys.argv[1])
    recursive = "--recursive" in sys.argv or "-r" in sys.argv

    if not target.exists():
        print(json.dumps({"error": f"Path does not exist: {target}"}))
        sys.exit(1)

    if target.is_file():
        result = scan_file(target)
    else:
        # Check if it's a Spring Boot project first
        project_check = check_spring_boot_project(target)
        result = scan_directory(target, recursive)
        result["project_info"] = project_check

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
