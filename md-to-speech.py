#!/usr/bin/env python3
import asyncio
import markdown
import re
import sys
from edge_tts import Communicate

# ================== 配置区 ==================
INPUT_FILE = "input.md"           # 默认输入文件
OUTPUT_FILE = "output.mp3"        # 默认输出音频
VOICE = "zh-CN-XiaoxiaoNeural"    # 中文女声，可更换
# ============================================

async def main():
    # 支持命令行传参：python md_to_speech.py input.md output.mp3
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_file = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    print(f"🔍 正在读取文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"❌ 错误：文件 '{input_file}' 未找到！")
        return

    # Step 1: 移除 ``` 开头和结尾的代码块（支持多行）
    text_without_code = re.sub(r'```.*?```', '', md_text, flags=re.DOTALL)

    # Step 2: 将 Markdown 转为 HTML，再提取纯文本
    html = markdown.markdown(text_without_code)
    # 去除 HTML 标签（如 <p>, <h1> 等）
    text = re.sub(r'<[^>]+>', ' ', html)
    # 清理多余空白和换行
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        print("❌ 处理后文本为空，可能是只有代码块或格式问题。")
        return

    print(f"📝 提取有效文本（前200字）：{text[:200]}...")
    print(f"🎤 正在使用声音 '{VOICE}' 生成语音...")
    print(f"💾 音频将保存为: {output_file}")

    # 使用 edge-tts 生成音频
    communicate = Communicate(text, VOICE)
    try:
        await communicate.save(output_file)
        print(f"✅ 成功！音频已保存：{output_file}")
    except Exception as e:
        print(f"❌ 生成音频失败：{e}")

if __name__ == "__main__":
    asyncio.run(main())