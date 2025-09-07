#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

"""
安全批量JSON转语音处理脚本 - 避免edge-tts API频率限制
支持随机间隔和小批量处理，防止IP被封禁
"""

# 导入单个JSON转语音的转换器
from json_to_speech import JsonToSpeechConverter

class SafeBatchJsonToSpeechProcessor:
    def __init__(self, input_dir: str, output_dir: str, 
                 batch_size_range: tuple = (3, 5),
                 interval_range: tuple = (5, 15),
                 skip_existing: bool = False,
                 debug: bool = False):
        """
        安全批量JSON转语音处理器
        
        Args:
            input_dir: 输入JSON文件目录
            output_dir: 输出音频文件目录
            batch_size_range: 每批处理的文件数量范围 (最小, 最大)
            interval_range: 批次间隔时间范围 (最小分钟, 最大分钟)
            skip_existing: 是否跳过已经生成的音频文件
            debug: 是否开启调试模式
        """
        self.input_dir = Path(input_dir)
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
        
        # 已存在的音频文件集合（如果启用跳过功能）
        self.existing_audios = set()
        if self.skip_existing:
            self._scan_existing_audios()
    
    def _scan_existing_audios(self):
        """扫描输出目录中已存在的音频文件"""
        import re
        
        if not self.output_dir.exists():
            self.log("输出目录不存在，无法扫描已存在的音频文件")
            return
        
        # 扫描目录中的音频文件（格式: audioKey_audio_xxx.mp3）
        audio_pattern = re.compile(r'^(.*?)_audio_.*\.mp3$')
        
        existing_count = 0
        for item in self.output_dir.iterdir():
            if item.is_file() and item.suffix == '.mp3':
                match = audio_pattern.match(item.name)
                if match:
                    audio_key = match.group(1)
                    self.existing_audios.add(audio_key)
                    existing_count += 1
        
        if existing_count > 0:
            self.log(f"扫描完成，发现 {existing_count} 个已存在的音频文件，对应的 {len(self.existing_audios)} 个音频键")
        else:
            self.log("未发现已存在的音频文件，将处理所有JSON文件")
    
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
            'processed_files': 0,
            'total_files': 0,
            'failed_files': [],
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
    
    def get_json_files(self) -> List[Path]:
        """获取所有JSON文件"""
        if not self.input_dir.exists():
            self.log(f"输入目录不存在: {self.input_dir}")
            return []
        
        json_files = list(self.input_dir.glob("*.json"))
        json_files.sort()  # 按文件名排序
        
        return json_files
    
    async def process_single_file(self, json_file: Path) -> bool:
        """处理单个JSON文件"""
        try:
            # 先读取audioKey以检查是否需要跳过
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            audio_key = data.get('audioKey')
            
            # 检查是否要跳过已存在的音频
            if self.skip_existing and audio_key and audio_key in self.existing_audios:
                self.log(f"✓ 文件 {json_file.name} 已存在对应的音频文件，跳过处理")
                return True
            
            # 创建转换器并处理文件
            converter = JsonToSpeechConverter(str(json_file), str(self.output_dir))
            success = await converter.convert()
            
            if success:
                # 如果处理成功，将audioKey添加到已存在集合
                if audio_key:
                    self.existing_audios.add(audio_key)
                self.log(f"✓ 文件 {json_file.name} 处理完成")
            
            return success
        except Exception as e:
            self.log(f"✗ 文件 {json_file.name} 处理出错: {e}")
            return False
    
    async def process_batch(self, json_files: List[Path], start_index: int, batch_size: int) -> Dict[str, int]:
        """处理一批JSON文件"""
        success_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i in range(batch_size):
            if start_index + i >= len(json_files):
                break
            
            json_file = json_files[start_index + i]
            
            try:
                # 预先检查是否需要跳过
                audio_key = None
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    audio_key = data.get('audioKey')
                except:
                    pass  # 如果无法读取文件，不跳过，让process_single_file处理错误
                
                if self.skip_existing and audio_key and audio_key in self.existing_audios:
                    skipped_count += 1
                    if self.debug:
                        self.log(f"[调试] 文件 {json_file.name} 已存在对应的音频文件，跳过处理")
                else:
                    if await self.process_single_file(json_file):
                        success_count += 1
                    else:
                        failed_count += 1
                
                # 文件之间小间隔（1-3秒）
                if i < batch_size - 1:
                    await asyncio.sleep(random.uniform(1, 3))
            except Exception as e:
                self.log(f"✗ 处理文件 {json_file.name} 时发生异常: {e}")
                failed_count += 1
        
        return {
            'success': success_count,
            'skipped': skipped_count,
            'failed': failed_count,
            'total': success_count + skipped_count + failed_count
        }
    
    def calculate_next_interval(self) -> int:
        """计算下次处理的间隔时间（秒）"""
        interval_minutes = random.uniform(self.interval_range[0], self.interval_range[1])
        return int(interval_minutes * 60)
    
    def calculate_batch_size(self) -> int:
        """计算本批次处理的文件数量"""
        return random.randint(self.batch_size_range[0], self.batch_size_range[1])
    
    async def run(self):
        """运行批量处理"""
        self.log("=" * 60)
        self.log("开始安全批量JSON转语音处理")
        self.log(f"输入目录: {self.input_dir}")
        self.log(f"输出目录: {self.output_dir}")
        self.log(f"批次大小范围: {self.batch_size_range}")
        self.log(f"间隔时间范围: {self.interval_range[0]}-{self.interval_range[1]} 分钟")
        if self.skip_existing:
            self.log(f"跳过已存在音频: 开启 (已发现 {len(self.existing_audios)} 个已存在的音频键)")
        else:
            self.log("跳过已存在音频: 关闭")
        self.log("=" * 60)
        
        # 获取所有JSON文件
        json_files = self.get_json_files()
        total_files = len(json_files)
        
        if total_files == 0:
            self.log("未找到任何JSON文件，退出处理")
            return
        
        # 加载进度
        progress = self.load_progress()
        progress['total_files'] = total_files
        
        if progress['start_time'] is None:
            progress['start_time'] = datetime.now().isoformat()
        
        self.log(f"总共发现 {total_files} 个JSON文件")
        if self.skip_existing and self.existing_audios:
            # 计算预计可以跳过的文件数
            skip_candidates = 0
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if data.get('audioKey') in self.existing_audios:
                        skip_candidates += 1
                except:
                    pass
            
            self.log(f"预计可跳过: {skip_candidates} 个文件")
            self.log(f"待处理文件: {total_files - skip_candidates} 个")
        self.log(f"已处理 {progress['processed_files']} 个文件")
        
        # 从上次停止的地方继续
        current_index = progress['processed_files']
        
        while current_index < total_files:
            if self.debug:
                self.log(f"[调试] 开始处理循环: current_index={current_index}, total_files={total_files}")
            
            # 计算本批次大小
            batch_size = self.calculate_batch_size()
            remaining = total_files - current_index
            actual_batch_size = min(batch_size, remaining)
            
            if self.debug:
                self.log(f"[调试] 批次大小: {batch_size}, 剩余: {remaining}, 实际处理: {actual_batch_size}")
            
            self.log(f"\n--- 批次 {progress['completed_batches'] + 1} ---")
            self.log(f"处理文件 {current_index + 1}-{current_index + actual_batch_size} / {total_files}")
            
            # 处理当前批次
            batch_result = await self.process_batch(json_files, current_index, actual_batch_size)
            
            # 更新进度
            current_index += actual_batch_size
            progress['processed_files'] = current_index
            progress['completed_batches'] += 1
            progress['last_batch_time'] = datetime.now().isoformat()
            
            # 处理失败的文件
            if batch_result['failed'] > 0:
                failed_files_start = current_index - batch_result['failed']
                for i in range(failed_files_start, failed_files_start + batch_result['failed']):
                    if i < len(json_files):
                        progress['failed_files'].append(json_files[i].name)
            
            self.save_progress(progress)
            
            # 显示批次结果
            if batch_result['skipped'] > 0:
                self.log(f"批次完成: {batch_result['success']}/{actual_batch_size} 成功, {batch_result['skipped']} 个跳过, {batch_result['failed']} 个失败")
            else:
                self.log(f"批次完成: {batch_result['success']}/{actual_batch_size} 成功")
            
            # 如果还有剩余文件，等待间隔时间
            if current_index < total_files:
                # 检查是否整个批次都被跳过（即所有文件都已存在）
                if self.skip_existing and batch_result['skipped'] == actual_batch_size and batch_result['success'] == 0 and batch_result['failed'] == 0:
                    self.log("整个批次的文件都已存在，跳过等待，立即处理下一批次")
                    continue  # 直接进入下一个循环，不等待
                
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
                    self.log(f"预计完成时间: {datetime.fromtimestamp(time.time() + interval_seconds * (total_files - current_index) / actual_batch_size).strftime('%Y-%m-%d %H:%M:%S')}")
                    
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
        self.log(f"总共处理: {progress['processed_files']}/{total_files} 个文件")
        self.log(f"总耗时: {total_time/3600:.1f} 小时")
        self.log(f"失败文件数: {len(progress['failed_files'])}")
        if progress['failed_files']:
            self.log(f"失败文件: {', '.join(progress['failed_files'][:5])}{'...' if len(progress['failed_files']) > 5 else ''}")
        self.log("=" * 60)

# 预定义的处理模式
MODES = {
    "conservative": {
        "batch_size_range": (2, 3),
        "interval_range": (10, 20),
        "description": "保守模式 - 每批2-3个文件，间隔10-20分钟，适用于100+个文件的大目录"
    },
    "balanced": {
        "batch_size_range": (3, 5),
        "interval_range": (5, 15),
        "description": "平衡模式 - 每批3-5个文件，间隔5-15分钟，适用于20-100个文件的中等目录"
    },
    "aggressive": {
        "batch_size_range": (5, 8),
        "interval_range": (2, 8),
        "description": "激进模式 - 每批5-8个文件，间隔2-8分钟，适用于<20个文件的小目录"
    },
    "test": {
        "batch_size_range": (1, 1),
        "interval_range": (0.5, 1),
        "description": "测试模式 - 每批1个文件，间隔0.5-1分钟，适用于测试和调试"
    }
}

async def main():
    """主函数"""
    if len(sys.argv) < 3 or len(sys.argv) > 6:
        print("使用方法:")
        print("  python3 json_to_speech_batch_safe.py <input_dir> <output_dir> [mode/custom_params] [--skip-existing] [--debug]")
        print("预定义模式:")
        for mode_name, mode_info in MODES.items():
            print(f"  {mode_name}: {mode_info['description']}")
        print("自定义参数格式:")
        print("  custom <batch_size_min>-<batch_size_max> <interval_min>-<interval_max>")
        print("示例:")
        print("  python3 json_to_speech_batch_safe.py questions-json questions-audio")
        print("  python3 json_to_speech_batch_safe.py questions-json questions-audio balanced --skip-existing")
        print("  python3 json_to_speech_batch_safe.py questions-json questions-audio custom 2-4 8-12 --skip-existing")
        print("参数说明:")
        print("  --skip-existing: 跳过已经生成的音频文件")
        print("  --debug: 开启调试模式，显示更详细的日志信息")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 检查是否启用跳过已存在的文件
    skip_existing = '--skip-existing' in sys.argv
    # 检查是否开启调试模式
    debug = '--debug' in sys.argv
    
    # 解析处理模式或自定义参数
    batch_size_range = (3, 5)  # 默认值（平衡模式）
    interval_range = (5, 15)   # 默认值（平衡模式）
    
    if len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
        mode_or_custom = sys.argv[3]
        
        # 检查是否是预定义模式
        if mode_or_custom in MODES:
            mode_info = MODES[mode_or_custom]
            batch_size_range = mode_info['batch_size_range']
            interval_range = mode_info['interval_range']
            print(f"使用预定义模式: {mode_or_custom} - {mode_info['description']}")
        # 检查是否是自定义模式
        elif mode_or_custom == 'custom' and len(sys.argv) > 5:
            try:
                # 解析自定义参数
                batch_parts = sys.argv[4].split('-')
                interval_parts = sys.argv[5].split('-')
                
                batch_size_range = (int(batch_parts[0]), int(batch_parts[1]))
                interval_range = (int(interval_parts[0]), int(interval_parts[1]))
                
                # 确保参数有效
                if batch_size_range[0] <= 0 or batch_size_range[1] < batch_size_range[0]:
                    raise ValueError("无效的批次大小范围")
                if interval_range[0] < 0 or interval_range[1] < interval_range[0]:
                    raise ValueError("无效的间隔时间范围")
                
                print(f"使用自定义参数: 批次大小 {batch_size_range}, 间隔时间 {interval_range} 分钟")
            except Exception as e:
                print(f"自定义参数格式错误: {e}")
                print("使用默认平衡模式")
        else:
            print(f"未知的模式: {mode_or_custom}")
            print("使用默认平衡模式")
    else:
        print("使用默认平衡模式")
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"✗ 错误: 输入目录 '{input_dir}' 不存在")
        sys.exit(1)
    
    # 创建处理器并运行
    processor = SafeBatchJsonToSpeechProcessor(input_dir, output_dir, batch_size_range, interval_range, skip_existing, debug)
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main())