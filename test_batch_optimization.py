#!/usr/bin/env python3
"""
测试批次优化功能
演示当批次内所有问题都已存在时，跳过等待直接进入下一批次
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, '/Users/xiongweiliu/workspaces/text-to-speech')

from question_to_speech_batch_safe import SafeBatchProcessor

async def test_batch_optimization():
    """测试批次优化功能"""
    
    input_file = "vue/vue_questions-md-format_uuid.md"
    output_dir = "output/vue"
    
    print("🔍 创建优化的批次处理器...")
    processor = SafeBatchProcessor(
        input_file=input_file,
        output_dir=output_dir,
        batch_size_range=(3, 3),  # 每批3个问题
        interval_range=(2, 2),    # 2分钟间隔
        skip_existing=True,
        debug=True
    )
    
    print("📊 检查现有问题...")
    print(f"   已发现现有问题: {len(processor.existing_questions)} 个")
    
    print("📖 读取问题块...")
    question_blocks = await processor.get_question_blocks()
    print(f"   总问题数: {len(question_blocks)}")
    
    # 找出缺失的问题
    missing_questions = []
    for i in range(1, len(question_blocks) + 1):
        if i not in processor.existing_questions:
            missing_questions.append(i)
    
    print(f"📋 缺失的问题: {missing_questions}")
    
    print("🚀 开始优化的批次处理...")
    print("   注意观察: 当整个批次的问题都已存在时，会跳过等待直接进入下一批次")
    print()
    
    try:
        await processor.run()
        print("✅ 处理完成")
    except Exception as e:
        print(f"❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("测试批次优化功能")
    print("演示：批次内所有问题都已存在时，跳过等待直接进入下一批次")
    print("=" * 60)
    asyncio.run(test_batch_optimization())