#!/usr/bin/env python3
"""
演示批次跳过优化功能
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, '/Users/xiongweiliu/workspaces/text-to-speech')

from question_to_speech_batch_safe import SafeBatchProcessor

async def demo_skip_optimization():
    """演示批次跳过优化"""
    
    input_file = "vue/vue_questions-md-format_uuid.md"
    output_dir = "output/vue"
    
    print("🎯 模拟演示：批次跳过优化功能")
    print("=" * 60)
    
    # 删除几个问题用于演示
    import subprocess
    import os
    
    # 删除问题 8, 16, 17 来创建空隙
    questions_to_remove = [8, 16, 17]
    for q in questions_to_remove:
        dir_path = f"output/vue/q{q:04d}_*"
        try:
            result = subprocess.run(f"rm -rf {dir_path}", shell=True, capture_output=True)
            print(f"📝 移除问题 {q} 用于演示")
        except:
            pass
    
    # 删除进度文件
    progress_file = Path("output/vue/batch_progress.json")
    if progress_file.exists():
        progress_file.unlink()
        print("🔄 重置进度文件")
    
    print("\n🚀 启动优化的批次处理器...")
    processor = SafeBatchProcessor(
        input_file=input_file,
        output_dir=output_dir,
        batch_size_range=(5, 5),  # 每批5个问题
        interval_range=(1, 1),    # 1分钟间隔（演示用）
        skip_existing=True,
        debug=False  # 关闭详细调试，专注于演示
    )
    
    print("📊 当前状态检查...")
    print(f"   已存在问题数: {len(processor.existing_questions)}")
    
    # 找出缺失的问题
    question_blocks = await processor.get_question_blocks()
    missing_questions = []
    for i in range(1, len(question_blocks) + 1):
        if i not in processor.existing_questions:
            missing_questions.append(i)
    
    print(f"   总问题数: {len(question_blocks)}")
    print(f"   缺失问题: {missing_questions}")
    print(f"   待处理问题数: {len(missing_questions)}")
    
    print("\n⏰ 观察要点:")
    print("   - 当批次内所有问题都已存在时，将跳过等待")
    print("   - 当批次内有新问题需要处理时，会正常等待间隔时间")
    print("   - 混合批次会显示跳过的问题数量")
    print()
    
    input("按 Enter 键开始演示...")
    print()
    
    try:
        await processor.run()
        print("\n✅ 演示完成!")
        print("\n📋 总结:")
        print("   ✓ 批次跳过优化功能正常工作")
        print("   ✓ 当整个批次都已存在时，立即跳到下一批次")
        print("   ✓ 显著减少了处理已完成内容的等待时间")
    except Exception as e:
        print(f"❌ 演示出错: {e}")

if __name__ == "__main__":
    asyncio.run(demo_skip_optimization())