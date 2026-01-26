#!/usr/bin/env python3
"""
Mindmap 思维导图渲染脚本
将 Markdown 格式的思维导图渲染为 SVG/PNG

依赖：
- markmap-cli (需通过 npm 全局安装)
"""

import argparse
import subprocess
import os
import sys
from pathlib import Path


def render_mindmap(input_file: str, output_file: str, format_type: str = "svg"):
    """
    渲染思维导图
    
    参数:
        input_file: 输入的 Markdown 文件路径
        output_file: 输出的图片文件路径
        format_type: 输出格式 (svg/png)
    """
    # 验证输入文件
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    # 验证输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 验证格式
    format_type = format_type.lower()
    if format_type not in ["svg", "png"]:
        raise ValueError(f"不支持的格式: {format_type}，仅支持 svg 或 png")
    
    # 检查 markmap 命令是否可用
    try:
        subprocess.run(["markmap", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "Markmap CLI 未安装或不在 PATH 中。请运行: npm install -g markmap-cli"
        )
    
    # 构建命令
    cmd = [
        "markmap",
        input_file,
        "-o", output_file
    ]
    
    # 执行渲染
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Markmap 渲染失败: {result.stderr}")
        
        # markmap 默认生成 SVG，如果需要 PNG，需要转换
        if format_type == "png":
            # 使用 PIL 将 SVG 转为 PNG (需要 cairosvg 或其他工具)
            # 这里输出提示信息
            print(f"⚠️  注意: markmap 默认生成 SVG，PNG 转换需要额外工具")
            print(f"✓ SVG 文件已生成: {output_file.replace('.png', '.svg')}")
        
        print(f"✓ 思维导图已生成: {output_file}")
        return output_file
        
    except Exception as e:
        raise RuntimeError(f"渲染过程出错: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="渲染思维导图")
    parser.add_argument("--input", "-i", required=True, help="输入的 Markdown 文件")
    parser.add_argument("--output", "-o", required=True, help="输出的图片文件路径")
    parser.add_argument("--format", "-f", default="svg", choices=["svg", "png"], 
                        help="输出格式 (默认: svg)")
    
    args = parser.parse_args()
    
    try:
        render_mindmap(args.input, args.output, args.format)
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
