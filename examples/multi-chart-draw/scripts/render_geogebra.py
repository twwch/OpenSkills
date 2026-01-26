#!/usr/bin/env python3
"""
GeoGebra 图形渲染脚本
将 GeoGebra 命令渲染为交互式 HTML

说明：
GeoGebra 提供了 Materials API，可以嵌入到 HTML 中
本脚本生成包含 GeoGebra 命令的 HTML 文件，可在浏览器中打开查看
"""

import argparse
import os
import sys


def render_geogebra(input_file: str, output_file: str):
    """
    渲染 GeoGebra 图形
    
    参数:
        input_file: 输入的 GeoGebra 命令文本文件
        output_file: 输出的 HTML 文件
    """
    # 验证输入文件
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    # 验证输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 读取 GeoGebra 命令
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            commands = f.read().strip()
    except Exception as e:
        raise RuntimeError(f"读取输入文件失败: {str(e)}")
    
    # 如果文件为空，提示错误
    if not commands:
        raise RuntimeError("输入文件为空，请添加 GeoGebra 命令")
    
    # 生成 HTML 内容
    html_content = generate_geogebra_html(commands)
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ GeoGebra HTML 已生成: {output_file}")
        print(f"⚠️  注意: 在浏览器中打开 HTML 文件可查看交互式图形")
        return output_file
        
    except Exception as e:
        raise RuntimeError(f"写入输出文件失败: {str(e)}")


def detect_app_type(commands: list) -> str:
    """
    根据命令内容自动检测应用类型

    参数:
        commands: 命令列表

    返回:
        应用类型: "graphing", "geometry", "3d", 或 "classic"
    """
    commands_text = ' '.join(commands).lower()

    # 3D 命令关键词
    if any(kw in commands_text for kw in ['sphere', 'cube', 'prism', 'pyramid', 'cone', 'cylinder',
                                           'tetrahedron', 'octahedron', 'dodecahedron', 'icosahedron',
                                           'plane(', 'surface(', '(0,0,0)', ', 0## )']):
        return "3d"

    # 几何命令关键词
    geometry_keywords = ['polygon', 'segment', 'circle(', 'ellipse(', 'hyperbola(', 'parabola(',
                         'line(', 'ray(', 'angle(', 'midpoint', 'perpendicular', 'parallel',
                         'reflect', 'rotate(', 'translate(', 'dilate', 'intersect(', 'tangent(']
    if any(kw in commands_text for kw in geometry_keywords):
        return "geometry"

    # 默认使用 graphing（适合函数绘图）
    return "graphing"


def generate_geogebra_html(commands: str) -> str:
    """
    生成包含 GeoGebra 的 HTML 内容

    参数:
        commands: GeoGebra 命令列表

    返回:
        HTML 内容字符串
    """
    # 将命令转换为 JavaScript 数组格式
    # 过滤掉注释行（以 # 开头）和空行
    commands_list = commands.split('\n')
    valid_commands = [cmd.strip() for cmd in commands_list if cmd.strip() and not cmd.strip().startswith('#')]
    commands_js = '[' + ', '.join([f'"{cmd}"' for cmd in valid_commands]) + ']'

    # 自动检测应用类型
    app_type = detect_app_type(valid_commands)
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoGebra 绘图</title>
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
        }}
        .info {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        #geogebra {{
            width: 100%;
            height: 600px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GeoGebra 数学绘图</h1>
            <div class="info">
                <p>提示：在下方图形中可以交互操作，拖动点、缩放视图等</p>
            </div>
        </div>
        <div id="geogebra"></div>
    </div>

    <!-- 加载 GeoGebra API -->
    <script src="https://www.geogebra.org/apps/deployggb.js"></script>
    <script>
        // GeoGebra 命令列表
        var commands = {commands_js};

        // Applet 加载完成后执行命令
        function ggbOnInit() {{
            console.log('GeoGebra 已加载，执行命令...');
            var ggbApplet = document.ggbApplet;

            // 执行每个命令
            for (var i = 0; i < commands.length; i++) {{
                var cmd = commands[i];
                if (cmd && cmd.trim()) {{
                    console.log('执行命令:', cmd);
                    ggbApplet.evalCommand(cmd);
                }}
            }}

            // 自动调整视图以显示所有对象
            // 使用 JavaScript API 而非 evalCommand
            setTimeout(function() {{
                try {{
                    // 获取所有对象的边界并设置坐标系统
                    var objNames = ggbApplet.getAllObjectNames();
                    if (objNames && objNames.length > 0) {{
                        var minX = Infinity, maxX = -Infinity;
                        var minY = Infinity, maxY = -Infinity;
                        for (var j = 0; j < objNames.length; j++) {{
                            var objType = ggbApplet.getObjectType(objNames[j]);
                            if (objType === 'point') {{
                                var x = ggbApplet.getXcoord(objNames[j]);
                                var y = ggbApplet.getYcoord(objNames[j]);
                                if (x < minX) minX = x;
                                if (x > maxX) maxX = x;
                                if (y < minY) minY = y;
                                if (y > maxY) maxY = y;
                            }}
                        }}
                        // 如果找到了点，调整视图
                        if (minX !== Infinity && maxX !== -Infinity) {{
                            var padding = Math.max((maxX - minX) * 0.2, (maxY - minY) * 0.2, 2);
                            ggbApplet.setCoordSystem(minX - padding, maxX + padding, minY - padding, maxY + padding);
                        }}
                    }}
                }} catch(e) {{
                    console.log('自动调整视图时出错:', e);
                }}
            }}, 500);
        }}

        var ggbApp = new GGBApplet(
            {{
                "appName": "{app_type}",
                "width": 1200,
                "height": 600,
                "showToolBar": true,
                "showAlgebraInput": true,
                "showMenuBar": true,
                "allowUpscale": true,
                "showResetIcon": true,
                "enableLabelDrags": true,
                "enableShiftDragZoom": true,
                "enableRightClick": true,
                "showToolBarHelp": true,
                "errorDialogsActive": true,
                "useBrowserForJS": false,
                "appletOnLoad": ggbOnInit
            }},
            true
        );

        ggbApp.inject('geogebra');
    </script>
</body>
</html>"""
    
    return html_template


def main():
    parser = argparse.ArgumentParser(description="渲染 GeoGebra 图形")
    parser.add_argument("--input", "-i", required=True, help="输入的 GeoGebra 命令文本文件")
    parser.add_argument("--output", "-o", required=True, help="输出的 HTML 文件路径")
    
    args = parser.parse_args()
    
    try:
        render_geogebra(args.input, args.output)
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
