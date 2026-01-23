"""
Sandbox Logger - Formatted progress output for sandbox operations.

Provides visual feedback during sandbox initialization and execution.
"""

from datetime import datetime
from typing import Callable

from rich.console import Console
from rich.text import Text


class SandboxLogger:
    """
    Logger for sandbox operations with formatted output.

    Provides visual progress indicators during sandbox lifecycle events.
    """

    # Status icons
    ICON_SPINNER = "⠋"
    ICON_SUCCESS = "✓"
    ICON_ERROR = "✗"
    ICON_INFO = "○"
    ICON_ARROW = "→"
    ICON_BOX = "▢"
    ICON_GEAR = "⚙"
    ICON_NETWORK = "🔗"
    ICON_DOWNLOAD = "↓"
    ICON_FOLDER = "📁"
    ICON_ROCKET = "🚀"
    ICON_CHECK = "◉"
    ICON_LOCK = "🔒"

    def __init__(
        self,
        console: Console | None = None,
        enabled: bool = True,
        prefix: str = "",
    ):
        """
        Initialize the sandbox logger.

        Args:
            console: Rich console instance
            enabled: Whether logging is enabled
            prefix: Prefix for all log messages
        """
        self.console = console or Console()
        self.enabled = enabled
        self.prefix = prefix

    def _timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("[%H:%M:%S]")

    def _print(self, icon: str, message: str, style: str = ""):
        """Print a formatted log line."""
        if not self.enabled:
            return

        timestamp = Text(self._timestamp(), style="dim")
        icon_text = Text(f" {icon} ", style=style)
        msg_text = Text(message)

        self.console.print(timestamp, icon_text, msg_text, sep="")

    def info(self, message: str):
        """Print info message."""
        self._print(self.ICON_INFO, message, "blue")

    def success(self, message: str):
        """Print success message."""
        self._print(self.ICON_SUCCESS, message, "green")

    def error(self, message: str):
        """Print error message."""
        self._print(self.ICON_ERROR, message, "red")

    def progress(self, message: str):
        """Print progress message."""
        self._print(self.ICON_ARROW, message, "cyan")

    def initializing(self):
        """Log sandbox initialization start."""
        self._print(self.ICON_GEAR, "正在初始化沙箱环境...", "yellow")

    def authenticating(self, token_preview: str = ""):
        """Log authentication."""
        if token_preview:
            masked = token_preview[:8] + "****" if len(token_preview) > 8 else "****"
            self._print(self.ICON_CHECK, f"认证通过。会话：{masked}", "green")
        else:
            self._print(self.ICON_LOCK, "正在验证连接...", "yellow")

    def allocating_resources(self, vcpu: int = 1, memory_mb: int = 2048, gpu: str = "N/A"):
        """Log resource allocation."""
        self._print(self.ICON_ARROW, "正在分配虚拟资源...", "cyan")
        self._print(
            self.ICON_BOX,
            f"vCPU: {vcpu} 核 | 内存: {memory_mb} MB | GPU: {gpu}",
            "dim"
        )

    def configuring_network(self):
        """Log network configuration."""
        self._print(self.ICON_NETWORK, "正在配置安全网络策略...", "cyan")

    def pulling_environment(self, image: str = "python:3.11-slim"):
        """Log environment pull."""
        self._print(self.ICON_DOWNLOAD, f"正在拉取运行环境: {image}", "cyan")

    def download_progress(self, percent: int = 100):
        """Log download progress."""
        bar_width = 20
        filled = int(bar_width * percent / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        self._print(self.ICON_DOWNLOAD, f"下载中: [{bar}] {percent}%", "dim")

    def mounting_workspace(self, path: str = "/workspace"):
        """Log workspace mounting."""
        self._print(self.ICON_FOLDER, f"正在挂载工作区卷 {path}...", "cyan")

    def starting_agent(self):
        """Log sandbox agent start."""
        self._print(self.ICON_ROCKET, "正在启动沙箱代理...", "cyan")

    def ready(self):
        """Log sandbox ready."""
        self._print(self.ICON_CHECK, "沙箱环境准备就绪。", "green bold")

    def installing_dependencies(self, packages: list[str]):
        """Log dependency installation."""
        if packages:
            pkg_list = ", ".join(packages[:3])
            if len(packages) > 3:
                pkg_list += f" 等 {len(packages)} 个包"
            self._print(self.ICON_DOWNLOAD, f"正在安装依赖: {pkg_list}...", "cyan")

    def dependency_installed(self, count: int):
        """Log dependency installation complete."""
        self._print(self.ICON_SUCCESS, f"已安装 {count} 个依赖包。", "green")

    def executing_script(self, script_name: str):
        """Log script execution."""
        self._print(self.ICON_GEAR, f"正在执行脚本: {script_name}...", "yellow")

    def script_complete(self, script_name: str, success: bool = True):
        """Log script execution complete."""
        if success:
            self._print(self.ICON_SUCCESS, f"脚本 {script_name} 执行完成。", "green")
        else:
            self._print(self.ICON_ERROR, f"脚本 {script_name} 执行失败。", "red")

    def running_system_command(self, command: str):
        """Log system command execution."""
        # Truncate long commands
        if len(command) > 50:
            command = command[:47] + "..."
        self._print(self.ICON_ARROW, f"执行系统命令: {command}", "dim")

    def cleanup(self):
        """Log cleanup."""
        self._print(self.ICON_INFO, "正在清理沙箱环境...", "dim")

    def disconnected(self):
        """Log disconnection."""
        self._print(self.ICON_INFO, "已断开沙箱连接。", "dim")


# Global logger instance
_logger: SandboxLogger | None = None


def get_logger(enabled: bool = True) -> SandboxLogger:
    """Get or create the global sandbox logger."""
    global _logger
    if _logger is None:
        _logger = SandboxLogger(enabled=enabled)
    return _logger


def set_logger(logger: SandboxLogger):
    """Set a custom logger instance."""
    global _logger
    _logger = logger
