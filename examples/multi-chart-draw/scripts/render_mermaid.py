#!/usr/bin/env python3
"""
Mermaid 图表渲染脚本
将 Mermaid 语法渲染为 PNG/SVG 格式

依赖：
- @mermaid-js/mermaid-cli (需通过 npm 全局安装)
"""

import argparse
import subprocess
import os
import sys
from pathlib import Path


def render_mermaid(input_file: str, output_file: str, format_type: str = "png"):
    """
    渲染 Mermaid 图表
    
    参数:
        input_file: 输入的 Mermaid 语法文件路径
        output_file: 输出的图片文件路径
        format_type: 输出格式 (png/svg)
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
    if format_type not in ["png", "svg"]:
        raise ValueError(f"不支持的格式: {format_type}，仅支持 png 或 svg")
    
    # 检查 mmdc 命令是否可用
    try:
        subprocess.run(["mmdc", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "Mermaid CLI (mmdc) 未安装或不在 PATH 中。请运行: npm install -g @mermaid-js/mermaid-cli"
        )
    
    # 确保输出文件扩展名正确（mermaid-cli 根据扩展名决定格式）
    output_path = Path(output_file)
    if output_path.suffix.lower() not in [f".{format_type}"]:
        output_file = str(output_path.with_suffix(f".{format_type}"))

    # 构建命令（格式由输出文件扩展名决定）
    cmd = [
        "mmdc",
        "-i", input_file,
        "-o", output_file
    ]
    
    # 执行渲染
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Mermaid 渲染失败: {result.stderr}")
        
        print(f"✓ Mermaid 图表已生成: {output_file}")
        return output_file
        
    except Exception as e:
        raise RuntimeError(f"渲染过程出错: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="渲染 Mermaid 图表")
    parser.add_argument("--input", "-i", required=True, help="输入的 Mermaid 语法文件")
    parser.add_argument("--output", "-o", required=True, help="输出的图片文件路径")
    parser.add_argument("--format", "-f", default="png", choices=["png", "svg"], 
                        help="输出格式 (默认: png)")
    
    args = parser.parse_args()
    
    try:
        render_mermaid(args.input, args.output, args.format)
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
