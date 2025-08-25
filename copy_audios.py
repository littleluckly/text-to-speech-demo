#!/usr/bin/env python3
"""
音频文件复制脚本
将所有问题目录下的音频文件复制到统一的audios目录中
"""

import os
import shutil
import sys
from pathlib import Path
import re

def copy_audio_files(source_dir: str, target_audio_dir: str = None):
    """
    复制所有问题目录下的音频文件到统一目录
    
    Args:
        source_dir: 源目录路径 (例如: output/vue)
        target_audio_dir: 目标音频目录 (如果不指定，默认为output/audios)
    """
    source_path = Path(source_dir)
    
    # 检查源目录是否存在
    if not source_path.exists():
        print(f"❌ 错误: 源目录 '{source_dir}' 不存在")
        return False
    
    # 设置目标目录
    if target_audio_dir is None:
        target_path = Path("output/audios")
    else:
        target_path = Path(target_audio_dir)
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 目标目录: {target_path}")
    
    # 查找所有问题目录（格式：q{编号}_{id}）
    question_dirs = []
    pattern = re.compile(r'^q\d{4}_[a-f0-9]{8}$')
    
    for item in source_path.iterdir():
        if item.is_dir() and pattern.match(item.name):
            question_dirs.append(item)
    
    if not question_dirs:
        print("⚠️  未找到符合格式的问题目录 (格式: q{编号}_{id})")
        return False
    
    print(f"🔍 找到 {len(question_dirs)} 个问题目录")
    
    # 统计信息
    total_copied = 0
    total_skipped = 0
    
    # 遍历每个问题目录
    for question_dir in sorted(question_dirs):
        print(f"\n📂 处理目录: {question_dir.name}")
        
        # 查找目录中的所有音频文件
        audio_files = list(question_dir.glob("*.mp3"))
        
        if not audio_files:
            print(f"   ⚠️  未找到音频文件")
            continue
        
        # 复制每个音频文件
        for audio_file in audio_files:
            target_file = target_path / audio_file.name
            
            try:
                # 检查目标文件是否已存在
                if target_file.exists():
                    print(f"   ⏭️  跳过 {audio_file.name} (已存在)")
                    total_skipped += 1
                else:
                    # 复制文件
                    shutil.copy2(audio_file, target_file)
                    print(f"   ✅ 复制 {audio_file.name}")
                    total_copied += 1
            except Exception as e:
                print(f"   ❌ 复制失败 {audio_file.name}: {e}")
    
    # 输出统计结果
    print(f"\n{'='*50}")
    print(f"📊 复制完成统计:")
    print(f"   ✅ 成功复制: {total_copied} 个文件")
    print(f"   ⏭️  跳过文件: {total_skipped} 个文件")
    print(f"   📁 目标目录: {target_path}")
    print(f"{'='*50}")
    
    return True

def list_audio_files(audios_dir: str):
    """列出audios目录中的所有音频文件"""
    audios_path = Path(audios_dir)
    
    if not audios_path.exists():
        print(f"❌ 目录 '{audios_dir}' 不存在")
        return
    
    audio_files = list(audios_path.glob("*.mp3"))
    
    if not audio_files:
        print(f"📁 目录 '{audios_dir}' 中没有音频文件")
        return
    
    print(f"🎵 {audios_dir} 中的音频文件:")
    print("-" * 50)
    
    # 按类型分组显示
    simple_files = [f for f in audio_files if "audio_simple" in f.name]
    question_files = [f for f in audio_files if "audio_question" in f.name]
    analysis_files = [f for f in audio_files if "audio_analysis" in f.name]
    
    for category, files, emoji in [
        ("简答音频", simple_files, "💡"),
        ("问题音频", question_files, "❓"),
        ("解析音频", analysis_files, "📖")
    ]:
        if files:
            print(f"\n{emoji} {category} ({len(files)} 个):")
            for audio_file in sorted(files):
                file_size = audio_file.stat().st_size / 1024  # KB
                print(f"   - {audio_file.name} ({file_size:.1f} KB)")
    
    print(f"\n📊 总计: {len(audio_files)} 个音频文件")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 copy_audios.py <源目录> [目标音频目录]")
        print("  python3 copy_audios.py --list <音频目录>")
        print("")
        print("示例:")
        print("  python3 copy_audios.py output/vue")
        print("  python3 copy_audios.py output/vue output/audios")
        print("  python3 copy_audios.py --list output/audios")
        sys.exit(1)
    
    # 列出音频文件模式
    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print("❌ 错误: --list 选项需要指定音频目录")
            sys.exit(1)
        list_audio_files(sys.argv[2])
        return
    
    # 复制音频文件模式
    source_dir = sys.argv[1]
    target_audio_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🎵 音频文件复制工具")
    print("=" * 50)
    
    success = copy_audio_files(source_dir, target_audio_dir)
    
    if success:
        # 显示复制后的文件列表
        actual_target = Path(target_audio_dir) if target_audio_dir else Path("output/audios")
        print(f"\n🎵 查看复制结果:")
        list_audio_files(str(actual_target))

if __name__ == "__main__":
    main()