#!/usr/bin/env python3
"""
重新处理之前失败的问题
仅处理批处理进度中记录的失败问题
"""

import asyncio
import json
import os
from pathlib import Path
from question_to_speech import MarkdownQuestionParser

async def reprocess_failed_questions():
    """重新处理失败的问题"""
    
    input_file = "vue/vue_questions-md-format_uuid.md"
    output_dir = "output/vue"
    progress_file = Path(output_dir) / "batch_progress.json"
    
    # 读取进度文件
    if not progress_file.exists():
        print("❌ 进度文件不存在，无法确定失败的问题")
        return
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
    
    failed_questions = progress.get('failed_questions', [])
    
    if not failed_questions:
        print("✅ 没有失败的问题需要重新处理")
        return
    
    print(f"发现 {len(failed_questions)} 个失败的问题: {failed_questions}")
    
    # 读取和解析文件内容
    parser = MarkdownQuestionParser(input_file, output_dir)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用和批处理脚本相同的分割逻辑
    import re
    
    # 寻找所有frontmatter块的位置
    frontmatter_starts = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if i == 0:
                frontmatter_starts.append(i)
            else:
                # 检查后面的几行是否包含 YAML 字段
                found_yaml_field = False
                for check_line in range(i + 1, min(i + 5, len(lines))):
                    if any(keyword in lines[check_line] for keyword in ['id:', 'type:', 'difficulty:', 'tags:']):
                        found_yaml_field = True
                        break
                if found_yaml_field:
                    frontmatter_starts.append(i)
    
    question_blocks = []
    
    # 根据frontmatter位置分割内容
    for i, start_line in enumerate(frontmatter_starts):
        if i + 1 < len(frontmatter_starts):
            end_line = frontmatter_starts[i + 1]
        else:
            end_line = len(lines)
        
        block_lines = lines[start_line:end_line]
        block_content = '\n'.join(block_lines).strip()
        
        if block_content and '题目' in block_content:
            question_blocks.append(block_content)
    
    print(f"找到 {len(question_blocks)} 个问题块")
    
    # 重新处理失败的问题
    success_count = 0
    newly_failed = []
    
    for question_num in failed_questions:
        if question_num <= len(question_blocks):
            block = question_blocks[question_num - 1]  # 转换为0索引
            
            try:
                print(f"\n重新处理问题 {question_num}...")
                
                # 解析问题块
                question_data = parser.parse_question_block(block)
                if not question_data:
                    print(f"✗ 问题 {question_num} 解析失败")
                    newly_failed.append(question_num)
                    continue
                
                # 创建问题目录和音频文件
                await parser.create_question_directory(question_data, question_num)
                
                question_id = question_data['metadata'].get('id', f'q{question_num:04d}')
                id_prefix = str(question_id)[:8] if question_id else f'q{question_num:04d}'
                print(f"✓ 问题 {question_num} 处理完成 (ID: {id_prefix}, 目录: q{question_num:04d}_{id_prefix})")
                success_count += 1
                
            except Exception as e:
                print(f"✗ 问题 {question_num} 处理出错: {e}")
                newly_failed.append(question_num)
        else:
            print(f"⚠️ 问题编号 {question_num} 超出范围")
            newly_failed.append(question_num)
    
    # 更新进度文件
    if success_count > 0:
        # 从失败列表中移除成功处理的问题
        progress['failed_questions'] = newly_failed
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 进度文件已更新")
    
    print(f"\n=== 重新处理结果 ===")
    print(f"原失败问题数: {len(failed_questions)}")
    print(f"成功处理: {success_count}")
    print(f"仍然失败: {len(newly_failed)}")
    
    if newly_failed:
        print(f"仍然失败的问题: {newly_failed}")
    else:
        print("🎉 所有失败的问题都已成功重新处理!")

if __name__ == "__main__":
    asyncio.run(reprocess_failed_questions())