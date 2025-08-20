#!/usr/bin/env python3
import asyncio
import markdown
import re
import os
import sys
from pathlib import Path
from edge_tts import Communicate

# ================== 配置区 ==================
VOICE = "zh-CN-XiaoxiaoNeural"      # 中文女声，也可换为：
                                   # zh-CN-YunyangNeural（男声）
                                   # en-US-JennyNeural（英文）
SPEED = "+10%"                     # 语速：+10% 稍快，-10% 稍慢
PITCH = "+5Hz"                     # 音调：可选 "+5Hz" 或 "-5Hz"
SENTENCE_BREAK_MS = 600            # 句子之间停顿 600 毫秒
SECTION_BREAK_MS = 1000            # 小节之间停顿 1000 毫秒
# ============================================

def split_by_headings(text):
    """按 # 和 ## 标题分割文本"""
    lines = text.splitlines()
    sections = []
    current_content = []
    current_title = "正文"
    current_level = 0

    for line in lines:
        heading = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if heading:
            if current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    sections.append((current_level, current_title, content_text))
                current_content = []
            level = len(heading.group(1))
            title = heading.group(2).strip()
            current_title = title
            current_level = level
        else:
            current_content.append(line)

    if current_content:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            sections.append((current_level, current_title, content_text))

    return sections

def clean_markdown_and_insert_pause(content):
    """清理 Markdown 并在句子后加停顿"""
    # 1. 删除代码块 ```...```
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # 2. 转成纯文本
    html = markdown.markdown(content)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        return ""

    # 3. 按句号、感叹号、问号分句
    sentences = re.split(r'([。！？.!?])', text)
    sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]

    # 4. 每个句子后加语音停顿
    paused_sentences = []
    for sent in sentences:
        if sent.strip():
            break_tag = f"<break time='{SENTENCE_BREAK_MS}ms'/>"
            paused_sentences.append(f"{sent}{break_tag}")

    return "".join(paused_sentences)

async def speak_section(text, output_path, section_index, title):
    """生成一段语音（使用 SSML）"""
    if not text.strip():
        print(f"🟡 跳过空章节: {title}")
        return

    # 添加章节间大停顿（非第一段）
    if section_index > 1:
        break_tag = f"<break time='{SECTION_BREAK_MS}ms'/>"
        text = break_tag + text

    # 构造语音指令（SSML）
    ssml = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
        <voice name='{VOICE}'>
            <prosody rate='{SPEED}' pitch='{PITCH}'>
                {text}
            </prosody>
        </voice>
    </speak>
    """.strip()

    # ✅ 正确方式：text=None 表示使用 SSML
    communicate = Communicate(text=None, ssml=ssml)
    try:
        await communicate.save(output_path)
        print(f"✅ [{section_index:02d}] 已生成: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {output_path} | 错误: {e}")

async def main():
    # 读取命令行参数
    if len(sys.argv) < 3:
        print("📌 用法: python3 md_to_speech.py <输入文件.md> <输出目录名>")
        print("示例: python3 md_to_speech.py demo.md audio_output")
        return

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    print(f"📖 正在处理: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 '{input_file}'")
        return

    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    print(f"📁 输出音频将保存在: ./{output_dir}/")

    # 分割章节
    sections = split_by_headings(md_text)
    print(f"🔍 共找到 {len(sections)} 个章节")

    # 逐段生成语音
    for idx, (level, title, content) in enumerate(sections, 1):
        cleaned_text = clean_markdown_and_insert_pause(content)
        
        # 安全化标题（避免文件名出错）
        safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', title)
        safe_title = safe_title[:50]  # 截断太长的标题
        output_path = os.path.join(output_dir, f"section_{idx:02d}_{safe_title}.mp3")

        await speak_section(cleaned_text, output_path, idx, title)

    print(f"🎉 所有音频已生成完毕！请查看目录: ./{output_dir}/")

if __name__ == "__main__":
    asyncio.run(main())