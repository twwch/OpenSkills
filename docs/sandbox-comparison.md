# 沙箱环境对比

本文档对比了几种常见的 Python 脚本沙箱执行环境，帮助选择适合的方案。

## 对比总览

| 特性 | AIO Sandbox | E2B | Modal | Docker 直接运行 | Pyodide (WASM) |
|------|-------------|-----|-------|----------------|----------------|
| 部署方式 | 自托管 Docker | 云服务 | 云服务 | 自托管 | 浏览器/本地 |
| 启动速度 | 快 (~100ms) | 中 (~1s) | 中 (~1-2s) | 慢 (~2-5s) | 快 |
| 网络隔离 | ✓ | ✓ | ✓ | 需配置 | ✓ (无网络) |
| 文件系统 | 隔离 | 隔离 | 隔离 | 可配置 | 虚拟 |
| GPU 支持 | ✗ | ✓ | ✓ | ✓ | ✗ |
| 免费额度 | 无限 (自托管) | 有限 | 有限 | 无限 | 无限 |
| 依赖安装 | pip | pip | pip/conda | pip/apt | 受限 |
| API 接口 | HTTP REST | SDK | SDK | Docker API | JS API |

## 详细对比

### 1. AIO Sandbox

**简介**: 轻量级自托管沙箱，专为 AI Agent 设计。

**优点**:
- 完全自托管，无外部依赖
- 启动速度快
- 简单的 HTTP API
- 免费无限制使用

**缺点**:
- 需要自己维护 Docker 环境
- 不支持 GPU
- 功能相对简单

**启动命令**:
```bash
docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest
```

**API 示例**:
```bash
curl -X POST http://localhost:8080/exec \
  -H "Content-Type: application/json" \
  -d '{"command": "python3 -c \"print(1+1)\""}'
```

---

### 2. E2B (e2b.dev)

**简介**: 云端代码执行沙箱，专为 AI 应用设计。

**优点**:
- 托管服务，无需运维
- 支持多种语言
- 提供 SDK (Python/JS)
- 支持持久化文件系统
- 支持 GPU

**缺点**:
- 需要付费（有免费额度）
- 依赖外部服务
- 网络延迟

**安装**:
```bash
pip install e2b
```

**使用示例**:
```python
from e2b import Sandbox

sandbox = Sandbox()
result = sandbox.run_code("print('Hello from E2B!')")
print(result.stdout)
sandbox.close()
```

**定价**:
- 免费: 100 小时/月
- Pro: $0.10/小时

---

### 3. Modal

**简介**: 云端无服务器计算平台，支持 GPU。

**优点**:
- 强大的 GPU 支持
- 自动扩缩容
- 支持自定义镜像
- Python 原生 SDK

**缺点**:
- 学习曲线较陡
- 冷启动时间较长
- 按使用量付费

**安装**:
```bash
pip install modal
```

**使用示例**:
```python
import modal

app = modal.App("sandbox-demo")

@app.function()
def run_in_sandbox(code: str):
    exec(code)
    return "done"

# 部署并调用
with app.run():
    result = run_in_sandbox.remote("print('Hello from Modal!')")
```

**定价**:
- CPU: $0.024/核/小时
- GPU (A10G): $1.10/小时

---

### 4. Docker 直接运行

**简介**: 使用 Docker 容器作为沙箱环境。

**优点**:
- 完全控制
- 支持任意配置
- 无外部依赖
- 支持 GPU (nvidia-docker)

**缺点**:
- 启动速度较慢
- 需要自己管理生命周期
- 需要编写更多代码

**使用示例**:
```python
import docker

client = docker.from_env()
result = client.containers.run(
    "python:3.11-slim",
    command='python -c "print(1+1)"',
    remove=True,
)
print(result.decode())
```

---

### 5. Pyodide (WebAssembly)

**简介**: 在 WebAssembly 中运行的 Python 解释器。

**优点**:
- 完全隔离
- 可在浏览器运行
- 无服务器成本
- 启动快

**缺点**:
- 不支持所有 Python 库
- 无网络访问
- 性能受限
- 文件系统是虚拟的

**使用示例** (JavaScript):
```javascript
const pyodide = await loadPyodide();
await pyodide.runPythonAsync(`
    print("Hello from Pyodide!")
`);
```

---

## 选型建议

### 场景 1: 本地开发/测试
**推荐**: AIO Sandbox 或 Docker 直接运行
- 完全本地，无网络依赖
- 免费无限制

### 场景 2: 生产环境 AI Agent
**推荐**: E2B 或 AIO Sandbox (自托管)
- E2B: 快速集成，托管服务
- AIO Sandbox: 完全控制，无外部依赖

### 场景 3: 需要 GPU 计算
**推荐**: Modal 或 E2B
- 两者都支持 GPU
- Modal 更适合批量计算
- E2B 更适合交互式执行

### 场景 4: 浏览器端执行
**推荐**: Pyodide
- 唯一的浏览器端方案
- 完全隔离，安全性高

### 场景 5: 高安全性要求
**推荐**: AIO Sandbox + 网络隔离
- 自托管，数据不出内网
- 可配置严格的网络策略

---

## OpenSkills 集成状态

| 沙箱 | 集成状态 | 模块 |
|------|----------|------|
| AIO Sandbox | ✓ 已集成 | `openskills.sandbox` |
| E2B | 计划中 | - |
| Modal | 计划中 | - |
| Docker | 计划中 | - |
| Pyodide | 不计划 | - |

## 参考链接

- [AIO Sandbox](https://github.com/anthropics/aio-sandbox)
- [E2B](https://e2b.dev/)
- [Modal](https://modal.com/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Pyodide](https://pyodide.org/)
