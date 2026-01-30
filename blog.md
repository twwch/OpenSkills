# 打破黑盒！OpenSkills：让 AI Agent 的技能调用不再神秘

> 当我们在使用 AI Agent 时，它是如何调用各种技能的？这个过程对开发者来说往往是个黑盒。今天，我要分享一个开源项目，它让你能在自己的代码中完全掌控 AI 技能的调用过程。

## 一、从一个真实痛点说起

**张三的年底困扰：**

张三是一名软件工程师，每周都要写周报发到飞书邮箱。到了年底，HR要求每个人写一份年度复盘报告。

张三打开邮箱一看：50+ 封周报邮件！要完成年度复盘，他需要：
1. 手动打开每封邮件
2. 复制粘贴到文档
3. 人工归纳总结（项目成果、技术成长、团队贡献）
4. 反复修改调整格式

**光是整理邮件就要花半天时间，累死人不说，还容易遗漏关键信息。**

张三想：能不能让 AI 帮我做？答案是可以，但问题来了：

**这个"技能"在 Claude、ChatGPT 等 AI 助手中如何实现？我能在自己的项目中复用吗？能自定义吗？**

大多数情况下，答案是：**不行**。技能调用是个黑盒，你只能通过聊天界面使用，无法集成到自己的代码中，更无法针对自己的实际场景（比如张三的飞书邮箱、公司的复盘模板）优化。

## 二、OpenSkills：打破黑盒的开源方案

OpenSkills 是一个开源的 AI Agent 技能框架，它的核心理念很简单：

> **让 AI 技能的定义、发现、匹配和执行过程完全透明，并且可以在你自己的代码中调用。**

**项目地址：** https://github.com/twwch/OpenSkills
**开源协议：** Apache 2.0
**技术栈：** Python 3.10+

### 核心特性

1. **技能定义简单** - 一个 `SKILL.md` 文件就是一个技能
2. **渐进式加载** - 三层架构，从元数据到完整指令，按需加载
3. **智能匹配** - LLM 自动判断何时加载参考资料
4. **沙箱执行** - 脚本在隔离容器中安全运行
5. **完全可控** - 你的代码，你的数据，你说了算

## 三、架构亮点：三层渐进式信息披露

这是 OpenSkills 最巧妙的设计。传统的技能系统要么一次性加载所有内容（浪费资源），要么只加载元数据（缺少上下文）。

OpenSkills 采用**三层架构**：

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Metadata（始终加载）                  │
│  • 技能名称、描述、版本                          │
│  • 触发词、标签                                  │
│  • 用途：快速发现和匹配                          │
├─────────────────────────────────────────────────┤
│  Layer 2: Instruction（按需加载）               │
│  • SKILL.md 正文内容                            │
│  • 详细的系统提示词                              │
│  • 用途：实际执行技能指令                        │
├─────────────────────────────────────────────────┤
│  Layer 3: Resources（条件加载）                 │
│  • References（参考资料）                        │
│  • Scripts（可执行脚本）                         │
│  • 用途：提供上下文和执行能力                    │
└─────────────────────────────────────────────────┘
```

**为什么这样设计？**

假设你有 100 个技能，每个技能都有大量参考文档。传统方式需要：
- 加载所有元数据（100个）
- 加载所有指令（100个）
- 加载所有参考资料（可能几百个文档）

而 OpenSkills 的流程是：
1. 只加载 100 个元数据（快速发现）
2. 匹配到 1 个相关技能后，只加载这 1 个的指令
3. 让 LLM 判断是否需要加载参考资料

**效率提升 10 倍以上！**

## 四、实战案例：从周报到年度复盘

让我用一个真实案例展示 OpenSkills 的威力。

### 场景描述

张三是一名软件工程师，在飞书邮箱里收到了一整年的周报邮件（50+ 封），现在年底要写年度复盘报告。

**用 OpenSkills 只需几行代码：**

```python
from openskills import create_agent

agent = await create_agent(
    skill_paths=["./examples/weekly-report-to-annual"],
    api_key="your-api-key",
    model="gpt-4",
)

response = await agent.chat("""
帮我生成张三的 2025 年度复盘报告。
从飞书邮箱获取所有标题包含"周报｜张三"的邮件。
""")

print(response.content)  # 完整的年度复盘报告
# 自动保存为：张三-2025年度复盘报告.md
```

**就这么简单！** 不需要手动复制粘贴，不需要人工归纳，AI 自动完成：
- 从邮箱获取张三的所有周报
- 提取关键信息（项目成果、技术成长、团队贡献）
- 按照模板生成结构化报告
- 保存到本地文件：`张三-2025年度复盘报告.md`

### 技能定义：`SKILL.md`

一个技能就是一个 Markdown 文件，包含 YAML 前置物和正文指令：

```yaml
---
name: weekly-report-to-annual
description: 从周报邮件生成年度复盘报告
version: 1.0.0

triggers:
  - 年度总结
  - 周报汇总
  - annual review

scripts:
  - name: fetch_emails
    path: scripts/fetch_emails.py
    description: 从 IMAP 服务器获取邮件

  - name: save_report
    path: scripts/save_report.py
    description: 保存报告到本地

references:
  - path: references/annual-review-template.md
    mode: always
    description: 年度复盘报告模板
---

# 周报年度复盘技能

你是一个专业的年度复盘助手。根据用户提供的周报内容，生成结构化的年度复盘报告。

## 执行步骤

1. 如果用户提供了邮箱配置，调用 [INVOKE:fetch_emails] 获取周报
2. 分析周报内容，提取关键信息：
   - 重要项目和成果
   - 技能成长和学习
   - 遇到的挑战和解决方案
   - 团队协作和贡献
3. 按照 references 中的模板生成报告
4. 调用 [INVOKE:save_report] 保存到本地
```

**关键点：**
- `triggers` - 定义触发词，用户说"年度总结"就会匹配到这个技能
- `scripts` - 可执行的 Python 脚本，通过 `[INVOKE:script_name]` 调用
- `references` - 参考资料，这里是年度复盘模板

### 脚本执行：`fetch_emails.py`

技能可以调用 Python 脚本来完成复杂任务。脚本会从飞书邮箱获取张三的所有周报，比如：

**张三的周报示例：**

```
【周报｜张三｜2025-01-08～2025-01-12】
本周工作：
1. 完成用户认证模块重构，支持 OAuth2.0 和微信登录
2. 修复3个生产环境bug，系统稳定性提升
3. 组织技术分享会，主题：微服务架构实践

【周报｜张三｜2025-06-23～2025-06-27】
本周工作：
1. 完成订单系统微服务拆分，拆分出用户、订单、支付、库存4个服务
2. 引入 AI 辅助代码审查工具 GitHub Copilot，开发效率提升30%
3. 参加 KubeCon 技术大会，学习云原生和 K8s 最佳实践
成果亮点：
- 服务拆分后部署时间从30分钟降到5分钟，效率提升6倍

【周报｜张三｜2025-12-02～2025-12-06】
本周工作：
1. 完成年度大版本 v3.0 发布，新增AI智能推荐、实时消息推送等10+功能
2. 主导架构评审，识别并解决5个潜在的性能瓶颈
3. 完成Q4季度总结和2026年度规划
成果亮点：
- 系统日活用户从5万增长到20万，增长4倍
```

**获取邮件的脚本实现：**

```python
#!/usr/bin/env python3
"""从飞书邮箱获取周报邮件"""

import imaplib
import json
import sys
from concurrent.futures import ThreadPoolExecutor

def fetch_emails_from_feishu(email, password, keyword="周报｜张三", year=2025):
    """通过 IMAP 获取邮件"""
    mail = imaplib.IMAP4_SSL("imap.feishu.cn", 993)
    mail.login(email, password)

    # 获取所有文件夹
    folders = list_folders(mail)

    # 并发搜索所有文件夹
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(search_folder, mail, folder, keyword, year): folder
            for folder in folders
        }

        all_emails = []
        for future in as_completed(futures):
            emails = future.result()
            all_emails.extend(emails)

    return all_emails

# 从 stdin 读取参数（JSON）
input_data = json.loads(sys.stdin.read())
emails = fetch_emails_from_feishu(
    input_data["email"],
    input_data["password"],
    keyword="周报｜张三",
    year=2025
)

# 输出结果（JSON）
print(json.dumps({
    "total": len(emails),
    "emails": emails
}))
```

**脚本特点：**
- 通过 stdin/stdout 与 Agent 通信（JSON 格式）
- 可以安装和使用任何 Python 库
- 支持沙箱隔离执行
- 自动过滤出张三的周报（通过关键词"周报｜张三"）

### 真实遇到的问题和优化

在实际开发中，我们遇到了一个性能问题：

**问题：** 从飞书 IMAP 服务器获取邮件时，程序卡住了很久。

**排查过程：**
```python
# 添加日志后发现
[DEBUG] 正在连接 IMAP 服务器: imap.feishu.cn:993
[DEBUG] 连接成功，正在登录...
[DEBUG] 登录成功
[DEBUG] 找到 18 个文件夹
[DEBUG] [1/18] 正在搜索文件夹: INBOX
[DEBUG] [2/18] 正在搜索文件夹: Sent
...
[DEBUG] [10/18] 正在搜索文件夹: 草稿箱
# 卡在这里，然后报错：
[错误] IMAP error: socket error: EOF occurred in violation of protocol
```

**原因分析：**
- 飞书邮箱有 18 个文件夹
- 串行搜索时，第 10 个文件夹就因为超时断开连接
- IMAP 服务器对单次连接有时间/操作数限制

**解决方案：** 改用并发模式，5 个线程同时搜索

```python
# 并发搜索所有文件夹
with ThreadPoolExecutor(max_workers=5) as executor:
    # 每个线程创建独立的 IMAP 连接
    futures = {
        executor.submit(
            search_folder_with_own_connection,
            folder, email, password
        ): folder
        for folder in all_folders
    }

    for future in as_completed(futures):
        folder, emails = future.result()
        all_emails.extend(emails)
```

**效果：**
- 速度提升 **4 倍**（18 个文件夹只需 4 轮并发）
- 不再超时断开
- 每个线程独立连接，互不干扰

**这个案例说明：掌控代码意味着你能真正优化性能。** 如果是黑盒系统，你只能干等着，无法针对实际场景优化。

### 完整的执行流程

```
用户提问："帮我生成张三的 2025 年度复盘报告"
  ↓
Agent 匹配到 weekly-report-to-annual 技能
  ↓
加载 Layer 1: Metadata（技能名称、描述）
  ↓
加载 Layer 2: Instruction（SKILL.md 正文）
  ↓
加载 Layer 3: Resources（年度复盘模板、邮件获取脚本）
  ↓
执行脚本：fetch_emails.py
  ├─ 并发连接 18 个文件夹（5个线程）
  ├─ 过滤关键词"周报｜张三"
  ├─ 只保留 2025 年邮件
  └─ 返回 50 封周报邮件
  ↓
LLM 分析张三的周报内容
  ├─ 提取关键项目（API网关重构、微服务拆分、支付系统等）
  ├─ 总结技能成长（掌握K8s、引入AI工具、架构设计能力）
  ├─ 识别挑战和解决方案（高并发优化、数据库性能调优）
  └─ 按模板生成结构化报告
  ↓
执行脚本：save_report.py
  └─ 保存为 "张三-2025年度复盘报告.md"
  ↓
返回给用户：完整的年度复盘报告
```

**最终生成的报告包含：**
1. 目标复盘（年度目标达成情况）
2. 工作亮点（API网关性能提升300%、微服务拆分、日活增长4倍）
3. 价值观复盘（成就客户、协作贡献、成长进化）
4. 项目贡献（技术方案设计、跨团队协作）
5. 经验与教训总结

### 生成的报告示例

AI 自动从 50 封周报中提炼出的年度复盘报告（节选）：

```markdown
# 张三-2025年度复盘报告

---

## 1. 目标复盘

| 年度目标 | 目标达成率 | 年度目标达成情况 | 后续改进行动 |
|----------|------------|------------------|--------------|
| 完成API网关性能优化 | 150% | QPS从2000提升到8000，超额完成目标 | 继续优化，目标达到10000 QPS |
| 微服务架构改造 | 100% | 成功拆分为4个独立服务，部署效率提升6倍 | 扩展到更多业务模块 |
| 系统日活用户增长 | 400% | 从5万增长到20万，远超预期 | 优化用户体验，提升留存率 |
| 掌握云原生技术栈 | 100% | 参加KubeCon大会，应用K8s到生产环境 | 深入学习服务网格和可观测性 |

---

## 2. 工作亮点

> 真正拿得出手的成果，尽量量化

- **API网关重构项目**: 通过连接池优化和对象复用，将QPS从2000提升到8000（**300%提升**），解决了高并发场景下的内存占用问题。这是今年最大的技术突破。

- **订单系统微服务化**: 成功将单体应用拆分为用户、订单、支付、库存4个独立服务，部署时间从30分钟降到5分钟（**6倍效率提升**），显著提高了系统灵活性和可维护性。

- **支付系统重构**: 完成微信、支付宝、银联三方支付对接，支付成功率从95%提升到99.2%（**减少客户投诉80%**），为公司带来直接经济效益。

- **实时数据看板开发**: 实现订单量、GMV、支付成功率等核心指标的实时展示，为业务决策提供了数据支持，帮助运营团队快速响应异常。

- **引入AI辅助工具**: 使用GitHub Copilot进行代码开发，编码效率提升30%，代码质量也显著提高。

---

## 3. 价值观复盘

### (1) 成就客户

> 2025年，你为外部客户/业务下游做了什么，为他们带来了什么价值？

- **案例1**: API网关性能优化后，页面加载速度从3秒降到1秒以内，用户体验大幅提升，用户留存率提高15%。

- **案例2**: 支付系统重构将支付成功率从95%提升到99.2%，每月减少客户投诉从200+降到40以内，客户满意度显著提高。

- **案例3**: 微服务架构改造后，新功能上线周期从2周缩短到3天，快速响应市场需求，帮助公司抢占市场先机。

### (2) 协作贡献

> 你在2025年做出了哪些组织贡献？

- **成果1**: 组织技术分享会《微服务架构实践》，分享API网关和服务拆分经验，帮助团队成员掌握微服务核心技术，推动了团队技术栈升级。

- **成果2**: 培训2名新人，完成入职技术指导，编写了《新人技术手册》，涵盖公司技术栈、开发流程、最佳实践等，加速新人成长。

- **成果3**: 撰写技术文档《API网关设计与实践》，沉淀了网关设计的核心思路和实践经验，成为团队的技术参考资料。

### (3) 成长进化

> 2025年，你在个人或团队方面有哪些方面的成长？

- **成果1**: 在云原生技术方面有重大突破，参加KubeCon技术大会，学习K8s最佳实践，并成功将K8s应用到生产环境，提升了系统的可扩展性和稳定性。

- **成果2**: 掌握了数据库性能优化技术，通过索引优化使复杂查询速度提升10倍，解决了系统性能瓶颈。

- **成果3**: 引入AI辅助开发工具GitHub Copilot，将AI技术应用到日常开发中，显著提高了编码效率和代码质量。

### (4) 项目贡献

> 2025年，你做了哪些项目，在这些项目中展现出了哪些能力？

- **项目1**:
  - 项目等级: S
  - 项目角色: 技术负责人
  - 项目结果: API网关重构，QPS从2000提升到8000，性能提升300%
  - 展现能力: 性能优化能力、架构设计能力、问题解决能力

- **项目2**:
  - 项目等级: A
  - 项目角色: 技术负责人
  - 项目结果: 订单系统微服务化，部署效率提升6倍
  - 展现能力: 系统架构设计、技术选型、项目管理

- **项目3**:
  - 项目等级: A
  - 项目角色: 核心开发
  - 项目结果: 支付系统重构，支付成功率提升到99.2%
  - 展现能力: 第三方系统对接、异常处理、系统稳定性保障

---

## 4. 经验&教训总结

### (1) 三点经验

1. **经验一**: 在性能优化中，先通过profiling工具（如pprof）定位瓶颈，再针对性优化，避免盲目优化。API网关项目就是通过这个方法，准确定位到连接池和对象复用的问题，实现了300%的性能提升。

2. **经验二**: 微服务拆分要遵循单一职责原则，按业务领域划分而不是技术层次划分。订单系统拆分为用户、订单、支付、库存4个服务，每个服务职责清晰，大大提高了系统的可维护性。

3. **经验三**: 引入新技术要循序渐进，先在非核心模块试点，验证效果后再推广。引入K8s时先在测试环境试点，积累经验后才应用到生产环境，避免了风险。

### (2) 三点教训

1. **教训一**: 在支付系统重构初期，低估了第三方接口的不稳定性，导致上线后频繁超时。应该在设计阶段就考虑容错和重试机制，而不是事后补救。

2. **教训二**: 数据库性能优化过程中，部分索引设计不合理，反而降低了写入性能。应该在索引设计时综合考虑读写平衡，必要时进行压测验证。

3. **教训三**: 微服务拆分后，服务间调用链路变长，排查问题变得困难。应该在拆分前就引入分布式追踪（如Jaeger），而不是事后补充。

---

## 附录：周报数据来源

| 序号 | 日期 | 周报主题 |
|------|------|----------|
| 1 | 2025-12-02 | 【周报】张三-12月02日 |
| 2 | 2025-11-25 | 【周报】张三-11月25日 |
| 3 | 2025-11-18 | 【周报】张三-11月18日 |
| ... | ... | ... |
| 50 | 2025-01-08 | 【周报】张三-01月08日 |

**报告生成时间**: 2025-12-28 15:30:00
**使用技能**: weekly-report-to-annual
**处理邮件数**: 50封
**报告字数**: 3500字
```

**看到了吗？** AI 自动从 50 封周报中：
- 提取量化数据（QPS提升300%、部署效率提升6倍、日活增长4倍）
- 归纳项目成果（API网关、微服务、支付系统）
- 总结技术成长（K8s、性能优化、AI工具）
- 分析经验教训（性能优化方法论、微服务拆分原则）

张三只需要稍作修改，一份完整的年度复盘报告就完成了！

### 项目结构

```
weekly-report-to-annual/
├── SKILL.md                          # 技能定义
├── scripts/                          # 可执行脚本
│   ├── fetch_emails.py              # 获取邮件
│   └── save_report.py               # 保存报告
├── references/                       # 参考资料
│   └── annual-review-template.md    # 年度复盘模板
└── demo.py                          # 演示程序
```

**只需要这几个文件，一个完整的技能就定义好了！**

## 五、技术架构一览

### 核心模块

```python
openskills/
├── core/                 # 核心功能
│   ├── manager.py        # SkillManager - 技能管理
│   ├── matcher.py        # 智能匹配引擎
│   ├── parser.py         # SKILL.md 解析
│   └── executor.py       # 脚本执行器
│
├── models/               # 数据模型（Pydantic）
│   ├── metadata.py       # Layer 1: 元数据
│   ├── instruction.py    # Layer 2: 指令
│   └── resource.py       # Layer 3: 资源
│
├── llm/                  # LLM 集成
│   ├── openai_compat.py  # OpenAI/Azure/Ollama 兼容
│   └── prompt_builder.py # 提示词构建
│
├── sandbox/              # 沙箱执行
│   ├── client.py         # HTTP 客户端
│   └── executor.py       # 沙箱执行器
│
└── agent.py              # SkillAgent - 高级 API
```

### 两种使用模式

**1. 低级 API（完全控制）**

适合需要精细控制每个步骤的场景：

```python
from openskills import SkillManager
from pathlib import Path

# 创建管理器
manager = SkillManager([Path("./skills")])

# 发现所有技能
await manager.discover()

# 匹配用户查询
skills = manager.match("生成年度报告")

# 手动加载指令
await manager.load_instruction(skills[0].name)

# 手动加载 references
await manager.load_references(skills[0].name)

# 执行脚本
result = await manager.execute_script(
    skills[0].name,
    "fetch_emails",
    {"email": "...", "password": "..."}
)
```

**2. 高级 API（推荐，自动化）**

适合快速开发，一切自动化：

```python
from openskills import create_agent

agent = await create_agent(
    skill_paths=["./skills"],
    api_key="your-key",
    auto_select_skill=True,      # 自动选择技能
    auto_execute_scripts=True,   # 自动执行脚本
    use_sandbox=True,            # 沙箱隔离
)

# 一行搞定
response = await agent.chat("帮我生成年度报告")
print(response.content)
print(f"使用的技能: {response.skill_used}")
```

## 六、安全性：沙箱执行

脚本执行是 AI Agent 最危险的部分。OpenSkills 通过 **AIO Sandbox** 提供隔离执行。

### 快速部署沙箱

```bash
# 启动沙箱容器
docker run --rm -p 8080:8080 ghcr.io/agent-infra/sandbox:latest
```

### 在 OpenSkills 中使用沙箱

```python
agent = await create_agent(
    skill_paths=["./skills"],
    api_key="your-key",
    use_sandbox=True,
    sandbox_base_url="http://localhost:8080",
    auto_execute_scripts=True,
)
```

### 沙箱特性

- ✅ 容器隔离，无法访问宿主机
- ✅ 自动依赖安装（Python、npm、系统包）
- ✅ 文件自动同步（上传/下载）
- ✅ 超时控制
- ✅ 资源限制（CPU、内存）

### 依赖声明

在 SKILL.md 中声明依赖，沙箱自动安装：

```yaml
dependency:
  python:
    - pandas>=2.0.0
    - requests>=2.31.0
  npm:
    - mermaid@latest
  system:
    - apt-get install -y imagemagick
```

## 七、多 LLM 支持

OpenSkills 不绑定任何特定的 LLM 提供商：

```python
from openskills.llm import OpenAICompatClient

# OpenAI
client = OpenAICompatClient(
    api_key="sk-...",
    model="gpt-4",
)

# Azure OpenAI
client = OpenAICompatClient(
    api_key="...",
    base_url="https://xxx.openai.azure.com/",
    model="gpt-4",
)

# Ollama（本地）
client = OpenAICompatClient(
    base_url="http://localhost:11434/v1",
    model="llama3.2",
    api_key="ollama",  # 任意值
)

# DeepSeek / Together AI / Groq 等都支持
```

## 八、开发者体验

### 1. CLI 工具

```bash
# 列出所有技能
openskills list

# 查看技能详情
openskills show weekly-report-to-annual

# 验证技能格式
openskills validate ./my-skill/

# 测试匹配
openskills match "生成年度报告"
```

### 2. 自动发现 References

把文件放到 `references/` 目录，自动识别：

```
my-skill/
├── SKILL.md
└── references/
    ├── template.md       # 自动发现
    ├── examples.md       # 自动发现
    └── appendix/
        └── glossary.md   # 子目录也支持
```

不需要在 SKILL.md 中逐一声明！

### 3. 智能加载模式

References 支持三种加载模式：

```yaml
references:
  # 1. always - 始终加载
  - path: references/guidelines.md
    mode: always
    description: 必读规范

  # 2. explicit - 有条件，LLM 判断是否满足
  - path: references/financial-handbook.md
    mode: explicit
    condition: 当讨论涉及财务、预算、成本时

  # 3. implicit - 无条件，LLM 决定是否有用（默认）
  - path: references/examples.md
    mode: implicit
    description: 示例参考
```

## 九、实战：5 分钟创建你的第一个技能

### Step 1: 创建技能目录

```bash
mkdir my-translator && cd my-translator
```

### Step 2: 编写 SKILL.md

```yaml
---
name: smart-translator
description: 智能翻译，自动识别源语言和目标语言
version: 1.0.0

triggers:
  - 翻译
  - translate
  - 翻成
---

# 智能翻译技能

你是一个专业的翻译助手。

## 翻译原则

1. 自动识别源语言和目标语言
2. 保持原文的语气和风格
3. 避免生硬的机翻腔

## 执行步骤

1. 识别源语言
2. 识别目标语言（如果未指定，中文↔英文互译）
3. 翻译内容
4. 检查术语准确性
```

### Step 3: 使用技能

```python
from openskills import create_agent

agent = await create_agent(
    skill_paths=["./my-translator"],
    api_key="your-key",
)

response = await agent.chat("""
翻译成英文：
这个项目让 AI Agent 的技能调用不再是黑盒。
""")

print(response.content)
# This project makes AI Agent skill invocation transparent.
```

**就这么简单！**

## 十、性能对比

我们用 50 个技能做了测试（每个技能有 10 个 reference 文档）：

| 方案 | 发现时间 | 内存占用 | 匹配速度 |
|------|--------|---------|---------|
| **全量加载** | 8.5s | 450MB | 1.2s |
| **OpenSkills** | 0.3s | 25MB | 0.8s |
| **提升** | **28x** | **18x** | **1.5x** |

**结论：** 渐进式架构在大规模技能库中优势明显。


**项目地址：** https://github.com/twwch/OpenSkills