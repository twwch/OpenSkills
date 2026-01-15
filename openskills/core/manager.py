"""
Skill Manager - Core entry point for skill management.

The SkillManager handles skill discovery, registration, and lifecycle
management. It implements the progressive disclosure pattern by
lazy-loading skill content on demand.
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator

from openskills.core.parser import SkillParser
from openskills.core.skill import Skill
from openskills.core.matcher import SkillMatcher
from openskills.core.executor import ScriptExecutor
from openskills.models.metadata import SkillMetadata
from openskills.models.instruction import SkillInstruction
from openskills.models.resource import Reference


class SkillManager:
    """
    Skill Manager - The core entry point for OpenSkills.

    Manages the lifecycle of skills including:
    - Discovery: Scanning directories for SKILL.md files
    - Registration: Loading and indexing skill metadata
    - Loading: On-demand loading of instructions and resources
    - Matching: Finding skills based on user input
    - Execution: Running skill scripts

    Example:
        >>> manager = SkillManager([Path("~/.openskills/skills")])
        >>> await manager.discover()
        >>> skills = manager.match("summarize meeting")
        >>> if skills:
        ...     await manager.load_instruction(skills[0].name)
    """

    SKILL_FILENAME = "SKILL.md"

    def __init__(
        self,
        skill_paths: list[Path] | None = None,
        parser: SkillParser | None = None,
        matcher: SkillMatcher | None = None,
        executor: ScriptExecutor | None = None,
    ):
        """
        Initialize the SkillManager.

        Args:
            skill_paths: List of directories to scan for skills
            parser: Custom skill parser (optional)
            matcher: Custom skill matcher (optional)
            executor: Custom script executor (optional)
        """
        self.skill_paths = skill_paths or []
        self.parser = parser or SkillParser()
        self.matcher = matcher or SkillMatcher()
        self.executor = executor or ScriptExecutor()

        # Internal state
        self._skills: dict[str, Skill] = {}
        self._metadata_index: list[SkillMetadata] = []
        self._discovered = False

    @property
    def skills(self) -> dict[str, Skill]:
        """Get all registered skills."""
        return self._skills.copy()

    @property
    def metadata_index(self) -> list[SkillMetadata]:
        """Get the metadata index (Layer 1)."""
        return self._metadata_index.copy()

    def add_skill_path(self, path: Path) -> None:
        """Add a skill directory to scan."""
        if path not in self.skill_paths:
            self.skill_paths.append(path)
            self._discovered = False

    async def discover(self, force: bool = False) -> list[SkillMetadata]:
        """
        Discover and register all skills from configured paths.

        This only loads Layer 1 (metadata) for each skill.

        Args:
            force: Force re-discovery even if already done

        Returns:
            List of discovered skill metadata
        """
        if self._discovered and not force:
            return self._metadata_index

        self._skills.clear()
        self._metadata_index.clear()

        for skill_path in self.skill_paths:
            expanded_path = Path(skill_path).expanduser().resolve()
            if not expanded_path.exists():
                continue

            async for skill in self._scan_directory(expanded_path):
                self._register_skill(skill)

        self._discovered = True
        return self._metadata_index

    async def _scan_directory(self, directory: Path) -> AsyncIterator[Skill]:
        """Scan a directory for SKILL.md files."""
        if not directory.is_dir():
            return

        # Look for SKILL.md in subdirectories
        for subdir in directory.iterdir():
            if subdir.is_dir():
                skill_file = subdir / self.SKILL_FILENAME
                if skill_file.exists():
                    try:
                        # Only load metadata for discovery
                        skill = self.parser.parse_file(skill_file, metadata_only=True)
                        yield skill
                    except Exception as e:
                        # Log error but continue scanning
                        print(f"Warning: Failed to parse {skill_file}: {e}")

        # Also check for SKILL.md in the directory itself
        direct_skill = directory / self.SKILL_FILENAME
        if direct_skill.exists():
            try:
                skill = self.parser.parse_file(direct_skill, metadata_only=True)
                yield skill
            except Exception:
                pass

    def _register_skill(self, skill: Skill) -> None:
        """Register a skill in the internal index."""
        self._skills[skill.name] = skill
        self._metadata_index.append(skill.metadata)

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    async def load_instruction(self, skill_name: str) -> SkillInstruction | None:
        """
        Load the instruction content for a skill (Layer 2).

        Args:
            skill_name: Name of the skill

        Returns:
            The skill instruction, or None if not found
        """
        skill = self._skills.get(skill_name)
        if not skill:
            return None

        if skill.is_instruction_loaded:
            return skill.instruction

        # Reload with full content
        if skill.source_path:
            full_skill = self.parser.parse_file(skill.source_path, metadata_only=False)
            skill.instruction = full_skill.instruction

        return skill.instruction

    async def load_reference(
        self,
        skill_name: str,
        ref_path: str,
    ) -> str | None:
        """
        Load a reference file content (Layer 3).

        Args:
            skill_name: Name of the skill
            ref_path: Path of the reference to load

        Returns:
            The reference content, or None if not found
        """
        skill = self._skills.get(skill_name)
        if not skill:
            return None

        ref = skill.resources.get_reference(ref_path)
        if not ref:
            return None

        if ref.is_loaded():
            return ref.content

        # Resolve and load the reference
        resolved_path = skill.resolve_reference_path(ref)
        if resolved_path and resolved_path.exists():
            ref.content = resolved_path.read_text(encoding="utf-8")
            return ref.content

        return None

    async def load_applicable_references(
        self,
        skill_name: str,
        context: str,
    ) -> list[Reference]:
        """
        Load all applicable references for a given context.

        Args:
            skill_name: Name of the skill
            context: The current context to evaluate conditions against

        Returns:
            List of loaded references
        """
        skill = self._skills.get(skill_name)
        if not skill:
            return []

        applicable = skill.resources.get_applicable_references(context)
        for ref in applicable:
            if not ref.is_loaded():
                await self.load_reference(skill_name, ref.path)

        return [ref for ref in applicable if ref.is_loaded()]

    async def execute_script(
        self,
        skill_name: str,
        script_name: str,
        **kwargs,
    ) -> str:
        """
        Execute a skill script (Layer 3).

        Args:
            skill_name: Name of the skill
            script_name: Name of the script to execute
            **kwargs: Arguments to pass to the script

        Returns:
            The script output

        Raises:
            ValueError: If skill or script not found
        """
        skill = self._skills.get(skill_name)
        if not skill:
            raise ValueError(f"Skill not found: {skill_name}")

        script = skill.resources.get_script(script_name)
        if not script:
            raise ValueError(f"Script not found: {script_name}")

        resolved_path = skill.resolve_script_path(script)
        if not resolved_path or not resolved_path.exists():
            raise ValueError(f"Script file not found: {script.path}")

        return await self.executor.execute(
            script_path=resolved_path,
            timeout=script.timeout,
            sandbox=script.sandbox,
            **kwargs,
        )

    def match(self, query: str, limit: int = 5) -> list[Skill]:
        """
        Find skills matching a user query.

        Args:
            query: User input to match against
            limit: Maximum number of results to return

        Returns:
            List of matching skills, sorted by relevance
        """
        matched_metadata = self.matcher.match(query, self._metadata_index, limit=limit)
        return [self._skills[m.name] for m in matched_metadata if m.name in self._skills]

    def get_all_metadata(self) -> list[dict]:
        """
        Get all skill metadata as dictionaries.

        Useful for sending to LLM as a skill catalog.
        """
        return [
            {
                "name": m.name,
                "description": m.description,
                "triggers": m.triggers,
            }
            for m in self._metadata_index
        ]
