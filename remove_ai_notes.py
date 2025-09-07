#!/usr/bin/env python3
import os
from pathlib import Path

"""
移除questions目录下所有文件中的AI生成注释标记
"""

# 定义需要移除的注释文本
AI_NOTE_PATTERN = '> （注：文档部分内容可能由 AI 生成）'

# 设置questions目录路径
QUESTIONS_DIR = Path("questions")

# 检查questions目录是否存在
if not QUESTIONS_DIR.exists() or not QUESTIONS_DIR.is_dir():
    print(f"错误：questions目录 '{QUESTIONS_DIR}' 不存在或不是一个目录")
    exit(1)

# 统计变量
total_files = 0
modified_files = 0

print(f"开始处理questions目录下的文件，查找并移除AI生成注释...")

# 遍历questions目录下的所有文件
for file_path in QUESTIONS_DIR.glob("**/*.md"):
    total_files += 1
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # 检查是否包含AI注释
        has_ai_note = any(AI_NOTE_PATTERN in line for line in lines)
        
        if has_ai_note:
            # 移除包含AI注释的行
            modified_lines = [line for line in lines if AI_NOTE_PATTERN not in line]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(modified_lines)
            
            modified_files += 1
            print(f"已移除文件中的AI注释: {file_path}")
            
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

# 输出处理结果
print(f"\n处理完成！")
print(f"总共处理文件数量: {total_files}")
print(f"修改文件数量: {modified_files}")
if modified_files == 0:
    print("没有找到包含AI注释的文件")