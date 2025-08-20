#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import re
import os
import tempfile
import markdown
from edge_tts import Communicate

# ======================
# 配置参数
# ======================
VOICE = "zh-CN-XiaoxiaoNeural"
SPEED = "+0%"          # 例如 "+10%" 或 "-5%"
PITCH = "+0Hz"         # 例如 "+2Hz" 或 "-2Hz"
SECTION_BREAK_MS = 1000  # 每个章节文件开头添加的静音时长

# ======================
# Markdown -> 纯文本
# ======================
def clean_markdown_and_insert_pause(content: str) -> str:
    # 去掉代码块
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    # 转 HTML 再剥标签，尽量保留段落分隔为换行
    html = markdown.markdown(content)
    # 用换行替换块级标签，减少一口气读完的问题
    html = re.sub(r"</(p|h[1-6]|li|ul|ol|blockquote|pre)>", r"</\1>\n", html, flags=re.I)

    # 去掉所有 HTML 标签
    text = re.sub(r"<[^>]+>", " ", html)

    # 规范空白：将连续空白压缩，同时保留换行的分段感
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()

    return text

# ======================
# 工具：安全生成文件名
# ======================
def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    return name[:120].strip() or "section"

# ======================
# 生成语音（不再传 SSML，而是直接传纯文本）
# 如果安装了 pydub + ffmpeg，则会在音频开头拼接静音以模拟 <break/>
# ======================
async def synthesize_with_optional_leading_silence(text: str, output_path: str, add_silence_ms: int):
    tmp_fd, tmp_mp3 = tempfile.mkstemp(suffix=".mp3")
    os.close(tmp_fd)
    try:
        communicate = Communicate(text, VOICE, rate=SPEED, pitch=PITCH)
        await communicate.save(tmp_mp3)
    except Exception as e:
        try:
            os.remove(tmp_mp3)
        except Exception:
            pass
        raise RuntimeError(f"edge-tts 合成失败: {e}")

    try:
        if add_silence_ms > 0:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(tmp_mp3)
            silence = AudioSegment.silent(duration=add_silence_ms)
            (silence + audio).export(output_path, format="mp3")
        else:
            os.replace(tmp_mp3, output_path)
    except Exception as e:
        print(f"⚠️ 未能添加静音（可能缺少 pydub/ffmpeg）：{e}")
        if add_silence_ms > 0:
            try:
                pseudo_pause = "…… " if add_silence_ms >= 800 else "，"
                communicate = Communicate(pseudo_pause + text, VOICE, rate=SPEED, pitch=PITCH)
                await communicate.save(output_path)
            except Exception as e2:
                print(f"⚠️ 文本停顿降级也失败，将直接输出：{e2}")
                os.replace(tmp_mp3, output_path)
        else:
            os.replace(tmp_mp3, output_path)
    finally:
        try:
            if os.path.exists(tmp_mp3):
                os.remove(tmp_mp3)
        except Exception:
            pass

async def speak_section(text: str, output_path: str, section_index: int):
    if not text.strip():
        print(f"🟡 跳过空章节: Section {section_index}")
        return
    leading_silence = SECTION_BREAK_MS if section_index > 1 else 0
    await synthesize_with_optional_leading_silence(text, output_path, leading_silence)
    print(f"✅ [{section_index:02d}] 已生成: {output_path}")

# ======================
# 主函数
# ======================
# ======================
# 主函数
# ======================
async def main():
    import sys
    if len(sys.argv) != 3:
        print("用法: python3 md_to_speech.py <input.md> <output_dir>")
        return

    md_file = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)

    print(f"📖 正在处理: {md_file}")
    print(f"📁 输出音频将保存在: {output_dir}/")

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 使用正则按分割线拆分，但保留内容块
    # 匹配三种 Markdown 分割线：---, ***, ___
    separator_pattern = r"^\s*(\*{3,}|\-{3,}|\_{3,})\s*$"
    lines = content.splitlines()

    sections = []
    current_section = []

    for line in lines:
        if re.match(separator_pattern, line, re.MULTILINE):
            # 遇到分割线，保存当前段落，开始新段落
            if current_section:
                sections.append("\n".join(current_section))
                current_section = []
            else:
                # 如果前面没有内容，忽略连续分割线
                continue
        else:
            current_section.append(line)

    # 别忘了最后一个段落
    if current_section:
        sections.append("\n".join(current_section))

    # 清理空段落
    sections = [s.strip() for s in sections if s.strip()]

    if not sections:
        print("❌ 未找到任何有效内容，请检查 Markdown 文件是否为空或缺少分割线。")
        return

    print(f"🔍 共找到 {len(sections)} 个章节")

    for idx, body in enumerate(sections, start=1):
        cleaned_text = clean_markdown_and_insert_pause(body)

        # 生成标题
        # 取内容前10个汉字作为标题（自动去首尾空格）
        preview = re.sub(r"\s+", " ", body.strip())  # 压缩空白
        preview = preview[:10]  # 取前10个字符
        title = f"第{idx:02d}章_{preview}"
        safe_title = sanitize_filename(title)
        output_path = os.path.join(output_dir, f"{safe_title}.mp3")

        await speak_section(cleaned_text, output_path, idx)

    print(f"🎉 所有音频已生成完毕！请查看目录: {output_dir}/")

# ======================
# 启动
# ======================
if __name__ == "__main__":
    asyncio.run(main())