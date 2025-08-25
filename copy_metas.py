#!/usr/bin/env python3
"""
Meta文件复制脚本
将所有问题目录下的meta.json文件复制到统一的meta目录中
"""

import os
import shutil
import sys
from pathlib import Path
import re
import json

def copy_meta_files(source_dir: str, target_meta_dir: str = None):
    """
    复制所有问题目录下的meta.json文件到统一目录
    
    Args:
        source_dir: 源目录路径 (例如: output/vue)
        target_meta_dir: 目标meta目录 (如果不指定，默认为output/meta)
    """
    source_path = Path(source_dir)
    
    # 检查源目录是否存在
    if not source_path.exists():
        print(f"❌ 错误: 源目录 '{source_dir}' 不存在")
        return False
    
    # 设置目标目录
    if target_meta_dir is None:
        # 默认放在output/meta目录
        output_base = source_path.parent if source_path.parent.name == "output" else source_path.parent
        target_path = output_base / "meta"
    else:
        target_path = Path(target_meta_dir)
    
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
    total_failed = 0
    
    # 遍历每个问题目录
    for question_dir in sorted(question_dirs):
        print(f"\n📂 处理目录: {question_dir.name}")
        
        # 查找目录中的meta.json文件
        # 从目录名提取ID和问题编号 (格式: q{编号}_{id})
        dir_parts = question_dir.name.split('_', 1)
        if len(dir_parts) == 2:
            question_num = dir_parts[0]  # q0001
            id_prefix = dir_parts[1]     # id前8位
            expected_meta_name = f"{question_num}_{id_prefix}_meta.json"
            meta_files = [f for f in question_dir.glob("*_meta.json") if f.name == expected_meta_name]
            
            # 如果没找到新格式，尝试旧格式兼容
            if not meta_files:
                meta_files = list(question_dir.glob("*_meta.json"))
        else:
            meta_files = list(question_dir.glob("*_meta.json"))
        
        if not meta_files:
            print(f"   ⚠️  未找到meta.json文件")
            total_failed += 1
            continue
        
        # 复制每个meta文件（通常只有一个）
        for meta_file in meta_files:
            target_file = target_path / meta_file.name
            
            try:
                # 检查目标文件是否已存在
                if target_file.exists():
                    print(f"   ⏭️  跳过 {meta_file.name} (已存在)")
                    total_skipped += 1
                else:
                    # 生成新的文件名（格式：q{编号}_{id}_meta.json）
                    dir_parts = question_dir.name.split('_', 1)
                    if len(dir_parts) == 2:
                        new_filename = f"{dir_parts[0]}_{dir_parts[1]}_meta.json"
                        new_target_file = target_path / new_filename
                    else:
                        new_target_file = target_file
                    
                    # 复制文件
                    shutil.copy2(meta_file, new_target_file)
                    print(f"   ✅ 复制 {meta_file.name} -> {new_target_file.name}")
                    total_copied += 1
                    
                    # 验证JSON格式
                    try:
                        with open(new_target_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                        print(f"   ✓  JSON格式验证通过")
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  JSON格式警告: {e}")
                        
            except Exception as e:
                print(f"   ❌ 复制失败 {meta_file.name}: {e}")
                total_failed += 1
    
    # 输出统计结果
    print(f"\n{'='*50}")
    print(f"📊 复制完成统计:")
    print(f"   ✅ 成功复制: {total_copied} 个文件")
    print(f"   ⏭️  跳过文件: {total_skipped} 个文件")
    print(f"   ❌ 失败文件: {total_failed} 个文件")
    print(f"   📁 目标目录: {target_path}")
    print(f"{'='*50}")
    
    return True

def list_meta_files(meta_dir: str):
    """列出meta目录中的所有meta.json文件"""
    meta_path = Path(meta_dir)
    
    if not meta_path.exists():
        print(f"❌ 目录 '{meta_dir}' 不存在")
        return
    
    meta_files = list(meta_path.glob("*_meta.json"))
    
    if not meta_files:
        print(f"📁 目录 '{meta_dir}' 中没有meta.json文件")
        return
    
    print(f"📄 {meta_dir} 中的meta.json文件:")
    print("-" * 50)
    
    for meta_file in sorted(meta_files):
        file_size = meta_file.stat().st_size / 1024  # KB
        
        # 尝试读取meta文件信息
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            question_title = meta_data.get('question', {}).get('title', 'N/A')[:50]
            difficulty = meta_data.get('metadata', {}).get('difficulty', 'N/A')
            question_type = meta_data.get('metadata', {}).get('type', 'N/A')
            
            print(f"   📄 {meta_file.name} ({file_size:.1f} KB)")
            print(f"      题目: {question_title}...")
            print(f"      难度: {difficulty} | 类型: {question_type}")
            
        except Exception as e:
            print(f"   📄 {meta_file.name} ({file_size:.1f} KB) - 读取失败: {e}")
    
    print(f"\n📊 总计: {len(meta_files)} 个meta.json文件")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 copy_metas.py <源目录> [目标meta目录]")
        print("  python3 copy_metas.py --list <meta目录>")
        print("")
        print("示例:")
        print("  python3 copy_metas.py output/vue")
        print("  python3 copy_metas.py output/vue output/meta")
        print("  python3 copy_metas.py --list output/meta")
        sys.exit(1)
    
    # 列出meta文件模式
    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print("❌ 错误: --list 选项需要指定meta目录")
            sys.exit(1)
        list_meta_files(sys.argv[2])
        return
    
    # 复制meta文件模式
    source_dir = sys.argv[1]
    target_meta_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("📄 Meta文件复制工具")
    print("=" * 50)
    
    success = copy_meta_files(source_dir, target_meta_dir)
    
    if success:
        # 显示复制后的文件列表
        if target_meta_dir:
            actual_target = Path(target_meta_dir)
        else:
            output_base = Path(source_dir).parent if Path(source_dir).parent.name == "output" else Path(source_dir).parent
            actual_target = output_base / "meta"
        
        print(f"\n📄 查看复制结果:")
        list_meta_files(str(actual_target))

if __name__ == "__main__":
    main()