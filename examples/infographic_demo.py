#!/usr/bin/env python3
"""
OpenSkills SDK Demo

演示 Reference 自动发现和 LLM 智能加载功能。
使用 infographic-skills skill 作为测试。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4

    # 或者使用 Azure OpenAI
    AZURE_OPENAI_API_KEY: Azure API Key
    AZURE_OPENAI_ENDPOINT: Azure Endpoint
    AZURE_OPENAI_DEPLOYMENT: 部署名称
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def demo_llm_reference_selection():
    """演示 LLM 智能选择 Reference"""
    from openskills import SkillAgent
    from openskills.llm.openai_compat import OpenAICompatClient

    print("\n" + "=" * 60)
    print("Demo: LLM 智能选择 Skills and Reference")
    print("=" * 60)

    # 获取 API 配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    if not api_key:
        print("\n[跳过] 未设置 OPENAI_API_KEY")
        return

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

    # 创建 Agent
    skills_path = Path(__file__).parent / "infographic-skills"
    agent = SkillAgent(
        skill_paths=[skills_path],
        llm_client=client,
        auto_select_skill=True,  # 自动选择 skill (关键词匹配 + LLM 智能选择)
        on_reference_loaded=on_reference_loaded,
        on_skill_selected=on_skill_selected,
    )
    await agent.initialize()

    print(f"\n[可用 Skills] {agent.available_skills}")

    # 手动选择 skill
    # print("\n[手动选择 Skill: infographic-syntax-creator]")
    # await agent.select_skill("infographic-syntax-creator")

    # 测试查询 - LLM 会智能选择相关的 reference
    user_message = """帮我生成一个饼图代码，数据你随便就行"""

    print(f"\n[用户请求] {user_message.split(chr(10))[0]}")  # 只显示第一行
    print("\n[LLM 正在判断需要加载哪些 references...]")

    response = await agent.chat(user_message)

    print(f"\n[加载的 References] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    print(f"\n[AI 回复]\n{response.content}")


async def main():
    """主函数"""
    print("=" * 60)
    print("OpenSkills SDK Demo")
    print("=" * 60)

    # 显示环境配置
    print(f"\n[环境变量]")
    print(f"  OPENAI_API_KEY: {'已设置' if os.environ.get('OPENAI_API_KEY') else '未设置'}")
    print(f"  OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', '(默认)')}")
    print(f"  OPENAI_MODEL: {os.environ.get('OPENAI_MODEL', '(默认 gpt-4)')}")
    print(f"  AZURE_OPENAI_ENDPOINT: {'已设置' if os.environ.get('AZURE_OPENAI_ENDPOINT') else '未设置'}")



    if os.environ.get("OPENAI_API_KEY"):
        await demo_llm_reference_selection()
    else:
        print("\n[提示] 设置 OPENAI_API_KEY 环境变量以运行 LLM 相关 demo:")
        print("  export OPENAI_API_KEY=your-api-key")

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
