#!/usr/bin/env python3
"""
测试脚本执行流程
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, '/Users/xiongweiliu/workspaces/text-to-speech')

from question_to_speech_batch_safe import SafeBatchProcessor

async def test_flow():
    """测试执行流程"""
    
    input_file = "vue/vue_questions-md-format_uuid.md"
    output_dir = "output/vue"
    
    print("🔍 创建处理器...")
    processor = SafeBatchProcessor(
        input_file=input_file,
        output_dir=output_dir,
        batch_size_range=(1, 1),
        interval_range=(0, 0),
        skip_existing=True,
        debug=True
    )
    
    print("📊 检查现有问题...")
    print(f"   已发现现有问题: {len(processor.existing_questions)} 个")
    print(f"   现有问题列表: {sorted(list(processor.existing_questions))[:10]}")
    
    print("📖 读取问题块...")
    question_blocks = await processor.get_question_blocks()
    print(f"   总问题数: {len(question_blocks)}")
    
    print("🚀 开始处理...")
    try:
        await processor.run()
        print("✅ 处理完成")
    except Exception as e:
        print(f"❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("测试脚本执行流程")
    print("=" * 50)
    asyncio.run(test_flow())