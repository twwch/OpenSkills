#!/usr/bin/env python3
"""
OpenSkills Usage Examples

This file demonstrates how to use the OpenSkills SDK for automatic
skill invocation in LLM conversations.

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL，默认 https://api.openai.com/v1
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
"""

import asyncio
import os
from pathlib import Path

# 示例会议记录
SAMPLE_MEETING_TRANSCRIPT = """
会议主题：Q1产品规划讨论
日期：2024年1月15日
参会人：张三（产品经理）、李四（技术负责人）、王五（设计师）、赵六（运营）

张三：大家好，今天主要讨论一下Q1的产品规划。首先我想说一下用户反馈的情况，上个月我们收到了200多条反馈，主要集中在搜索功能和页面加载速度上。

李四：关于页面加载速度，我们已经定位到问题了，主要是图片资源没有做CDN加速，预计两周内可以完成优化。

王五：设计这边准备重新设计一下搜索页面，增加筛选功能，预计需要一周出设计稿。

赵六：运营这边想问一下，新功能上线后能不能配合做一波推广活动？

张三：可以的，我们计划2月底上线新版本，届时可以一起做活动。另外关于预算的问题，这次CDN改造大概需要增加5万的服务器成本，需要和财务确认一下。

李四：技术团队这边没问题，我们会优先处理性能优化的任务。

张三：好的，那我们总结一下今天的会议。CDN优化两周内完成，搜索页面设计一周出稿，2月底上线新版本，同时配合运营活动。预算需要和财务确认。下次会议我们定在下周三，主要跟进进度。

王五：出差的 6000元找哪位审核？

大家有其他问题吗？没有的话今天就到这里。
"""


# Example 1: 完整的会议总结示例
async def example_meeting_summary():
    """完整的会议总结示例，传入实际会议记录。"""
    from openskills import create_agent

    print("=" * 60)
    print("示例：会议总结")
    print("=" * 60)

    # Reference 加载回调
    def on_reference_loaded(ref_path: str, content: str):
        print(f"\n[Reference 加载] {ref_path}")
        print(f"  内容预览: {content[:100]}...")

    # 脚本执行回调
    def on_script_executed(script_name: str, result: str):
        print(f"\n[脚本执行] {script_name}")
        print(f"  结果: {result}")

    # 从环境变量获取配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    if not api_key:
        print("\n[错误] 请设置 OPENAI_API_KEY 环境变量")
        print("  export OPENAI_API_KEY=your-api-key")
        print("  export OPENAI_BASE_URL=https://api.openai.com/v1  # 可选")
        print("  export OPENAI_MODEL=gpt-4  # 可选")
        return

    # 创建 agent
    agent = await create_agent(
        skill_paths=[Path(__file__).parent / "meeting-summary"],
        model=model,
        base_url=base_url,
        api_key=api_key,
        auto_execute_scripts=True,  # 启用脚本自动执行
        on_reference_loaded=on_reference_loaded,  # Reference 加载回调
        on_script_executed=on_script_executed,  # 脚本执行回调
    )

    print(f"\n发现 {len(agent.available_skills)} 个 Skills:")
    for name in agent.available_skills:
        print(f"  - {name}")

    # 构造用户消息：查询 + 会议内容
    user_message = f"""帮我总结会议

以下是会议记录：
{SAMPLE_MEETING_TRANSCRIPT}

然后上传到云端
"""

    print(f"\n用户输入（截取前100字符）:")
    print(f"  {user_message[:100]}...")

    # 调用 agent（需要设置 API key 才能实际调用）
    response = await agent.chat(user_message)
    print(f"\n回复: {response.content}")
    print(f"使用的 Skill: {response.skill_used}")
    if response.references_loaded:
        print(f"加载的 References: {response.references_loaded}")
    if response.scripts_executed:
        print(f"执行的脚本: {response.scripts_executed}")


# Example 2: 手动传入内容的方式
async def example_with_content():
    """手动构造消息的方式。"""
    from openskills import SkillManager
    from openskills.llm import OpenAICompatClient, Message

    print("\n" + "=" * 60)
    print("示例：使用 SkillManager 手动构建 prompt")
    print("=" * 60)

    # 1. 加载 skill
    manager = SkillManager([Path(__file__).parent / "meeting-summary"])
    await manager.discover()

    # 2. 匹配并加载 skill
    matched = manager.match("会议总结")
    if not matched:
        print("没有匹配的 skill")
        return

    skill_name = matched[0].name
    print(f"\n匹配到 Skill: {skill_name}")

    # 3. 加载完整指令
    instruction = await manager.load_instruction(skill_name)
    print(f"指令内容（前200字符）:\n  {instruction.content[:200]}...")

    # 4. 构建 system prompt（skill 指令作为 system）
    system_prompt = instruction.content

    # 5. 用户消息（包含会议内容）
    user_message = f"""请总结以下会议：

{SAMPLE_MEETING_TRANSCRIPT}
"""

    print(f"\n构建的消息:")
    print(f"  System: {system_prompt[:100]}...")
    print(f"  User: {user_message[:100]}...")

    # 6. 调用 LLM（需要 API key）
    # client = OpenAICompatClient(model="gpt-4")
    # response = await client.chat(
    #     messages=[Message.user(user_message)],
    #     system=system_prompt,
    # )
    # print(f"\n回复: {response.content}")


# Example 3: 带图片的会议总结（白板照片等）
async def example_with_image():
    """带图片的会议总结示例。"""
    from openskills import create_agent
    from openskills.llm import image_file, image_url

    print("\n" + "=" * 60)
    print("示例：带图片的会议总结（如白板照片）")
    print("=" * 60)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    agent = await create_agent(
        skill_paths=[Path(__file__).parent / "meeting-summary"],
        model="gpt-4-vision-preview",  # 需要视觉模型
        api_key=api_key,
        base_url=base_url,
    )

    # 方式1：图片 URL
    # response = await agent.chat(
    #     "请根据这张白板照片总结会议要点",
    #     images=[image_url("https://example.com/whiteboard.jpg")]
    # )

    # 方式2：本地图片文件
    # response = await agent.chat(
    #     "总结这张会议纪要的照片",
    #     images=[image_file("./meeting_notes.jpg")]
    # )

    print("\n[示例代码]")
    print("""
    response = await agent.chat(
        "请根据这张白板照片总结会议要点",
        images=[image_url("https://example.com/whiteboard.jpg")]
    )
    """)


# Example 4: 流式输出
async def example_streaming():
    """流式输出示例。"""
    from openskills import create_agent

    print("\n" + "=" * 60)
    print("示例：流式输出")
    print("=" * 60)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")

    agent = await create_agent(
        skill_paths=[Path(__file__).parent / "meeting-summary"],
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

    user_message = f"总结会议:\n{SAMPLE_MEETING_TRANSCRIPT}"

    print("\n[示例代码]")
    print("""
    async for chunk in agent.chat_stream(user_message):
        print(chunk, end="", flush=True)
    """)

    # 实际调用（需要 API key）
    # async for chunk in agent.chat_stream(user_message):
    #     print(chunk, end="", flush=True)


# Example 5: 完整调用流程演示
async def example_full_flow():
    """演示完整的调用流程。"""
    from openskills import SkillManager

    print("\n" + "=" * 60)
    print("完整调用流程演示")
    print("=" * 60)

    manager = SkillManager([Path(__file__).parent / "meeting-summary"])

    # Step 1: 发现 Skills（仅加载元数据 - Layer 1）
    print("\n[Step 1] 发现 Skills（Layer 1 - 元数据）")
    metadata_list = await manager.discover()
    for meta in metadata_list:
        print(f"  Name: {meta.name}")
        print(f"  Description: {meta.description}")
        print(f"  Triggers: {meta.triggers}")

    # Step 2: 匹配用户查询
    print("\n[Step 2] 匹配用户查询")
    query = "帮我总结一下今天的会议"
    matched = manager.match(query)
    print(f"  查询: '{query}'")
    print(f"  匹配: {[m.name for m in matched]}")

    # Step 3: 加载指令（Layer 2）
    if matched:
        print("\n[Step 3] 加载指令（Layer 2）")
        instruction = await manager.load_instruction(matched[0].name)
        print(f"  指令长度: {len(instruction.content)} 字符")

        # Step 4: 检查 References（Layer 3）
        skill = manager.get_skill(matched[0].name)
        print("\n[Step 4] 检查 References（Layer 3）")
        print(f"  可用 References: {len(skill.references)}")
        for ref in skill.references:
            print(f"    - {ref.path}")
            print(f"      条件: {ref.condition}")

        # Step 5: 检查 Scripts（Layer 3）
        print("\n[Step 5] 检查 Scripts（Layer 3）")
        print(f"  可用 Scripts: {len(skill.scripts)}")
        for script in skill.scripts:
            print(f"    - {script.name}: {script.description}")

    print("\n[Step 6] 调用 LLM（需要 API key）")
    print("  构建 system prompt = skill 指令 + 加载的 references")
    print("  用户消息 = 用户查询 + 会议内容")
    print("  调用 LLM API...")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenSkills 使用示例")
    print("=" * 60)

    # 运行演示
    # asyncio.run(example_full_flow())

    # 其他示例（取消注释运行）
    asyncio.run(example_meeting_summary())
    # asyncio.run(example_with_content())
    # asyncio.run(example_with_image())
    # asyncio.run(example_streaming())
