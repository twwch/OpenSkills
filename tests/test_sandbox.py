"""
Tests for sandbox integration.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from openskills.models.dependency import SkillDependency
from openskills.sandbox.client import (
    SandboxClient,
    CommandResult,
    SandboxExecutionError,
    SandboxConnectionError,
)
from openskills.sandbox.executor import SandboxExecutor
from openskills.sandbox.manager import SandboxManager, SandboxStrategy


class TestSkillDependency:
    """Test SkillDependency model."""

    def test_empty_dependency(self):
        """Test creating empty dependency."""
        dep = SkillDependency()
        assert dep.python == []
        assert dep.system == []
        assert not dep.has_dependencies()
        assert dep.get_pip_install_command() is None

    def test_from_dict_none(self):
        """Test from_dict with None."""
        dep = SkillDependency.from_dict(None)
        assert dep.python == []
        assert dep.system == []

    def test_from_dict_with_python(self):
        """Test from_dict with python dependencies."""
        data = {
            "python": ["numpy>=1.20", "pandas==2.0.0"],
        }
        dep = SkillDependency.from_dict(data)
        assert dep.python == ["numpy>=1.20", "pandas==2.0.0"]
        assert dep.system == []
        assert dep.has_dependencies()

    def test_from_dict_with_system(self):
        """Test from_dict with system commands."""
        data = {
            "system": ["mkdir -p output", "chmod +x scripts/*.sh"],
        }
        dep = SkillDependency.from_dict(data)
        assert dep.python == []
        assert dep.system == ["mkdir -p output", "chmod +x scripts/*.sh"]
        assert dep.has_dependencies()

    def test_from_dict_full(self):
        """Test from_dict with all fields."""
        data = {
            "python": ["PyMuPDF==1.23.8", "python-docx"],
            "system": ["mkdir -p output/images"],
        }
        dep = SkillDependency.from_dict(data)
        assert dep.python == ["PyMuPDF==1.23.8", "python-docx"]
        assert dep.system == ["mkdir -p output/images"]
        assert dep.has_dependencies()

    def test_get_pip_install_command(self):
        """Test generating pip install command."""
        dep = SkillDependency(
            python=["numpy>=1.20", "pandas==2.0.0"]
        )
        cmd = dep.get_pip_install_command()
        assert cmd == 'pip install "numpy>=1.20" "pandas==2.0.0"'

    def test_get_pip_packages(self):
        """Test getting pip packages list."""
        dep = SkillDependency(python=["numpy", "pandas"])
        packages = dep.get_pip_packages()
        assert packages == ["numpy", "pandas"]
        # Ensure it's a copy
        packages.append("scipy")
        assert dep.python == ["numpy", "pandas"]

    def test_get_system_commands(self):
        """Test getting system commands list."""
        dep = SkillDependency(system=["mkdir -p output"])
        commands = dep.get_system_commands()
        assert commands == ["mkdir -p output"]
        # Ensure it's a copy
        commands.append("rm -rf temp")
        assert dep.system == ["mkdir -p output"]


class TestCommandResult:
    """Test CommandResult dataclass."""

    def test_success_result(self):
        """Test successful command result."""
        result = CommandResult(exit_code=0, stdout="output", stderr="")
        assert result.success
        assert result.output == "output"
        result.raise_for_status()  # Should not raise

    def test_failed_result(self):
        """Test failed command result."""
        result = CommandResult(exit_code=1, stdout="", stderr="error")
        assert not result.success
        with pytest.raises(SandboxExecutionError) as exc_info:
            result.raise_for_status()
        assert exc_info.value.exit_code == 1
        assert exc_info.value.stderr == "error"


class TestSandboxClient:
    """Test SandboxClient with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as context manager."""
        async with SandboxClient("http://localhost:8080") as client:
            assert client._client is not None
        assert client._client is None

    @pytest.mark.asyncio
    async def test_ensure_client_raises_without_context(self):
        """Test that methods fail without context manager."""
        client = SandboxClient()
        with pytest.raises(RuntimeError, match="async context manager"):
            client._ensure_client()

    @pytest.mark.asyncio
    async def test_exec_command_success(self):
        """Test successful command execution."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "exit_code": 0,
            "stdout": "hello",
            "stderr": "",
        }

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.aclose = AsyncMock()
            MockClient.return_value = mock_client

            async with SandboxClient() as client:
                result = await client.exec_command("echo hello")

            assert result.success
            assert result.stdout == "hello"

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test health check success."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.aclose = AsyncMock()
            MockClient.return_value = mock_client

            async with SandboxClient() as client:
                healthy = await client.health_check()

            assert healthy

    @pytest.mark.asyncio
    async def test_write_file(self):
        """Test file write."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.aclose = AsyncMock()
            MockClient.return_value = mock_client

            async with SandboxClient() as client:
                await client.write_file("/test.py", "print('hello')")

            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "/files/write"


class TestSandboxExecutor:
    """Test SandboxExecutor."""

    @pytest.mark.asyncio
    async def test_executor_context_manager(self):
        """Test executor as context manager."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"exit_code": 0, "stdout": "", "stderr": ""}
            mock_client.post.return_value = mock_response
            mock_client.aclose = AsyncMock()
            MockClient.return_value = mock_client

            async with SandboxExecutor() as executor:
                assert executor._client is not None
            assert executor._client is None

    @pytest.mark.asyncio
    async def test_setup_environment(self):
        """Test environment setup with dependencies."""
        dep = SkillDependency(
            python=["numpy"],
            system=["mkdir -p output"],
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"exit_code": 0, "stdout": "", "stderr": ""}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.aclose = AsyncMock()
            MockClient.return_value = mock_client

            async with SandboxExecutor() as executor:
                results = await executor.setup_environment(dep)

            # Should have 2 commands: pip install and mkdir
            assert len(results) == 2


class TestSandboxManager:
    """Test SandboxManager."""

    @pytest.mark.asyncio
    async def test_manager_not_active_raises(self):
        """Test that methods fail without context."""
        manager = SandboxManager()
        with pytest.raises(RuntimeError, match="async context manager"):
            await manager.get_executor("test-skill")

    @pytest.mark.asyncio
    async def test_per_skill_strategy_caching(self):
        """Test PER_SKILL strategy caches executors."""
        call_count = 0

        def create_mock_executor(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_executor = AsyncMock()
            mock_executor.__aenter__ = AsyncMock(return_value=mock_executor)
            mock_executor.__aexit__ = AsyncMock()
            mock_executor._id = call_count  # Track which instance
            return mock_executor

        with patch("openskills.sandbox.manager.SandboxExecutor", side_effect=create_mock_executor):
            async with SandboxManager(strategy=SandboxStrategy.PER_SKILL) as manager:
                # First call creates executor
                exec1 = await manager.get_executor("skill-a")
                # Second call for same skill returns cached
                exec2 = await manager.get_executor("skill-a")
                # Third call for different skill creates new
                exec3 = await manager.get_executor("skill-b")

            assert exec1 is exec2  # Same instance for same skill
            assert exec1._id != exec3._id  # Different instance for different skill
            assert call_count == 2  # Only 2 executors created

    @pytest.mark.asyncio
    async def test_persistent_strategy(self):
        """Test PERSISTENT strategy uses single executor."""
        with patch("openskills.sandbox.manager.SandboxExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.__aenter__ = AsyncMock(return_value=mock_executor)
            mock_executor.__aexit__ = AsyncMock()
            MockExecutor.return_value = mock_executor

            async with SandboxManager(strategy=SandboxStrategy.PERSISTENT) as manager:
                exec1 = await manager.get_executor("skill-a")
                exec2 = await manager.get_executor("skill-b")

            assert exec1 is exec2  # Same instance for all skills

    def test_get_cache_info(self):
        """Test cache info reporting."""
        manager = SandboxManager(strategy=SandboxStrategy.PER_SKILL, cache_size=5)
        info = manager.get_cache_info()
        assert info["strategy"] == "per_skill"
        assert info["cache_size"] == 5
        assert info["cached_count"] == 0
