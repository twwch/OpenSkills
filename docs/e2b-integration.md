# E2B 沙箱集成指南

[E2B](https://e2b.dev) 是专为 AI Agent 设计的云端代码执行沙箱服务。

## 获取 API Key

1. 访问 **https://e2b.dev**
2. 点击 **Sign Up** 注册账号（支持 GitHub 登录）
3. 登录后进入 **Dashboard**
4. 在 **API Keys** 页面创建新的 API Key
5. 复制保存 API Key

## API 信息

| 配置项 | 值 |
|--------|-----|
| API Base URL | `https://api.e2b.dev` |
| SDK | `pip install e2b-code-interpreter` |
| 文档 | https://e2b.dev/docs |

## 免费额度

- **免费版**: 100 小时/月 沙箱运行时间
- **Pro 版**: $0.10/小时

## 安装 SDK

```bash
pip install e2b-code-interpreter
```

## 基本使用

```python
import os
from e2b_code_interpreter import Sandbox

# 设置 API Key
os.environ["E2B_API_KEY"] = "your-api-key"

# 创建沙箱
sandbox = Sandbox()

# 执行代码
execution = sandbox.run_code("print('Hello from E2B!')")
print(execution.text)

# 安装依赖
sandbox.run_code("!pip install pandas numpy")

# 执行更多代码
result = sandbox.run_code("""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(df.describe())
""")
print(result.text)

# 关闭沙箱
sandbox.kill()
```

## 文件操作

```python
from e2b_code_interpreter import Sandbox

sandbox = Sandbox()

# 写入文件
sandbox.files.write("/home/user/script.py", "print('hello')")

# 读取文件
content = sandbox.files.read("/home/user/script.py")

# 执行文件
result = sandbox.run_code("exec(open('/home/user/script.py').read())")

sandbox.kill()
```

## 与 OpenSkills 集成

### 方案 1：创建 E2B 适配器

创建 `openskills/sandbox/e2b_client.py`:

```python
"""E2B Sandbox Client - 适配 E2B API 到 OpenSkills 接口"""

import os
from dataclasses import dataclass
from typing import Self

from e2b_code_interpreter import Sandbox


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


class E2BSandboxClient:
    """E2B 沙箱客户端，兼容 OpenSkills SandboxClient 接口"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("E2B_API_KEY")
        self._sandbox: Sandbox | None = None

    async def __aenter__(self) -> Self:
        self._sandbox = Sandbox(api_key=self.api_key)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._sandbox:
            self._sandbox.kill()
            self._sandbox = None

    async def health_check(self) -> bool:
        return self._sandbox is not None

    async def exec_command(self, command: str, **kwargs) -> CommandResult:
        if not self._sandbox:
            raise RuntimeError("Sandbox not initialized")

        # E2B 使用 run_code 执行 shell 命令
        if command.startswith("pip "):
            command = f"!{command}"

        try:
            result = self._sandbox.run_code(command)
            return CommandResult(
                exit_code=0 if not result.error else 1,
                stdout=result.text or "",
                stderr=result.error or "",
            )
        except Exception as e:
            return CommandResult(exit_code=1, stdout="", stderr=str(e))

    async def write_file(self, path: str, content: str, **kwargs) -> None:
        if not self._sandbox:
            raise RuntimeError("Sandbox not initialized")
        self._sandbox.files.write(path, content)

    async def read_file(self, path: str) -> str:
        if not self._sandbox:
            raise RuntimeError("Sandbox not initialized")
        return self._sandbox.files.read(path)
```

### 方案 2：直接在代码中使用

```python
import os
from e2b_code_interpreter import Sandbox

# 设置 API Key
os.environ["E2B_API_KEY"] = "your-api-key"

# 执行 Skill 脚本
def execute_in_e2b(script_content: str, input_data: str = "") -> str:
    sandbox = Sandbox()
    try:
        # 安装依赖
        sandbox.run_code("!pip install python-docx openpyxl")

        # 写入脚本
        sandbox.files.write("/home/user/script.py", script_content)

        # 写入输入数据
        if input_data:
            sandbox.files.write("/home/user/input.json", input_data)

        # 执行
        result = sandbox.run_code("""
import sys
sys.stdin = open('/home/user/input.json') if os.path.exists('/home/user/input.json') else sys.stdin
exec(open('/home/user/script.py').read())
""")
        return result.text or ""
    finally:
        sandbox.kill()
```

## 环境变量配置

```bash
# 必需
export E2B_API_KEY=e2b_xxxxxxxxxxxxxxxx

# 可选（如果使用自托管）
export E2B_API_URL=https://api.e2b.dev
```

## 注意事项

1. **超时**: 默认沙箱 5 分钟后自动关闭，可通过 `timeout` 参数调整
2. **并发**: 免费版限制同时运行的沙箱数量
3. **网络**: 沙箱可以访问外网，注意安全
4. **存储**: 沙箱关闭后数据不保留

## 参考链接

- 官网: https://e2b.dev
- 文档: https://e2b.dev/docs
- GitHub: https://github.com/e2b-dev/e2b
- SDK 文档: https://e2b.dev/docs/code-interpreter/installation
- 定价: https://e2b.dev/pricing
