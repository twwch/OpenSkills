# ECharts 配置参考

## 目录
1. [配置格式](#配置格式)
2. [标准格式](#标准格式)
3. [简化格式](#简化格式)
4. [常见示例](#常见示例)

## 概览
ECharts 是一个功能强大的数据可视化库，支持多种图表类型。本 Skill 使用 ECharts 标准格式生成图表。

## 配置格式

### 支持的格式
1. **ECharts 标准格式**（推荐）：完全兼容 ECharts 官方文档
2. **简化格式**（兼容）：向后兼容的简化配置

### 标准格式结构
```json
{
  "title": {"text": "图表标题"},
  "tooltip": {},
  "xAxis": {"type": "category", "data": [...]},
  "yAxis": {"type": "value"},
  "series": [{"type": "bar", "data": [...]}]
}
```

## 标准格式

### 基础结构
```json
{
  "title": {
    "text": "图表标题",
    "subtext": "副标题"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "legend": {
    "data": ["系列1", "系列2"]
  },
  "xAxis": {
    "type": "category",
    "data": ["A", "B", "C"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [
    {
      "name": "系列1",
      "type": "bar",
      "data": [1, 2, 3]
    }
  ]
}
```

## 简化格式

### 基础结构（兼容旧版本）
```json
{
  "type": "bar",
  "title": {
    "text": "图表标题"
  },
  "data": {
    "xAxis": ["A", "B", "C"],
    "seriesName": "系列名称",
    "series": [1, 2, 3]
  },
  "xAxisName": "X轴名称",
  "yAxisName": "Y轴名称"
}
```

### 说明
- 简化格式会自动转换为标准格式
- 推荐使用标准格式，可以获得更多控制选项
- 参考示例：`assets/examples/echarts-bar-standard.json`

## 常见示例

### 示例 1：单系列柱状图（标准格式）
```json
{
  "title": {
    "text": "2024年季度销售额",
    "subtext": "单位：万元"
  },
  "tooltip": {
    "trigger": "axis",
    "axisPointer": {
      "type": "shadow"
    }
  },
  "xAxis": {
    "type": "category",
    "data": ["Q1", "Q2", "Q3", "Q4"],
    "name": "季度"
  },
  "yAxis": {
    "type": "value",
    "name": "销售额(万元)"
  },
  "series": [
    {
      "name": "销售额",
      "type": "bar",
      "data": [1200, 1500, 1800, 2100],
      "itemStyle": {
        "color": "#5470c6"
      }
    }
  ]
}
```

### 示例 2：多系列柱状图
```json
{
  "title": {
    "text": "2024年季度销售额对比",
    "subtext": "单位：万元"
  },
  "tooltip": {
    "trigger": "axis",
    "axisPointer": {
      "type": "shadow"
    }
  },
  "legend": {
    "data": ["产品A", "产品B", "产品C"]
  },
  "xAxis": {
    "type": "category",
    "data": ["Q1", "Q2", "Q3", "Q4"]
  },
  "yAxis": {
    "type": "value",
    "name": "销售额(万元)"
  },
  "series": [
    {
      "name": "产品A",
      "type": "bar",
      "data": [1200, 1500, 1800, 2100],
      "itemStyle": {"color": "#5470c6"}
    },
    {
      "name": "产品B",
      "type": "bar",
      "data": [900, 1100, 1300, 1600],
      "itemStyle": {"color": "#91cc75"}
    },
    {
      "name": "产品C",
      "type": "bar",
      "data": [600, 800, 1000, 1200],
      "itemStyle": {"color": "#fac858"}
    }
  ]
}
```

**重要提示**：
- 所有系列必须放在同一个 `series` 数组中
- 不要为每个系列创建单独的配置文件
- 这样可以在一个图表中同时显示多个系列

### 示例 3：多系列折线图（标准格式）
```json
{
  "title": {
    "text": "用户增长趋势"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "legend": {
    "data": ["用户数", "活跃用户"]
  },
  "xAxis": {
    "type": "category",
    "data": ["1月", "2月", "3月", "4月", "5月", "6月"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [
    {
      "name": "用户数",
      "type": "line",
      "data": [120, 132, 101, 134, 90, 230],
      "smooth": true
    },
    {
      "name": "活跃用户",
      "type": "line",
      "data": [220, 182, 191, 234, 290, 330],
      "smooth": true
    }
  ]
}
```

### 示例 4：饼图（标准格式）
```json
{
  "title": {
    "text": "产品收入占比",
    "subtext": "2024年度",
    "left": "center"
  },
  "tooltip": {
    "trigger": "item",
    "formatter": "{a} <br/>{b}: {c} ({d}%)"
  },
  "legend": {
    "orient": "vertical",
    "left": "left"
  },
  "series": [
    {
      "name": "收入来源",
      "type": "pie",
      "radius": "50%",
      "data": [
        {"value": 1048, "name": "云服务"},
        {"value": 735, "name": "SaaS"},
        {"value": 580, "name": "咨询"},
        {"value": 484, "name": "培训"}
      ],
      "emphasis": {
        "itemStyle": {
          "shadowBlur": 10,
          "shadowOffsetX": 0,
          "shadowColor": "rgba(0, 0, 0, 0.5)"
        }
      }
    }
  ]
}
```

### 示例 5：组合图（柱状+折线）
```json
{
  "title": {
    "text": "销售与利润对比"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "legend": {
    "data": ["销售额", "利润"]
  },
  "xAxis": {
    "type": "category",
    "data": ["Q1", "Q2", "Q3", "Q4"]
  },
  "yAxis": [
    {
      "type": "value",
      "name": "销售额"
    },
    {
      "type": "value",
      "name": "利润"
    }
  ],
  "series": [
    {
      "name": "销售额",
      "type": "bar",
      "data": [1200, 1500, 1800, 2100]
    },
    {
      "name": "利润",
      "type": "line",
      "yAxisIndex": 1,
      "data": [300, 450, 540, 630]
    }
  ]
}
```

### 示例 6：堆叠柱状图
```json
{
  "title": {
    "text": "各部门销售额"
  },
  "tooltip": {
    "trigger": "axis"
  },
  "legend": {
    "data": ["产品A", "产品B", "产品C"]
  },
  "xAxis": {
    "type": "category",
    "data": ["Q1", "Q2", "Q3", "Q4"]
  },
  "yAxis": {
    "type": "value"
  },
  "series": [
    {
      "name": "产品A",
      "type": "bar",
      "stack": "总量",
      "data": [320, 332, 301, 334]
    },
    {
      "name": "产品B",
      "type": "bar",
      "stack": "总量",
      "data": [220, 182, 191, 234]
    },
    {
      "name": "产品C",
      "type": "bar",
      "stack": "总量",
      "data": [150, 232, 201, 154]
    }
  ]
}
```

## 配置参数说明

### 常用参数
- `title`: 标题配置
  - `text`: 主标题
  - `subtext`: 副标题
  - `left`: 位置（'center', 'left', 'right', 或像素值）
- `tooltip`: 提示框配置
  - `trigger`: 触发方式（'item' 或 'axis'）
- `legend`: 图例配置
  - `data`: 图例数据
  - `orient`: 方向（'horizontal' 或 'vertical'）
- `xAxis`: X 轴配置
  - `type`: 类型（'category', 'value', 'time'）
  - `data`: 类目数据
- `yAxis`: Y 轴配置
  - `type`: 类型（'value', 'category'）
- `series`: 系列数据
  - `type`: 图表类型（'bar', 'line', 'pie', 'scatter' 等）
  - `name`: 系列名称
  - `data`: 数据

### 输出格式
- HTML：交互式图表，支持缩放、提示框等
- 使用 ECharts CDN (v5.4.3)

## 注意事项
- JSON 格式必须正确，注意引号和逗号
- 推荐使用标准格式，完全兼容 ECharts 官方文档
- 可以参考 ECharts 官方示例：https://echarts.apache.org/examples/
- 简化格式仅支持单系列基础图表

## 多系列图表配置规范

### ✅ 正确做法
将所有系列放在一个配置文件的 `series` 数组中：
```json
{
  "series": [
    {"name": "系列A", "type": "bar", "data": [...]},
    {"name": "系列B", "type": "bar", "data": [...]},
    {"name": "系列C", "type": "bar", "data": [...]}
  ]
}
```

### ❌ 错误做法
不要为每个系列创建单独的配置文件：
- ❌ `series-a.json`
- ❌ `series-b.json`  
- ❌ `series-c.json`

这样会生成多个独立的图表，而不是一个图表中的多个系列。

### 原因说明
- ECharts 的设计就是一个配置文件对应一个图表
- 一个图表中的多个系列通过 `series` 数组中的多个对象表示
- 如果需要多个独立的图表，才应该创建多个配置文件

### 使用场景
- **一个配置文件**：需要在一个图表中对比多个系列（如产品A、B、C的销售数据）
- **多个配置文件**：需要多个独立的图表（如销售额图表、利润图表、用户增长图表）
