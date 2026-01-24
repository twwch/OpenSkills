"""
Sandbox Client - HTTP API wrapper for AIO Sandbox.

Provides async methods to interact with AIO Sandbox for executing
commands and managing files in an isolated environment.

AIO Sandbox API docs: http://localhost:8080/v1/docs
"""

from dataclasses import dataclass, field
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


@dataclass
class CodeResult:
    """Result of code execution."""

    language: str
    status: str
    stdout: str | None
    stderr: str | None
    outputs: list[dict] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status == "ok"

    @property
    def output(self) -> str:
        return self.stdout or ""


@dataclass
class FileInfo:
    """File or directory information."""

    name: str
    path: str
    is_dir: bool
    size: int = 0
    modified: str = ""

    @property
    def is_file(self) -> bool:
        """Check if this is a file (not a directory)."""
        return not self.is_dir


@dataclass
class SessionInfo:
    """Shell session information."""

    session_id: str
    working_dir: str
    status: str
    created_at: str
    last_used_at: str
    current_command: str = ""


@dataclass
class SandboxInfo:
    """Sandbox environment information."""

    version: str
    home_dir: str
    os: str
    user: str
    python_versions: list[str] = field(default_factory=list)
    nodejs_versions: list[str] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)


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

    Provides comprehensive methods to interact with the sandbox:
    - Shell command execution and session management
    - File operations (read, write, list, search, upload, download)
    - Code execution (Python, JavaScript)
    - Package management (pip, npm)
    - Browser automation
    - Jupyter notebook integration
    - Terminal WebSocket access

    API Endpoints (AIO Sandbox):
        - /v1/sandbox - Get sandbox info
        - /v1/shell/* - Shell operations
        - /v1/file/* - File operations
        - /v1/code/* - Code execution
        - /v1/browser/* - Browser automation
        - /v1/jupyter/* - Jupyter integration
        - /terminal - WebSocket terminal

    Example:
        async with SandboxClient("http://localhost:8080") as client:
            # Execute commands
            result = await client.exec_command("pip install numpy")

            # Execute code directly
            result = await client.execute_code("print(1+1)", "python")

            # File operations
            await client.write_file("/home/gem/script.py", "print('hello')")
            files = await client.list_files("/home/gem")

            # Get terminal URL for UI
            url = await client.get_terminal_url()
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

    # ============================================================
    # Sandbox Info API
    # ============================================================

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

    async def get_info(self) -> SandboxInfo:
        """
        Get sandbox environment information.

        Returns:
            SandboxInfo with version, OS, available tools, etc.
        """
        client = self._ensure_client()
        response = await client.get("/v1/sandbox")
        response.raise_for_status()
        data = response.json()

        detail = data.get("data", {}) if isinstance(data.get("data"), dict) else {}
        if not detail:
            detail = data.get("detail", {})

        system = detail.get("system", {})
        runtime = detail.get("runtime", {})

        python_versions = [
            p.get("ver", "") for p in runtime.get("python", [])
        ]
        nodejs_versions = [
            n.get("ver", "") for n in runtime.get("nodejs", [])
        ]
        tools = []
        for cat in detail.get("utils", []):
            for tool in cat.get("tools", []):
                tools.append(tool.get("name", ""))

        return SandboxInfo(
            version=data.get("version", ""),
            home_dir=data.get("home_dir", "/home/gem"),
            os=system.get("os", ""),
            user=system.get("user", "gem"),
            python_versions=python_versions,
            nodejs_versions=nodejs_versions,
            available_tools=tools,
        )

    # ============================================================
    # Shell API
    # ============================================================

    async def exec_command(
        self,
        command: str,
        timeout: float | None = None,
        workdir: str | None = None,
        session_id: str | None = None,
    ) -> CommandResult:
        """
        Execute a shell command in the sandbox.

        Args:
            command: Shell command to execute
            timeout: Optional timeout override in seconds
            workdir: Optional working directory
            session_id: Optional session ID for persistent sessions

        Returns:
            CommandResult with exit code, stdout, and stderr

        Raises:
            SandboxConnectionError: If cannot connect to sandbox
            httpx.TimeoutException: If command times out
        """
        client = self._ensure_client()

        payload: dict = {"command": command}
        if workdir:
            payload["workdir"] = workdir
        if session_id:
            payload["session_id"] = session_id

        try:
            response = await client.post(
                "/v1/shell/exec",
                json=payload,
                timeout=timeout or self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # AIO Sandbox 响应格式: {"data": {"output": "...", "exit_code": 0}, "success": true}
            if "data" in data:
                result_data = data["data"]
                output = result_data.get("output", "")
                exit_code = result_data.get("exit_code", 0 if data.get("success", True) else 1)
                return CommandResult(
                    exit_code=exit_code,
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

    async def get_sessions(self) -> list[SessionInfo]:
        """
        Get all active shell sessions.

        Returns:
            List of SessionInfo objects
        """
        client = self._ensure_client()
        response = await client.get("/v1/shell/sessions")
        response.raise_for_status()
        data = response.json()

        sessions = []
        sessions_data = data.get("data", {}).get("sessions", {})
        for session_id, info in sessions_data.items():
            sessions.append(SessionInfo(
                session_id=session_id,
                working_dir=info.get("working_dir", ""),
                status=info.get("status", ""),
                created_at=info.get("created_at", ""),
                last_used_at=info.get("last_used_at", ""),
                current_command=info.get("current_command", ""),
            ))
        return sessions

    async def create_session(self, workdir: str | None = None) -> str:
        """
        Create a new shell session.

        Args:
            workdir: Optional working directory

        Returns:
            Session ID
        """
        client = self._ensure_client()
        payload = {}
        if workdir:
            payload["workdir"] = workdir

        response = await client.post("/v1/shell/sessions/create", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("session_id", "")

    async def get_session(self, session_id: str) -> SessionInfo | None:
        """
        Get information about a specific session.

        Args:
            session_id: Session ID

        Returns:
            SessionInfo or None if not found
        """
        client = self._ensure_client()
        response = await client.get(f"/v1/shell/sessions/{session_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        info = data.get("data", {})
        return SessionInfo(
            session_id=session_id,
            working_dir=info.get("working_dir", ""),
            status=info.get("status", ""),
            created_at=info.get("created_at", ""),
            last_used_at=info.get("last_used_at", ""),
            current_command=info.get("current_command", ""),
        )

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a shell session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted successfully
        """
        client = self._ensure_client()
        response = await client.delete(f"/v1/shell/sessions/{session_id}")
        return response.status_code == 200

    async def get_terminal_url(self, session_id: str | None = None) -> str:
        """
        Get WebSocket terminal URL for UI integration.

        This URL can be used to connect to an interactive terminal
        via WebSocket for real-time terminal access.

        Args:
            session_id: Optional session ID to reuse

        Returns:
            Terminal WebSocket URL (e.g., "http://localhost:8080/terminal?session_id=xxx")
        """
        client = self._ensure_client()
        params = {}
        if session_id:
            params["session_id"] = session_id

        response = await client.get("/v1/shell/terminal-url", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", "")

    async def shell_write(self, session_id: str, input_text: str) -> bool:
        """
        Write input to a shell session.

        Args:
            session_id: Session ID
            input_text: Text to write to shell

        Returns:
            True if successful
        """
        client = self._ensure_client()
        payload = {
            "session_id": session_id,
            "input": input_text,
        }
        response = await client.post("/v1/shell/write", json=payload)
        return response.status_code == 200

    async def shell_view(self, session_id: str) -> str:
        """
        View current output of a shell session.

        Args:
            session_id: Session ID

        Returns:
            Current shell output
        """
        client = self._ensure_client()
        response = await client.get(f"/v1/shell/view", params={"session_id": session_id})
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("output", "")

    async def shell_kill(self, session_id: str) -> bool:
        """
        Kill the current process in a shell session.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        client = self._ensure_client()
        response = await client.post("/v1/shell/kill", json={"session_id": session_id})
        return response.status_code == 200

    # ============================================================
    # File API
    # ============================================================

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

    async def list_files(self, path: str = "/home/gem") -> list[FileInfo]:
        """
        List files in a directory.

        Args:
            path: Directory path to list

        Returns:
            List of FileInfo objects
        """
        client = self._ensure_client()
        response = await client.post("/v1/file/list", json={"path": path})
        response.raise_for_status()
        data = response.json()

        files = []
        raw_files = data.get("data", {}).get("files", [])

        for f in raw_files:
            # Handle various API field name conventions
            is_dir = (
                f.get("is_directory") or  # AIO Sandbox format
                f.get("is_dir") or
                f.get("isDir") or
                f.get("IsDir") or
                f.get("type") == "directory" or
                f.get("mode", "").startswith("d")  # Unix-style mode
            )
            files.append(FileInfo(
                name=f.get("name") or f.get("Name", ""),
                path=f.get("path") or f.get("Path", ""),
                is_dir=bool(is_dir),
                size=f.get("size") or f.get("Size") or 0,
                modified=f.get("modified") or f.get("modified_time") or f.get("modTime") or "",
            ))
        return files

    async def find_files(
        self,
        pattern: str,
        path: str = "/home/gem",
        max_results: int = 100,
    ) -> list[str]:
        """
        Find files matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "*.py")
            path: Directory to search in
            max_results: Maximum number of results

        Returns:
            List of matching file paths
        """
        client = self._ensure_client()
        payload = {
            "path": path,
            "pattern": pattern,
            "max_results": max_results,
        }
        response = await client.post("/v1/file/find", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("files", [])

    async def search_files(
        self,
        query: str,
        path: str = "/home/gem",
        file_pattern: str = "*",
        max_results: int = 100,
    ) -> list[dict]:
        """
        Search for text in files.

        Args:
            query: Search query (regex supported)
            path: Directory to search in
            file_pattern: File pattern to include
            max_results: Maximum number of results

        Returns:
            List of matches with file path, line number, and content
        """
        client = self._ensure_client()
        payload = {
            "path": path,
            "query": query,
            "file_pattern": file_pattern,
            "max_results": max_results,
        }
        response = await client.post("/v1/file/search", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("matches", [])

    async def upload_file(
        self,
        local_content: bytes,
        remote_path: str,
        filename: str | None = None,
    ) -> str:
        """
        Upload a file to the sandbox.

        Args:
            local_content: File content as bytes
            remote_path: Full remote file path (e.g., "/home/gem/workspace/file.pdf")
                        or directory path if filename is provided
            filename: Optional filename (if remote_path is a directory)

        Returns:
            Full path of uploaded file
        """
        client = self._ensure_client()

        # 如果提供了 filename，则 remote_path 是目录
        if filename:
            full_path = f"{remote_path.rstrip('/')}/{filename}"
        else:
            full_path = remote_path
            filename = full_path.split("/")[-1]

        files = {"file": (filename, local_content)}
        data = {"path": full_path}
        response = await client.post("/v1/file/upload", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("data", {}).get("file_path", full_path)

    async def download_file(self, path: str) -> bytes:
        """
        Download a file from the sandbox.

        Args:
            path: File path in sandbox

        Returns:
            File content as bytes
        """
        client = self._ensure_client()
        response = await client.get("/v1/file/download", params={"path": path})
        response.raise_for_status()
        return response.content

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

    # ============================================================
    # Code Execution API
    # ============================================================

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: float | None = None,
    ) -> CodeResult:
        """
        Execute code directly without creating a file.

        Supports Python and JavaScript.

        Args:
            code: Code to execute
            language: "python" or "javascript"/"nodejs"
            timeout: Optional timeout

        Returns:
            CodeResult with output
        """
        client = self._ensure_client()
        payload = {
            "code": code,
            "language": language,
        }
        response = await client.post(
            "/v1/code/execute",
            json=payload,
            timeout=timeout or self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        result_data = data.get("data", {})
        return CodeResult(
            language=result_data.get("language", language),
            status=result_data.get("status", "ok" if data.get("success") else "error"),
            stdout=result_data.get("stdout"),
            stderr=result_data.get("stderr"),
            outputs=result_data.get("outputs", []),
        )

    async def get_code_info(self) -> dict:
        """
        Get code execution runtime information.

        Returns:
            Dict with available languages and versions
        """
        client = self._ensure_client()
        response = await client.get("/v1/code/info")
        response.raise_for_status()
        return response.json().get("data", {})

    # ============================================================
    # Package Management API
    # ============================================================

    async def install_python_packages(
        self,
        packages: list[str],
        upgrade: bool = False,
    ) -> CommandResult:
        """
        Install Python packages using pip.

        Args:
            packages: List of package names (e.g., ["numpy", "pandas>=2.0"])
            upgrade: Whether to upgrade existing packages

        Returns:
            CommandResult from pip install
        """
        # 使用 pip install 命令安装
        upgrade_flag = "--upgrade" if upgrade else ""
        packages_str = " ".join(f'"{p}"' for p in packages)
        cmd = f"pip install {upgrade_flag} {packages_str}".strip()
        return await self.exec_command(cmd, timeout=300)

    async def install_nodejs_packages(
        self,
        packages: list[str],
        global_install: bool = False,
    ) -> CommandResult:
        """
        Install Node.js packages using npm.

        Args:
            packages: List of package names
            global_install: Whether to install globally

        Returns:
            CommandResult from npm install
        """
        # 使用 npm install 命令安装
        global_flag = "-g" if global_install else ""
        packages_str = " ".join(packages)
        cmd = f"npm install {global_flag} {packages_str}".strip()
        return await self.exec_command(cmd, timeout=300)

    # ============================================================
    # Browser API
    # ============================================================

    async def browser_screenshot(self, url: str | None = None) -> bytes:
        """
        Take a screenshot of the browser.

        Args:
            url: Optional URL to navigate to first

        Returns:
            Screenshot as PNG bytes
        """
        client = self._ensure_client()
        params = {}
        if url:
            params["url"] = url
        response = await client.get("/v1/browser/screenshot", params=params)
        response.raise_for_status()
        return response.content

    async def browser_action(
        self,
        action: str,
        params: dict | None = None,
    ) -> dict:
        """
        Perform a browser action.

        Actions include: navigate, click, type, scroll, etc.

        Args:
            action: Action name
            params: Action parameters

        Returns:
            Action result
        """
        client = self._ensure_client()
        payload = {
            "action": action,
            "params": params or {},
        }
        response = await client.post("/v1/browser/actions", json=payload)
        response.raise_for_status()
        return response.json().get("data", {})

    async def browser_info(self) -> dict:
        """
        Get browser information.

        Returns:
            Browser state and configuration
        """
        client = self._ensure_client()
        response = await client.get("/v1/browser/info")
        response.raise_for_status()
        return response.json().get("data", {})

    # ============================================================
    # Jupyter API
    # ============================================================

    async def jupyter_execute(
        self,
        code: str,
        session_id: str | None = None,
    ) -> dict:
        """
        Execute code in a Jupyter kernel.

        Args:
            code: Code to execute
            session_id: Optional session ID

        Returns:
            Execution result with outputs
        """
        client = self._ensure_client()
        payload = {"code": code}
        if session_id:
            payload["session_id"] = session_id

        response = await client.post("/v1/jupyter/execute", json=payload)
        response.raise_for_status()
        return response.json().get("data", {})

    async def jupyter_sessions(self) -> list[dict]:
        """
        Get active Jupyter sessions.

        Returns:
            List of session information
        """
        client = self._ensure_client()
        response = await client.get("/v1/jupyter/sessions")
        response.raise_for_status()
        return response.json().get("data", {}).get("sessions", [])

    async def jupyter_info(self) -> dict:
        """
        Get Jupyter kernel information.

        Returns:
            Jupyter configuration and status
        """
        client = self._ensure_client()
        response = await client.get("/v1/jupyter/info")
        response.raise_for_status()
        return response.json().get("data", {})

    # ============================================================
    # Utility API
    # ============================================================

    async def convert_to_markdown(
        self,
        content: str | bytes,
        source_type: str = "html",
    ) -> str:
        """
        Convert content to Markdown.

        Args:
            content: Content to convert
            source_type: Source format (html, pdf, etc.)

        Returns:
            Markdown text
        """
        client = self._ensure_client()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")

        payload = {
            "content": content,
            "source_type": source_type,
        }
        response = await client.post("/v1/util/convert_to_markdown", json=payload)
        response.raise_for_status()
        return response.json().get("data", {}).get("markdown", "")
