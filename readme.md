# 环境安装

python 环境安装 `brew install python`
验证安装
`python3 --version`
`pip3 --version`

# 虚拟环境

```bash
# 1. 创建一个虚拟环境（比如叫 venv 或 tts-env）
python3 -m venv ~/venv-tts

# 2. 激活它
source ~/venv-tts/bin/activate

# 3. 现在可以正常安装 edge-tts和markdown解析库
pip install edge-tts markdown

# 4. 使用完成后退出
deactivate
```

# 使用

1. 将文件转成语音输入到指定目录
   命令格式： `python3 脚本目录 待转换的文件 输出mp3的路径`
   如：`python3 /Users/xiongweiliu/workspaces/text-to-speech/md_to_speech.py /Users/xiongweiliu/workspaces/text-to-speech/demo.md /Users/xiongweiliu/workspaces/text-to-speech/output`

2. 可使用的语音类型
   常见中文语音：
   zh-CN-XiaoxiaoNeural：女声，标准普通话
   zh-CN-YunyangNeural：男声，新闻播报风
   zh-CN-XiaoyiNeural：女声，活泼清晰
   查看当前可以使用的语音类型：`python -m edge_tts --list-voices | grep zh-CN`

3. 格式化输出
   `python3 /Users/xiongweiliu/workspaces/text-to-speech/question_to_speech.py /Users/xiongweiliu/workspaces/text-to-speech/vue_questions-md-format.md /Users/xiongweiliu/workspaces/text-to-speech/format-output`
