---
name: feishu-doc-to-dev-spec
description: 读取飞书云文档（支持多个链接），解析文档中的文本、表格、图片等内容，根据用户选择的开发语言和存储结构，将产品需求文档转换为研发开发需求文档
triggers:
  - "飞书文档"
  - "需求文档"
  - "PRD转研发"
  - "feishu"
  - "产品需求转开发"
dependency:
  python:
    - httpx>=0.25.0
    - lark-oapi>=1.0.0
  system:
    - mkdir -p output/images
---

# 飞书云文档转研发需求文档

## 任务目标

本 Skill 用于：
1. 读取飞书云文档内容（支持多个文档链接）
2. 完整解析文档中的所有内容：文本、表格、图片、代码块等
3. 根据用户选择的开发语言和存储结构
4. 将产品需求文档（PRD）转换为结构化的研发开发需求文档

## 前置准备

### 飞书应用配置

使用前需要创建飞书应用并获取凭证：

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 配置应用权限：
   - `docx:document:readonly` - 读取文档内容
   - `drive:drive:readonly` - 读取云空间文件
   - `wiki:wiki:readonly` - 读取知识库（如需要）

### 环境变量

```bash
export FEISHU_APP_ID=your-app-id
export FEISHU_APP_SECRET=your-app-secret
```

## 操作步骤

### 标准流程

1. **收集文档链接**
   - 用户提供一个或多个飞书文档链接
   - 支持的链接格式：
     - `https://xxx.feishu.cn/docx/xxxxx` - 新版文档
     - `https://xxx.feishu.cn/docs/xxxxx` - 旧版文档
     - `https://xxx.feishu.cn/wiki/xxxxx` - 知识库文档

2. **确认技术选型**
   - 询问用户选择的开发语言（如：Python、Java、Go、Node.js、Rust 等）
   - 询问存储结构（如：PostgreSQL、MySQL、MongoDB、Redis 等）
   - 询问其他技术栈偏好（框架、部署方式等）

3. **读取文档内容**
   - 调用 `[INVOKE:fetch_feishu_doc]` 脚本
   - 传入文档链接列表
   - 脚本会返回完整的文档内容，包括：
     - 文本段落
     - 表格数据（转换为 Markdown 表格）
     - 图片（下载到本地并返回路径）
     - 代码块
     - 有序/无序列表

4. **分析需求内容**
   - 识别功能需求、非功能需求
   - 提取业务规则和约束
   - 整理用户故事和验收标准

5. **生成研发需求文档**
   - 根据用户选择的技术栈
   - 生成包含以下内容的研发文档：
     - 技术架构设计
     - 数据模型设计（表结构）
     - API 接口设计
     - 核心功能实现方案
     - 技术风险评估

6. **输出结果**
   - 生成 Markdown 格式的研发需求文档
   - 保存到 `./output/` 目录

## 资源索引

### 脚本

- **飞书文档读取**：`scripts/fetch_feishu_doc.py`
  - 用途：读取飞书云文档的完整内容
  - 输入参数（JSON 格式）：
    ```json
    {
      "doc_urls": ["https://xxx.feishu.cn/docx/xxxxx"],
      "app_id": "飞书应用ID（可选，默认从环境变量读取）",
      "app_secret": "飞书应用密钥（可选，默认从环境变量读取）"
    }
    ```
  - 输出：文档内容的 JSON 结构

### 参考文档

- **研发文档模板**：`references/dev-spec-template.md`
  - 何时读取：生成研发需求文档时
  - 包含标准的研发文档结构和示例

- **技术选型指南**：`references/tech-stack-guide.md`
  - 何时读取：帮助用户选择技术栈时
  - 包含常见技术栈的特点和适用场景

## 注意事项

### 文档权限
- 确保飞书应用有权限访问目标文档
- 如果文档是私有的，需要将应用添加为文档协作者

### 图片处理
- 文档中的图片会被下载到 `./output/images/` 目录
- 图片链接会被替换为本地相对路径

### 多文档合并
- 当用户提供多个文档链接时，会按顺序读取并合并内容
- 每个文档的内容会用分隔线区分

### 输出格式
- 研发需求文档采用 Markdown 格式
- 表格使用 Markdown 表格语法
- 代码块使用对应语言的语法高亮标记

## 使用示例

### 示例 1：单个文档转换

**用户输入**：
```
请帮我把这个产品需求文档转换为研发需求文档：
https://example.feishu.cn/docx/abc123

技术栈：
- 语言：Python
- 框架：FastAPI
- 数据库：PostgreSQL
- 缓存：Redis
```

**执行流程**：
1. 调用 `[INVOKE:fetch_feishu_doc]` 读取文档
2. 分析需求内容
3. 根据 Python + FastAPI + PostgreSQL 技术栈生成研发文档
4. 输出到 `./output/dev-spec.md`

### 示例 2：多个文档合并

**用户输入**：
```
这是我们的产品需求文档，包含多个部分：
1. 总体需求：https://example.feishu.cn/docx/main
2. 用户模块：https://example.feishu.cn/docx/user
3. 订单模块：https://example.feishu.cn/docx/order

请使用 Java + Spring Boot + MySQL 生成研发文档
```

**执行流程**：
1. 依次读取三个文档
2. 合并并分析需求
3. 生成 Java 技术栈的研发文档

## 研发文档输出结构

生成的研发需求文档包含以下章节：

```markdown
# 研发需求文档

## 1. 项目概述
- 项目背景
- 项目目标
- 技术栈选型

## 2. 系统架构
- 整体架构图
- 模块划分
- 技术组件

## 3. 数据模型设计
- ER 图
- 表结构定义
- 索引设计

## 4. API 接口设计
- 接口列表
- 请求/响应格式
- 错误码定义

## 5. 功能模块详设
- 模块 A
  - 功能描述
  - 实现方案
  - 关键代码示例
- 模块 B
  - ...

## 6. 非功能需求
- 性能要求
- 安全要求
- 可用性要求

## 7. 开发计划
- 里程碑
- 任务分解
- 风险评估
```
