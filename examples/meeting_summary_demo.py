#!/usr/bin/env python3
"""
Meeting Summary Demo - 会议总结示例

演示使用 OpenSkills SDK 在沙箱环境中执行会议总结技能。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL，默认 https://api.openai.com/v1
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080

使用方法:
    # 启动沙箱服务
    docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

    # 运行示例
    python meeting_summary_demo.py
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


async def run_meeting_summary():
    """运行会议总结示例（沙箱模式）"""
    from openskills import create_agent

    print("=" * 60)
    print("Meeting Summary Demo - 会议总结示例")
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
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[错误] 请设置 OPENAI_API_KEY 环境变量")
        print("  export OPENAI_API_KEY=your-api-key")
        print("  export OPENAI_BASE_URL=https://api.openai.com/v1  # 可选")
        print("  export OPENAI_MODEL=gpt-4  # 可选")
        print("  export SANDBOX_URL=http://localhost:8080  # 沙箱地址")
        return

    print("\n[配置]")
    print(f"  模型: {model}")
    print(f"  沙箱: {sandbox_url}")

    # 创建 agent（沙箱模式）
    agent = await create_agent(
        skill_paths=[Path(__file__).parent / "meeting-summary"],
        model=model,
        base_url=base_url,
        api_key=api_key,
        auto_execute_scripts=True,
        use_sandbox=True,  # 启用沙箱
        sandbox_base_url=sandbox_url,
        on_reference_loaded=on_reference_loaded,
        on_script_executed=on_script_executed,
    )

    print(f"\n[Skills] 发现 {len(agent.available_skills)} 个技能:")
    for name in agent.available_skills:
        print(f"  - {name}")

    # 构造用户消息
    user_message = f"""帮我总结会议

以下是会议记录：
{SAMPLE_MEETING_TRANSCRIPT}

然后上传到云端
"""

    print(f"\n[输入] 用户消息（截取前100字符）:")
    print(f"  {user_message[:100]}...")

    # 调用 agent
    print("\n[执行中]")
    response = await agent.chat(user_message)

    print(f"\n[输出]")
    print(f"回复: {response.content}")
    print(f"\n使用的 Skill: {response.skill_used}")
    if response.references_loaded:
        print(f"加载的 References: {response.references_loaded}")
    if response.scripts_executed:
        print(f"执行的脚本: {response.scripts_executed}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║           Meeting Summary Demo - 会议总结示例            ║
║                                                          ║
║  [前置条件] 启动沙箱服务:                                ║
║  docker run --rm -p 8080:8080 \\                         ║
║      ghcr.io/agent-infra/sandbox:latest                  ║
╚══════════════════════════════════════════════════════════╝
""")
    asyncio.run(run_meeting_summary())
