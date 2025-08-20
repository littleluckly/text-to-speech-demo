from edge_tts import Communicate
import asyncio

async def main():
    ssml = """
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
        <voice name='zh-CN-XiaoxiaoNeural'>
            你好，这是测试语音。 <break time='500ms'/> 听到停顿了吗？
        </voice>
    </speak>
    """
    communicate = Communicate(text=None, ssml=ssml)
    await communicate.save("test_audio.mp3")
    print("✅ 测试音频已生成：test_audio.mp3")

if __name__ == "__main__":
    asyncio.run(main())