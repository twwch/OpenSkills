# AIO Sandbox 集成指南

[AIO Sandbox](https://sandbox.agent-infra.com/) 是 agent-infra 提供的 All-in-One 沙箱环境，专为 AI Agent 设计。

## 官方资源

| 资源 | 链接 |
|------|------|
| 官网 | https://sandbox.agent-infra.com/ |
| GitHub | https://github.com/agent-infra/sandbox |
| 文档 | https://sandbox.agent-infra.com/guide/start/introduction |
| 示例 | https://sandbox.agent-infra.com/examples/ |

## 安装 SDK

```bash
pip install aio-sandbox
```

## API 信息

| 配置项 | 值 |
|--------|-----|
| API Base URL (本地) | `http://localhost:8080` |
| API 文档 | `http://localhost:8080/v1/docs` |
| SDK 包名 | `aio-sandbox` |

## 启动沙箱服务

### Docker 方式

```bash
docker run -d -p 8080:8080 ghcr.io/agent-infra/sandbox:latest
```

### Docker Compose 方式

```yaml
version: '3.8'
services:
  sandbox:
    image: ghcr.io/agent-infra/sandbox:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## Python SDK 使用

### 基础用法

```python
from aio_sandbox import AioClient

# 初始化客户端
client = AioClient(
    base_url="http://localhost:8080",
    timeout=30.0,
    retries=3,
    retry_delay=1.0,
)

# 执行 Shell 命令
result = await client.shell.exec(command="ls -la")
print(result)

# 执行 Python 代码
result = await client.shell.exec(command="python3 -c \"print('Hello!')\"")
print(result)
```

### 文件操作

```python
# 写入文件
await client.file.write(
    file="/tmp/script.py",
    content="print('Hello from sandbox!')"
)

# 读取文件
content = await client.file.read(file="/tmp/script.py")

# 列出文件
files = await client.file.list(path="/tmp", recursive=True)

# 搜索文件内容
results = await client.file.search(file="/tmp", regex=r"pattern")
```

### Shell 会话管理

```python
# 创建持续会话
result1 = await client.shell.exec(
    command="cd /workspace && export FOO=bar",
    session_id="my-session"
)

# 在同一会话中执行（保持环境变量和目录）
result2 = await client.shell.exec(
    command="echo $FOO && pwd",
    session_id="my-session"
)
```

### 异步执行长任务

```python
# 异步执行（不等待完成）
task = await client.shell.exec(
    command="pip install pandas numpy scipy",
    async_mode=True
)

# 稍后检查状态
status = await client.shell.get_status(task_id=task.id)
```

### Jupyter 代码执行

```python
# 执行 Python 代码（Jupyter 环境）
result = await client.jupyter.execute(
    code="""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
print(df.describe())
""",
    timeout=60
)
```

### Node.js 代码执行

```python
# 执行 JavaScript 代码
result = await client.nodejs.execute(
    code="console.log('Hello from Node.js!')",
    timeout=30
)
```

## 与 OpenSkills 集成

更新 `openskills/sandbox/client.py` 以使用 AIO Sandbox SDK：

```python
from aio_sandbox import AioClient
from dataclasses import dataclass

@dataclass
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    @property
    def output(self) -> str:
        return self.stdout


class AioSandboxClient:
    """AIO Sandbox 客户端封装"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self._client: AioClient | None = None

    async def __aenter__(self):
        self._client = AioClient(base_url=self.base_url)
        return self

    async def __aexit__(self, *args):
        self._client = None

    async def exec_command(self, command: str, **kwargs) -> CommandResult:
        result = await self._client.shell.exec(command=command)
        return CommandResult(
            exit_code=0,  # 解析 result 获取实际状态
            stdout=str(result),
            stderr="",
        )

    async def write_file(self, path: str, content: str) -> None:
        await self._client.file.write(file=path, content=content)

    async def read_file(self, path: str) -> str:
        return await self._client.file.read(file=path)

    async def health_check(self) -> bool:
        try:
            await self._client.shell.exec(command="echo ok")
            return True
        except Exception:
            return False
```

## 在 OpenSkills 中使用

```python
from openskills import create_agent

agent = await create_agent(
    skill_paths=["./skills"],
    use_sandbox=True,
    sandbox_base_url="http://localhost:8080",
    auto_execute_scripts=True,
)

response = await agent.chat("处理这个文档")
```

## 验证服务

```bash
# 健康检查
curl http://localhost:8080/v1/docs

# 测试执行命令
curl -X POST http://localhost:8080/v1/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "python3 --version"}'
```

## 注意事项

- 默认工作目录是 `/home/gem`，不是 `/workspace`
- 脚本会上传到 `/home/gem/scripts/` 目录
- 沙箱用户是 `gem`，有写入 `/home/gem` 和 `/tmp` 的权限

## 功能特性

AIO Sandbox 提供：

- **Shell 执行**: 命令行操作、会话管理
- **文件系统**: 读写、搜索、列表
- **代码执行**: Python (Jupyter)、Node.js
- **浏览器自动化**: 截图、导航、点击
- **MCP 集成**: Model Context Protocol 支持
- **VNC 访问**: 可视化桌面环境
- **VS Code Server**: 在线 IDE

## 参考链接

- [官方网站](https://sandbox.agent-infra.com/)
- [GitHub 仓库](https://github.com/agent-infra/sandbox)
- [使用示例](https://sandbox.agent-infra.com/examples/)
- [API 文档](https://sandbox.agent-infra.com/guide/start/introduction)
