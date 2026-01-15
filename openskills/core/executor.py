"""
Script Executor - Safe execution of skill scripts.

Executes scripts with proper sandboxing and resource limits.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class ScriptExecutionError(Exception):
    """Error during script execution."""
    def __init__(self, message: str, returncode: int = -1, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class ScriptExecutor:
    """
    Safe script executor with sandboxing support.

    Executes scripts (Python, Shell, etc.) with:
    - Timeout limits
    - Output capture
    - Error handling
    - Optional sandboxing

    Note: Full sandboxing requires additional system-level setup.
    The current implementation provides basic process isolation.
    """

    SUPPORTED_EXTENSIONS = {
        ".py": [sys.executable],
        ".sh": ["/bin/bash"],
        ".bash": ["/bin/bash"],
        ".js": ["node"],
        ".ts": ["npx", "ts-node"],
    }

    def __init__(
        self,
        default_timeout: int = 30,
        max_output_size: int = 1024 * 1024,  # 1MB
    ):
        """
        Initialize the executor.

        Args:
            default_timeout: Default timeout in seconds
            max_output_size: Maximum output size in bytes
        """
        self.default_timeout = default_timeout
        self.max_output_size = max_output_size

    async def execute(
        self,
        script_path: Path,
        timeout: int | None = None,
        sandbox: bool = True,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        input_data: str | None = None,
        **kwargs,
    ) -> str:
        """
        Execute a script and return its output.

        Args:
            script_path: Path to the script file
            timeout: Execution timeout in seconds
            sandbox: Whether to apply sandboxing
            args: Command line arguments
            env: Additional environment variables
            input_data: Data to pass to stdin
            **kwargs: Additional arguments passed as JSON to stdin

        Returns:
            The script's stdout output

        Raises:
            ScriptExecutionError: If execution fails
            FileNotFoundError: If script doesn't exist
            ValueError: If script type is not supported
        """
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        ext = script_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported script type: {ext}")

        interpreter = self.SUPPORTED_EXTENSIONS[ext]
        cmd = interpreter + [str(script_path)]

        if args:
            cmd.extend(args)

        # Prepare environment
        script_env = self._prepare_environment(env, sandbox)

        # Prepare input
        stdin_data = input_data
        if kwargs and not stdin_data:
            stdin_data = json.dumps(kwargs)

        timeout = timeout or self.default_timeout

        try:
            result = await asyncio.wait_for(
                self._run_process(cmd, script_env, stdin_data, script_path.parent),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            raise ScriptExecutionError(
                f"Script execution timed out after {timeout} seconds",
                returncode=-1,
            )

    async def _run_process(
        self,
        cmd: list[str],
        env: dict[str, str],
        stdin_data: str | None,
        cwd: Path,
    ) -> str:
        """Run a subprocess asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=cwd,
        )

        stdin_bytes = stdin_data.encode() if stdin_data else None
        stdout, stderr = await process.communicate(input=stdin_bytes)

        if process.returncode != 0:
            raise ScriptExecutionError(
                f"Script failed with exit code {process.returncode}",
                returncode=process.returncode,
                stderr=stderr.decode(errors="replace"),
            )

        output = stdout.decode(errors="replace")

        # Truncate if too large
        if len(output) > self.max_output_size:
            output = output[:self.max_output_size] + "\n... (output truncated)"

        return output

    def _prepare_environment(
        self,
        extra_env: dict[str, str] | None,
        sandbox: bool,
    ) -> dict[str, str]:
        """Prepare the execution environment."""
        # Start with a copy of current environment
        env = os.environ.copy()

        # Add extra environment variables
        if extra_env:
            env.update(extra_env)

        # Apply sandboxing restrictions
        if sandbox:
            # Remove sensitive environment variables
            sensitive_vars = [
                "AWS_SECRET_ACCESS_KEY",
                "AWS_SESSION_TOKEN",
                "GITHUB_TOKEN",
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "DATABASE_URL",
                "DB_PASSWORD",
            ]
            for var in sensitive_vars:
                env.pop(var, None)

            # Mark as sandboxed
            env["OPENSKILLS_SANDBOX"] = "1"

        return env

    def execute_sync(
        self,
        script_path: Path,
        timeout: int | None = None,
        sandbox: bool = True,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        **kwargs,
    ) -> str:
        """
        Synchronous version of execute.

        Useful when async is not available.
        """
        return asyncio.run(
            self.execute(
                script_path=script_path,
                timeout=timeout,
                sandbox=sandbox,
                args=args,
                env=env,
                **kwargs,
            )
        )

    def validate_script(self, script_path: Path) -> tuple[bool, str]:
        """
        Validate a script file.

        Args:
            script_path: Path to the script

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not script_path.exists():
            return False, f"Script not found: {script_path}"

        ext = script_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported script type: {ext}"

        # Check if file is readable
        try:
            script_path.read_text()
        except Exception as e:
            return False, f"Cannot read script: {e}"

        # For Python scripts, try to compile
        if ext == ".py":
            try:
                source = script_path.read_text()
                compile(source, str(script_path), "exec")
            except SyntaxError as e:
                return False, f"Python syntax error: {e}"

        return True, ""
