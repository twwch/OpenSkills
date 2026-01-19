"""
File system loader for infographic-skills.

Loads infographic-skills from local file system directories.
"""

from pathlib import Path
from typing import AsyncIterator

from openskills.core.parser import SkillParser
from openskills.core.skill import Skill


class FileLoader:
    """
    Loads infographic-skills from the local file system.

    Scans directories for SKILL.md files and parses them into Skill objects.
    """

    SKILL_FILENAME = "SKILL.md"

    def __init__(self, parser: SkillParser | None = None):
        """
        Initialize the loader.

        Args:
            parser: Skill parser to use
        """
        self.parser = parser or SkillParser()

    async def load_from_directory(
        self,
        directory: Path,
        metadata_only: bool = True,
    ) -> AsyncIterator[Skill]:
        """
        Load infographic-skills from a directory.

        Args:
            directory: Directory to scan
            metadata_only: If True, only load metadata

        Yields:
            Skill objects
        """
        directory = Path(directory).expanduser().resolve()

        if not directory.exists() or not directory.is_dir():
            return

        # Scan subdirectories for SKILL.md
        for path in directory.iterdir():
            if path.is_dir():
                skill_file = path / self.SKILL_FILENAME
                if skill_file.exists():
                    try:
                        skill = self.parser.parse_file(skill_file, metadata_only=metadata_only)
                        yield skill
                    except Exception as e:
                        # Log warning but continue
                        print(f"Warning: Failed to load skill from {skill_file}: {e}")

        # Check directory root for SKILL.md
        root_skill = directory / self.SKILL_FILENAME
        if root_skill.exists():
            try:
                skill = self.parser.parse_file(root_skill, metadata_only=metadata_only)
                yield skill
            except Exception:
                pass

    async def load_skill(
        self,
        path: Path,
        metadata_only: bool = False,
    ) -> Skill:
        """
        Load a single skill.

        Args:
            path: Path to SKILL.md file or directory containing it
            metadata_only: If True, only load metadata

        Returns:
            The loaded Skill

        Raises:
            FileNotFoundError: If skill file not found
        """
        path = Path(path).expanduser().resolve()

        if path.is_dir():
            path = path / self.SKILL_FILENAME

        if not path.exists():
            raise FileNotFoundError(f"Skill not found: {path}")

        return self.parser.parse_file(path, metadata_only=metadata_only)

    def find_skills(self, directory: Path) -> list[Path]:
        """
        Find all SKILL.md files in a directory.

        Args:
            directory: Directory to search

        Returns:
            List of paths to SKILL.md files
        """
        directory = Path(directory).expanduser().resolve()
        skills = []

        if not directory.exists():
            return skills

        # Use glob to find all SKILL.md files
        for skill_file in directory.rglob(self.SKILL_FILENAME):
            skills.append(skill_file)

        return skills
