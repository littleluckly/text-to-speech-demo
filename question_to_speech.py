import os
# 导入必要的模块
import re              # 正则表达式模块，用于文本处理
import json            # JSON处理模块，用于读写JSON文件
from pathlib import Path  # 路径处理模块，用于跨平台文件路径操作
import markdown        # Markdown解析模块
from bs4 import BeautifulSoup  # HTML解析模块
import edge_tts        # Edge TTS语音合成模块
import asyncio         # 异步编程模块
from typing import Dict, List, Any  # 类型提示模块

# 定义MarkdownQuestionParser类，用于解析Markdown文件并生成语音
class MarkdownQuestionParser:
    # 构造函数，初始化解析器
    # input_file: 输入的Markdown文件路径
    # output_dir: 输出目录，默认为"questions"
    def __init__(self, input_file: str, output_dir: str = "questions"):
        self.input_file = input_file  # 存储输入文件路径
        self.output_dir = Path(output_dir)  # 将输出目录转换为Path对象
        self.voice = "zh-CN-YunyangNeural"  # 设置默认语音为中文男声
        
    # 清理Markdown文本，移除所有格式标记，返回纯文本
    # text: 输入的Markdown文本
    # 返回: 清理后的纯文本
    def clean_markdown_text(self, text: str) -> str:
        """移除Markdown格式并返回纯文本"""
        # 移除Markdown标题标记（# 到 ######）
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 移除粗体和斜体格式标记
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # 移除粗体标记 (**粗体**)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # 移除斜体标记 (*斜体*)
        text = re.sub(r'__([^_]+)__', r'\1', text)      # 移除另一种粗体标记 (__粗体__)
        text = re.sub(r'_([^_]+)_', r'\1', text)        # 移除另一种斜体标记 (_斜体_)
        
        # 移除链接标记，但保留链接文本
        text = re.sub(r'\[([^\]]+)\]\$\$[^)]+\$\$', r'\1', text)
        
        # 移除图片标记（完全删除，不保留alt文本）
        text = re.sub(r'!\[([^\]]*)\]\$\$[^)]+\$\$', '', text)
        
        # 移除表情符号（基本表情符号模式）
        text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # 移除表情符号（笑脸等）
        text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # 移除符号和象形图
        text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # 移除交通和地图图标
        text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # 移除国旗图标
        
        # 移除特殊的Markdown符号
        text = re.sub(r'[✅📘]', '', text)  # 移除对勾和书本图标
        
        # 清理多余的空白行
        text = re.sub(r'\n\s*\n', '\n\n', text)  # 合并多个空行为一个空行
        text = text.strip()  # 移除文本两端的空白字符
        
        return text
    
    # 解析YAML前置元数据（frontmatter）
    # content: 包含前置元数据的文本内容
    # 返回: 包含元数据字典和剩余内容的元组
    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """解析YAML前置元数据并返回元数据和剩余内容"""
        # 改进的匹配YAML前置元数据的正则表达式模式
        # 匹配以---开头（行首），中间是YAML内容，以---结尾（可选地在行尾）
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*(?:\n|$)'
        # 使用正则表达式查找前置元数据
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            # 提取前置元数据的文本内容
            frontmatter_text = match.group(1)
            # 提取去除前置元数据后的剩余内容
            remaining_content = content[match.end():]
            # 添加调试日志，显示提取的前置元数据内容
            print(f"\nExtracted frontmatter text (first 100 chars): {frontmatter_text[:100]}...")
            
            # 手动解析类YAML格式的前置元数据
            metadata = {}  # 创建空字典存储元数据
            # 逐行解析前置元数据
            for line in frontmatter_text.split('\n'):
                line = line.strip()  # 去除每行两端的空白
                # 检查行是否包含冒号（YAML键值对的分隔符）
                if ':' in line and not line.startswith('#'):  # 忽略注释行
                    # 分割键和值，只分割第一个冒号
                    key, value = line.split(':', 1)
                    key = key.strip()  # 去除键两端的空白
                    value = value.strip()  # 去除值两端的空白
                    
                    # 处理数组类型的值（以[开头并以]结尾）
                    if value.startswith('[') and value.endswith(']'):
                        # 提取数组内容（去除括号）
                        array_content = value[1:-1]
                        # 按逗号分割并去除每个元素的空白，创建列表
                        metadata[key] = [item.strip() for item in array_content.split(',') if item.strip()]
                    else:
                        # 去除引号（如果有的话）
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        metadata[key] = value
            
            print(f"Parsed metadata keys: {list(metadata.keys())}")
            return metadata, remaining_content
        else:
            print("No frontmatter pattern matched")
            print(f"Content starts with: {content[:100]}...")
        
        return {}, content
    
    # 解析单个问题块
    # block: 包含单个问题的文本块
    # 返回: 包含问题元数据、题目、答案和解析的字典，如果解析失败则返回None
    def parse_question_block(self, block: str) -> Dict[str, Any]:
        """解析单个问题块"""
        # 解析问题块中的前置元数据
        metadata, content = self.parse_frontmatter(block)
        # 添加调试日志，显示解析出的元数据
        print(f"Parsed metadata: {metadata}")
        
        # 查找题目部分
        # 使用正则表达式匹配以"## **题目：**"开头，到"## **✅ 精简答案：**"结束的内容
        question_match = re.search(r'## \*\*题目：\*\* (.+?)(?=\n## \*\*✅ 精简答案：\*\*)', content, re.DOTALL)
        # 如果没有找到题目部分，返回None表示解析失败
        if not question_match:
            return None
        
        # 提取题目文本并去除两端空白
        question_text = question_match.group(1).strip()
        
        # 查找精简答案部分
        # 使用正则表达式匹配以"## **✅ 精简答案：**"开头，到"**📘 详细解析：**"结束的内容
        # 考虑到"**📘 详细解析：**"前面可能有换行符也可能没有，使用更灵活的模式
        simple_answer_match = re.search(r'## \*\*✅ 精简答案：\*\*\s*(.+?)(?=\n?\*\*📘 详细解析：\*\*)', content, re.DOTALL)
        # 如果没有找到精简答案部分，返回None表示解析失败
        if not simple_answer_match:
            return None
        
        # 提取精简答案文本并去除两端空白
        simple_answer = simple_answer_match.group(1).strip()
        
        # 查找详细解析部分
        # 使用正则表达式匹配以"**📘 详细解析：**"开头的内容
        # 考虑到详细解析可能是文件的最后部分，或者后面跟着---分隔符或其他标题
        analysis_match = re.search(r'\*\*📘 详细解析：\*\*\s*(.+?)(?=\n\s*---\s*\n|\n\s*##|\s*$)', content, re.DOTALL)
        # 初始化详细解析为空字符串
        detailed_analysis = ""
        # 如果找到详细解析部分，则提取并去除两端空白
        if analysis_match:
            detailed_analysis = analysis_match.group(1).strip()
        
        # 返回包含所有解析内容的字典
        # 注意：所有文本内容都通过clean_markdown_text方法清理了Markdown格式
        return {
            'metadata': metadata,  # 元数据信息
            'question': self.clean_markdown_text(question_text),  # 清理后的题目文本
            'simple_answer': self.clean_markdown_text(simple_answer),  # 清理后的精简答案文本
            'detailed_analysis': self.clean_markdown_text(detailed_analysis)  # 清理后的详细解析文本
        }
    
    # 预处理文本以提高语音合成的可读性，添加适当的停顿
    # text: 需要预处理的文本
    # 返回: 预处理后的文本，适合语音合成
    def preprocess_text_for_speech(self, text: str) -> str:
        """预处理文本以提高语音可读性，添加适当的停顿"""
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
        text = re.sub(r'→', '，然后', text)  # 替换右箭头为"，然后"
        text = re.sub(r'←', '，返回', text)  # 替换左箭头为"，返回"
        text = re.sub(r'↑', '，向上', text)  # 替换上箭头为"，向上"
        text = re.sub(r'↓', '，向下', text)  # 替换下箭头为"，向下"
        
        # 在Vue生命周期方法和技术术语之间添加停顿
        lifecycle_methods = [
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeDestroy', 'destroyed',
            'beforeUnmount', 'unmounted', 'activated', 'deactivated'
        ]
        
        for method in lifecycle_methods:
            # 在每个生命周期方法后添加停顿（中文逗号）
            text = re.sub(rf'\b{method}\b', f'{method}，', text)
        
        # 在由空格分隔的代码元素之间添加停顿
        text = re.sub(r'(\w+)\s+(\w+)\s+(\w+)', r'\1，\2，\3', text)
        
        # Add pauses around parentheses and brackets
        text = re.sub(r'\(', '，开括号，', text)
        text = re.sub(r'\)', '，闭括号，', text)
        text = re.sub(r'\[', '，开方括号，', text)
        text = re.sub(r'\]', '，闭方括号，', text)
        text = re.sub(r'\{', '，开花括号，', text)
        text = re.sub(r'\}', '，闭花括号，', text)
        
        # Add pauses around equals signs and operators
        text = re.sub(r'=', '，等于，', text)
        text = re.sub(r'\+', '，加，', text)
        text = re.sub(r'\*', '，乘，', text)
        text = re.sub(r'/', '，除，', text)
        
        # Add pauses between camelCase words
        text = re.sub(r'([a-z])([A-Z])', r'\1，\2', text)
        
        # Add pauses around dots in method calls
        text = re.sub(r'\.', '，点，', text)
        
        # Clean up multiple consecutive commas
        text = re.sub(r'，+', '，', text)
        
        # Ensure proper spacing around Chinese punctuation
        text = re.sub(r'，\s*，', '，', text)
        text = re.sub(r'，\s*$', '。', text)  # End with period instead of comma
        
        return text.strip()
    
    # 异步方法：使用edge-tts生成音频文件
    # text: 要转换为语音的文本内容
    # output_path: 生成的音频文件保存路径
    async def generate_audio(self, text: str, output_path: Path):
        """使用edge_tts 7.x从文本生成音频文件"""
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
                return
            
            # 创建edge-tts语音管理器
            voices_manager = await edge_tts.VoicesManager.create()
            
            # 首选的中文语音列表（按优先级排序）
            preferred_voices = [
                "zh-CN-YunyangNeural",  # 云杨（男）
                "zh-CN-YunjianNeural",  # 云健（男）
                "zh-CN-YunxiNeural",    # 云溪（女）
                "zh-CN-YunhaoNeural",   # 云浩（男）
                "zh-CN-YunzeNeural"     # 云泽（男）
            ]
            
            selected_voice = None  # 初始化选中的语音为None
            all_voices = voices_manager.find()  # 获取所有可用语音
            
            print(f"Looking for voice from preferred list...")
            
            # 尝试从首选语音列表中找到可用的语音
            for voice in preferred_voices:
                matching_voices = [v for v in all_voices if v["Name"] == voice]
                if matching_voices:
                    selected_voice = voice
                    print(f"✓ Found preferred voice: {selected_voice}")
                    break
                else:
                    print(f"✗ Voice not available: {voice}")
            
            # 如果没有找到首选语音，则查找任何中文(zh-CN)语音作为备选
            if not selected_voice:
                print("No preferred voices found, looking for any zh-CN voice...")
                zh_cn_voices = [v for v in all_voices if v["Locale"].startswith("zh-CN")]
                if zh_cn_voices:
                    selected_voice = zh_cn_voices[0]["Name"]
                    print(f"✓ Using fallback zh-CN voice: {selected_voice}")
                    print(f"  Available zh-CN voices: {[v['Name'] for v in zh_cn_voices[:3]]}")
                else:
                    print("⚠️  No zh-CN voices found! This might cause issues.")
                    # 列出实际可用的语言区域
                    available_locales = list(set([v["Locale"] for v in all_voices]))
                    print(f"Available locales: {available_locales[:10]}")
                    selected_voice = "zh-CN-YunyangNeural"  # 默认备选语音
            
            # 使用edge-tts 7.x创建TTS通信对象
            communicate = edge_tts.Communicate(clean_text, selected_voice)
            
            # 保存音频到文件
            await communicate.save(str(output_path))
            print(f"✓ Generated audio: {output_path.name}")
        except Exception as e:
            print(f"✗ Error generating audio for {output_path}: {e}")
    
    # 异步方法：为单个问题创建目录结构和相关文件
    # question_data: 包含问题信息的字典
    # question_num: 问题编号
    async def create_question_directory(self, question_data: Dict[str, Any], question_num: int):
        """为单个问题创建目录结构和相关文件"""
        # 获取问题ID，如果没有ID则使用问题编号
        question_id = question_data['metadata'].get('id', f'q{question_num:04d}')
        # 截取ID的前8位字符，避免文件名过长
        id_prefix = str(question_id)[:8] if question_id else f'q{question_num:04d}'
        
        # 创建问题目录，使用新的命名格式 q{编号}_{ID前缀}
        question_dir = self.output_dir / f"q{question_num:04d}_{id_prefix}"
        # 创建目录，如果父目录不存在则自动创建，如果目录已存在则不报错
        question_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义音频文件路径，使用新的命名格式
        audio_simple_file = question_dir / f"q{question_num:04d}_{id_prefix}_audio_simple.mp3"  # 简单答案音频文件
        audio_question_file = question_dir / f"q{question_num:04d}_{id_prefix}_audio_question.mp3"  # 问题音频文件
        audio_analysis_file = question_dir / f"q{question_num:04d}_{id_prefix}_audio_analysis.mp3"  # 详细解析音频文件
        
        # 生成音频文件
        await self.generate_audio(question_data['simple_answer'], audio_simple_file)  # 生成简单答案音频
        await self.generate_audio(question_data['question'], audio_question_file)  # 生成问题音频
        await self.generate_audio(question_data['detailed_analysis'], audio_analysis_file)  # 生成详细解析音频
        
        # 创建meta.json文件，包含问题的所有元数据和内容字符串
        meta_data = {
            'id': question_data['metadata'].get('id', None),  # 问题ID，优先使用原始文件中的UUID，不使用question_num作为默认值
            'type': question_data['metadata'].get('type', 'unknown'),  # 问题类型，默认为unknown
            'difficulty': question_data['metadata'].get('difficulty', 'medium'),  # 难度级别，默认为medium
            'tags': question_data['metadata'].get('tags', []),  # 标签列表，默认为空列表
            'question_length': len(question_data['question']),  # 问题文本长度
            'simple_answer_length': len(question_data['simple_answer']),  # 简单答案文本长度
            'detailed_analysis_length': len(question_data['detailed_analysis']),  # 详细解析文本长度
            'created_at': None,  # 创建时间，可以添加时间戳
            # 直接添加内容字符串，以文件名作为key
            'question_markdown': question_data['question'],  # 问题文本内容
            'answer_simple_markdown': question_data['simple_answer'],  # 简单答案文本内容
            'answer_analysis_markdown': question_data['detailed_analysis'],  # 详细解析文本内容
            'files': {  # 文件映射，记录相关文件的路径（使用新的命名格式）
                'audio_simple': f'q{question_num:04d}_{id_prefix}_audio_simple.mp3',  # 简单答案音频文件
                'audio_question': f'q{question_num:04d}_{id_prefix}_audio_question.mp3',  # 问题音频文件
                'audio_analysis': f'q{question_num:04d}_{id_prefix}_audio_analysis.mp3',  # 详细解析音频文件
                'meta': f'q{question_num:04d}_{id_prefix}_meta.json'  # 元数据文件本身的文件名
            }
        }
        
        # 定义meta.json文件路径，使用新的命名格式
        meta_file = question_dir / f"q{question_num:04d}_{id_prefix}_meta.json"
        # 写入meta.json文件，使用UTF-8编码，保留中文字符不进行ASCII转义，缩进2个空格
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)
        
        # 打印创建成功的信息
        print(f"✓ Created question directory: {question_dir}")
    
    # 异步方法：主要处理方法，用于解析markdown文件并生成问题目录
    async def parse_and_generate(self):
        """解析markdown文件并生成问题目录的主要方法"""
        print(f"Reading markdown file: {self.input_file}")
        
        # 读取输入的markdown文件
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将内容分割成问题块 - 每个问题块都以YAML前置元数据开头
        # 使用更智能的分割策略来正确处理frontmatter和内容的组合
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
        
        print(f"Total question blocks found: {len(question_blocks)}")
        
        # 过滤掉空块和不包含'题目'的块（可能不是有效的问题块）
        question_blocks = [block for block in question_blocks if block.strip() and '题目' in block]
        print(f"Filtered question blocks count: {len(question_blocks)}")
        
        # 打印找到的问题块数量
        print(f"Found {len(question_blocks)} question blocks")
        
        # 创建输出目录（如果不存在）
        self.output_dir.mkdir(exist_ok=True)
        
        # 处理每个问题块
        question_count = 0  # 用于记录成功处理的问题数量
        for i, block in enumerate(question_blocks):
            try:
                # 解析问题块
                question_data = self.parse_question_block(block)
                if question_data:
                    question_count += 1  # 增加成功处理的问题计数
                    # 为这个问题创建目录和相关文件
                    await self.create_question_directory(question_data, question_count)
                else:
                    print(f"Skipping invalid block {i+1}")
            except Exception as e:
                # 捕获并打印处理过程中的错误
                print(f"✗ Error processing block {i+1}: {e}")
        
        # 打印处理结果统计信息
        print(f"\n✓ Successfully processed {question_count} questions")
        print(f"Output directory: {self.output_dir.absolute()}")
    
    # 异步方法：列出所有可用的中文语音选项
    async def list_available_voices(self):
        """列出所有可用的中文语音"""
        try:
            # 创建edge-tts语音管理器
            voices_manager = await edge_tts.VoicesManager.create()
            # 获取所有可用语音
            all_voices = voices_manager.find()
            
            # 过滤出中文语音（语言区域以zh开头）
            chinese_voices = [v for v in all_voices if v["Locale"].startswith("zh")]
            
            # 打印可用的中文语音列表
            print("\n=== Available Chinese Voices ===")
            for voice in chinese_voices:
                print(f"Name: {voice['Name']}")  # 语音名称（用于API调用）
                print(f"  Locale: {voice['Locale']}")  # 语言区域
                print(f"  Gender: {voice['Gender']}")  # 性别
                print(f"  Display Name: {voice['FriendlyName']}")  # 显示名称（友好名称）
                print()
            
            print(f"Total Chinese voices found: {len(chinese_voices)}")
            return chinese_voices  # 返回找到的中文语音列表
        except Exception as e:
            print(f"✗ Error listing voices: {e}")  # 打印错误信息
            return []  # 发生错误时返回空列表

# 主函数：程序的入口逻辑
async def main():
    import sys  # 导入系统模块以获取命令行参数
    
    # 检查是否是列出语音的命令
    if len(sys.argv) == 2 and sys.argv[1] == "--list-voices":
        # 创建一个临时的解析器实例（输入输出路径不重要）
        parser = MarkdownQuestionParser("", "")
        # 调用列出语音的方法
        await parser.list_available_voices()
        return  # 完成后返回，不执行后续代码
    
    # 检查命令行参数是否正确
    if len(sys.argv) != 3:
        # 打印使用说明
        print("Usage: python3 question_to_speech.py <input_markdown_file> <output_directory>")
        print("       python3 question_to_speech.py --list-voices")
        print("Example: python3 question_to_speech.py vue_questions.md format-output")
        sys.exit(1)  # 退出程序，返回错误码1
    
    # 获取命令行参数
    input_file = sys.argv[1]  # 第一个参数是输入markdown文件路径
    output_dir = sys.argv[2]  # 第二个参数是输出目录路径
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"✗ Error: Input file '{input_file}' does not exist.")
        sys.exit(1)  # 退出程序，返回错误码1
    
    # 创建解析器实例并执行处理
    parser = MarkdownQuestionParser(input_file, output_dir)
    await parser.parse_and_generate()

# 程序入口点：当直接运行脚本时执行
if __name__ == "__main__":
    # 使用asyncio运行异步的main函数
    asyncio.run(main())
