#!/usr/bin/env python3
"""
演示跳过已存在问题的功能
"""

import sys
import os
from pathlib import Path
import re

def demo_skip_existing(output_dir: str):
    """演示扫描已存在问题的功能"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"❌ 输出目录不存在: {output_dir}")
        return
    
    print(f"🔍 扫描目录: {output_dir}")
    print("=" * 60)
    
    # 扫描目录中的问题文件夹
    question_pattern = re.compile(r'^q(\d+)_([a-f0-9]{8})$')
    existing_questions = set()
    incomplete_questions = []
    
    for item in output_path.iterdir():
        if item.is_dir():
            match = question_pattern.match(item.name)
            if match:
                question_num = int(match.group(1))
                question_id = match.group(2)
                
                # 检查目录中是否包含必要的文件
                required_files = [
                    f'q{question_num:04d}_{question_id}_audio_simple.mp3',
                    f'q{question_num:04d}_{question_id}_audio_question.mp3', 
                    f'q{question_num:04d}_{question_id}_audio_analysis.mp3',
                    f'q{question_num:04d}_{question_id}_meta.json'
                ]
                
                all_files_exist = all((item / file_name).exists() for file_name in required_files)
                
                if all_files_exist:
                    existing_questions.add(question_num)
                    print(f"✅ 问题 {question_num} (ID: {question_id}) - 完整")
                else:
                    incomplete_questions.append((question_num, question_id))
                    missing_files = [f for f in required_files if not (item / f).exists()]
                    print(f"⚠️  问题 {question_num} (ID: {question_id}) - 不完整，缺少: {missing_files}")
    
    print("=" * 60)
    print(f"📊 统计结果:")
    print(f"   已完成问题: {len(existing_questions)} 个")
    print(f"   不完整问题: {len(incomplete_questions)} 个")
    
    if existing_questions:
        sorted_existing = sorted(list(existing_questions))
        print(f"   完整问题列表: {sorted_existing}")
    
    if incomplete_questions:
        incomplete_nums = [num for num, _ in incomplete_questions]
        print(f"   不完整问题列表: {incomplete_nums}")
    
    print("\n🚀 使用示例:")
    print("   # 跳过已存在的问题:")
    print("   python3 question_to_speech_batch_safe.py input.md output --skip-existing")
    print("   # 重新处理所有问题:")
    print("   python3 question_to_speech_batch_safe.py input.md output")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 demo_skip_existing.py <output_dir>")
        print("示例: python3 demo_skip_existing.py output/vue")
        sys.exit(1)
    
    demo_skip_existing(sys.argv[1])