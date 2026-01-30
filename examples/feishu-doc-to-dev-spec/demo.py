#!/usr/bin/env python3
"""
飞书云文档转研发需求文档 Demo（沙箱模式）

读取飞书云文档（产品需求文档），根据用户选择的技术栈，
生成结构化的研发开发需求文档。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080
    FEISHU_APP_ID: 飞书应用 ID
    FEISHU_APP_SECRET: 飞书应用密钥

前置条件:
    1. 启动沙箱服务:
       docker run --rm -p 8080:8080 ghcr.io/agent-infra/aio-sandbox:latest

    2. 配置飞书应用:
       - 访问 https://open.feishu.cn/ 创建应用
       - 获取 App ID 和 App Secret
       - 配置权限: docx:document:readonly, drive:drive:readonly

使用方法:
    python demo.py
    python demo.py "https://xxx.feishu.cn/docx/xxxxx"
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# 预设的技术栈选项
TECH_STACKS = {
    "1": {
        "name": "Python 全栈",
        "language": "Python",
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "cache": "Redis",
        "description": "适合快速开发、AI/ML 相关项目",
    },
    "2": {
        "name": "Java 企业级",
        "language": "Java",
        "framework": "Spring Boot",
        "database": "MySQL",
        "cache": "Redis",
        "description": "适合大型企业应用、复杂业务逻辑",
    },
    "3": {
        "name": "Go 高性能",
        "language": "Go",
        "framework": "Gin",
        "database": "PostgreSQL",
        "cache": "Redis",
        "description": "适合高并发、云原生应用",
    },
    "4": {
        "name": "Node.js 全栈",
        "language": "TypeScript",
        "framework": "NestJS",
        "database": "PostgreSQL",
        "cache": "Redis",
        "description": "适合全栈团队、实时应用",
    },
    "5": {
        "name": "Rust 高性能",
        "language": "Rust",
        "framework": "Axum",
        "database": "PostgreSQL",
        "cache": "Redis",
        "description": "适合对性能和安全性要求极高的场景",
    },
}


async def check_sandbox(sandbox_url: str) -> bool:
    """检查沙箱服务是否可用"""
    from openskills.sandbox import SandboxClient

    try:
        async with SandboxClient(sandbox_url) as client:
            return await client.health_check()
    except Exception:
        return False


async def run_demo(doc_urls: list[str], tech_stack: dict):
    """运行 demo"""
    from openskills import create_agent

    # 获取配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[错误] 请设置 OPENAI_API_KEY 环境变量")
        return None

    print(f"\n[配置]")
    print(f"  沙箱地址: {sandbox_url}")
    print(f"  模型: {model}")
    print(f"  文档数量: {len(doc_urls)}")
    print(f"  技术栈: {tech_stack['name']}")

    # 回调函数
    def on_reference_loaded(ref_path: str, content: str):
        ref_name = Path(ref_path).name
        print(f"  [加载参考] {ref_name}")

    def on_skill_selected(skill):
        print(f"  [选择 Skill] {skill.name}")

    def on_script_executed(script_name: str, result: str):
        print(f"  [脚本执行] {script_name}")
        # 显示执行结果摘要
        try:
            import json
            data = json.loads(result)
            if data.get("success"):
                docs = data.get("documents", [])
                print(f"    成功读取 {len(docs)} 个文档")
                for doc in docs:
                    print(f"    - {doc.get('title', '未知')}")
            else:
                print(f"    错误: {data.get('error', '未知错误')}")
        except:
            pass

    # 创建 Agent（沙箱模式）
    print("\n[初始化 Agent (沙箱模式)...]")
    skills_path = Path(__file__).parent
    agent = await create_agent(
        skill_paths=[skills_path],
        model=model,
        base_url=base_url,
        api_key=api_key,
        auto_execute_scripts=True,
        use_sandbox=True,
        sandbox_base_url=sandbox_url,
        on_reference_loaded=on_reference_loaded,
        on_skill_selected=on_skill_selected,
        on_script_executed=on_script_executed,
    )

    print(f"  [可用 Skills] {agent.available_skills}")

    # 构建用户消息
    doc_urls_str = "\n".join([f"- {url}" for url in doc_urls])
    user_message = f"""请帮我将以下飞书产品需求文档转换为研发开发需求文档。

## 文档链接
{doc_urls_str}

## 技术栈选型
- 开发语言: {tech_stack['language']}
- Web 框架: {tech_stack['framework']}
- 数据库: {tech_stack['database']}
- 缓存: {tech_stack['cache']}

## 要求
1. 首先使用 [INVOKE:fetch_feishu_doc] 脚本读取所有文档内容
2. 分析产品需求，提取功能点和业务规则
3. 根据选定的技术栈，生成包含以下内容的研发需求文档:
   - 项目概述（背景、目标、技术栈）
   - 系统架构设计
   - 数据模型设计（表结构、索引）
   - API 接口设计（RESTful 规范）
   - 核心功能模块详设
   - 非功能需求（性能、安全）
4. 使用 Markdown 格式输出
5. 代码示例使用 {tech_stack['language']} 语言
"""

    print("\n[处理中...]")
    print("-" * 60)

    response = await agent.chat(user_message)

    print("-" * 60)
    print(f"\n[加载的参考文档] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    if response.scripts_executed:
        print(f"[执行的脚本] {response.scripts_executed}")

    return response


def get_doc_urls_input() -> list[str]:
    """获取用户输入的文档链接"""
    print("\n请输入飞书文档链接（每行一个，输入空行结束）:")
    urls = []
    while True:
        url = input().strip()
        if not url:
            break
        if "feishu.cn" in url or "larksuite.com" in url:
            urls.append(url)
        else:
            print(f"  [警告] 跳过非飞书链接: {url}")
    return urls


def select_tech_stack() -> dict:
    """让用户选择技术栈"""
    print("\n请选择技术栈:\n")
    for key, stack in TECH_STACKS.items():
        print(f"  {key}. {stack['name']}")
        print(f"     {stack['description']}")
        print(f"     {stack['language']} + {stack['framework']} + {stack['database']}")
        print()

    while True:
        choice = input("请输入选项 (1-5): ").strip()
        if choice in TECH_STACKS:
            return TECH_STACKS[choice]
        print("无效选项，请重新输入")


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║   飞书云文档转研发需求文档 Demo (沙箱模式)               ║
║                                                          ║
║  功能:                                                   ║
║  - 读取飞书云文档（支持多个链接）                        ║
║  - 解析文本、表格、图片等内容                            ║
║  - 根据技术栈生成研发需求文档                            ║
║                                                          ║
║  [前置条件]                                              ║
║  1. 启动沙箱服务:                                        ║
║     docker run --rm -p 8080:8080 \                       ║
║         ghcr.io/agent-infra/aio-sandbox:latest           ║
║                                                          ║
║  2. 配置飞书应用:                                        ║
║     export FEISHU_APP_ID=your-app-id                     ║
║     export FEISHU_APP_SECRET=your-app-secret             ║
╚══════════════════════════════════════════════════════════╝
""")

    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    # 环境检查
    print("[环境检查]")
    print(f"  OPENAI_API_KEY: {'✓ 已设置' if os.environ.get('OPENAI_API_KEY') else '✗ 未设置'}")
    print(f"  FEISHU_APP_ID: {'✓ 已设置' if os.environ.get('FEISHU_APP_ID') else '✗ 未设置'}")
    print(f"  FEISHU_APP_SECRET: {'✓ 已设置' if os.environ.get('FEISHU_APP_SECRET') else '✗ 未设置'}")
    print(f"  SANDBOX_URL: {sandbox_url}")

    # 检查必要环境变量
    missing_vars = []
    if not os.environ.get("OPENAI_API_KEY"):
        missing_vars.append("OPENAI_API_KEY")
    if not os.environ.get("FEISHU_APP_ID"):
        missing_vars.append("FEISHU_APP_ID")
    if not os.environ.get("FEISHU_APP_SECRET"):
        missing_vars.append("FEISHU_APP_SECRET")

    if missing_vars:
        print(f"\n[错误] 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("\n请设置以下环境变量:")
        for var in missing_vars:
            print(f"  export {var}=your-value")
        return

    # 检查沙箱服务
    print("\n[沙箱服务检查]")
    sandbox_ok = await check_sandbox(sandbox_url)
    if sandbox_ok:
        print(f"  ✓ 沙箱服务正常运行")
    else:
        print(f"  ✗ 沙箱服务未启动")
        print(f"\n[提示] 请先启动沙箱服务:")
        print(f"  docker run --rm -p 8080:8080 ghcr.io/agent-infra/aio-sandbox:latest")
        return

    # 获取文档链接
    if len(sys.argv) > 1:
        # 从命令行参数获取
        doc_urls = [url for url in sys.argv[1:] if "feishu.cn" in url or "larksuite.com" in url]
        if not doc_urls:
            print("\n[错误] 未提供有效的飞书文档链接")
            return
    else:
        # 交互式输入
        doc_urls = get_doc_urls_input()
        if not doc_urls:
            print("\n[错误] 未输入任何文档链接")
            return

    print(f"\n[文档列表]")
    for url in doc_urls:
        print(f"  - {url}")

    # 选择技术栈
    tech_stack = select_tech_stack()
    print(f"\n[选择的技术栈] {tech_stack['name']}")

    # 运行
    print("\n" + "=" * 60)
    response = await run_demo(doc_urls, tech_stack)

    if response:
        print("\n" + "=" * 60)
        print("[生成的研发需求文档]")
        print("=" * 60)
        print(response.content)

        # 保存文档
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "dev-spec.md"
        output_file.write_text(response.content, encoding="utf-8")
        print(f"\n[已保存] {output_file}")

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
