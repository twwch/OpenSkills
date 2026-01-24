#!/usr/bin/env python3
"""
OpenSkills SDK Demo - Prompt Optimizer

演示 Reference 自动发现和 LLM 智能加载功能。
使用 prompt-optimizer skill 作为测试。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080

    # 或者使用 Azure OpenAI
    AZURE_OPENAI_API_KEY: Azure API Key
    AZURE_OPENAI_ENDPOINT: Azure Endpoint
    AZURE_OPENAI_DEPLOYMENT: 部署名称

使用方法:
    # 启动沙箱服务
    docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

    # 运行示例
    python demo.py
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def demo_auto_discovery():
    """演示 Reference 自动发现"""
    from openskills import SkillManager

    print("\n" + "=" * 60)
    print("Demo 1: Reference 自动发现")
    print("=" * 60)

    skills_path = Path(__file__).parent / "prompt-optimizer"
    manager = SkillManager([skills_path])
    await manager.discover()

    skill = manager.get_skill("prompt-optimizer")
    if not skill:
        print("[错误] 未找到 prompt-optimizer skill")
        print(f"  请确保目录存在: {skills_path}")
        return

    print(f"\n[Skill] {skill.name}")
    print(f"[描述] {skill.description[:60]}...")
    print(f"\n[自动发现的 References] 共 {len(skill.references)} 个")

    # 按目录分组显示
    root_refs = [r for r in skill.references if "/" not in r.path.replace("references/", "")]
    framework_refs = [r for r in skill.references if "frameworks/" in r.path]

    print(f"\n  根目录文件: {len(root_refs)} 个")
    for ref in root_refs[:3]:
        print(f"    - {ref.path} (mode={ref.mode.value})")

    print(f"\n  frameworks/ 目录: {len(framework_refs)} 个")
    for ref in framework_refs[:5]:
        print(f"    - {ref.path} (mode={ref.mode.value})")
    if len(framework_refs) > 5:
        print(f"    ... 还有 {len(framework_refs) - 5} 个")


async def demo_llm_reference_selection():
    """演示 LLM 智能选择 Reference（沙箱模式）"""
    from openskills import SkillAgent
    from openskills.llm.openai_compat import OpenAICompatClient

    print("\n" + "=" * 60)
    print("Demo 2: LLM 智能选择 Reference (沙箱模式)")
    print("=" * 60)

    # 获取 API 配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[跳过] 未设置 OPENAI_API_KEY")
        return

    print(f"\n[沙箱地址] {sandbox_url}")

    # 回调：显示加载了哪些 reference
    def on_reference_loaded(ref_path: str, content: str):
        print(f"  [加载] {ref_path} ({len(content)} 字符)")

    def on_skill_selected(skill):
        print(f"  [选择 Skill] {skill.name}")

    # 创建 LLM 客户端
    client = OpenAICompatClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    # 创建 Agent（沙箱模式）
    skills_path = Path(__file__).parent / "prompt-optimizer"
    agent = SkillAgent(
        skill_paths=[skills_path],
        llm_client=client,
        auto_select_skill=False,  # 手动选择 skill
        auto_execute_scripts=True,
        use_sandbox=True,
        sandbox_base_url=sandbox_url,
        on_reference_loaded=on_reference_loaded,
        on_skill_selected=on_skill_selected,
    )
    await agent.initialize()

    print(f"\n[可用 Skills] {agent.available_skills}")

    # 手动选择 skill
    print("\n[手动选择 Skill: prompt-optimizer]")
    await agent.select_skill("prompt-optimizer")

    # 测试查询 - LLM 会智能选择相关的 reference
    user_message = """帮我优化一个营销文案的 prompt。

要求：
1. 直接参考 References 中的框架
2. 直接输出优化后的 prompt，不需要解释为什么选择这个框架
3. 输出格式简洁明了"""

    print(f"\n[用户请求] {user_message.split(chr(10))[0]}")  # 只显示第一行
    print("\n[LLM 正在判断需要加载哪些 references...]")

    response = await agent.chat(user_message)

    print(f"\n[加载的 References] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    print(f"\n[AI 回复]\n{response.content}")


async def demo_different_queries():
    """演示不同查询加载不同 Reference（沙箱模式）"""
    from openskills import SkillAgent
    from openskills.llm.openai_compat import OpenAICompatClient

    print("\n" + "=" * 60)
    print("Demo 3: 不同查询 → 不同 Reference (沙箱模式)")
    print("=" * 60)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[跳过] 未设置 OPENAI_API_KEY")
        return

    skills_path = Path(__file__).parent / "prompt-optimizer"

    queries = [
        "帮我写一个简单的 prompt",
        "我需要一个用于决策分析的 prompt",
        "帮我优化一个教育培训的 prompt",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n--- 查询 {i}: {query} ---")

        loaded_refs = []

        def on_ref_loaded(path: str, content: str):
            loaded_refs.append(path)

        client = OpenAICompatClient(api_key=api_key, base_url=base_url, model=model)
        agent = SkillAgent(
            skill_paths=[skills_path],
            llm_client=client,
            auto_select_skill=False,
            auto_execute_scripts=True,
            use_sandbox=True,
            sandbox_base_url=sandbox_url,
            on_reference_loaded=on_ref_loaded,
        )
        await agent.initialize()
        await agent.select_skill("prompt-optimizer")

        response = await agent.chat(query)
        print(f"[加载的 References]")
        for ref in loaded_refs:
            print(f"  - {ref}")


async def demo_azure_openai():
    """演示 Azure OpenAI 支持（沙箱模式）"""
    from openskills import AzureOpenAIClient, SkillAgent

    print("\n" + "=" * 60)
    print("Demo 4: Azure OpenAI 支持 (沙箱模式)")
    print("=" * 60)

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not endpoint or not api_key:
        print("\n[跳过] 未设置 Azure 环境变量")
        print("  需要设置:")
        print("    AZURE_OPENAI_ENDPOINT")
        print("    AZURE_OPENAI_API_KEY")
        print("    AZURE_OPENAI_DEPLOYMENT")
        return

    # 创建 Azure 客户端
    client = AzureOpenAIClient()
    print(f"\n[Azure 配置]")
    print(f"  Endpoint: {client.endpoint}")
    print(f"  Deployment: {client.deployment}")
    print(f"  API Version: {client.api_version}")
    print(f"[沙箱地址] {sandbox_url}")

    # 使用 Azure 客户端创建 Agent（沙箱模式）
    skills_path = Path(__file__).parent / "prompt-optimizer"
    agent = SkillAgent(
        skill_paths=[skills_path],
        llm_client=client,
        auto_execute_scripts=True,
        use_sandbox=True,
        sandbox_base_url=sandbox_url,
    )
    await agent.initialize()

    print(f"\n[测试请求]")
    response = await agent.chat("写一个简单的 prompt")
    print(f"[回复预览] {response.content[:200]}...")


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║       OpenSkills SDK Demo - Prompt Optimizer             ║
║                                                          ║
║  [前置条件] 启动沙箱服务:                                ║
║  docker run --rm -p 8080:8080 \\                         ║
║      ghcr.io/agent-infra/sandbox:latest                  ║
╚══════════════════════════════════════════════════════════╝
""")

    # 显示环境配置
    print(f"[环境变量]")
    print(f"  OPENAI_API_KEY: {'已设置' if os.environ.get('OPENAI_API_KEY') else '未设置'}")
    print(f"  OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', '(默认)')}")
    print(f"  OPENAI_MODEL: {os.environ.get('OPENAI_MODEL', '(默认 gpt-4)')}")
    print(f"  SANDBOX_URL: {os.environ.get('SANDBOX_URL', '(默认 http://localhost:8080)')}")
    print(f"  AZURE_OPENAI_ENDPOINT: {'已设置' if os.environ.get('AZURE_OPENAI_ENDPOINT') else '未设置'}")

    # 检查 prompt-optimizer skill 是否存在
    skills_path = Path(__file__).parent / "prompt-optimizer"
    if not skills_path.exists():
        print(f"\n[错误] prompt-optimizer skill 不存在: {skills_path}")
        return

    # 运行 demo
    await demo_auto_discovery()

    if os.environ.get("OPENAI_API_KEY"):
        await demo_llm_reference_selection()
        # await demo_different_queries()  # 取消注释测试多个查询
    else:
        print("\n[提示] 设置 OPENAI_API_KEY 环境变量以运行 LLM 相关 demo:")
        print("  export OPENAI_API_KEY=your-api-key")

    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        await demo_azure_openai()

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
