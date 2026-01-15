"""
SKILL.md parser.

Parses SKILL.md files into Skill objects, handling the three-layer
progressive disclosure structure.
"""

from pathlib import Path
from typing import Any

from openskills.core.skill import Skill
from openskills.models.metadata import SkillMetadata
from openskills.models.instruction import SkillInstruction
from openskills.models.resource import Reference, Script, SkillResources
from openskills.utils.frontmatter import parse_frontmatter


class SkillParser:
    """
    Parser for SKILL.md files.

    Supports two parsing modes:
    1. Metadata-only: Quick parsing that only extracts frontmatter (Layer 1)
    2. Full parsing: Extracts all content including instructions (Layer 1+2)

    Layer 3 resources (References and Scripts) are defined in frontmatter
    but their content is loaded separately on demand.
    """

    REQUIRED_FIELDS = ["name", "description"]

    def parse_file(
        self,
        path: Path,
        metadata_only: bool = False,
    ) -> Skill:
        """
        Parse a SKILL.md file.

        Args:
            path: Path to the SKILL.md file
            metadata_only: If True, only parse metadata (Layer 1)

        Returns:
            A Skill object

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {path}")

        content = path.read_text(encoding="utf-8")
        return self.parse_content(content, source_path=path, metadata_only=metadata_only)

    def parse_content(
        self,
        content: str,
        source_path: Path | None = None,
        metadata_only: bool = False,
    ) -> Skill:
        """
        Parse SKILL.md content.

        Args:
            content: The raw content of the SKILL.md file
            source_path: Optional path to the source file
            metadata_only: If True, only parse metadata (Layer 1)

        Returns:
            A Skill object
        """
        frontmatter, body = parse_frontmatter(content)

        # Validate required fields
        self._validate_frontmatter(frontmatter)

        # Parse metadata (Layer 1)
        metadata = self._parse_metadata(frontmatter)

        # Parse resources definition (Layer 3 - definitions only, not content)
        resources = self._parse_resources(frontmatter)

        # Create skill
        skill = Skill(
            metadata=metadata,
            resources=resources,
            source_path=source_path,
        )

        # Parse instructions if not metadata-only (Layer 2)
        if not metadata_only and body:
            skill.instruction = SkillInstruction(
                content=body,
                raw_content=content,
            )

        return skill

    def _validate_frontmatter(self, frontmatter: dict[str, Any]) -> None:
        """Validate that required fields are present."""
        missing = [f for f in self.REQUIRED_FIELDS if f not in frontmatter]
        if missing:
            raise ValueError(f"Missing required fields in frontmatter: {missing}")

    def _parse_metadata(self, frontmatter: dict[str, Any]) -> SkillMetadata:
        """Parse metadata from frontmatter."""
        return SkillMetadata(
            name=frontmatter["name"],
            description=frontmatter["description"],
            version=frontmatter.get("version", "1.0.0"),
            triggers=frontmatter.get("triggers", []),
            author=frontmatter.get("author"),
            tags=frontmatter.get("tags", []),
        )

    def _parse_resources(self, frontmatter: dict[str, Any]) -> SkillResources:
        """Parse resource definitions from frontmatter."""
        references = []
        scripts = []

        # Parse references
        for ref_data in frontmatter.get("references", []):
            if isinstance(ref_data, dict):
                references.append(Reference(
                    path=ref_data.get("path", ""),
                    condition=ref_data.get("condition", ""),
                    description=ref_data.get("description", ""),
                ))
            elif isinstance(ref_data, str):
                # Simple path string
                references.append(Reference(path=ref_data))

        # Parse scripts
        for script_data in frontmatter.get("scripts", []):
            if isinstance(script_data, dict):
                scripts.append(Script(
                    name=script_data.get("name", ""),
                    path=script_data.get("path", ""),
                    description=script_data.get("description", ""),
                    args=script_data.get("args", []),
                    timeout=script_data.get("timeout", 30),
                    sandbox=script_data.get("sandbox", True),
                ))

        return SkillResources(references=references, scripts=scripts)

    def parse_metadata_only(self, path: Path) -> SkillMetadata:
        """
        Quick parse to extract only metadata.

        This is optimized for skill discovery where only Layer 1
        information is needed.

        Args:
            path: Path to the SKILL.md file

        Returns:
            SkillMetadata object
        """
        skill = self.parse_file(path, metadata_only=True)
        return skill.metadata
