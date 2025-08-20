#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 通过标题分割音频

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
SECTION_BREAK_MS = 1000  # 每个章节文件开头添加的静音时长（第1章不加）

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
    # 先把多个换行折叠成单个换行
    text = re.sub(r"\n\s*\n+", "\n", text)
    # 行内多余空格压缩
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()

    return text

# ======================
# 工具：安全生成文件名
# ======================
def sanitize_filename(name: str) -> str:
    # 移除不适合文件名的字符
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    # 控制长度，避免过长文件名
    return name[:120].strip() or "section"

# ======================
# 生成语音（不再传 SSML，而是直接传纯文本）
# 如果安装了 pydub + ffmpeg，则会在音频开头拼接静音以模拟 <break/>
# ======================
async def synthesize_with_optional_leading_silence(text: str, output_path: str, add_silence_ms: int):
    """
    使用 edge-tts 合成文本到临时 mp3，
    如可用 pydub 则在前面拼接 add_silence_ms 的静音后导出到 output_path。
    否则直接保存为 output_path，并在控制台提示降级。
    """
    # 先合成为临时 mp3
    tmp_fd, tmp_mp3 = tempfile.mkstemp(suffix=".mp3")
    os.close(tmp_fd)  # 只要路径
    try:
        communicate = Communicate(text, VOICE, rate=SPEED, pitch=PITCH)
        await communicate.save(tmp_mp3)
    except Exception as e:
        # 确保失败时清理临时文件
        try:
            os.remove(tmp_mp3)
        except Exception:
            pass
        raise RuntimeError(f"edge-tts 合成失败: {e}")

    # 尝试用 pydub 拼接静音
    try:
        if add_silence_ms > 0:
            from pydub import AudioSegment  # 需要 pip install pydub 且系统可用 ffmpeg
            audio = AudioSegment.from_file(tmp_mp3)
            silence = AudioSegment.silent(duration=add_silence_ms)
            (silence + audio).export(output_path, format="mp3")
        else:
            # 直接移动到目标
            os.replace(tmp_mp3, output_path)
    except Exception as e:
        # pydub 或 ffmpeg 不可用时降级：直接输出原音频并警告
        print(f"⚠️ 未能添加静音（可能缺少 pydub/ffmpeg）：{e}")
        # 降级方案：在文本最前面追加几个顿号/省略号以产生短暂停顿（不精确）
        # 仅在确实需要静音且尚未追加时重试一次
        if add_silence_ms > 0:
            try:
                # 估算一个很粗的“文本停顿”长度（中文里几个标点可拉出短暂停顿）
                pseudo_pause = "…… " if add_silence_ms >= 800 else "，"
                communicate = Communicate(pseudo_pause + text, VOICE, rate=SPEED, pitch=PITCH)
                await communicate.save(output_path)
            except Exception as e2:
                # 最后兜底：直接输出原音频
                print(f"⚠️ 文本停顿降级也失败，将直接输出：{e2}")
                os.replace(tmp_mp3, output_path)
        else:
            os.replace(tmp_mp3, output_path)
    finally:
        # 清理临时文件（若仍存在）
        try:
            if os.path.exists(tmp_mp3):
                os.remove(tmp_mp3)
        except Exception:
            pass

async def speak_section(text: str, output_path: str, section_index: int, title: str):
    if not text.strip():
        print(f"🟡 跳过空章节: {title}")
        return
    # 第 2 章及以后在文件开头加入静音
    leading_silence = SECTION_BREAK_MS if section_index > 1 else 0
    await synthesize_with_optional_leading_silence(text, output_path, leading_silence)
    print(f"✅ [{section_index:02d}] 已生成: {output_path}")

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

    # 按 "## 标题" 分割为 [title1, body1, title2, body2, ...]
    parts = re.split(r"(^##\s+.*)", content, flags=re.MULTILINE)
    parts = [s.strip() for s in parts if s.strip()]

    # 如果开头不是二级标题，补一个“简介”
    if not parts or not parts[0].startswith("##"):
        parts = ["## 简介"] + parts

    total_sections = len(parts) // 2
    print(f"🔍 共找到 {total_sections} 个章节")

    for i in range(0, len(parts), 2):
        raw_title = parts[i].replace("##", "").strip()
        body = parts[i + 1]
        cleaned_text = clean_markdown_and_insert_pause(body)

        safe_title = sanitize_filename(raw_title)
        output_path = os.path.join(output_dir, f"section_{(i // 2) + 1:02d}_{safe_title}.mp3")

        await speak_section(cleaned_text, output_path, (i // 2) + 1, raw_title)

    print(f"🎉 所有音频已生成完毕！请查看目录: {output_dir}/")

# ======================
# 启动
# ======================
if __name__ == "__main__":
    asyncio.run(main())