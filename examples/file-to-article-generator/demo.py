#!/usr/bin/env python3
"""
File to Article Generator Demo - 文件解析与文章生成示例

演示使用 file-to-article-generator skill 在沙箱环境中解析 PDF 文件并生成文章。
文件上传和下载由 Agent 自动处理，用户只需指定本地文件路径。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080

使用方法:
    # 启动沙箱服务
    docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

    # 运行示例
    python demo.py [pdf_file_path]
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 默认测试文件
DEFAULT_PDF = "/Users/chenhao/Downloads/11月-CEM-《小野和子：从百万买家对话找到增长方向》.pdf"


async def demo_file_to_article(pdf_path: str):
    """演示文件解析与文章生成（沙箱模式）"""
    from openskills import create_agent

    print("\n" + "=" * 60)
    print("Demo: 文件解析与文章生成 (沙箱模式)")
    print("=" * 60)

    # 获取配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[错误] 请设置 OPENAI_API_KEY 环境变量")
        return

    # 检查 PDF 文件
    if not os.path.exists(pdf_path):
        print(f"\n[错误] PDF 文件不存在: {pdf_path}")
        return

    pdf_name = Path(pdf_path).name
    pdf_size = os.path.getsize(pdf_path) / 1024 / 1024  # MB

    print(f"\n[配置]")
    print(f"  沙箱地址: {sandbox_url}")
    print(f"  模型: {model}")
    print(f"  PDF 文件: {pdf_name}")
    print(f"  文件大小: {pdf_size:.2f} MB")

    # Step 1: 初始化 Agent（自动处理沙箱环境、依赖安装）
    print("\n" + "-" * 40)
    print("[Step 1] 初始化 Agent (沙箱模式)...")
    print("-" * 40)

    # 回调函数
    def on_reference_loaded(ref_path: str, content: str):
        print(f"  [加载 Reference] {ref_path}")

    def on_skill_selected(skill):
        print(f"  [选择 Skill] {skill.name}")

    def on_script_executed(script_name: str, result: str):
        print(f"  [脚本执行完成] {script_name}")
        # 显示脚本结果摘要
        try:
            data = json.loads(result)
            if "text_content" in data:
                print(f"    提取文本: {len(data['text_content'])} 字符")
            if "images" in data:
                print(f"    提取图片: {len(data['images'])} 张")
        except:
            pass

    # 创建 Agent - 自动处理：
    # 1. 沙箱环境初始化
    # 2. 依赖安装
    # 3. 文件上传（脚本执行时自动上传本地文件）
    # 4. 文件下载（脚本执行后自动下载 outputs 目录）
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

    print(f"\n  [可用 Skills] {agent.available_skills}")

    # Step 2: 调用 Agent 处理文件
    # 注意：直接传递本地文件路径，Agent 会自动上传到沙箱
    print("\n" + "-" * 40)
    print("[Step 2] 使用 AI 处理文件并生成文章...")
    print("-" * 40)

    # 构建用户消息 - 使用本地文件路径
    # Agent 内部会自动：
    # 1. 检测到这是本地文件路径
    # 2. 上传到沙箱 /home/gem/uploads/
    # 3. 将路径替换为沙箱路径传给脚本
    user_message = f"""请帮我处理这个 PDF 文件并生成一篇文章。

## 文件信息
- 文件路径: {pdf_path}
- 文件名: {pdf_name}

## 生成要求
- 目标受众: 电商从业者、客户体验管理者
- 文章类型: 行业资讯/客户证言
- 语言风格: 专业、有洞察力
- 重点: 提炼核心观点和可操作的建议

请先使用 [INVOKE:parse_file] 脚本解析文件，然后根据内容生成文章并进行质量评分。
"""

    print("\n  [正在处理...]")
    response = await agent.chat(user_message)

    print(f"\n[加载的 References] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    if response.scripts_executed:
        print(f"[执行的脚本] {response.scripts_executed}")

    # Step 3: 输出结果
    print("\n" + "=" * 60)
    print("[生成的文章]")
    print("=" * 60)
    print(response.content)

    # Step 4: 保存文章
    # 注意：图片等输出文件已由 Agent 自动下载到 skill_dir/output/
    print("\n" + "-" * 40)
    print("[Step 3] 保存结果...")
    print("-" * 40)

    local_output_dir = Path(__file__).parent / "output"
    local_output_dir.mkdir(parents=True, exist_ok=True)

    # 保存文章
    output_file = local_output_dir / "generated_article.md"
    output_file.write_text(response.content, encoding="utf-8")
    print(f"  已保存文章: {output_file}")

    # 检查自动下载的文件
    images_dir = local_output_dir / "images"
    if images_dir.exists():
        images = list(images_dir.glob("*"))
        if images:
            print(f"  已下载图片: {len(images)} 张")
            for img in images:
                print(f"    - {img.name}")


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║    File to Article Generator - 文件解析与文章生成示例    ║
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

    # 获取 PDF 文件路径
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = DEFAULT_PDF
        print(f"\n[提示] 使用默认 PDF 文件: {pdf_path}")
        print(f"       也可以指定其他文件: python demo.py <pdf_path>")

    if os.environ.get("OPENAI_API_KEY"):
        await demo_file_to_article(pdf_path)
    else:
        print("\n[提示] 设置环境变量以运行 demo:")
        print("  export OPENAI_API_KEY=your-api-key")

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
