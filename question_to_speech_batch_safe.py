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
                 interval_range: tuple = (5, 15)):
        """
        安全批量处理器
        
        Args:
            input_file: 输入markdown文件路径
            output_dir: 输出目录路径
            batch_size_range: 每批处理的问题数量范围 (最小, 最大)
            interval_range: 批次间隔时间范围 (最小分钟, 最大分钟)
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.batch_size_range = batch_size_range
        self.interval_range = interval_range
        
        # 状态文件，用于记录处理进度
        self.progress_file = self.output_dir / "batch_progress.json"
        
        # 日志文件
        self.log_file = self.output_dir / "batch_processing.log"
        
        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)
        
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
        parser = MarkdownQuestionParser(self.input_file, str(self.output_dir))
        
        # 读取文件内容
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析问题块（使用原始解析逻辑）
        lines = content.split('\n')
        frontmatter_starts = []
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if i == 0 or (i + 1 < len(lines) and any(keyword in lines[i + 1] for keyword in ['id:', 'type:', 'difficulty:', 'tags:'])):
                    frontmatter_starts.append(i)
        
        question_blocks = []
        for i, start_line in enumerate(frontmatter_starts):
            if i + 1 < len(frontmatter_starts):
                end_line = frontmatter_starts[i + 1]
            else:
                end_line = len(lines)
            
            block_lines = lines[start_line:end_line]
            block_content = '\n'.join(block_lines).strip()
            
            if block_content and '题目' in block_content:
                question_blocks.append(block_content)
        
        return question_blocks
    
    async def process_single_question(self, question_block: str, question_num: int) -> bool:
        """处理单个问题"""
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
            self.log(f"✓ 问题 {question_num} 处理完成 (ID: {question_id[:8]})")
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
        self.log(f"已处理 {progress['processed_questions']} 个问题")
        
        # 从上次停止的地方继续
        current_index = progress['processed_questions']
        
        while current_index < total_questions:
            # 计算本批次大小
            batch_size = self.calculate_batch_size()
            remaining = total_questions - current_index
            actual_batch_size = min(batch_size, remaining)
            
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
        print("  python3 question_to_speech_batch_safe.py <input_file> <output_dir> [batch_size_min-max] [interval_min-max]")
        print("示例:")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output 3-5 5-15")
        print("  python3 question_to_speech_batch_safe.py vue_questions.md output 2-4 10-20")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 解析批次大小范围
    batch_size_range = (3, 5)  # 默认值
    if len(sys.argv) > 3:
        try:
            batch_parts = sys.argv[3].split('-')
            batch_size_range = (int(batch_parts[0]), int(batch_parts[1]))
        except:
            print("批次大小格式错误，使用默认值 3-5")
    
    # 解析间隔时间范围
    interval_range = (5, 15)  # 默认值
    if len(sys.argv) > 4:
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
    processor = SafeBatchProcessor(input_file, output_dir, batch_size_range, interval_range)
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main())