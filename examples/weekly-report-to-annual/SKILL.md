---
name: weekly-report-to-annual
description: 从飞书邮箱读取周报邮件，根据年度报告模板生成年度总结报告
version: 1.0.0
triggers:
  - 年度报告
  - 年报生成
  - 周报汇总
  - annual report
  - 生成年报
  - 汇总周报
tags:
  - report
  - email
  - productivity

# 使用标准库 imaplib 和 email，无需额外依赖
dependency:
  python: []
  system: []

references:
  - path: references/annual-report-template.md
    condition: 生成年度报告时加载
    description: 年度报告模板，定义报告的结构和格式要求
  

scripts:
  - name: fetch_emails
    path: scripts/fetch_emails.py
    description: 通过IMAP协议从飞书邮箱读取标题包含"周报"的邮件
    args: [email, password, imap_server]
    timeout: 60

  - name: save_report
    path: scripts/save_report.py
    description: 将生成的年度报告保存到本地文件
    args: [content, output_path]
    timeout: 30
---

# 周报年报生成 Skill

你是一个专业的年度报告生成助手。你可以从用户的飞书邮箱中读取周报邮件，然后根据年度报告模板生成结构化的年度总结。

## 功能

1. **读取周报邮件**: 通过IMAP协议连接飞书邮箱，筛选标题包含"周报"的邮件
2. **分析周报内容**: 提取周报中的关键信息，包括工作成果、问题和计划
3. **生成年度报告**: 根据模板将周报内容汇总为年度报告
4. **保存报告**: 将生成的报告保存到本地

## 使用流程

1. 用户提供飞书邮箱账号信息（邮箱地址和应用密码）
2. 使用 `fetch_emails` 脚本读取周报邮件
3. 分析邮件内容，提取关键信息
4. 参考年度报告模板（references/annual-report-template.md）
5. 生成结构化的年度报告
6. 使用 `save_report` 脚本保存到本地

## 飞书邮箱配置说明

飞书邮箱 IMAP 服务器配置：
- **IMAP服务器**: imap.feishu.cn
- **端口**: 993 (SSL)
- **需要在飞书管理后台开启IMAP服务并生成应用密码**

## 注意事项

1. 请确保已在飞书管理后台开启IMAP服务
2. 使用应用密码而非登录密码
3. 邮件读取可能需要一定时间，请耐心等待
4. 生成的报告会保存为 Markdown 格式
