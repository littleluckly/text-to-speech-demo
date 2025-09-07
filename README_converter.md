# Markdown to JSON 转换器使用说明

## 脚本功能

`md_to_json_converter.py` 是一个用于将特定格式的 Markdown 文件转换为结构化 JSON 文件的工具。该脚本特别设计用于处理题库类 Markdown 文件，能够提取问题、答案和元数据，并将其转换为便于程序处理的 JSON 格式。

## 功能特点

1. 支持处理单个 Markdown 文件或整个目录中的所有 Markdown 文件
2. 可以指定要转换的文件数量，方便测试和批量处理
3. 提供详细的转换报告，包括成功和失败的文件列表
4. 自动提取 Markdown 文件中的元数据、问题标题、不同类型的答案
5. 生成符合指定格式的 JSON 文件，包含音频文件路径信息

## 安装依赖

该脚本使用 Python 标准库，无需安装额外依赖。确保您的系统已安装 Python 3.6 或更高版本。

## 使用方法

### 基本语法

```bash
python3 md_to_json_converter.py -i <输入路径> -o <输出目录> [-n <文件数量>]
```

### 命令行参数说明

- `-i`, `--input`: 输入路径，可以是单个 Markdown 文件路径或包含 Markdown 文件的目录路径（默认为 `questions` 目录）
- `-o`, `--output`: 输出目录路径，用于存放生成的 JSON 文件（默认为 `questions-json` 目录）
- `-n`, `--number`: 可选参数，指定要转换的文件数量（不指定则转换所有文件）

## 示例用法

### 1. 转换单个文件

```bash
python3 md_to_json_converter.py -i demo.md -o test-output
```

此命令将 `demo.md` 文件转换为 JSON 格式，并将结果保存到 `test-output` 目录中。

### 2. 转换整个目录中的文件

```bash
python3 md_to_json_converter.py -i questions -o questions-json
```

此命令将 `questions` 目录中的所有 Markdown 文件转换为 JSON 格式，并将结果保存到 `questions-json` 目录中。

### 3. 限制转换文件数量

```bash
python3 md_to_json_converter.py -i questions -o test-output -n 10
```

此命令将 `questions` 目录中的前 10 个 Markdown 文件转换为 JSON 格式，并将结果保存到 `test-output` 目录中。

### 4. 使用虚拟环境（如果需要）

```bash
source ~/venv-tts/bin/activate  # 激活虚拟环境
python3 md_to_json_converter.py -i questions -o questions-json
```

## 输入文件格式要求

输入的 Markdown 文件需要遵循以下格式：

### 1. 元数据部分

```markdown
## meta 元数据

```
{
 "id": "f8e7d6c5-b4a3-2109-fedc-ba9876543210",
 "type": "answer",
 "difficulty": "easy",
 "tags": ["算法"]
}
```
```

### 2. 答案部分

```markdown
## 答案 1：核心简洁的口语化回答

・内容...

## 答案 2：口语化扩展回答

内容...

## 答案 3：技术深度解析

内容...
```

## 输出文件格式说明

生成的 JSON 文件包含以下字段：

```json
{
  "audioKey": "q34a7144a_demo",  // 自动生成的音频键值
  "id": "f8e7d6c5-b4a3-2109-fedc-ba9876543210",  // 从元数据提取的ID
  "type": "answer",  // 从元数据提取的类型
  "difficulty": "easy",  // 从元数据提取的难度
  "tags": ["算法"],  // 从元数据提取的标签
  "question_markdown": "demo",  // 问题标题（使用文件名）
  "answer_simple_markdown": "...",  // 答案 1 的内容
  "answer_detail_markdown": "...",  // 答案 2 的内容
  "answer_analysis_markdown": "...",  // 答案 3 的内容
  "files": {
    "audio_answer_simple": "q34a7144a_demo_audio_answer_simple.mp3",  // 简单答案音频文件路径
    "audio_answer_detail": "q34a7144a_demo_audio_answer_detail.mp3",  // 详细答案音频文件路径
    "audio_answer_analysis": "q34a7144a_demo_audio_answer_analysis.mp3",  // 答案分析音频文件路径
    "audio_question": "q34a7144a_demo_audio_question.mp3"  // 问题音频文件路径
  }
}
```

## 转换报告

脚本执行完成后，会输出详细的转换报告，包括：

- 总文件数
- 成功转换的文件数
- 失败转换的文件数
- 失败文件列表及失败原因

## 注意事项

1. 确保输入的 Markdown 文件遵循指定的格式，特别是元数据和答案部分的标题格式
2. 输出目录会自动创建，如果目录已存在则不会覆盖现有文件
3. 如果 Markdown 文件中的元数据格式不正确，脚本会给出警告并尝试继续处理
4. 生成的 JSON 文件使用 UTF-8 编码，确保中文和其他非ASCII字符能正确显示