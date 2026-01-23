#!/usr/bin/env python3
"""
测试沙箱功能是否正常工作
"""

import asyncio
from pathlib import Path


async def test_sandbox_direct():
    """直接测试沙箱执行"""
    from openskills.sandbox import SandboxExecutor
    from openskills.models.dependency import SkillDependency

    print("=" * 60)
    print("测试沙箱直接执行")
    print("=" * 60)

    # 创建测试依赖
    dependency = SkillDependency(
        python=["requests"],
        system=["mkdir -p /home/gem/test"],
    )

    print("\n[1] 初始化沙箱...")
    async with SandboxExecutor(
        base_url="http://localhost:8080",
        verbose=True,
    ) as executor:
        print("\n[2] 安装依赖...")
        await executor.setup_environment(dependency)

        print("\n[3] 执行 Python 代码...")
        # 创建临时脚本
        test_script = Path("/tmp/test_sandbox_script.py")
        test_script.write_text("""
import json
import sys

data = {"status": "success", "message": "Hello from sandbox!"}
print(json.dumps(data, indent=2))
""")

        result = await executor.execute(test_script)
        print(f"\n[结果]\n{result}")

    print("\n[4] 沙箱已关闭")


async def test_skill_with_sandbox():
    """测试 Skill 在沙箱中执行脚本"""
    from openskills import SkillManager

    print("\n" + "=" * 60)
    print("测试 Skill 在沙箱中执行脚本")
    print("=" * 60)

    # 使用沙箱模式的 SkillManager
    async with SkillManager(
        skill_paths=[Path(__file__).parent / "meeting-summary"],
        use_sandbox=True,
        sandbox_base_url="http://localhost:8080",
    ) as manager:
        await manager.discover()

        print(f"\n发现 Skills: {list(manager.skills.keys())}")

        # 直接执行脚本
        print("\n[执行脚本 upload]...")
        result = await manager.execute_script(
            "meeting-summary",
            "upload",
            input_data='{"content": "测试内容", "filename": "test.md"}',
        )
        print(f"\n[结果]\n{result}")


if __name__ == "__main__":
    import sys

    if "--skill" in sys.argv:
        asyncio.run(test_skill_with_sandbox())
    else:
        asyncio.run(test_sandbox_direct())
