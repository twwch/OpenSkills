#!/usr/bin/env python3
"""
ECharts 图表渲染脚本
将 ECharts 配置渲染为 HTML 格式

支持两种配置格式：
1. ECharts 标准格式（推荐）
2. 简化格式（兼容旧版本）

使用方法：
python render_echarts.py --config config.json --output output.html
"""

import argparse
import json
import os
import sys


def convert_simplified_to_standard(config) -> dict:
    """
    将简化格式转换为 ECharts 标准格式

    简化格式示例：
    {
      "type": "bar",
      "title": {"text": "标题"},
      "data": {
        "xAxis": ["A", "B", "C"],
        "seriesName": "系列名",
        "series": [1, 2, 3]
      }
    }

    ECharts 标准格式示例：
    {
      "title": {"text": "标题"},
      "xAxis": {"data": ["A", "B", "C"]},
      "yAxis": {},
      "series": [{"name": "系列名", "type": "bar", "data": [1, 2, 3]}]
    }
    """
    # 处理配置是列表的情况（可能是多图表或包装在数组中的单个配置）
    if isinstance(config, list):
        if len(config) == 1:
            config = config[0]
        elif len(config) > 1:
            # 多个配置，取第一个并警告
            print("警告: 配置文件包含多个图表配置，将使用第一个", file=sys.stderr)
            config = config[0]
        else:
            raise ValueError("配置文件为空列表")

    if not isinstance(config, dict):
        raise ValueError(f"配置格式无效，期望字典类型，实际为 {type(config).__name__}")

    chart_type = config.get("type", "bar")
    
    # 如果已经是标准格式（直接包含 series 数组），则不转换
    if "series" in config and isinstance(config["series"], list):
        # 可能已经是标准格式，检查一下
        if len(config["series"]) > 0 and "type" in config["series"][0]:
            return config
    
    # 转换简化格式
    data = config.get("data", {})
    x_data = data.get("xAxis", [])
    y_data = data.get("series", [])
    series_name = data.get("seriesName", "系列1")
    
    # 构建标准格式
    standard_config = {
        "title": config.get("title", {}),
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"}
        },
        "xAxis": {
            "type": "category",
            "data": x_data,
            "name": config.get("xAxisName", "")
        },
        "yAxis": {
            "type": "value",
            "name": config.get("yAxisName", "")
        },
        "series": [{
            "name": series_name,
            "type": chart_type,
            "data": y_data
        }]
    }
    
    # 折线图特有的平滑选项
    if chart_type == "line" and data.get("smooth"):
        standard_config["series"][0]["smooth"] = True
    
    return standard_config


def generate_echarts_html(config: dict) -> str:
    """
    生成 ECharts HTML 内容
    
    参数:
        config: ECharts 配置字典（标准格式）
    
    返回:
        HTML 内容字符串
    """
    title = config.get("title", {}).get("text", "ECharts 图表")
    width = config.get("width", "100%")
    height = config.get("height", "500px")
    
    # 转换配置为 JSON 字符串
    option_json = json.dumps(config, ensure_ascii=False, indent=2)
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .header h1 {{
            color: #333;
            margin: 0;
            font-size: 24px;
        }}
        #chart {{
            width: {width};
            height: {height};
            min-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div id="chart"></div>
    </div>
    
    <!-- 加载 ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        // 初始化图表
        var chartDom = document.getElementById('chart');
        var myChart = echarts.init(chartDom);
        
        // ECharts 配置
        var option = {option_json};
        
        // 渲染图表
        myChart.setOption(option);
        
        // 响应窗口大小变化
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
        
        // 显示加载状态（如果有问题）
        myChart.showLoading();
        setTimeout(function() {{
            myChart.hideLoading();
        }}, 500);
    </script>
</body>
</html>"""
    
    return html_template


def render_echarts(config_file: str, output_file: str):
    """
    渲染 ECharts 图表
    
    参数:
        config_file: ECharts 配置 JSON 文件路径
        output_file: 输出 HTML 文件路径
    """
    # 验证输入文件
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    # 验证输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 读取配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 解析失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"读取配置文件失败: {str(e)}")
    
    # 转换为标准格式
    standard_config = convert_simplified_to_standard(config)
    
    # 生成 HTML
    html_content = generate_echarts_html(standard_config)
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ ECharts HTML 已生成: {output_file}")
        return output_file
        
    except Exception as e:
        raise RuntimeError(f"写入输出文件失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="渲染 ECharts 图表")
    parser.add_argument("--config", "-c", required=True, help="ECharts 配置 JSON 文件")
    parser.add_argument("--output", "-o", required=True, help="输出 HTML 文件路径")
    
    args = parser.parse_args()
    
    try:
        render_echarts(args.config, args.output)
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
