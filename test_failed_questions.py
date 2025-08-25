#!/usr/bin/env python3
"""
测试之前失败的问题是否现在可以正确解析
"""

import asyncio
from question_to_speech import MarkdownQuestionParser

async def test_failed_questions():
    """测试之前失败的问题编号"""
    
    failed_question_ids = [
        "fac17292-5e10-4948-bd65-c553edf01cb4",  # Question 7
        "5c73cd33-c6cd-4eb7-8bef-0c213c301db8",  # Question 8  
        "e176a38d-a0ad-46b9-8584-8f269801008b",  # Question 9
        "090b9d95-af93-4c9b-9a82-d45f7c2eef81",  # Question 17
        "84d6c3ff-3786-4554-84ba-00012764a836"   # Question 19
    ]
    
    input_file = "vue/vue_questions-md-format_uuid.md"
    output_dir = "test_output"
    
    parser = MarkdownQuestionParser(input_file, output_dir)
    
    # 读取文件内容
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
    
    print(f"Found {len(question_blocks)} question blocks total")
    
    # 测试每个之前失败的问题
    success_count = 0
    for i, block in enumerate(question_blocks):
        # 检查这个块是否包含失败的ID之一
        contains_failed_id = any(failed_id in block for failed_id in failed_question_ids)
        
        if contains_failed_id:
            # 获取这个块的ID
            id_match = re.search(r'id: ([a-f0-9-]+)', block)
            block_id = id_match.group(1) if id_match else "unknown"
            
            question_num = i + 1
            print(f"\nTesting Question {question_num} (ID: {block_id[:8]})")
            
            try:
                # 尝试解析问题块
                question_data = parser.parse_question_block(block)
                if question_data:
                    print(f"  ✓ Parsing successful!")
                    print(f"    Question: {question_data['question'][:50]}...")
                    print(f"    Answer: {question_data['simple_answer'][:50]}...")
                    print(f"    Analysis: {question_data['detailed_analysis'][:50]}...")
                    success_count += 1
                else:
                    print(f"  ✗ Parsing failed - returned None")
            except Exception as e:
                print(f"  ✗ Parsing failed with error: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Successfully parsed: {success_count}/{len(failed_question_ids)} previously failed questions")
    
    if success_count == len(failed_question_ids):
        print("🎉 All previously failed questions can now be parsed successfully!")
    else:
        print("⚠️  Some questions still have parsing issues")

if __name__ == "__main__":
    asyncio.run(test_failed_questions())