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
from openskills.models.dependency import SkillDependency
from openskills.models.resource import Reference, Script, SkillResources, ReferenceMode
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
        resources = self._parse_resources(frontmatter, source_path)

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

    def _parse_resources(
        self, frontmatter: dict[str, Any], source_path: Path | None = None
    ) -> SkillResources:
        """Parse resource definitions from frontmatter and auto-discover from directory."""
        references = []
        scripts = []
        declared_paths = set()  # Track paths declared in frontmatter

        # Parse dependency configuration
        dependency = SkillDependency.from_dict(frontmatter.get("dependency"))

        # Parse references from frontmatter
        for ref_data in frontmatter.get("references", []):
            if isinstance(ref_data, dict):
                # Parse mode field
                mode_str = ref_data.get("mode", "implicit")
                try:
                    mode = ReferenceMode(mode_str)
                except ValueError:
                    mode = ReferenceMode.IMPLICIT

                path = ref_data.get("path", "")
                declared_paths.add(path)
                references.append(Reference(
                    path=path,
                    condition=ref_data.get("condition", ""),
                    description=ref_data.get("description", ""),
                    mode=mode,
                ))
            elif isinstance(ref_data, str):
                # Simple path string - default to implicit
                declared_paths.add(ref_data)
                references.append(Reference(path=ref_data))

        # Auto-discover references from references/ directory
        if source_path:
            references_dir = source_path.parent / "references"
            if references_dir.exists() and references_dir.is_dir():
                discovered = self._discover_references(references_dir, declared_paths)
                references.extend(discovered)

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
                    outputs=script_data.get("outputs", []),
                ))

        return SkillResources(references=references, scripts=scripts, dependency=dependency)

    def _discover_references(
        self, references_dir: Path, declared_paths: set[str]
    ) -> list[Reference]:
        """
        Auto-discover reference files from references/ directory.

        Args:
            references_dir: Path to the references directory
            declared_paths: Set of paths already declared in frontmatter

        Returns:
            List of discovered Reference objects (implicit mode)
        """
        discovered = []
        # Supported file extensions for references
        supported_extensions = {".md", ".txt", ".json", ".yaml", ".yml"}

        def scan_dir(dir_path: Path, base_path: Path):
            """Recursively scan directory for reference files."""
            for item in dir_path.iterdir():
                if item.is_file() and item.suffix.lower() in supported_extensions:
                    # Create relative path from skill root
                    rel_path = f"references/{item.relative_to(base_path)}"
                    if rel_path not in declared_paths:
                        discovered.append(Reference(
                            path=rel_path,
                            description=f"Auto-discovered: {item.name}",
                            mode=ReferenceMode.IMPLICIT,
                        ))
                elif item.is_dir():
                    scan_dir(item, base_path)

        scan_dir(references_dir, references_dir)
        return discovered

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
