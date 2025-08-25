#!/usr/bin/env python3
"""
修复Markdown格式问题的脚本
主要解决缺少 ## 前缀的答案和解析部分
"""

import re
import os
import sys
from pathlib import Path

def fix_markdown_format(input_file: str, output_file: str = None):
    """
    修复Markdown文件的格式问题
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径，如果为None则覆盖原文件
    """
    if output_file is None:
        output_file = input_file
    
    print(f"Reading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_count = 0
    
    # 修复缺少 ## 前缀的 ✅ 精简答案 部分
    # 查找行首的 **✅ 精简答案：** 前面没有 ## 的情况
    pattern1 = r'^(\*\*✅ 精简答案：\*\*)'
    matches1 = re.findall(pattern1, content, flags=re.MULTILINE)
    content = re.sub(pattern1, r'## \1', content, flags=re.MULTILINE)
    fixes_count += len(matches1)
    
    # 修复缺少 ## 前缀的 📘 详细解析 部分  
    # 查找行首的 **📘 详细解析：** 前面没有 ## 的情况
    pattern2 = r'^(\*\*📘 详细解析：\*\*)'
    matches2 = re.findall(pattern2, content, flags=re.MULTILINE)
    content = re.sub(pattern2, r'## \1', content, flags=re.MULTILINE)
    fixes_count += len(matches2)
    
    # 显示修复的详情
    if fixes_count > 0:
        print(f"✓ Fixed {len(matches1)} instances of missing ## before **✅ 精简答案：**")
        print(f"✓ Fixed {len(matches2)} instances of missing ## before **📘 详细解析：**")
        print(f"Total fixes applied: {fixes_count}")
    else:
        print("No formatting issues found")
    
    print(f"Writing fixed content to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Markdown format fixed successfully!")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 fix_markdown_format.py <input_file> [output_file]")
        print("示例:")
        print("  python3 fix_markdown_format.py vue_questions.md")
        print("  python3 fix_markdown_format.py vue_questions.md vue_questions_fixed.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"✗ 错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    # 修复格式
    fix_markdown_format(input_file, output_file)

if __name__ == "__main__":
    main()