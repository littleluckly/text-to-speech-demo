#!/usr/bin/env python3
import os
import sys
import json
import re
import asyncio
from pathlib import Path
import edge_tts
from typing import Dict, Any, Optional

"""
JSON文件转语音工具
将questions-json目录下的JSON文件中的question_markdown,answer_simple_markdown,answer_detail_markdown,answer_analysis_markdown
分别通过edge-tts转成语音文件，文件名称格式为<audioKey>_audio_<字段名去掉markdown>.mp3
"""

class JsonToSpeechConverter:
    def __init__(self, input_file: str, output_dir: str = "questions-audio"):
        """
        初始化JSON转语音转换器
        
        Args:
            input_file: 输入的JSON文件路径
            output_dir: 输出音频文件的目录
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 首选的中文语音列表（按优先级排序）
        self.preferred_voices = [
            "zh-CN-YunyangNeural",  # 云杨（男）
            "zh-CN-YunjianNeural",  # 云健（男）
            "zh-CN-YunxiNeural",    # 云溪（女）
            "zh-CN-YunhaoNeural",   # 云浩（男）
            "zh-CN-YunzeNeural"     # 云泽（男）
        ]
        
        self.selected_voice = None
    
    async def initialize_voice(self):
        """初始化语音选择"""
        try:
            # 创建edge-tts语音管理器
            voices_manager = await edge_tts.VoicesManager.create()
            all_voices = voices_manager.find()
            
            # 尝试从首选语音列表中找到可用的语音
            for voice in self.preferred_voices:
                matching_voices = [v for v in all_voices if v["Name"] == voice]
                if matching_voices:
                    self.selected_voice = voice
                    print(f"✓ Found preferred voice: {self.selected_voice}")
                    break
            
            # 如果没有找到首选语音，则查找任何中文(zh-CN)语音作为备选
            if not self.selected_voice:
                print("No preferred voices found, looking for any zh-CN voice...")
                zh_cn_voices = [v for v in all_voices if v["Locale"].startswith("zh-CN")]
                if zh_cn_voices:
                    self.selected_voice = zh_cn_voices[0]["Name"]
                    print(f"✓ Using fallback zh-CN voice: {self.selected_voice}")
                else:
                    print("⚠️  No zh-CN voices found! This might cause issues.")
                    self.selected_voice = "zh-CN-YunyangNeural"  # 默认备选语音
        except Exception as e:
            print(f"Error initializing voice: {e}")
            self.selected_voice = "zh-CN-YunyangNeural"  # 默认备选语音
    
    def preprocess_text_for_speech(self, text: str) -> str:
        """预处理文本以提高语音合成的可读性"""
        # 移除Markdown代码块（```xxx```格式）
        text = re.sub(r'\`\`\`[^`]*\`\`\`', '', text, flags=re.DOTALL)
        
        # 移除行内代码（`code`格式）
        text = re.sub(r'`([^`]+)`', '', text)
        
        # 移除Markdown列表符号（-, *, +）
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # 移除编号列表符号（1. 2. 等）
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 移除剩余的Markdown符号（# * _ ~ `）
        text = re.sub(r'[#*_~`]', '', text)
        
        # 替换箭头和特殊符号为中文描述并添加停顿
        text = re.sub(r'→', '，然后', text)
        text = re.sub(r'←', '，返回', text)
        text = re.sub(r'↑', '，向上', text)
        text = re.sub(r'↓', '，向下', text)
        
        # 在Vue生命周期方法和技术术语之间添加停顿
        lifecycle_methods = [
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeDestroy', 'destroyed',
            'beforeUnmount', 'unmounted', 'activated', 'deactivated'
        ]
        
        for method in lifecycle_methods:
            text = re.sub(rf'\b{method}\b', f'{method}，', text)
        
        # 在由空格分隔的代码元素之间添加停顿
        text = re.sub(r'(\w+)\s+(\w+)\s+(\w+)', r'\1，\2，\3', text)
        
        # 在括号和方括号周围添加停顿
        text = re.sub(r'\(', '，开括号，', text)
        text = re.sub(r'\)', '，闭括号，', text)
        text = re.sub(r'\[', '，开方括号，', text)
        text = re.sub(r'\]', '，闭方括号，', text)
        text = re.sub(r'\{', '，开花括号，', text)
        text = re.sub(r'\}', '，闭花括号，', text)
        
        # 在等号和运算符周围添加停顿
        text = re.sub(r'=', '，等于，', text)
        text = re.sub(r'\+', '，加，', text)
        text = re.sub(r'\*', '，乘，', text)
        text = re.sub(r'/', '，除，', text)
        
        # 在驼峰命名法单词之间添加停顿
        text = re.sub(r'([a-z])([A-Z])', r'\1，\2', text)
        
        # 在方法调用的点号周围添加停顿
        text = re.sub(r'\.', '，点，', text)
        
        # 清理连续的逗号
        text = re.sub(r'，+', '，', text)
        
        # 确保中文标点符号周围的适当间距
        text = re.sub(r'，\s*，', '，', text)
        text = re.sub(r'，\s*$', '。', text)  # 以句号结束而不是逗号
        
        return text.strip()
    
    async def generate_audio(self, text: str, output_path: Path) -> bool:
        """生成单个音频文件"""
        if not self.selected_voice:
            await self.initialize_voice()
        
        try:
            # 预处理文本以提高语音可读性
            processed_text = self.preprocess_text_for_speech(text)
            
            # 为TTS做额外的文本清理
            # 保留中文、英文、数字、空格和基本中文标点符号
            clean_text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：]', ' ', processed_text)
            clean_text = re.sub(r'\s+', ' ', clean_text)  # 规范化空白字符
            clean_text = clean_text.strip()
            
            # 如果文本为空，则跳过处理
            if not clean_text:
                print(f"Skipping empty text for {output_path}")
                return False
            
            # 使用edge-tts创建TTS通信对象
            communicate = edge_tts.Communicate(clean_text, self.selected_voice)
            
            # 保存音频到文件
            await communicate.save(str(output_path))
            print(f"✓ Generated audio: {output_path.name}")
            return True
        except Exception as e:
            print(f"✗ Error generating audio for {output_path}: {e}")
            return False
    
    async def convert(self) -> bool:
        """转换JSON文件为语音"""
        try:
            # 读取JSON文件
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查必要的字段
            required_fields = ['audioKey']
            for field in required_fields:
                if field not in data:
                    print(f"✗ Missing required field: {field}")
                    return False
            
            audio_key = data['audioKey']
            
            # 需要转换的字段映射
            fields_to_convert = {
                'question_markdown': 'question',
                'answer_simple_markdown': 'answer_simple',
                'answer_detail_markdown': 'answer_detail',
                'answer_analysis_markdown': 'answer_analysis'
            }
            
            success_count = 0
            # 转换每个字段
            for json_field, audio_suffix in fields_to_convert.items():
                if json_field in data and data[json_field]:
                    output_file = self.output_dir / f"{audio_key}_audio_{audio_suffix}.mp3"
                    if await self.generate_audio(data[json_field], output_file):
                        success_count += 1
                else:
                    print(f"✗ Skipping empty or missing field: {json_field}")
            
            print(f"✓ Successfully converted {success_count}/{len(fields_to_convert)} fields for {self.input_file.name}")
            return True
        except Exception as e:
            print(f"✗ Error converting {self.input_file}: {e}")
            return False

async def main():
    """主函数"""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage:")
        print("  python3 json_to_speech.py <input_json_file> [output_directory]")
        print("Example:")
        print("  python3 json_to_speech.py questions-json/question1.json")
        print("  python3 json_to_speech.py questions-json/question1.json custom-output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "questions-audio"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"✗ Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # 创建转换器并执行转换
    converter = JsonToSpeechConverter(input_file, output_dir)
    await converter.convert()

if __name__ == "__main__":
    asyncio.run(main())