#!/usr/bin/env python3
"""
安全批量处理脚本 - 避免edge-tts API频率限制
支持随机间隔和小批量处理，防止IP被封禁
"""

import os
import sys
import json
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 导入原始的question_to_speech模块
from question_to_speech import MarkdownQuestionParser

class SafeBatchProcessor:
    def __init__(self, input_file: str, output_dir: str, 
                 batch_size_range: tuple = (3, 5),
                 interval_range: tuple = (5, 15),
                 skip_existing: bool = False,
                 debug: bool = False):
        """
        安全批量处理器
        
        Args:
            input_file: 输入markdown文件路径
            output_dir: 输出目录路径
            batch_size_range: 每批处理的问题数量范围 (最小, 最大)
            interval_range: 批次间隔时间范围 (最小分钟, 最大分钟)
            skip_existing: 是否跳过已经转换成功的题目
            debug: 是否开启调试模式
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.batch_size_range = batch_size_range
        self.interval_range = interval_range
        self.skip_existing = skip_existing
        self.debug = debug
        
        # 状态文件，用于记录处理进度
        self.progress_file = self.output_dir / "batch_progress.json"
        
        # 日志文件
        self.log_file = self.output_dir / "batch_processing.log"
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 已存在的问题集合（如果启用跳过功能）
        self.existing_questions = set()
        if self.skip_existing:
            self._scan_existing_questions()
        
    def _scan_existing_questions(self):
        """扫描输出目录中已存在的问题目录"""
        import re
        
        if not self.output_dir.exists():
            self.log("输出目录不存在，无法扫描已存在的问题")
            return
        
        # 扫描目录中的问题文件夹（格式: q{number}_{id}）
        question_pattern = re.compile(r'^q(\d+)_([a-f0-9]{8})$')
        
        existing_count = 0
        for item in self.output_dir.iterdir():
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
                        self.existing_questions.add(question_num)
                        existing_count += 1
                    else:
                        self.log(f"问题 {question_num} 目录存在但文件不完整，将重新处理")
        
        if existing_count > 0:
            self.log(f"扫描完成，发现 {existing_count} 个已存在的问题: {sorted(list(self.existing_questions))[:10]}{'...' if len(self.existing_questions) > 10 else ''}")
        else:
            self.log("未发现已存在的问题，将处理所有问题")
        
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # 输出到控制台
        print(log_message)
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_progress(self) -> Dict[str, Any]:
        """加载处理进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"加载进度文件失败: {e}")
        
        return {
            'processed_questions': 0,
            'total_questions': 0,
            'failed_questions': [],
            'completed_batches': 0,
            'start_time': None,
            'last_batch_time': None
        }
    
    def save_progress(self, progress: Dict[str, Any]):
        """保存处理进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存进度文件失败: {e}")
    
    async def get_question_blocks(self) -> List[str]:
        """获取所有问题块"""
        # 读取文件内容
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用与主脚本相同的解析逻辑（来自 question_to_speech.py）
        import re
        
        # 寻找所有frontmatter块的位置（以---开始的行）
        frontmatter_starts = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                # 检查这是否是frontmatter的开始
                # 对于第一行或者在接下来的几行中包含id:/type:等字段的情况
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
        
        question_blocks = []  # 用于存储处理后的问题块
        
        print(f"Found {len(frontmatter_starts)} frontmatter start positions: {frontmatter_starts[:5]}")
        
        # 根据frontmatter位置分割内容
        for i, start_line in enumerate(frontmatter_starts):
            # 确定当前块的结束位置
            if i + 1 < len(frontmatter_starts):
                end_line = frontmatter_starts[i + 1]
            else:
                end_line = len(lines)
            
            # 提取当前问题块的所有行
            block_lines = lines[start_line:end_line]
            block_content = '\n'.join(block_lines).strip()
            
            if block_content and '题目' in block_content:
                question_blocks.append(block_content)
                print(f"Added question block {len(question_blocks)} (first 50 chars): {block_content[:50]}...")
        
        return question_blocks
    
    async def process_single_question(self, question_block: str, question_num: int) -> bool:
        """处理单个问题"""
        # 检查是否要跳过已存在的问题
        if self.skip_existing and question_num in self.existing_questions:
            self.log(f"✓ 问题 {question_num} 已存在，跳过处理")
            return True
        
        try:
            parser = MarkdownQuestionParser(self.input_file, str(self.output_dir))
            
            # 解析问题块
            question_data = parser.parse_question_block(question_block)
            if not question_data:
                self.log(f"✗ 问题 {question_num} 解析失败")
                return False
            
            # 创建问题目录和音频文件
            await parser.create_question_directory(question_data, question_num)
            
            question_id = question_data['metadata'].get('id', f'q{question_num:04d}')
            id_prefix = str(question_id)[:8] if question_id else f'q{question_num:04d}'
            self.log(f"✓ 问题 {question_num} 处理完成 (ID: {id_prefix}, 目录: q{question_num:04d}_{id_prefix})")
            return True
            
        except Exception as e:
            self.log(f"✗ 问题 {question_num} 处理出错: {e}")
            return False
    
    async def process_batch(self, question_blocks: List[str], start_index: int, batch_size: int) -> int:
        """处理一批问题"""
        success_count = 0
        
        for i in range(batch_size):
            if start_index + i >= len(question_blocks):
                break
            
            question_num = start_index + i + 1
            block = question_blocks[start_index + i]
            
            if await self.process_single_question(block, question_num):
                success_count += 1
            
            # 问题之间小间隔（1-3秒）
            if i < batch_size - 1:
                await asyncio.sleep(random.uniform(1, 3))
        
        return success_count
    
    def calculate_next_interval(self) -> int:
        """计算下次处理的间隔时间（秒）"""
        interval_minutes = random.uniform(self.interval_range[0], self.interval_range[1])
        return int(interval_minutes * 60)
    
    def calculate_batch_size(self) -> int:
        """计算本批次处理的问题数量"""
        return random.randint(self.batch_size_range[0], self.batch_size_range[1])
    
    async def run(self):
        """运行批量处理"""
        self.log("=" * 60)
        self.log("开始安全批量处理")
        self.log(f"输入文件: {self.input_file}")
        self.log(f"输出目录: {self.output_dir}")
        self.log(f"批次大小范围: {self.batch_size_range}")
        self.log(f"间隔时间范围: {self.interval_range[0]}-{self.interval_range[1]} 分钟")
        if self.skip_existing:
            self.log(f"跳过已存在问题: 开启 (已发现 {len(self.existing_questions)} 个已存在问题)")
        else:
            self.log("跳过已存在问题: 关闭")
        self.log("=" * 60)
        
        # 获取所有问题块
        question_blocks = await self.get_question_blocks()
        total_questions = len(question_blocks)
        
        if total_questions == 0:
            self.log("未找到任何问题块，退出处理")
            return
        
        # 加载进度
        progress = self.load_progress()
        progress['total_questions'] = total_questions
        
        if progress['start_time'] is None:
            progress['start_time'] = datetime.now().isoformat()
        
        self.log(f"总共发现 {total_questions} 个问题")
        if self.skip_existing and self.existing_questions:
            remaining_questions = total_questions - len(self.existing_questions)
            self.log(f"已存在问题: {len(self.existing_questions)} 个")
            self.log(f"待处理问题: {remaining_questions} 个")
        self.log(f"已处理 {progress['processed_questions']} 个问题")
        
        # 从上次停止的地方继续
        current_index = progress['processed_questions']
        
        # 如果启用跳过功能，调整进度计数
        if self.skip_existing:
            # 重新计算实际需要处理的问题数
            questions_to_process = total_questions - len(self.existing_questions)
            already_processed_new = 0
            
            # 计算已经处理的新问题数量（排除跳过的）
            for i in range(1, current_index + 1):
                if i not in self.existing_questions:
                    already_processed_new += 1
            
            self.log(f"跳过模式: 总问题 {total_questions} 个，跳过 {len(self.existing_questions)} 个，待处理 {questions_to_process} 个")
            self.log(f"新问题中已处理 {already_processed_new} 个")
            
            # 如果所有问题都已经存在，直接结束
            if questions_to_process == 0:
                self.log("所有问题都已存在，无需处理")
                return
        
        while current_index < total_questions:
            if self.debug:
                self.log(f"[调试] 开始处理循环: current_index={current_index}, total_questions={total_questions}")
            
            # 计算本批次大小
            batch_size = self.calculate_batch_size()
            remaining = total_questions - current_index
            actual_batch_size = min(batch_size, remaining)
            
            if self.debug:
                self.log(f"[调试] 批次大小: {batch_size}, 剩余: {remaining}, 实际处理: {actual_batch_size}")
            
            self.log(f"\n--- 批次 {progress['completed_batches'] + 1} ---")
            self.log(f"处理问题 {current_index + 1}-{current_index + actual_batch_size} / {total_questions}")
            
            # 处理当前批次
            success_count = await self.process_batch(question_blocks, current_index, actual_batch_size)
            
            # 更新进度
            current_index += actual_batch_size
            progress['processed_questions'] = current_index
            progress['completed_batches'] += 1
            progress['last_batch_time'] = datetime.now().isoformat()
            
            if success_count < actual_batch_size:
                failed_count = actual_batch_size - success_count
                progress['failed_questions'].extend(range(current_index - failed_count + 1, current_index + 1))
            
            self.save_progress(progress)
            
            self.log(f"批次完成: {success_count}/{actual_batch_size} 成功")
            
            # 如果还有剩余问题，等待间隔时间
            if current_index < total_questions:
                interval_seconds = self.calculate_next_interval()
                interval_minutes = interval_seconds / 60
                
                # 如果间隔时间为0或很小，则跳过等待
                if interval_seconds <= 0:
                    self.log("间隔时间为0，立即处理下一批次...")
                elif interval_seconds < 60:
                    self.log(f"等待 {interval_seconds} 秒后处理下一批次...")
                    await asyncio.sleep(interval_seconds)
                else:
                    self.log(f"等待 {interval_minutes:.1f} 分钟后处理下一批次...")
                    self.log(f"预计完成时间: {datetime.fromtimestamp(time.time() + interval_seconds * (total_questions - current_index) / actual_batch_size).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 分段显示倒计时
                    for remaining_time in range(interval_seconds, 0, -60):
                        minutes_left = remaining_time // 60
                        if minutes_left > 0:
                            self.log(f"剩余等待时间: {minutes_left} 分钟")
                        await asyncio.sleep(min(60, remaining_time))
        
        # 处理完成
        total_time = (datetime.now() - datetime.fromisoformat(progress['start_time'])).total_seconds()
        self.log("\n" + "=" * 60)
        self.log("批量处理完成!")
        self.log(f"总共处理: {progress['processed_questions']}/{total_questions} 个问题")
        self.log(f"总耗时: {total_time/3600:.1f} 小时")
        self.log(f"失败问题数: {len(progress['failed_questions'])}")
        if progress['failed_questions']:
            self.log(f"失败问题编号: {progress['failed_questions']}")
        self.log("=" * 60)

async def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python3 question_to_speech_batch_safe.py <input_file> <output_dir> [batch_size_min-max] [interval_min-max] [--skip-existing] [--debug]")
        print("示例:")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output 3-5 5-15")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output 2-4 10-20 --skip-existing")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output 1-1 0-0 --skip-existing --debug")
        print("参数说明:")
        print("  --skip-existing: 跳过已经转换成功的题目，从输出目录扫描已存在的问题文件夹")
        print("  --debug: 开启调试模式，显示更详细的日志信息")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 检查是否启用跳过已存在的问题
    skip_existing = '--skip-existing' in sys.argv
    # 检查是否开启调试模式
    debug = '--debug' in sys.argv
    
    # 解析批次大小范围
    batch_size_range = (3, 5)  # 默认值
    if len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
        try:
            batch_parts = sys.argv[3].split('-')
            batch_size_range = (int(batch_parts[0]), int(batch_parts[1]))
        except:
            print("批次大小格式错误，使用默认值 3-5")
    
    # 解析间隔时间范围
    interval_range = (5, 15)  # 默认值
    if len(sys.argv) > 4 and not sys.argv[4].startswith('--'):
        try:
            interval_parts = sys.argv[4].split('-')
            interval_range = (int(interval_parts[0]), int(interval_parts[1]))
        except:
            print("间隔时间格式错误，使用默认值 5-15 分钟")
    
    # 检查输入文件
    if not os.path.exists(input_file):
        print(f"✗ 错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    # 创建处理器并运行
    processor = SafeBatchProcessor(input_file, output_dir, batch_size_range, interval_range, skip_existing, debug)
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main())