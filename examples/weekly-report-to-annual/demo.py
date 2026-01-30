#!/usr/bin/env python3
"""
Weekly Report to Annual Report Demo - 周报年度复盘示例

演示如何使用 weekly-report-to-annual skill 从飞书邮箱读取周报并生成年度报告。

环境变量:
    OPENAI_API_KEY: OpenAI API Key
    OPENAI_BASE_URL: (可选) API Base URL
    OPENAI_MODEL: (可选) 模型名称，默认 gpt-4
    SANDBOX_URL: (可选) 沙箱地址，默认 http://localhost:8080

    # 飞书邮箱配置
    FEISHU_EMAIL: 飞书邮箱地址
    FEISHU_PASSWORD: 飞书邮箱应用密码（非登录密码）

使用方法:
    # 启动沙箱服务
    docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

    # 运行示例
    python demo.py
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def fetch_emails_from_feishu(email: str, password: str, imap_server: str = "imap.feishu.cn") -> dict:
    """调用 fetch_emails.py 脚本获取邮件"""
    script_path = Path(__file__).parent / "scripts" / "fetch_emails.py"

    input_data = json.dumps({
        "email": email,
        "password": password,
        "imap_server": imap_server,
        "search_keyword": "",
        "max_emails": 100,
        "year": 2025,  # 只获取2025年的周报
        # folders 不指定，使用并发方式搜索所有文件夹（快速且不会超时）
    })

    print(f"\n[调用脚本] {script_path}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=input_data,
        capture_output=True,
        text=True,
    )

    # 打印调试日志（stderr）
    if result.stderr:
        print(result.stderr)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stderr or result.stdout or "Unknown error"}


def save_report_to_file(content: str, output_path: str = "", filename: str = "") -> dict:
    """调用 save_report.py 脚本保存报告"""
    script_path = Path(__file__).parent / "scripts" / "save_report.py"

    input_data = json.dumps({
        "content": content,
        "output_path": output_path,
        "filename": filename,
    })

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=input_data,
        capture_output=True,
        text=True,
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stderr or result.stdout or "Unknown error"}


async def demo_annual_report_generation():
    """演示年度报告生成流程（沙箱模式）"""
    from openskills import SkillAgent
    from openskills.llm.openai_compat import OpenAICompatClient

    print("\n" + "=" * 60)
    print("Demo: 周报汇总生成年度复盘报告 (沙箱模式)")
    print("=" * 60)

    # 获取 API 配置
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-4")
    sandbox_url = os.environ.get("SANDBOX_URL", "http://localhost:8080")

    if not api_key:
        print("\n[跳过] 未设置 OPENAI_API_KEY")
        return

    # 获取飞书邮箱配置
    feishu_email = os.environ.get("FEISHU_EMAIL")
    feishu_password = os.environ.get("FEISHU_PASSWORD")

    print(f"\n[沙箱地址] {sandbox_url}")

    # 回调：显示加载了哪些 reference
    def on_reference_loaded(ref_path: str, content: str):
        print(f"  [加载 Reference] {ref_path} ({len(content)} 字符)")

    def on_skill_selected(skill):
        print(f"  [选择 Skill] {skill.name}")

    # 创建 LLM 客户端
    client = OpenAICompatClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    # 创建 Agent（沙箱模式）
    skills_path = Path(__file__).parent
    agent = SkillAgent(
        skill_paths=[skills_path],
        llm_client=client,
        auto_select_skill=True,
        auto_execute_scripts=True,
        use_sandbox=False,
        sandbox_base_url=sandbox_url,
        on_reference_loaded=on_reference_loaded,
        on_skill_selected=on_skill_selected,
    )
    await agent.initialize()

    print(f"\n[可用 Skills] {agent.available_skills}")

    # Step 1: 获取邮件
    emails_data = None
    if feishu_email and feishu_password:
        print("\n" + "-" * 40)
        print("[Step 1] 从飞书邮箱获取周报邮件...")
        print("-" * 40)

        emails_data = fetch_emails_from_feishu(feishu_email, feishu_password)

        if "error" in emails_data:
            print(f"\n[错误] 获取邮件失败: {emails_data['error']}")
            print("[提示] 将使用模拟数据继续演示")
            emails_data = None
        else:
            # 打印调试信息
            print(f"\n[年份过滤] {emails_data.get('year_filter', 'N/A')}")
            print(f"[可用文件夹] {emails_data.get('available_folders', [])}")
            print(f"[已搜索文件夹] {emails_data.get('searched_folders', [])}")
            if emails_data.get('warnings'):
                print(f"[警告] {emails_data.get('warnings')}")
            print(f"\n[成功] 获取到 {emails_data.get('total_found', 0)} 封周报邮件")

            # 打印邮件内容
            print("\n" + "-" * 40)
            print("[邮件内容预览]")
            print("-" * 40)
            for i, email_item in enumerate(emails_data.get("emails", []), 1):
                print(f"\n--- 邮件 {i} ---")
                print(f"标题: {email_item.get('subject', 'N/A')}")
                print(f"发件人: {email_item.get('sender', 'N/A')}")
                print(f"收件人: {email_item.get('to', 'N/A')}")
                print(f"日期: {email_item.get('date', 'N/A')}")
                print(f"文件夹: {email_item.get('folder', 'N/A')}")
                print(f"内容预览:")
                body = email_item.get('body', '')[:500]  # 只显示前500字符
                print(body)
                if len(email_item.get('body', '')) > 500:
                    print("... (内容已截断)")
            print("-" * 40)

    # 构建用户请求
    if emails_data and "emails" in emails_data and emails_data["emails"]:
        # 使用真实邮件数据
        emails_text = "\n\n".join([
            f"【{e.get('subject', '周报')}】\n日期: {e.get('date', 'N/A')}\n{e.get('body', '')}"
            for e in emails_data["emails"]
        ])
        user_message = f"""帮我生成2025年度复盘报告。

以下是从飞书邮箱获取的周报邮件内容：

--- 周报数据 ---
{emails_text}
--- 结束 ---

请根据以上周报内容和 references 中的年度复盘模板生成完整的年度复盘报告。"""
    else:
        print("\n[提示] 未设置飞书邮箱配置或获取失败，使用模拟数据演示")
        user_message = """帮我生成2025年度复盘报告。

由于没有邮箱配置，请基于以下模拟周报数据，根据年度复盘模板生成报告：

--- 模拟周报数据 ---

【周报｜陈毫｜2025-01-06～2025-01-10】
本周工作：
1. 完成用户认证模块重构，支持 OAuth2.0
2. 修复3个生产环境bug，系统稳定性提升
3. 组织技术分享会，主题：微服务架构实践
下周计划：
1. 开始 API 网关优化

【周报｜陈毫｜2025-03-10～2025-03-14】
本周工作：
1. 完成API网关重构，性能提升40%
2. 培训2名新人，完成入职指导
3. 撰写技术文档《网关设计规范》
遇到问题：
- 高并发场景下内存占用过高，通过对象池优化解决

【周报｜陈毫｜2025-06-16～2025-06-20】
本周工作：
1. 完成微服务拆分第一阶段，拆分出5个独立服务
2. 引入 AI 辅助代码审查工具，效率提升30%
3. 参加行业大会，学习云原生最佳实践
成果亮点：
- 服务拆分后部署效率提升60%

【周报｜陈毫｜2025-10-13～2025-10-17】
本周工作：
1. 完成年度大版本 v3.0 发布，新增10+功能
2. 主导代码review，发现并修复5个潜在问题
3. 完成Q4规划，明确4个重点项目
客户价值：
- 为业务团队提供数据分析平台，日活用户500+

--- 结束 ---

请根据以上周报内容和 references 中的年度复盘模板生成完整的年度复盘报告。"""

    # Step 2: 生成报告
    print("\n" + "-" * 40)
    print("[Step 2] 使用 AI 生成年度复盘报告...")
    print("-" * 40)

    response = await agent.chat(user_message)

    print(f"\n[加载的 References] {response.references_loaded}")
    print(f"[使用的 Skill] {response.skill_used}")
    print(f"\n[生成的报告内容]")
    print("=" * 40)
    print(response.content)
    print("=" * 40)

    # Step 3: 保存报告
    print("\n" + "-" * 40)
    print("[Step 3] 保存报告到本地...")
    print("-" * 40)

    save_result = save_report_to_file(
        content=response.content,
        output_path=str(Path.cwd()),
        filename="2025年度复盘报告.md"
    )

    if "error" in save_result:
        print(f"\n[错误] 保存失败: {save_result['error']}")
    else:
        print(f"\n[保存成功]")
        print(f"  文件路径: {save_result.get('file_path', 'N/A')}")
        print(f"  文件名: {save_result.get('filename', 'N/A')}")
        print(f"  文件大小: {save_result.get('size_bytes', 0)} 字节")
        print(f"  保存时间: {save_result.get('timestamp', 'N/A')}")


async def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║    Weekly Report to Annual Report - 周报年度复盘示例     ║
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
    print(f"  FEISHU_EMAIL: {'已设置' if os.environ.get('FEISHU_EMAIL') else '未设置'}")
    print(f"  FEISHU_PASSWORD: {'已设置' if os.environ.get('FEISHU_PASSWORD') else '未设置'}")

    if os.environ.get("OPENAI_API_KEY"):
        await demo_annual_report_generation()
    else:
        print("\n[提示] 设置以下环境变量以运行 demo:")
        print("  export OPENAI_API_KEY=your-api-key")
        print("  export FEISHU_EMAIL=your-email@feishu.cn")
        print("  export FEISHU_PASSWORD=your-app-password")

    print("\n" + "=" * 60)
    print("Demo 完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
