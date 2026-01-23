"""
Sandbox Client - HTTP API wrapper for AIO Sandbox.

Provides async methods to interact with AIO Sandbox for executing
commands and managing files in an isolated environment.

AIO Sandbox API docs: http://localhost:8080/v1/docs
"""

from dataclasses import dataclass
from typing import Self

import httpx


@dataclass
class CommandResult:
    """Result of a command execution in the sandbox."""

    exit_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Check if the command succeeded."""
        return self.exit_code == 0

    @property
    def output(self) -> str:
        """Get combined stdout output (primary output)."""
        return self.stdout

    def raise_for_status(self) -> None:
        """Raise an exception if the command failed."""
        if not self.success:
            raise SandboxExecutionError(
                f"Command failed with exit code {self.exit_code}",
                exit_code=self.exit_code,
                stderr=self.stderr,
            )


class SandboxExecutionError(Exception):
    """Error during sandbox command execution."""

    def __init__(self, message: str, exit_code: int = -1, stderr: str = ""):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class SandboxConnectionError(Exception):
    """Error connecting to sandbox."""

    pass


class SandboxClient:
    """
    Async HTTP client for AIO Sandbox API.

    Provides methods to execute shell commands and manage files
    in the sandbox environment.

    API Endpoints (AIO Sandbox):
        - /v1/sandbox - Get sandbox info
        - /v1/shell/exec - Execute shell commands
        - /v1/file/read - Read file
        - /v1/file/write - Write file

    Example:
        async with SandboxClient("http://localhost:8080") as client:
            result = await client.exec_command("pip install numpy")
            await client.write_file("/workspace/script.py", "print('hello')")
            result = await client.exec_command("python /workspace/script.py")
    """

    DEFAULT_TIMEOUT = 120.0  # 2 minutes default timeout
    HEALTH_CHECK_TIMEOUT = 5.0

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float | None = None,
    ):
        """
        Initialize the sandbox client.

        Args:
            base_url: Base URL of the AIO Sandbox server
            timeout: Default timeout for operations in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        """Enter async context and create HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context and close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if not self._client:
            raise RuntimeError(
                "SandboxClient must be used as async context manager: "
                "async with SandboxClient() as client: ..."
            )
        return self._client

    async def health_check(self) -> bool:
        """
        Check if the sandbox is healthy and responsive.

        Returns:
            True if sandbox is healthy, False otherwise
        """
        client = self._ensure_client()
        try:
            response = await client.get(
                "/v1/sandbox",
                timeout=self.HEALTH_CHECK_TIMEOUT,
            )
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def exec_command(
        self,
        command: str,
        timeout: float | None = None,
        workdir: str | None = None,
    ) -> CommandResult:
        """
        Execute a shell command in the sandbox.

        Args:
            command: Shell command to execute
            timeout: Optional timeout override in seconds
            workdir: Optional working directory

        Returns:
            CommandResult with exit code, stdout, and stderr

        Raises:
            SandboxConnectionError: If cannot connect to sandbox
            httpx.TimeoutException: If command times out
        """
        client = self._ensure_client()

        payload = {"command": command}
        if workdir:
            payload["workdir"] = workdir

        try:
            response = await client.post(
                "/v1/shell/exec",
                json=payload,
                timeout=timeout or self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # AIO Sandbox 响应格式: {"data": {"output": "..."}, "success": true}
            if "data" in data:
                output = data["data"].get("output", "")
                return CommandResult(
                    exit_code=0 if data.get("success", True) else 1,
                    stdout=output,
                    stderr="",
                )
            else:
                # 兼容其他格式
                return CommandResult(
                    exit_code=data.get("exit_code", 0),
                    stdout=data.get("stdout", data.get("output", "")),
                    stderr=data.get("stderr", ""),
                )
        except httpx.ConnectError as e:
            raise SandboxConnectionError(
                f"Cannot connect to sandbox at {self.base_url}: {e}"
            ) from e

    async def write_file(
        self,
        path: str,
        content: str | bytes,
        mode: str = "0644",
    ) -> None:
        """
        Write a file to the sandbox filesystem.

        Args:
            path: Absolute path in the sandbox
            content: File content (string or bytes)
            mode: File permissions (default: 0644)

        Raises:
            SandboxConnectionError: If cannot connect to sandbox
            SandboxExecutionError: If file write fails
        """
        client = self._ensure_client()

        # Convert bytes to string if needed
        if isinstance(content, bytes):
            content_str = content.decode("utf-8", errors="replace")
        else:
            content_str = content

        payload = {
            "file": path,
            "content": content_str,
        }

        try:
            response = await client.post("/v1/file/write", json=payload)
            response.raise_for_status()
        except httpx.ConnectError as e:
            raise SandboxConnectionError(
                f"Cannot connect to sandbox at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise SandboxExecutionError(
                f"Failed to write file {path}: {e.response.text}",
                exit_code=-1,
                stderr=e.response.text,
            ) from e

    async def read_file(self, path: str) -> str:
        """
        Read a file from the sandbox filesystem.

        Args:
            path: Absolute path in the sandbox

        Returns:
            File content as string

        Raises:
            SandboxConnectionError: If cannot connect to sandbox
            SandboxExecutionError: If file read fails
        """
        client = self._ensure_client()

        payload = {"file": path}

        try:
            response = await client.post("/v1/file/read", json=payload)
            response.raise_for_status()
            data = response.json()
            # AIO Sandbox 响应格式: {"data": {"content": "..."}}
            if "data" in data:
                return data["data"].get("content", "")
            return data.get("content", "")
        except httpx.ConnectError as e:
            raise SandboxConnectionError(
                f"Cannot connect to sandbox at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise SandboxExecutionError(
                f"Failed to read file {path}: {e.response.text}",
                exit_code=-1,
                stderr=e.response.text,
            ) from e

    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in the sandbox.

        Args:
            path: Absolute path in the sandbox

        Returns:
            True if file exists, False otherwise
        """
        result = await self.exec_command(f"test -f {path} && echo 1 || echo 0")
        return result.stdout.strip() == "1"

    async def mkdir(self, path: str, parents: bool = True) -> CommandResult:
        """
        Create a directory in the sandbox.

        Args:
            path: Directory path to create
            parents: Create parent directories if needed

        Returns:
            CommandResult from mkdir command
        """
        flag = "-p" if parents else ""
        return await self.exec_command(f"mkdir {flag} {path}")
