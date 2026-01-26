#!/usr/bin/env python3
"""
DrawIO 图表渲染脚本
使用 DrawIO 官方 iframe 嵌入方式 + postMessage 加载 XML

说明：
- 使用 DrawIO 官方 embed API
- 通过 postMessage 加载 XML 数据
- 完整的编辑和交互功能
"""

import argparse
import os
import sys
import json


def render_drawio_to_html(input_file: str, output_file: str):
    """
    渲染 DrawIO 图表为 HTML
    
    参数:
        input_file: 输入的 DrawIO XML 文件路径
        output_file: 输出的 HTML 文件路径
    """
    # 验证输入文件
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    # 验证输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 读取 DrawIO XML
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            drawio_xml = f.read()
    except Exception as e:
        raise RuntimeError(f"读取输入文件失败: {str(e)}")
    
    # 验证是否是有效的 DrawIO XML
    if "<mxfile" not in drawio_xml or "</mxfile>" not in drawio_xml:
        raise RuntimeError("输入文件不是有效的 DrawIO XML 格式")
    
    # 生成 HTML 内容
    html_content = generate_drawio_html(drawio_xml)
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ DrawIO HTML 已生成: {output_file}")
        return output_file
        
    except Exception as e:
        raise RuntimeError(f"写入输出文件失败: {str(e)}")


def generate_drawio_html(drawio_xml: str) -> str:
    """
    生成包含 DrawIO iframe 的 HTML 内容
    
    通过 postMessage 加载 XML 数据
    
    参数:
        drawio_xml: DrawIO XML 内容
    
    返回:
        HTML 内容字符串
    """
    
    # 将 XML 转义为 JSON 字符串
    xml_escaped = json.dumps(drawio_xml)
    
    # 生成 URL 参数
    params = {
        'embed': '1',
        'ui': 'atlas',
        'spin': '1',
        'proto': 'json',
        'p': '*'  # 允许 postMessage 通信
    }
    
    # 构建 URL
    url_params = '&'.join([f"{k}={v}" for k, v in params.items()])
    drawio_url = f"https://embed.diagrams.net/?{url_params}"
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DrawIO 图表</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            padding: 10px 20px;
            background-color: white;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
        }}
        .header h1 {{
            margin: 0;
            font-size: 18px;
            color: #333;
        }}
        .header .info {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        .toolbar {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            text-decoration: none;
            display: inline-block;
        }}
        .btn:hover {{
            background-color: #45a049;
        }}
        .btn-secondary {{
            background-color: #2196F3;
        }}
        .btn-secondary:hover {{
            background-color: #0b7dda;
        }}
        .btn-warning {{
            background-color: #ff9800;
        }}
        .btn-warning:hover {{
            background-color: #f57c00;
        }}
        #drawio-container {{
            position: absolute;
            top: 60px;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: white;
        }}
        #drawio-iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #666;
            z-index: 100;
        }}
        .loading-spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .fallback {{
            display: none;
            padding: 40px;
            text-align: center;
        }}
        .fallback.show {{
            display: block;
        }}
        .fallback-btn {{
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>DrawIO 图表</h1>
            <div class="info">完整编辑功能：拖动、缩放、编辑文本、修改样式</div>
        </div>
        <div class="toolbar">
            <a href="https://app.diagrams.net/" target="_blank" class="btn btn-secondary">打开在线编辑器</a>
            <button class="btn btn-warning" onclick="openFullscreen()">全屏查看</button>
        </div>
    </div>
    
    <div id="drawio-container">
        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
            <div>加载中...</div>
        </div>
        <div class="fallback" id="fallback">
            <h3>DrawIO 加载失败</h3>
            <p>可能的原因：网络连接问题或 iframe 被阻止</p>
            <button class="fallback-btn" onclick="openInNewTab()">在新标签页中打开</button>
        </div>
        <iframe
            id="drawio-iframe"
            src="{drawio_url}"
            title="Draw.io Editor"
            allowfullscreen="true"
        ></iframe>
    </div>
    
    <script>
        var iframe = document.getElementById('drawio-iframe');
        var loading = document.getElementById('loading');
        var fallback = document.getElementById('fallback');
        var xmlData = {xml_escaped};
        var isLoaded = false;
        var loadTimeout = null;
        var isIframeReady = false;
        
        // 发送 XML 数据到 iframe
        function sendXmlToIframe() {{
            if (iframe.contentWindow && isIframeReady) {{
                var message = {{
                    action: 'load',
                    xml: xmlData,
                    title: 'DrawIO 图表'
                }};
                console.log('发送 XML 数据到 DrawIO iframe...');
                // proto=json 时需要发送 JSON 字符串
                iframe.contentWindow.postMessage(JSON.stringify(message), '*');
            }} else {{
                console.warn('iframe 未准备好，等待加载完成...');
            }}
        }}
        
        // iframe 加载完成
        iframe.addEventListener('load', function() {{
            console.log('DrawIO iframe 已加载，等待 init 事件...');
            isIframeReady = true;
            // 等待 DrawIO 初始化完成
            setTimeout(sendXmlToIframe, 1000);
        }});
        
        // 监听来自 iframe 的消息
        window.addEventListener('message', function(event) {{
            // 检查是否是来自我们的 iframe
            if (event.source !== iframe.contentWindow) {{
                return;
            }}

            // proto=json 时消息是 JSON 字符串，需要解析
            var msg;
            try {{
                msg = (typeof event.data === 'string') ? JSON.parse(event.data) : event.data;
            }} catch (e) {{
                console.warn('无法解析消息:', event.data);
                return;
            }}

            console.log('收到 DrawIO 消息:', msg);

            // 处理初始化消息 (DrawIO 已准备好)
            if (msg.event === 'init') {{
                console.log('DrawIO 已初始化，发送 XML 数据...');
                isLoaded = true;
                sendXmlToIframe();
            }}

            // 处理加载完成消息
            if (msg.event === 'ready' || msg.event === 'load') {{
                console.log('DrawIO 准备就绪');
                loading.style.display = 'none';
                if (loadTimeout) {{
                    clearTimeout(loadTimeout);
                    loadTimeout = null;
                }}
            }}

            // 处理错误消息
            if (msg.event === 'error') {{
                console.error('DrawIO 错误:', msg);
                loading.style.display = 'none';
                fallback.classList.add('show');
            }}

            // 处理保存消息
            if (msg.event === 'save') {{
                console.log('用户点击保存:', msg.xml);
            }}
        }});
        
        // 全屏查看
        function openFullscreen() {{
            if (iframe.requestFullscreen) {{
                iframe.requestFullscreen();
            }} else if (iframe.webkitRequestFullscreen) {{
                iframe.webkitRequestFullscreen();
            }} else if (iframe.msRequestFullscreen) {{
                iframe.msRequestFullscreen();
            }}
        }}
        
        // 在新标签页打开
        function openInNewTab() {{
            window.open('https://app.diagrams.net/', '_blank');
        }}
        
        // 超时检测（15秒）
        loadTimeout = setTimeout(function() {{
            if (!isLoaded) {{
                console.warn('DrawIO 加载超时');
                loading.style.display = 'none';
            }}
        }}, 15000);
    </script>
</body>
</html>"""
    
    return html_template


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='DrawIO 图表渲染工具')
    parser.add_argument('--input', required=True, help='输入的 DrawIO XML 文件路径')
    parser.add_argument('--output', required=True, help='输出的 HTML 文件路径')
    
    args = parser.parse_args()
    
    try:
        render_drawio_to_html(args.input, args.output)
        sys.exit(0)
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
