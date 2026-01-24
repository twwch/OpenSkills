"""
Sandbox Executor - Script execution in AIO Sandbox.

Provides the same interface as ScriptExecutor but runs scripts
in an isolated sandbox environment.
"""

import hashlib
import json
from pathlib import Path
from typing import Self

from openskills.models.dependency import SkillDependency
from openskills.sandbox.client import (
    SandboxClient,
    CommandResult,
    SandboxExecutionError,
)
from openskills.sandbox.logger import SandboxLogger, get_logger


class SandboxExecutor:
    """
    Execute scripts in an AIO Sandbox environment.

    Provides script execution with:
    - Dependency installation (pip packages, system commands)
    - File upload to sandbox
    - Script execution with stdin/args
    - Output capture

    Example:
        async with SandboxExecutor(base_url="http://localhost:8080") as executor:
            await executor.setup_environment(dependency)
            result = await executor.execute(script_path, input_data="...")
    """

    WORKSPACE_DIR = "/home/gem"
    SCRIPTS_DIR = "/home/gem/scripts"

    # Interpreter mapping by file extension
    INTERPRETERS = {
        ".py": "python3",
        ".sh": "bash",
        ".bash": "bash",
        ".js": "node",
    }

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 120.0,
        logger: SandboxLogger | None = None,
        verbose: bool = True,
    ):
        """
        Initialize the sandbox executor.

        Args:
            base_url: Base URL of the AIO Sandbox server
            timeout: Default timeout for operations
            logger: Custom logger instance
            verbose: Whether to print progress logs
        """
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logger or get_logger(enabled=verbose)
        self.verbose = verbose
        self._client: SandboxClient | None = None
        self._environment_ready = False
        self._ready_logged = False

    async def __aenter__(self) -> Self:
        """Enter async context and initialize sandbox client."""
        self.logger.initializing()

        self._client = SandboxClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )
        await self._client.__aenter__()

        # Generate session token for display
        session_id = hashlib.md5(f"{self.base_url}:{id(self)}".encode()).hexdigest()[:16]
        self.logger.authenticating(session_id)

        self.logger.allocating_resources(vcpu=1, memory_mb=2048)
        self.logger.configuring_network()
        self.logger.pulling_environment("python:3.11-slim")
        self.logger.mounting_workspace(self.WORKSPACE_DIR)

        # Initialize workspace
        await self._client.mkdir(self.SCRIPTS_DIR)

        self.logger.starting_agent()
        # Note: ready() is called after setup_environment() completes

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and cleanup."""
        self.logger.cleanup()
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None
        self._environment_ready = False
        self.logger.disconnected()

    def _ensure_client(self) -> SandboxClient:
        """Ensure sandbox client is initialized."""
        if not self._client:
            raise RuntimeError(
                "SandboxExecutor must be used as async context manager: "
                "async with SandboxExecutor() as executor: ..."
            )
        return self._client

    async def health_check(self) -> bool:
        """Check if sandbox is healthy."""
        client = self._ensure_client()
        return await client.health_check()

    async def setup_environment(
        self,
        dependency: SkillDependency,
        upgrade_pip: bool = False,
    ) -> list[CommandResult]:
        """
        Setup the sandbox environment with required dependencies.

        Installs Python packages and executes system commands.

        Args:
            dependency: SkillDependency with packages and commands
            upgrade_pip: Whether to upgrade pip first

        Returns:
            List of CommandResults from setup commands

        Raises:
            SandboxExecutionError: If any setup command fails
        """
        client = self._ensure_client()
        results = []

        # Optionally upgrade pip first
        if upgrade_pip:
            self.logger.progress("升级 pip...")
            result = await client.exec_command("pip install --upgrade pip")
            results.append(result)

        # Install Python packages
        if dependency.python:
            self.logger.installing_dependencies(dependency.python)
            pip_cmd = dependency.get_pip_install_command()
            if pip_cmd:
                result = await client.exec_command(pip_cmd)
                result.raise_for_status()
                results.append(result)
            self.logger.dependency_installed(len(dependency.python))

        # Execute system commands
        for cmd in dependency.get_system_commands():
            self.logger.running_system_command(cmd)
            result = await client.exec_command(cmd, workdir=self.WORKSPACE_DIR)
            result.raise_for_status()
            results.append(result)

        self._environment_ready = True
        self._log_ready_once()
        return results

    def _log_ready_once(self) -> None:
        """Log ready message only once."""
        if not hasattr(self, '_ready_logged') or not self._ready_logged:
            self._ready_logged = True
            self.logger.ready()

    def mark_ready(self) -> None:
        """Mark environment as ready (call when no dependencies to install)."""
        if not self._environment_ready:
            self._environment_ready = True
            self._log_ready_once()

    async def upload_script(
        self,
        local_path: Path,
        remote_name: str | None = None,
    ) -> str:
        """
        Upload a script file to the sandbox.

        Args:
            local_path: Local path to the script file
            remote_name: Optional remote filename (defaults to local name)

        Returns:
            Remote path of the uploaded script

        Raises:
            FileNotFoundError: If local script doesn't exist
        """
        client = self._ensure_client()

        if not local_path.exists():
            raise FileNotFoundError(f"Script not found: {local_path}")

        remote_name = remote_name or local_path.name
        remote_path = f"{self.SCRIPTS_DIR}/{remote_name}"

        content = local_path.read_text(encoding="utf-8")
        await client.write_file(remote_path, content, mode="0755")

        return remote_path

    async def upload_directory(
        self,
        local_dir: Path,
        remote_subdir: str = "",
    ) -> list[str]:
        """
        Upload a directory of files to the sandbox.

        Args:
            local_dir: Local directory path
            remote_subdir: Optional subdirectory in workspace

        Returns:
            List of remote paths of uploaded files
        """
        client = self._ensure_client()

        if not local_dir.exists() or not local_dir.is_dir():
            raise FileNotFoundError(f"Directory not found: {local_dir}")

        remote_base = f"{self.WORKSPACE_DIR}/{remote_subdir}".rstrip("/")
        await client.mkdir(remote_base)

        uploaded = []
        for item in local_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(local_dir)
                remote_path = f"{remote_base}/{rel_path}"

                # Ensure parent directory exists
                remote_parent = str(Path(remote_path).parent)
                await client.mkdir(remote_parent)

                content = item.read_bytes()
                await client.write_file(remote_path, content)
                uploaded.append(remote_path)

        return uploaded

    async def execute(
        self,
        script_path: Path,
        timeout: float | None = None,
        args: list[str] | None = None,
        input_data: str | None = None,
        workdir: str | None = None,
        **kwargs,
    ) -> str:
        """
        Execute a script in the sandbox.

        The script is uploaded to the sandbox and executed.

        Args:
            script_path: Local path to the script file
            timeout: Execution timeout in seconds
            args: Command line arguments
            input_data: Data to pass to stdin
            workdir: Working directory for execution
            **kwargs: Additional arguments passed as JSON to stdin

        Returns:
            Script stdout output

        Raises:
            SandboxExecutionError: If script execution fails
            FileNotFoundError: If script doesn't exist
            ValueError: If script type is not supported
        """
        client = self._ensure_client()
        script_name = script_path.name

        # Validate script extension
        ext = script_path.suffix.lower()
        if ext not in self.INTERPRETERS:
            raise ValueError(f"Unsupported script type: {ext}")

        # Upload script
        self.logger.progress(f"上传脚本: {script_name}")
        remote_script = await self.upload_script(script_path)

        # Build command
        interpreter = self.INTERPRETERS[ext]
        cmd_parts = [interpreter, remote_script]

        if args:
            cmd_parts.extend(args)

        command = " ".join(cmd_parts)

        # Handle input data
        stdin_data = input_data
        if kwargs and not stdin_data:
            stdin_data = json.dumps(kwargs)

        # If we have stdin data, use echo with pipe
        if stdin_data:
            # Escape single quotes in the data
            escaped_data = stdin_data.replace("'", "'\"'\"'")
            command = f"echo '{escaped_data}' | {command}"

        # Execute
        self.logger.executing_script(script_name)
        try:
            result = await client.exec_command(
                command,
                timeout=timeout or self.timeout,
                workdir=workdir or self.WORKSPACE_DIR,
            )
            result.raise_for_status()
            self.logger.script_complete(script_name, success=True)
            return result.output
        except SandboxExecutionError:
            self.logger.script_complete(script_name, success=False)
            raise

    async def execute_command(
        self,
        command: str,
        timeout: float | None = None,
        workdir: str | None = None,
    ) -> CommandResult:
        """
        Execute a raw shell command in the sandbox.

        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds
            workdir: Working directory

        Returns:
            CommandResult with output
        """
        client = self._ensure_client()
        return await client.exec_command(
            command,
            timeout=timeout or self.timeout,
            workdir=workdir or self.WORKSPACE_DIR,
        )
