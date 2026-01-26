---
name: multi-chart-draw
description: 支持多种图表类型的绘制工具，包括思维导图、流程图、数据可视化图表、数学函数图等；可根据用户需求生成 Mermaid、ECharts、Mindmap、DrawIO、GeoGebra 等格式的图表，并导出为 PNG、SVG、HTML 等格式
dependency:
  python:
    - pyecharts>=2.0.0
  system:
    - npm install -g @mermaid-js/mermaid-cli
    - npm install -g markmap-cli
---

# 多类型绘图工具

## 任务目标
- 本 Skill 用于：根据用户需求生成多种类型的图表，包括思维导图、流程图、数据可视化图表等
- 能力包含：
  1. Mermaid 图表绘制（流程图、序列图、甘特图等）
  2. ECharts 数据可视化（柱状图、折线图、饼图等）
  3. Mindmap 思维导图
  4. DrawIO 通用绘图
  5. Flowchart 流程图（基于 Mermaid）
  6. GeoGebra 数学绘图（函数、几何图形、代数方程）
- 触发条件：用户表达"画个图"、"绘制图表"、"生成流程图"等需求

## 前置准备

### 依赖说明
- Python 依赖包：
  - `pyecharts>=2.0.0`：用于生成 ECharts 图表
  - `pillow>=10.0.0`：图像处理库
- 系统依赖（需提前安装）：
  - `@mermaid-js/mermaid-cli`：用于渲染 Mermaid 图表
  - `markmap-cli`：用于渲染思维导图

### 安装系统依赖
在使用 Skill 之前，需要安装以下系统工具：

```bash
# 安装 Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# 安装 Markmap CLI
npm install -g markmap-cli

# 验证安装
mmdc --version
markmap --version
```

### 输出目录准备
```bash
# 创建输出目录
mkdir -p ./charts-output
```

## 操作步骤

### 标准流程

1. **需求分析与类型选择**
   - 智能体理解用户绘图需求，确定图表类型：
     - 层级关系、知识结构、脑图整理 → Mindmap
     - 流程逻辑、步骤关系、业务流程 → Flowchart (Mermaid)
     - 时序交互、API调用、消息传递 → Mermaid Sequence
     - 数据对比、趋势分析、统计图表 → ECharts
     - **系统架构、网络拓扑、部署图、ER图 → DrawIO**
     - 数学函数、几何图形、代数方程 → GeoGebra
   - 确定输出格式（PNG/SVG/HTML）

2. **生成图表配置**
   - 根据选定的图表类型，智能体生成相应的文本配置：
     - Mermaid：生成 mermaid 语法
     - ECharts：生成 option 配置 JSON
     - Mindmap：生成 Markdown 格式内容
     - DrawIO：生成 XML 格式内容
     - GeoGebra：生成命令列表或数学表达式
   - 参考 [references/](references/) 中的语法指南

3. **调用脚本渲染**
   - 根据图表类型调用对应的渲染脚本：
     - Mermaid 图表：`scripts/render_mermaid.py`
     - ECharts 图表：`scripts/render_echarts.py`
     - 思维导图：`scripts/render_mindmap.py`
     - DrawIO 图表：`scripts/render_drawio.py`
     - GeoGebra 图表：`scripts/render_geogebra.py`
   - 指定输出路径和格式

4. **结果验证与交付**
   - 检查生成的图表文件
   - 确认格式和内容符合预期
   - 将输出文件路径提供给用户

### 可选分支

- 当需要 **交互式图表**：使用 ECharts 生成 HTML 格式
- 当需要 **矢量图**：选择 SVG 输出格式
- 当需要 **高质量位图**：选择 PNG 并设置高分辨率

## 资源索引

### 渲染脚本
- **Mermaid 渲染**：见 [scripts/render_mermaid.py](scripts/render_mermaid.py)
  - 用途：将 Mermaid 语法渲染为 PNG/SVG
  - 参数：`--input`（输入文件）、`--output`（输出文件）、`--format`（格式：png/svg）
  
- **ECharts 渲染**：见 [scripts/render_echarts.py](scripts/render_echarts.py)
  - 用途：将 ECharts 配置渲染为 HTML（交互式图表）
  - 参数：`--config`（配置文件）、`--output`（输出文件）

- **Mindmap 渲染**：见 [scripts/render_mindmap.py](scripts/render_mindmap.py)
  - 用途：将 Markdown 格式的思维导图渲染为 SVG/PNG
  - 参数：`--input`（输入文件）、`--output`（输出文件）、`--format`（格式：svg/png）

- **DrawIO 图表**：见 [scripts/render_drawio.py](scripts/render_drawio.py)
  - 用途：将 DrawIO XML 渲染为 HTML（交互式图表）
  - 参数：`--input`（输入文件）、`--output`（输出文件）

- **GeoGebra 渲染**：见 [scripts/render_geogebra.py](scripts/render_geogebra.py)
  - 用途：将 GeoGebra 命令渲染为交互式 HTML
  - 参数：`--input`（输入文件）、`--output`（输出文件）

### 参考文档
- **Mermaid 语法**：见 [references/mermaid-syntax.md](references/mermaid-syntax.md)
  - 何时读取：生成 Mermaid 图表时
  
- **ECharts 配置**：见 [references/echarts-guide.md](references/echarts-guide.md)
  - 何时读取：生成 ECharts 图表时
  
- **Mindmap 格式**：见 [references/mindmap-guide.md](references/mindmap-guide.md)
  - 何时读取：生成思维导图时
  
- **DrawIO 格式**：见 [references/drawio-guide.md](references/drawio-guide.md)
  - 何时读取：生成 DrawIO 图表时

- **GeoGebra 语法**：见 [references/geogebra-guide.md](references/geogebra-guide.md)
  - 何时读取：生成数学函数图或几何图形时

### 示例资源
- **图表示例**：见 [assets/examples/](assets/examples/)
  - 包含各种图表类型的示例配置文件

## 注意事项

### 智能体能力
- 智能体负责理解用户需求、生成图表的文本配置、选择合适的图表类型
- 智能体应充分利用其语言理解和创作能力，生成高质量的图表内容

### 脚本使用
- 脚本仅负责技术性渲染工作，接收文本输入并生成图像文件
- 所有参数必须通过命令行参数传递，不要在脚本中硬编码
- 确保脚本具有适当的错误处理和日志输出

### 格式选择指南
- **Mindmap**：适合层级结构、知识梳理、项目规划、概念关系
- **Mermaid Flowchart**：适合简单流程图、决策流程、算法流程
- **Mermaid Sequence**：适合时序图、API调用、消息传递、交互流程
- **Mermaid 其他**：甘特图（项目进度）、状态图、类图、ER图（简单）
- **ECharts**：适合数据可视化（柱状图、折线图、饼图、散点图等）
- **DrawIO**：适合系统架构图、网络拓扑、部署图、ER图（复杂）、UML图
- **GeoGebra**：适合数学函数、几何图形、代数方程、统计分析

### 类型选择示例
- "项目计划" → Mindmap
- "用户注册流程" → Mermaid Flowchart
- "API调用时序" → Mermaid Sequence
- "季度销售额" → ECharts 柱状图
- "系统架构图" → DrawIO
- "函数图像" → GeoGebra

### 输出管理
- 建议将输出文件统一放在 `./charts-output/` 目录下
- 使用有意义的文件名，如 `mindmap-project-plan.svg`、`flowchart-api-call.png`
- 注意输出格式的适用场景（SVG 适合矢量编辑，PNG 适合展示）

## 使用示例

### 示例 1：绘制流程图
**需求**：绘制一个用户注册流程图

**执行方式**：
1. 智能体生成 Mermaid flowchart 语法
2. 调用 `scripts/render_mermaid.py --input temp.mmd --output ./charts-output/registration-flow.png --format png`

**关键参数**：
- 输入：Mermaid 语法的 `.mmd` 文件
- 输出：PNG 格式图片

### 示例 2：生成数据可视化图表
**需求**：生成月度销售数据的柱状图（包含多个产品系列）

**执行方式**：
1. 智能体生成 ECharts option 配置 JSON（在一个配置文件中包含所有系列）
2. 调用 `scripts/render_echarts.py --config sales-data.json --output ./charts-output/sales-chart.html`

**关键说明**：
- 所有系列应放在同一个配置文件的 `series` 数组中
- 不要为每个系列创建单独的配置文件
- 示例：`assets/examples/echarts-multi-series.json`

### 示例 3：创建思维导图
**需求**：为项目规划创建思维导图

**执行方式**：
1. 智能体生成 Markdown 格式的思维导图内容
2. 调用 `scripts/render_mindmap.py --input project-plan.md --output ./charts-output/project-mindmap.svg --format svg`

**关键参数**：
- 输入：Markdown 格式的 `.md` 文件
- 输出：SVG 格式（矢量图）

### 示例 4：绘制系统架构图
**需求**：绘制微服务系统架构图（包含前端、后端、数据库、缓存等组件）

**执行方式**：
1. 智能体生成 DrawIO XML 格式
2. 调用 `scripts/render_drawio.py --input architecture.xml --output ./charts-output/system-architecture.html`

**关键参数**：
- 输入：DrawIO XML 格式的 `.xml` 文件
- 输出：HTML 格式（交互式图表，支持导出 SVG/PNG）
- 特点：可在浏览器中直接查看、缩放、拖动

### 示例 5：绘制数学函数图
**需求**：绘制函数 y = x² 和 y = sin(x) 的图像

**执行方式**：
1. 智能体生成 GeoGebra 命令列表
2. 调用 `scripts/render_geogebra.py --input function-commands.txt --output ./charts-output/function-plot.html`

**关键参数**：
- 输入：包含 GeoGebra 命令的文本文件
- 输出：HTML 格式（交互式 GeoGebra 图形）

## 重要提示

### ECharts 多系列图表
- ✅ **正确做法**：将所有系列放在一个配置文件的 `series` 数组中
  ```json
  {
    "series": [
      {"name": "系列1", "type": "bar", "data": [...]},
      {"name": "系列2", "type": "bar", "data": [...]},
      {"name": "系列3", "type": "bar", "data": [...]}
    ]
  }
  ```
- ❌ **错误做法**：为每个系列创建单独的配置文件
  - 不要创建 `series1.json`、`series2.json`、`series3.json`
  - 这会生成多个独立的图表，而不是一个图表中的多个系列

### 参考示例
- 单系列示例：`assets/examples/echarts-bar-standard.json`
- 多系列示例：`assets/examples/echarts-multi-series.json`
- 折线图多系列：`assets/examples/echarts-line-standard.json`
