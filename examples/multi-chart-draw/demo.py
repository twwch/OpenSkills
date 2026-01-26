#!/usr/bin/env python3
"""
Multi Chart Draw Demo - 多类型绘图工具示例（沙箱模式）

演示使用 multi-chart-draw skill 在沙箱环境中生成各种类型的图表：
- Mermaid 流程图、时序图
- ECharts 数据可视化
- Mindmap 思维导图
- DrawIO 架构图
- GeoGebra 数学函数图

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080

前置条件:
    启动沙箱服务:
    docker run --rm -p 8080:8080 ghcr.io/agent-infra/aio-sandbox:latest

使用方法:
    python demo.py                      # 运行交互式 demo
    python demo.py "画一个用户登录流程图"  # 直接执行指定任务
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# 示例任务列表
DEMO_TASKS = [
    {
        "name": "流程图",
        "description": "用户登录流程图 (Mermaid)",
        "prompt": "画一个用户登录流程图，包含：输入账号密码 -> 验证 -> 成功/失败 -> 跳转页面",
    },
    {
        "name": "时序图",
        "description": "API 调用时序图 (Mermaid)",
        "prompt": "画一个前端调用后端 API 的时序图，包含：前端 -> API Gateway -> Auth Service -> Backend -> Database",
    },
    {
        "name": "数据图表",
        "description": "季度销售数据 (ECharts)",
        "prompt": "生成一个柱状图，展示2024年四个季度的销售额：Q1: 120万, Q2: 150万, Q3: 180万, Q4: 200万",
    },
    {
        "name": "思维导图",
        "description": "项目规划思维导图 (Mindmap)",
        "prompt": "画一个「AI 产品开发」的思维导图，包含：需求分析、技术选型、开发实现、测试上线、运营迭代 等主要节点",
    },
    {
        "name": "架构图",
        "description": "微服务架构图 (DrawIO)",
        "prompt": "画一个电商系统的微服务架构图，包含：用户服务、商品服务、订单服务、支付服务、网关、数据库、缓存",
    },
    {
        "name": "数学函数",
        "description": "函数图像 (GeoGebra)",
        "prompt": "画出 y = sin(x) 和 y = cos(x) 两个函数在 -2π 到 2π 范围内的图像",
    },
]


async def run_chart_demo(prompt: str):
    """运行图表生成 demo（沙箱模式）"""
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
    print(f"  任务: {prompt[:50]}...")

    # 回调函数
    def on_reference_loaded(ref_path: str, content: str):
        ref_name = Path(ref_path).name
        print(f"  [加载参考] {ref_name}")

    def on_skill_selected(skill):
        print(f"  [选择 Skill] {skill.name}")

    def on_script_executed(script_name: str, result: str):
        print(f"  [脚本执行] {script_name}")
        # 显示输出文件
        if "output" in result.lower() or ".html" in result or ".png" in result or ".svg" in result:
            lines = result.strip().split("\n")
            for line in lines[-5:]:  # 显示最后几行
                if line.strip():
                    print(f"    {line.strip()}")

    # 创建 Agent（沙箱模式）
    # 沙箱会自动安装依赖：pyecharts, mermaid-cli, markmap-cli
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

    # 发送请求
    print("\n[生成图表中...]")
    response = await agent.chat(prompt)

    print(f"\n[加载的参考文档] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    if response.scripts_executed:
        print(f"[执行的脚本] {response.scripts_executed}")

    return response


async def interactive_demo():
    """交互式 demo"""
    print("\n请选择要演示的图表类型:\n")
    for i, task in enumerate(DEMO_TASKS, 1):
        print(f"  {i}. {task['name']} - {task['description']}")
    print(f"  0. 自定义输入")
    print(f"  q. 退出")

    while True:
        choice = input("\n请输入选项 (1-6/0/q): ").strip()

        if choice.lower() == "q":
            print("退出 demo")
            break

        if choice == "0":
            prompt = input("请输入你的绘图需求: ").strip()
            if not prompt:
                print("输入不能为空")
                continue
        elif choice.isdigit() and 1 <= int(choice) <= len(DEMO_TASKS):
            task = DEMO_TASKS[int(choice) - 1]
            print(f"\n选择: {task['name']}")
            print(f"描述: {task['description']}")
            prompt = task["prompt"]
        else:
            print("无效选项，请重新输入")
            continue

        print("\n" + "=" * 60)
        response = await run_chart_demo(prompt)

        if response:
            print("\n" + "=" * 60)
            print("[AI 回复]")
            print("=" * 60)
            print(response.content)

        print("\n" + "-" * 60)
        continue_choice = input("继续演示其他图表? (y/n): ").strip().lower()
        if continue_choice != "y":
            break


async def check_sandbox(sandbox_url: str) -> bool:
    """检查沙箱服务是否可用"""
    from openskills.sandbox import SandboxClient

    try:
        async with SandboxClient(sandbox_url) as client:
            return await client.health_check()
    except Exception:
        return False


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     Multi Chart Draw - 多类型绘图工具示例 (沙箱模式)     ║
║                                                          ║
║  支持图表类型:                                           ║
║  - Mermaid: 流程图、时序图、甘特图、类图                ║
║  - ECharts: 柱状图、折线图、饼图、散点图                ║
║  - Mindmap: 思维导图                                     ║
║  - DrawIO: 架构图、拓扑图、UML图                        ║
║  - GeoGebra: 数学函数、几何图形                         ║
║                                                          ║
║  [前置条件] 启动沙箱服务:                                ║
║  docker run --rm -p 8080:8080 \                          ║
║      ghcr.io/agent-infra/aio-sandbox:latest              ║
╚══════════════════════════════════════════════════════════╝
""")

    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    # 检查环境
    print("[环境检查]")
    print(f"  OPENAI_API_KEY: {'✓ 已设置' if os.environ.get('OPENAI_API_KEY') else '✗ 未设置'}")
    print(f"  OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', '(默认)')}")
    print(f"  OPENAI_MODEL: {os.environ.get('OPENAI_MODEL', '(默认 gpt-4)')}")
    print(f"  SANDBOX_URL: {sandbox_url}")

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

    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[提示] 设置环境变量以运行 demo:")
        print("  export OPENAI_API_KEY=your-api-key")
        return

    # 检查命令行参数
    if len(sys.argv) > 1:
        # 直接执行指定任务
        prompt = " ".join(sys.argv[1:])
        print(f"\n[直接模式] 执行任务: {prompt}")
        response = await run_chart_demo(prompt)
        if response:
            print("\n" + "=" * 60)
            print("[AI 回复]")
            print("=" * 60)
            print(response.content)
    else:
        # 交互式 demo
        await interactive_demo()

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print(f"输出目录: {Path(__file__).parent / 'charts-output'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
