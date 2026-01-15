"""
Skill - The complete skill object combining all layers.

A Skill represents a complete agent skill with its metadata, instructions,
and resources. It implements the progressive disclosure pattern where
different layers are loaded at different times.
"""

from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, model_validator

from openskills.models.metadata import SkillMetadata
from openskills.models.instruction import SkillInstruction
from openskills.models.resource import Reference, Script, SkillResources


class Skill(BaseModel):
    """
    Complete Skill object implementing three-layer progressive disclosure.

    Layer 1 (Metadata): Always loaded - used for discovery and matching
    Layer 2 (Instruction): Loaded on demand - the actual skill instructions
    Layer 3 (Resources): Conditionally loaded - References and Scripts

    Attributes:
        metadata: The skill metadata (always available)
        instruction: The skill instructions (loaded on demand)
        resources: References and scripts (conditionally loaded)
        source_path: Path to the SKILL.md file
    """

    metadata: SkillMetadata = Field(
        ...,
        description="Skill metadata (Layer 1 - always loaded)",
    )

    instruction: SkillInstruction | None = Field(
        default=None,
        description="Skill instructions (Layer 2 - loaded on demand)",
    )

    resources: SkillResources = Field(
        default_factory=SkillResources,
        description="Skill resources (Layer 3 - conditionally loaded)",
    )

    source_path: Path | None = Field(
        default=None,
        description="Path to the source SKILL.md file",
    )

    model_config = {
        "arbitrary_types_allowed": True,
    }

    @property
    def name(self) -> str:
        """Get the skill name."""
        return self.metadata.name

    @property
    def description(self) -> str:
        """Get the skill description."""
        return self.metadata.description

    @property
    def is_instruction_loaded(self) -> bool:
        """Check if instructions are loaded."""
        return self.instruction is not None

    @property
    def references(self) -> list[Reference]:
        """Get all references."""
        return self.resources.references

    @property
    def scripts(self) -> list[Script]:
        """Get all scripts."""
        return self.resources.scripts

    def get_base_path(self) -> Path | None:
        """Get the base directory path for resolving relative paths."""
        if self.source_path:
            return self.source_path.parent
        return None

    def resolve_reference_path(self, ref: Reference) -> Path | None:
        """Resolve a reference's relative path to absolute."""
        base = self.get_base_path()
        if base:
            return (base / ref.path).resolve()
        return None

    def resolve_script_path(self, script: Script) -> Path | None:
        """Resolve a script's relative path to absolute."""
        base = self.get_base_path()
        if base:
            return (base / script.path).resolve()
        return None

    def get_system_prompt(self, include_resources: bool = False) -> str:
        """
        Generate the system prompt for this skill.

        Args:
            include_resources: Whether to include loaded reference content

        Returns:
            The complete system prompt
        """
        parts = []

        # Add instruction content
        if self.instruction:
            parts.append(self.instruction.content)

        # Add script invocation hints
        if self.scripts:
            parts.append("\n## Available Actions\n")
            for script in self.scripts:
                parts.append(f"- {script.get_invocation_hint()}")

        # Add loaded reference content
        if include_resources:
            for ref in self.references:
                if ref.is_loaded() and ref.content:
                    parts.append(f"\n## Reference: {ref.path}\n")
                    parts.append(ref.content)

        return "\n".join(parts)

    def to_summary(self) -> dict:
        """
        Get a summary representation of the skill.

        Useful for displaying skill information without loading all content.
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.metadata.version,
            "triggers": self.metadata.triggers,
            "has_instruction": self.is_instruction_loaded,
            "reference_count": len(self.references),
            "script_count": len(self.scripts),
            "source": str(self.source_path) if self.source_path else None,
        }
