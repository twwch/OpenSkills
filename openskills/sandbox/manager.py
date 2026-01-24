"""
Sandbox Manager - Lifecycle management for sandbox instances.

Manages sandbox executor instances with different strategies
for reuse and cleanup.
"""

import asyncio
from collections import OrderedDict
from enum import Enum
from typing import Self

from openskills.models.dependency import SkillDependency
from openskills.sandbox.executor import SandboxExecutor


class SandboxStrategy(str, Enum):
    """Strategy for sandbox instance management."""

    # Create new sandbox for each script execution
    PER_EXECUTION = "per_execution"

    # Reuse sandbox per skill (cache by skill name)
    PER_SKILL = "per_skill"

    # Single persistent sandbox for all executions
    PERSISTENT = "persistent"


class SandboxManager:
    """
    Manage sandbox executor instances.

    Provides lifecycle management with different strategies:
    - PER_EXECUTION: Fresh sandbox for each execution (safest)
    - PER_SKILL: Cached sandbox per skill (balanced)
    - PERSISTENT: Single sandbox for all (fastest)

    Example:
        manager = SandboxManager(strategy=SandboxStrategy.PER_SKILL)
        async with manager:
            executor = await manager.get_executor("my-skill", dependency)
            result = await executor.execute(script_path)
    """

    DEFAULT_CACHE_SIZE = 10

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        strategy: SandboxStrategy = SandboxStrategy.PER_SKILL,
        cache_size: int = DEFAULT_CACHE_SIZE,
        timeout: float = 120.0,
        verbose: bool = True,
    ):
        """
        Initialize the sandbox manager.

        Args:
            base_url: Base URL of the AIO Sandbox server
            strategy: Sandbox reuse strategy
            cache_size: Maximum cached executors (for PER_SKILL)
            timeout: Default timeout for operations
            verbose: Whether to print progress logs
        """
        self.base_url = base_url
        self.strategy = strategy
        self.cache_size = cache_size
        self.timeout = timeout
        self.verbose = verbose

        # LRU cache for skill executors
        self._cache: OrderedDict[str, SandboxExecutor] = OrderedDict()
        self._persistent_executor: SandboxExecutor | None = None
        self._installed_deps: set[str] = set()  # Track installed dependencies
        self._lock = asyncio.Lock()
        self._active = False

    async def __aenter__(self) -> Self:
        """Enter async context."""
        self._active = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and cleanup all executors."""
        await self.cleanup()
        self._active = False

    async def get_executor(
        self,
        skill_name: str,
        dependency: SkillDependency | None = None,
    ) -> SandboxExecutor:
        """
        Get a sandbox executor for a skill.

        Based on the strategy, may return a cached executor or create new one.

        Args:
            skill_name: Name of the skill
            dependency: Optional dependency to setup

        Returns:
            SandboxExecutor ready for use

        Raises:
            RuntimeError: If manager is not active
        """
        if not self._active:
            raise RuntimeError(
                "SandboxManager must be used as async context manager: "
                "async with SandboxManager() as manager: ..."
            )

        async with self._lock:
            if self.strategy == SandboxStrategy.PER_EXECUTION:
                return await self._create_executor(dependency)

            elif self.strategy == SandboxStrategy.PERSISTENT:
                if not self._persistent_executor:
                    self._persistent_executor = await self._create_executor(dependency)
                    # Track installed deps
                    if dependency and dependency.has_dependencies():
                        self._installed_deps.add(skill_name)
                elif dependency and dependency.has_dependencies():
                    # Install new dependencies if not already installed for this skill
                    if skill_name not in self._installed_deps:
                        await self._persistent_executor.setup_environment(dependency)
                        self._installed_deps.add(skill_name)
                return self._persistent_executor

            else:  # PER_SKILL
                if skill_name in self._cache:
                    # Move to end (LRU)
                    self._cache.move_to_end(skill_name)
                    return self._cache[skill_name]

                # Create new executor
                executor = await self._create_executor(dependency)
                self._cache[skill_name] = executor

                # Evict oldest if cache is full
                while len(self._cache) > self.cache_size:
                    oldest_name, oldest_executor = self._cache.popitem(last=False)
                    await self._cleanup_executor(oldest_executor)

                return executor

    async def _create_executor(
        self,
        dependency: SkillDependency | None = None,
    ) -> SandboxExecutor:
        """Create and initialize a new executor."""
        executor = SandboxExecutor(
            base_url=self.base_url,
            timeout=self.timeout,
            verbose=self.verbose,
        )
        await executor.__aenter__()

        # Setup environment if dependency provided
        if dependency and dependency.has_dependencies():
            await executor.setup_environment(dependency)
        else:
            # No dependencies, mark as ready immediately
            executor.mark_ready()

        return executor

    async def _cleanup_executor(self, executor: SandboxExecutor) -> None:
        """Cleanup a single executor."""
        try:
            await executor.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors

    async def cleanup(self) -> None:
        """Cleanup all cached executors."""
        async with self._lock:
            # Cleanup cached executors
            for executor in self._cache.values():
                await self._cleanup_executor(executor)
            self._cache.clear()

            # Cleanup persistent executor
            if self._persistent_executor:
                await self._cleanup_executor(self._persistent_executor)
                self._persistent_executor = None

            # Reset installed deps tracking
            self._installed_deps.clear()

    async def warmup(self, skill_name: str = "_default") -> SandboxExecutor:
        """
        Warmup the sandbox by creating an executor early.

        This displays initialization logs during agent setup rather than
        waiting until script execution.

        Args:
            skill_name: Name to cache the executor under

        Returns:
            The initialized executor
        """
        return await self.get_executor(skill_name, dependency=None)

    async def health_check(self) -> bool:
        """
        Check if the sandbox server is healthy.

        Creates a temporary executor for the check.

        Returns:
            True if sandbox is healthy
        """
        executor = SandboxExecutor(
            base_url=self.base_url,
            timeout=5.0,
            verbose=False,  # Silent health check
        )
        try:
            async with executor:
                return await executor.health_check()
        except Exception:
            return False

    def get_cache_info(self) -> dict:
        """Get information about cached executors."""
        return {
            "strategy": self.strategy.value,
            "cache_size": self.cache_size,
            "cached_skills": list(self._cache.keys()),
            "cached_count": len(self._cache),
            "has_persistent": self._persistent_executor is not None,
        }
