"""
Skill resource models - Layer 3 (Conditionally loaded).

The resource layer contains References and Scripts that are loaded
only when specific conditions are met.

Standard Directory Structure:
    skill-name/
    ├── SKILL.md           # Skill definition file
    ├── references/        # Reference documents directory
    │   ├── handbook.md
    │   └── api-docs.md
    └── scripts/           # Executable scripts directory
        ├── upload.py
        └── notify.sh
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from openskills.models.dependency import SkillDependency


# Standard directory names for skill resources
REFERENCES_DIR = "references"
SCRIPTS_DIR = "scripts"


class ResourceType(str, Enum):
    """Type of resource."""
    REFERENCE = "reference"
    SCRIPT = "script"


class ReferenceMode(str, Enum):
    """Reference loading mode."""
    EXPLICIT = "explicit"  # Has condition, LLM evaluates condition
    IMPLICIT = "implicit"  # No condition, LLM decides if useful (Claude style)
    ALWAYS = "always"      # Always load (e.g., safety guidelines, specs)


class Reference(BaseModel):
    """
    Reference: Conditionally loaded document.

    References are additional documents that are loaded into the context
    only when specific conditions are met. They are "read" by the model,
    consuming context tokens.

    Example use case: Loading a finance handbook only when the meeting
    content involves financial topics.
    """

    path: str = Field(
        ...,
        description="Relative path to the reference file (should be in references/ directory)",
        examples=["references/finance-handbook.md", "references/api-docs.md"],
    )

    condition: str = Field(
        default="",
        description="Natural language condition for when to load this reference",
        examples=["When the content involves financial or budget topics"],
    )

    description: str = Field(
        default="",
        description="Brief description of what this reference contains",
    )

    mode: ReferenceMode = Field(
        default=ReferenceMode.IMPLICIT,
        description="Loading mode: explicit (condition-based), implicit (LLM decides), always (always load)",
    )

    content: str | None = Field(
        default=None,
        description="Loaded content (None until loaded)",
        exclude=True,  # Don't serialize
    )

    _resolved_path: Path | None = None

    def is_loaded(self) -> bool:
        """Check if the reference content has been loaded."""
        return self.content is not None

    def should_load(self, context: str) -> bool:
        """
        Simple check if reference should be loaded (fallback when no LLM available).

        For accurate evaluation, use `evaluate_condition_with_llm` instead.

        Args:
            context: The current conversation or content context

        Returns:
            True if the reference should be loaded
        """
        # Always mode: always load
        if self.mode == ReferenceMode.ALWAYS:
            return True

        # For explicit and implicit modes, let the LLM decide
        # This fallback returns False to defer to LLM evaluation
        return False


class Script(BaseModel):
    """
    Script: Executable code triggered by conditions.

    Scripts are executed (not read) by the model. The model only sees
    the execution result, not the script content itself, making them
    very token-efficient.

    Example use case: Uploading meeting notes to cloud storage,
    sending notifications, or running calculations.
    """

    name: str = Field(
        ...,
        description="Unique name for the script",
        examples=["upload", "notify", "calculate"],
    )

    path: str = Field(
        ...,
        description="Relative path to the script file (should be in scripts/ directory)",
        examples=["scripts/upload.py", "scripts/notify.sh"],
    )

    description: str = Field(
        ...,
        description="Description of what the script does",
        examples=["Uploads the meeting summary to cloud storage"],
    )

    args: list[str] = Field(
        default_factory=list,
        description="Expected arguments for the script",
    )

    timeout: int = Field(
        default=30,
        description="Maximum execution time in seconds",
        ge=1,
        le=300,
    )

    sandbox: bool = Field(
        default=True,
        description="Whether to run in a sandboxed environment",
    )

    outputs: list[str] = Field(
        default_factory=list,
        description="Sandbox paths to sync back to local after execution",
        examples=[["/home/gem/output"]],
    )

    _resolved_path: Path | None = None

    def get_invocation_hint(self) -> str:
        """
        Get a hint for how the model should invoke this script.

        Returns:
            Natural language description for the model
        """
        args_hint = ""
        if self.args:
            args_hint = f" with arguments: {', '.join(self.args)}"
        return f"To {self.description.lower()}, invoke the '{self.name}' script{args_hint}."


class SkillResources(BaseModel):
    """Container for all resources associated with a skill."""

    references: list[Reference] = Field(default_factory=list)
    scripts: list[Script] = Field(default_factory=list)
    dependency: SkillDependency = Field(default_factory=SkillDependency)

    def get_reference(self, path: str) -> Reference | None:
        """Get a reference by path."""
        for ref in self.references:
            if ref.path == path:
                return ref
        return None

    def get_script(self, name: str) -> Script | None:
        """Get a script by name."""
        for script in self.scripts:
            if script.name == name:
                return script
        return None

    def get_applicable_references(self, context: str) -> list[Reference]:
        """Get all references that should be loaded for the given context."""
        return [ref for ref in self.references if ref.should_load(context)]
