"""
Skill Manager - Core entry point for skill management.

The SkillManager handles skill discovery, registration, and lifecycle
management. It implements the progressive disclosure pattern by
lazy-loading skill content on demand.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator, Self

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

    Manages the lifecycle of infographic-skills including:
    - Discovery: Scanning directories for SKILL.md files
    - Registration: Loading and indexing skill metadata
    - Loading: On-demand loading of instructions and resources
    - Matching: Finding infographic-skills based on user input
    - Execution: Running skill scripts

    Example:
        >>> manager = SkillManager([Path("~/.openskills/infographic-skills")])
        >>> await manager.discover()
        >>> infographic-skills = manager.match("summarize meeting")
        >>> if infographic-skills:
        ...     await manager.load_instruction(infographic-skills[0].name)
    """

    SKILL_FILENAME = "SKILL.md"

    def __init__(
        self,
        skill_paths: list[Path] | None = None,
        parser: SkillParser | None = None,
        matcher: SkillMatcher | None = None,
        executor: ScriptExecutor | None = None,
        use_sandbox: bool = False,
        sandbox_base_url: str = "http://localhost:8080",
    ):
        """
        Initialize the SkillManager.

        Args:
            skill_paths: List of directories to scan for infographic-skills
            parser: Custom skill parser (optional)
            matcher: Custom skill matcher (optional)
            executor: Custom script executor (optional)
            use_sandbox: Whether to execute scripts in AIO Sandbox
            sandbox_base_url: Base URL of the sandbox server
        """
        self.skill_paths = skill_paths or []
        self.parser = parser or SkillParser()
        self.matcher = matcher or SkillMatcher()
        self.executor = executor or ScriptExecutor()
        self.use_sandbox = use_sandbox
        self.sandbox_base_url = sandbox_base_url

        # Internal state
        self._skills: dict[str, Skill] = {}
        self._metadata_index: list[SkillMetadata] = []
        self._discovered = False

        # Sandbox manager (lazy initialized)
        self._sandbox_manager: "SandboxManager | None" = None

    async def __aenter__(self) -> Self:
        """Enter async context (required for sandbox mode)."""
        if self.use_sandbox:
            from openskills.sandbox.manager import SandboxManager, SandboxStrategy

            self._sandbox_manager = SandboxManager(
                base_url=self.sandbox_base_url,
                strategy=SandboxStrategy.PERSISTENT,  # Share executor, install deps on demand
            )
            await self._sandbox_manager.__aenter__()
            # Warmup: initialize sandbox early to show logs during agent setup
            await self._sandbox_manager.warmup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and cleanup sandbox."""
        if self._sandbox_manager:
            await self._sandbox_manager.__aexit__(exc_type, exc_val, exc_tb)
            self._sandbox_manager = None

    @property
    def skills(self) -> dict[str, Skill]:
        """Get all registered infographic-skills."""
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
        Discover and register all infographic-skills from configured paths.

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
        use_sandbox: bool | None = None,
        **kwargs,
    ) -> str:
        """
        Execute a skill script (Layer 3).

        Args:
            skill_name: Name of the skill
            script_name: Name of the script to execute
            use_sandbox: Override sandbox setting for this execution
            **kwargs: Arguments to pass to the script

        Returns:
            The script output

        Raises:
            ValueError: If skill or script not found
            RuntimeError: If sandbox is requested but manager not initialized
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

        # Determine if sandbox should be used
        should_use_sandbox = use_sandbox if use_sandbox is not None else self.use_sandbox

        if should_use_sandbox:
            return await self._execute_in_sandbox(
                skill=skill,
                script_path=resolved_path,
                timeout=script.timeout,
                script=script,
                **kwargs,
            )
        else:
            return await self.executor.execute(
                script_path=resolved_path,
                timeout=script.timeout,
                sandbox=script.sandbox,
                **kwargs,
            )

    async def _execute_in_sandbox(
        self,
        skill: Skill,
        script_path: Path,
        timeout: int,
        script: "Script | None" = None,
        **kwargs,
    ) -> str:
        """Execute a script in the sandbox environment with automatic file sync."""
        if not self._sandbox_manager:
            raise RuntimeError(
                "Sandbox manager not initialized. "
                "Use 'async with SkillManager(...) as manager:' when use_sandbox=True"
            )

        # Get executor with skill's dependencies
        dependency = skill.resources.dependency
        executor = await self._sandbox_manager.get_executor(
            skill_name=skill.name,
            dependency=dependency if dependency.has_dependencies() else None,
        )

        # Upload local files to sandbox and replace paths
        kwargs = await self._upload_local_files(executor, kwargs)

        # Execute the script
        result = await executor.execute(
            script_path=script_path,
            timeout=float(timeout),
            **kwargs,
        )

        # Download output files from sandbox
        if script and script.outputs:
            local_output_dir = skill.source_path.parent / "output" if skill.source_path else None
            if local_output_dir:
                count = await self._download_sandbox_files(executor, script.outputs, local_output_dir)
                if count > 0:
                    from openskills.sandbox.logger import get_logger
                    get_logger().progress(f"共下载 {count} 个文件到 {local_output_dir}")

        return result

    async def _upload_local_files(
        self,
        executor: "SandboxExecutor",
        kwargs: dict,
    ) -> dict:
        """
        Scan kwargs for local file paths and upload to sandbox.

        Returns updated kwargs with sandbox paths.
        """
        import os
        import json

        updated_kwargs = kwargs.copy()

        # Check input_data for file paths
        input_data = kwargs.get("input_data", "")
        if input_data:
            try:
                # Try to parse as JSON
                data = json.loads(input_data) if isinstance(input_data, str) else input_data
                if isinstance(data, dict):
                    updated_data = await self._process_file_paths(executor, data)
                    updated_kwargs["input_data"] = json.dumps(updated_data, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, check if it's a file path directly
                if isinstance(input_data, str) and os.path.isfile(input_data):
                    sandbox_path = await self._upload_single_file(executor, input_data)
                    updated_kwargs["input_data"] = sandbox_path

        return updated_kwargs

    async def _process_file_paths(
        self,
        executor: "SandboxExecutor",
        data: dict,
    ) -> dict:
        """Recursively process dict and upload any file paths found."""
        import os

        result = {}
        for key, value in data.items():
            if isinstance(value, str) and os.path.isfile(value):
                # Upload file and replace with sandbox path
                result[key] = await self._upload_single_file(executor, value)
            elif isinstance(value, dict):
                result[key] = await self._process_file_paths(executor, value)
            elif isinstance(value, list):
                result[key] = [
                    await self._upload_single_file(executor, v) if isinstance(v, str) and os.path.isfile(v) else v
                    for v in value
                ]
            else:
                result[key] = value
        return result

    async def _upload_single_file(
        self,
        executor: "SandboxExecutor",
        local_path: str,
    ) -> str:
        """Upload a single file to sandbox and return sandbox path."""
        from pathlib import Path

        client = executor._ensure_client()
        local_file = Path(local_path)

        # Create uploads directory
        sandbox_uploads = "/home/gem/uploads"
        await client.mkdir(sandbox_uploads)

        # Upload file
        content = local_file.read_bytes()
        sandbox_path = f"{sandbox_uploads}/{local_file.name}"
        await client.upload_file(content, sandbox_path)

        return sandbox_path

    async def _download_sandbox_files(
        self,
        executor: "SandboxExecutor",
        sandbox_paths: list[str],
        local_output_dir: Path,
    ) -> int:
        """
        Download files from sandbox to local directory.

        Returns:
            Number of files downloaded
        """
        from openskills.sandbox.logger import get_logger

        logger = get_logger()
        client = executor._ensure_client()
        local_output_dir.mkdir(parents=True, exist_ok=True)
        downloaded_count = 0

        for sandbox_path in sandbox_paths:
            try:
                # List files in sandbox path
                files = await client.list_files(sandbox_path)
                logger.progress(f"从沙箱同步文件: {sandbox_path} ({len(files)} 项)")

                for file_info in files:

                    if file_info.is_dir:
                        # Recursively download directory
                        sub_count = await self._download_sandbox_files(
                            executor,
                            [file_info.path],
                            local_output_dir / file_info.name,
                        )
                        downloaded_count += sub_count
                    else:
                        # Download file
                        try:
                            content = await client.download_file(file_info.path)

                            # Determine local path (preserve subdirectory structure)
                            rel_path = file_info.path.replace(sandbox_path, "").lstrip("/")
                            local_path = local_output_dir / rel_path if rel_path else local_output_dir / file_info.name
                            local_path.parent.mkdir(parents=True, exist_ok=True)

                            local_path.write_bytes(content)
                            downloaded_count += 1
                            logger.progress(f"  已下载: {file_info.name}")
                        except Exception as download_err:
                            logger.progress(f"  文件下载失败: {file_info.path} - {download_err}")
            except Exception as e:
                logger.progress(f"  列目录失败: {sandbox_path} - {e}")

        return downloaded_count

    def match(self, query: str, limit: int = 5) -> list[Skill]:
        """
        Find infographic-skills matching a user query.

        Args:
            query: User input to match against
            limit: Maximum number of results to return

        Returns:
            List of matching infographic-skills, sorted by relevance
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
