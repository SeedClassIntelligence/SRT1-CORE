"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: TRACING_AUDIT
Key Symbols: SeedTemplate, SeedTemplateRegistry, get_registry, to_dict, to_summary ... and 12 more

Extracted Purposes:
  - SeedTemplate: A pre-built intent pattern for a common development task.
  - SeedTemplateRegistry: Singleton registry holding all seed templates (built-in + user-defined).
  - get_registry: Get the global template registry singleton.
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Seed Templates — Pre-Built Intent Patterns
==================================================

Provides curated seed templates for common development tasks.
Each template ships with optimized keywords, domain context,
priority levels, tags, and checklists — giving SRT-1 higher
coherence scores out of the box.

Instead of:
    srt.plant_seed("add authentication")
    → generic keywords, weak coherence

Use:
    registry.plant_from_template("auth_flow", "Add JWT auth to API", srt)
    → curated keywords, strong coherence, step-by-step checklist

Templates are auto-detected: if a raw task matches a template pattern,
the template is automatically applied.

User-defined templates can be loaded from .srt1/templates/*.yaml

Author : William Darnell Jernigan IV (Architect)
License: Business Source License 1.1
"""

import os
import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("srt1.templates")


# ==============================================================================
# SEED TEMPLATE DATACLASS
# ==============================================================================

@dataclass
class SeedTemplate:
    """
    A pre-built intent pattern for a common development task.

    Each template provides curated keywords, domain context, and a
    checklist optimized for high SRT-1 coherence scores. When a seed
    is planted using a template, the template's keywords are merged
    with the user's task-specific terms, resulting in much better
    drift detection.
    """
    template_id: str
    name: str
    description: str
    domain: str
    keywords: List[str]
    default_priority: int = 5
    default_tags: List[str] = field(default_factory=list)
    checklist: List[str] = field(default_factory=list)
    risk_areas: List[str] = field(default_factory=list)
    category: str = "backend"
    # Patterns that trigger auto-detection (regex-compatible)
    match_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "keywords": self.keywords,
            "default_priority": self.default_priority,
            "default_tags": self.default_tags,
            "checklist": self.checklist,
            "risk_areas": self.risk_areas,
            "category": self.category,
        }

    def to_summary(self) -> Dict[str, Any]:
        """Compact representation for API list views."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "domain": self.domain,
            "priority": self.default_priority,
            "keywords_count": len(self.keywords),
            "checklist_steps": len(self.checklist),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeedTemplate":
        """Deserialize from a dict (used for YAML loading)."""
        return cls(
            template_id=data["template_id"],
            name=data.get("name", data["template_id"].replace("_", " ").title()),
            description=data.get("description", ""),
            domain=data.get("domain", "general"),
            keywords=data.get("keywords", []),
            default_priority=data.get("default_priority", 5),
            default_tags=data.get("default_tags", data.get("tags", [])),
            checklist=data.get("checklist", []),
            risk_areas=data.get("risk_areas", []),
            category=data.get("category", "backend"),
            match_patterns=data.get("match_patterns", []),
        )


# ==============================================================================
# TEMPLATE REGISTRY
# ==============================================================================

class SeedTemplateRegistry:
    """
    Singleton registry holding all seed templates (built-in + user-defined).

    Usage:
        registry = get_registry()
        template = registry.get("auth_flow")
        seed = registry.plant_from_template("auth_flow", "Add JWT auth", srt)
    """

    def __init__(self):
        self._templates: Dict[str, SeedTemplate] = {}
        self._loaded_user_dirs: set = set()
        self._register_builtins()

    def register(self, template: SeedTemplate) -> None:
        """Register a template. Overwrites existing template with same ID."""
        self._templates[template.template_id] = template
        logger.debug(f"Registered template: {template.template_id}")

    def get(self, template_id: str) -> Optional[SeedTemplate]:
        """Retrieve a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all templates, optionally filtered by category."""
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        templates.sort(key=lambda t: (t.category, t.name))
        return [t.to_summary() for t in templates]

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Fuzzy-match templates by name, description, keywords, and domain.
        Returns templates sorted by relevance score.
        """
        query_lower = query.lower()
        query_words = set(re.findall(r"[a-z][a-z0-9_]+", query_lower))
        results: List[Tuple[int, SeedTemplate]] = []

        for template in self._templates.values():
            score = 0

            # Match against template ID
            if query_lower in template.template_id:
                score += 10

            # Match against name
            if query_lower in template.name.lower():
                score += 8

            # Match against description
            if query_lower in template.description.lower():
                score += 5

            # Match against domain
            if query_lower in template.domain:
                score += 6

            # Match against keywords (word-level)
            keyword_set = set(k.lower() for k in template.keywords)
            keyword_overlap = query_words & keyword_set
            score += len(keyword_overlap) * 3

            # Match against tags
            tag_set = set(t.lower() for t in template.default_tags)
            tag_overlap = query_words & tag_set
            score += len(tag_overlap) * 2

            if score > 0:
                results.append((score, template))

        results.sort(key=lambda x: -x[0])
        return [t.to_summary() for _, t in results]

    def detect_template(self, task: str) -> Optional[SeedTemplate]:
        """
        Auto-detect the best matching template for a raw task string.

        Uses match_patterns first (regex), then falls back to keyword
        overlap scoring. Returns the best match if confidence is high
        enough, otherwise None.
        """
        task_lower = task.lower()

        # Phase 1: Check explicit match patterns (highest confidence)
        for template in self._templates.values():
            for pattern in template.match_patterns:
                try:
                    if re.search(pattern, task_lower):
                        logger.info(
                            f"Auto-detected template '{template.template_id}' "
                            f"for task: {task[:50]}..."
                        )
                        return template
                except re.error:
                    continue

        # Phase 2: Keyword overlap scoring (fuzzy match)
        task_words = set(re.findall(r"[a-z][a-z0-9_]+", task_lower))
        best_score = 0
        best_template = None

        for template in self._templates.values():
            keyword_set = set(k.lower() for k in template.keywords)
            overlap = task_words & keyword_set
            # Normalize by template keyword count to prevent bias toward
            # templates with more keywords
            if keyword_set:
                score = len(overlap) / len(keyword_set)
            else:
                score = 0.0

            # Also boost if domain words appear
            domain_words = set(template.domain.split("_"))
            domain_overlap = task_words & domain_words
            score += len(domain_overlap) * 0.1

            if score > best_score:
                best_score = score
                best_template = template

        # Require at least 20% keyword overlap to auto-apply
        if best_score >= 0.20 and best_template:
            logger.info(
                f"Auto-detected template '{best_template.template_id}' "
                f"(score={best_score:.2f}) for task: {task[:50]}..."
            )
            return best_template

        return None

    def plant_from_template(
        self,
        template_id: str,
        task: str,
        srt_tool,
        seed_queue=None,
        source: str = "api",
        priority_override: Optional[int] = None,
    ) -> Any:
        """
        Plant a seed using a template's curated defaults.

        Merges the template's keywords with task-extracted keywords
        for maximum coherence coverage. Uses the template's domain
        and priority unless overridden.

        Args:
            template_id: Template to use
            task: The user's specific task description
            srt_tool: SRT instance to plant the seed in
            seed_queue: Optional SCIASeedQueue for lifecycle tracking
            source: Where the seed came from
            priority_override: Override the template's default priority

        Returns:
            The planted Seed object
        """
        template = self.get(template_id)
        if not template:
            raise ValueError(f"Unknown template: {template_id}")

        # Merge keywords: template keywords + task-extracted keywords
        noise = {
            "a", "an", "the", "to", "in", "on", "at", "for", "of", "and",
            "or", "is", "it", "my", "i", "we", "do", "that", "this", "with",
            "from", "into", "add", "create", "make", "build", "implement",
        }
        task_words = re.findall(r"[a-z][a-z0-9_]+", task.lower())
        task_keywords = [w for w in task_words if w not in noise and len(w) > 2]

        merged_keywords = list(template.keywords)
        for kw in task_keywords:
            if kw not in merged_keywords:
                merged_keywords.append(kw)

        priority = priority_override or template.default_priority

        # Plant in SRT
        seed = srt_tool.plant_seed(
            task=task,
            domain=template.domain,
            keywords=merged_keywords,
            metadata={
                "template_id": template.template_id,
                "template_name": template.name,
                "checklist": template.checklist,
                "risk_areas": template.risk_areas,
            },
        )

        # Also register in seed queue if available
        if seed_queue:
            seed_queue.plant(
                intent=task,
                source=source,
                priority=priority,
                tags=template.default_tags,
            )

        logger.info(
            f"Planted seed from template '{template.template_id}' "
            f"with {len(merged_keywords)} keywords (domain={template.domain})"
        )
        return seed

    def plant_auto(
        self,
        task: str,
        srt_tool,
        seed_queue=None,
        source: str = "api",
    ) -> Tuple[Any, Optional[str]]:
        """
        Plant a seed, auto-detecting the best template.

        If a template matches, it's applied automatically.
        If no template matches, plants a plain seed.

        Returns:
            Tuple of (Seed, template_id or None)
        """
        template = self.detect_template(task)
        if template:
            seed = self.plant_from_template(
                template_id=template.template_id,
                task=task,
                srt_tool=srt_tool,
                seed_queue=seed_queue,
                source=source,
            )
            return seed, template.template_id

        # No template match — plant a plain seed
        seed = srt_tool.plant_seed(task=task, domain="general")
        if seed_queue:
            seed_queue.plant(intent=task, source=source)
        return seed, None

    # ------------------------------------------------------------------
    # USER-DEFINED TEMPLATE LOADING
    # ------------------------------------------------------------------

    def load_user_templates(self, directory: str) -> int:
        """
        Load user-defined templates from .yaml files in a directory.

        Supports both full YAML (if PyYAML is installed) and a simple
        key: value fallback parser for zero-dependency operation.

        Args:
            directory: Path to scan for .yaml/.yml files

        Returns:
            Number of templates loaded
        """
        if not os.path.isdir(directory):
            return 0

        if directory in self._loaded_user_dirs:
            return 0
        self._loaded_user_dirs.add(directory)

        loaded = 0
        for fname in os.listdir(directory):
            if not fname.endswith((".yaml", ".yml")):
                continue
            filepath = os.path.join(directory, fname)
            try:
                data = self._parse_yaml_file(filepath)
                if data and "template_id" in data:
                    template = SeedTemplate.from_dict(data)
                    self.register(template)
                    loaded += 1
                    logger.info(f"Loaded user template: {template.template_id} from {fname}")
            except Exception as e:
                logger.warning(f"Failed to load template from {fname}: {e}")

        return loaded

    @staticmethod
    def _parse_yaml_file(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Parse a YAML file. Uses PyYAML if available, otherwise falls
        back to a simple parser that handles flat key-value pairs and
        simple lists (sufficient for template definitions).
        """
        try:
            import yaml
            with open(filepath, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            pass

        # Fallback: simple YAML-subset parser (no PyYAML needed)
        result: Dict[str, Any] = {}
        current_key = None
        current_list: Optional[List[str]] = None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.rstrip()

                    # Skip comments and empty lines
                    if not stripped or stripped.startswith("#"):
                        continue

                    # List item
                    if stripped.startswith("  - ") or stripped.startswith("    - "):
                        if current_list is not None:
                            value = stripped.lstrip().lstrip("- ").strip()
                            # Remove quotes
                            if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                                value = value[1:-1]
                            current_list.append(value)
                        continue

                    # Inline list: key: [val1, val2]
                    if ":" in stripped and "[" in stripped:
                        key, val = stripped.split(":", 1)
                        key = key.strip()
                        val = val.strip()
                        if val.startswith("[") and val.endswith("]"):
                            items = [
                                v.strip().strip("'\"")
                                for v in val[1:-1].split(",")
                                if v.strip()
                            ]
                            result[key] = items
                            current_key = key
                            current_list = None
                            continue

                    # Key-value pair
                    if ":" in stripped and not stripped.startswith(" "):
                        # Save previous list
                        if current_list is not None and current_key:
                            result[current_key] = current_list

                        key, val = stripped.split(":", 1)
                        key = key.strip()
                        val = val.strip()

                        if val:
                            # Remove quotes
                            if val.startswith(("'", '"')) and val.endswith(("'", '"')):
                                val = val[1:-1]
                            # Try int conversion
                            try:
                                result[key] = int(val)
                            except ValueError:
                                result[key] = val
                            current_key = key
                            current_list = None
                        else:
                            # Value will be a list on subsequent lines
                            current_key = key
                            current_list = []

                # Save final list
                if current_list is not None and current_key:
                    result[current_key] = current_list

        except (IOError, OSError) as e:
            logger.warning(f"Failed to read {filepath}: {e}")
            return None

        return result if result else None

    # ------------------------------------------------------------------
    # BUILT-IN TEMPLATES
    # ------------------------------------------------------------------

    def _register_builtins(self) -> None:
        """Register all built-in seed templates."""

        self.register(SeedTemplate(
            template_id="auth_flow",
            name="Authentication Flow",
            description="User authentication: login, signup, JWT, OAuth, session management",
            domain="auth_security",
            category="backend",
            keywords=[
                "auth", "authentication", "login", "signup", "register",
                "jwt", "token", "oauth", "session", "password", "hash",
                "credentials", "permission", "role", "middleware", "guard",
                "verify", "validate", "secure", "user",
            ],
            default_priority=8,
            default_tags=["auth", "security", "backend"],
            checklist=[
                "Identify existing auth patterns in the codebase",
                "Define user model/schema if not present",
                "Implement registration endpoint with password hashing",
                "Implement login endpoint with token generation",
                "Add auth middleware/guard for protected routes",
                "Add token refresh and session management",
                "Write tests for auth flows (happy path + edge cases)",
            ],
            risk_areas=["AUTH_SENSITIVE", "WRITES_TO_DB", "HAS_LOGGING"],
            match_patterns=[
                r"\b(add|implement|create|build)\b.*\b(auth|login|signup|jwt|oauth)\b",
                r"\b(jwt|oauth|authentication)\b.*\b(flow|system|endpoint)\b",
                r"\buser\s+(login|registration|signup)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="crud_api",
            name="CRUD API Endpoints",
            description="REST or GraphQL CRUD endpoints with validation and error handling",
            domain="api_development",
            category="backend",
            keywords=[
                "api", "endpoint", "route", "crud", "create", "read",
                "update", "delete", "rest", "get", "post", "put", "patch",
                "request", "response", "validate", "serialize", "controller",
                "handler", "status", "json",
            ],
            default_priority=6,
            default_tags=["api", "crud", "backend"],
            checklist=[
                "Define the data model/schema for the resource",
                "Create the route/controller with all CRUD operations",
                "Add input validation and serialization",
                "Add error handling with proper HTTP status codes",
                "Add pagination for list endpoints",
                "Write integration tests for each endpoint",
            ],
            risk_areas=["WRITES_TO_DB", "FILE_IO"],
            match_patterns=[
                r"\b(add|create|build|implement)\b.*\b(api|endpoint|route|crud)\b",
                r"\bcrud\b.*\b(endpoint|api|route)\b",
                r"\brest\s*(api|endpoint)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="data_pipeline",
            name="Data Pipeline",
            description="ETL processes, data processing, batch jobs, data transformation",
            domain="data_engineering",
            category="data",
            keywords=[
                "data", "pipeline", "etl", "extract", "transform", "load",
                "batch", "process", "stream", "ingest", "parse", "csv",
                "json", "database", "query", "aggregate", "filter",
                "validate", "clean", "normalize",
            ],
            default_priority=6,
            default_tags=["data", "pipeline", "etl"],
            checklist=[
                "Define input data source and format",
                "Build extraction/ingestion layer",
                "Implement transformation and validation logic",
                "Add error handling and retry logic",
                "Implement the load/output stage",
                "Add logging and progress tracking",
                "Write tests with sample data",
            ],
            risk_areas=["FILE_IO", "EXTERNAL_API_CALL", "WRITES_TO_DB"],
            match_patterns=[
                r"\b(data|etl)\b.*\b(pipeline|process|transform)\b",
                r"\b(extract|ingest|import)\b.*\b(data|csv|json)\b",
                r"\bbatch\s+(job|process|pipeline)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="test_suite",
            name="Test Suite",
            description="Unit tests, integration tests, fixtures, and test utilities",
            domain="quality_assurance",
            category="testing",
            keywords=[
                "test", "unit", "integration", "fixture", "mock", "assert",
                "coverage", "pytest", "spec", "suite", "case", "expect",
                "setup", "teardown", "parametrize", "conftest", "verify",
                "validate", "edge", "regression",
            ],
            default_priority=5,
            default_tags=["testing", "quality"],
            checklist=[
                "Identify the code to be tested",
                "Set up test fixtures and mock data",
                "Write happy-path unit tests",
                "Write edge-case and error-path tests",
                "Add integration tests if applicable",
                "Verify test coverage meets threshold",
            ],
            risk_areas=[],
            match_patterns=[
                r"\b(add|write|create|implement)\b.*\b(test|spec|unittest)\b",
                r"\btest\s+(suite|coverage|case)\b",
                r"\bunit\s+test\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="refactor",
            name="Code Refactoring",
            description="Code refactoring, consolidation, cleanup, and architectural improvement",
            domain="code_maintenance",
            category="backend",
            keywords=[
                "refactor", "consolidate", "cleanup", "reorganize", "extract",
                "simplify", "deduplicate", "merge", "split", "rename",
                "move", "encapsulate", "decouple", "modular", "pattern",
                "abstract", "interface", "reduce", "optimize", "clean",
            ],
            default_priority=4,
            default_tags=["refactor", "maintenance", "cleanup"],
            checklist=[
                "Identify code to refactor and its dependents",
                "Document current behavior (snapshot tests if needed)",
                "Extract/consolidate common patterns",
                "Update all import paths and references",
                "Run existing tests to verify no regressions",
                "Update documentation if API surface changed",
            ],
            risk_areas=["FILE_IO"],
            match_patterns=[
                r"\b(refactor|consolidate|clean\s*up|reorganize)\b",
                r"\b(deduplicate|merge|split)\b.*\b(code|module|function|class)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="bugfix",
            name="Bug Fix",
            description="Bug investigation, root cause analysis, and targeted fix",
            domain="debugging",
            category="backend",
            keywords=[
                "bug", "fix", "debug", "error", "crash", "issue", "broken",
                "failing", "traceback", "exception", "regression", "patch",
                "investigate", "root", "cause", "reproduce", "stack",
                "trace", "resolve", "repair",
            ],
            default_priority=8,
            default_tags=["bugfix", "urgent"],
            checklist=[
                "Reproduce the bug reliably",
                "Read error messages and stack traces",
                "Identify the root cause",
                "Implement the minimal fix",
                "Write a regression test",
                "Verify the fix doesn't break other functionality",
            ],
            risk_areas=["AUTH_SENSITIVE", "WRITES_TO_DB"],
            match_patterns=[
                r"\b(fix|debug|resolve|repair)\b.*\b(bug|error|crash|issue)\b",
                r"\b(bug|error|crash)\b.*\b(in|with|when)\b",
                r"\b(broken|failing|not\s+working)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="feature_add",
            name="New Feature",
            description="New feature implementation with full integration",
            domain="feature_development",
            category="backend",
            keywords=[
                "feature", "implement", "add", "new", "build", "create",
                "functionality", "capability", "enhancement", "extend",
                "integrate", "support", "enable", "introduce", "develop",
                "module", "component", "service", "logic",
            ],
            default_priority=6,
            default_tags=["feature", "enhancement"],
            checklist=[
                "Review existing code for related patterns",
                "Define the feature's data model and interfaces",
                "Implement core logic",
                "Add integration points with existing code",
                "Add error handling and edge cases",
                "Write tests",
                "Update documentation",
            ],
            risk_areas=["FILE_IO", "WRITES_TO_DB"],
            match_patterns=[
                r"\b(add|implement|build|create)\b.*\b(feature|functionality|support)\b",
                r"\bnew\b.*\b(feature|capability|module)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="api_integration",
            name="API Integration",
            description="Third-party API integration with error handling and rate limiting",
            domain="integration",
            category="backend",
            keywords=[
                "api", "integration", "third-party", "external", "webhook",
                "http", "request", "response", "client", "sdk", "rate",
                "limit", "retry", "timeout", "callback", "payload",
                "endpoint", "service", "connect", "fetch",
            ],
            default_priority=6,
            default_tags=["integration", "api", "external"],
            checklist=[
                "Review the external API documentation",
                "Create an API client class with authentication",
                "Implement request/response handling with error codes",
                "Add retry logic and rate limiting",
                "Add timeout handling",
                "Write tests with mocked API responses",
                "Add logging for API calls",
            ],
            risk_areas=["EXTERNAL_API_CALL", "AUTH_SENSITIVE", "HAS_LOGGING"],
            match_patterns=[
                r"\b(integrate|connect|hook\s*up)\b.*\b(api|service|webhook)\b",
                r"\bthird.?party\b.*\b(api|service|integration)\b",
                r"\b(stripe|twilio|sendgrid|slack|github|aws)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="db_migration",
            name="Database Migration",
            description="Schema changes, migrations, data seeding, and model updates",
            domain="database",
            category="data",
            keywords=[
                "database", "migration", "schema", "table", "column",
                "index", "foreign", "key", "alter", "migrate", "seed",
                "model", "orm", "relation", "constraint", "nullable",
                "default", "rollback", "upgrade", "downgrade",
            ],
            default_priority=7,
            default_tags=["database", "migration", "schema"],
            checklist=[
                "Document the current schema state",
                "Write the migration (up and down)",
                "Update ORM models to match",
                "Add seed data if needed",
                "Test migration on a copy of production data",
                "Verify rollback works",
            ],
            risk_areas=["WRITES_TO_DB", "SYSTEM_SIDE_EFFECT"],
            match_patterns=[
                r"\b(database|db|schema)\b.*\b(migration|change|update|alter)\b",
                r"\b(add|create|modify|drop)\b.*\b(table|column|index)\b",
                r"\bmigration\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="frontend_component",
            name="Frontend Component",
            description="UI component creation with styling, state, and interactions",
            domain="ui_development",
            category="frontend",
            keywords=[
                "component", "ui", "frontend", "react", "vue", "angular",
                "render", "state", "props", "style", "css", "layout",
                "responsive", "button", "form", "input", "modal",
                "animation", "hook", "event",
            ],
            default_priority=5,
            default_tags=["frontend", "ui", "component"],
            checklist=[
                "Define component props/interface",
                "Create the component structure",
                "Add styling (CSS/styled-components)",
                "Implement state management and event handlers",
                "Make it responsive",
                "Write component tests",
            ],
            risk_areas=[],
            match_patterns=[
                r"\b(create|build|add)\b.*\b(component|ui|page|widget|modal)\b",
                r"\bfrontend\b.*\b(component|feature|page)\b",
                r"\b(react|vue|angular)\b.*\b(component|page)\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="devops_pipeline",
            name="DevOps Pipeline",
            description="CI/CD setup, Docker configuration, deployment automation",
            domain="infrastructure",
            category="devops",
            keywords=[
                "ci", "cd", "pipeline", "deploy", "docker", "container",
                "kubernetes", "github", "actions", "workflow", "build",
                "test", "release", "infra", "terraform", "ansible",
                "monitoring", "logs", "environment", "staging",
            ],
            default_priority=5,
            default_tags=["devops", "ci-cd", "infrastructure"],
            checklist=[
                "Define the deployment target and requirements",
                "Create Dockerfile / container configuration",
                "Set up CI pipeline (build → test → deploy)",
                "Add environment variable management",
                "Configure staging and production environments",
                "Add monitoring and alerting",
                "Document the deployment process",
            ],
            risk_areas=["SYSTEM_SIDE_EFFECT", "FILE_IO", "AUTH_SENSITIVE"],
            match_patterns=[
                r"\b(set\s*up|create|add|configure)\b.*\b(ci|cd|pipeline|docker|deploy)\b",
                r"\b(docker|kubernetes|terraform)\b.*\b(config|setup|deploy)\b",
                r"\bgithub\s+actions\b",
            ],
        ))

        self.register(SeedTemplate(
            template_id="documentation",
            name="Documentation",
            description="Documentation, READMEs, API specs, and user guides",
            domain="documentation",
            category="docs",
            keywords=[
                "docs", "documentation", "readme", "guide", "tutorial",
                "api", "spec", "openapi", "swagger", "markdown", "write",
                "explain", "describe", "reference", "example", "usage",
                "getting", "started", "changelog", "contributing",
            ],
            default_priority=3,
            default_tags=["docs", "documentation"],
            checklist=[
                "Identify what needs to be documented",
                "Review existing documentation for gaps",
                "Write/update the documentation",
                "Add code examples and usage patterns",
                "Verify all links and references work",
                "Get peer review on clarity",
            ],
            risk_areas=[],
            match_patterns=[
                r"\b(write|update|add|create)\b.*\b(docs|documentation|readme|guide)\b",
                r"\bdocument\b.*\b(api|code|feature|project)\b",
                r"\breadme\b",
            ],
        ))


# ==============================================================================
# SINGLETON
# ==============================================================================

_registry_instance: Optional[SeedTemplateRegistry] = None


def get_registry() -> SeedTemplateRegistry:
    """Get the global template registry singleton."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SeedTemplateRegistry()
    return _registry_instance
