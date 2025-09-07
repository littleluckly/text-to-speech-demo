# JSON 转语音工具使用说明

## 脚本功能

`json_to_speech.py` 和 `json_to_speech_batch_safe.py` 是一套用于将 JSON 格式题库文件转换为语音文件的工具。这两个脚本特别设计用于处理 `questions-json` 目录下的 JSON 文件，能够提取问题和不同类型的答案，并使用 Microsoft Edge TTS 服务将其转换为音频文件。

## 功能特点

### json_to_speech.py (单个文件处理)

- 支持处理单个 JSON 文件，提取其中的问题和答案文本
- 自动生成四种类型的音频文件：问题、简洁答案、详细答案和分析答案
- 使用高质量的中文语音合成引擎
- 可自定义输出目录

### json_to_speech_batch_safe.py (批量安全处理)

- 支持批量处理目录中的所有 JSON 文件
- 提供四种预定义处理模式（保守、平衡、激进、测试），满足不同规模的文件处理需求
- 实现随机间隔和小批量处理，防止 API 频率限制导致 IP 封禁
- 支持进度保存和恢复功能，可随时中断后继续处理
- 支持跳过已存在的音频文件，提高处理效率
- 提供详细的日志记录和处理统计
- 支持自定义批次大小和间隔时间

## 安装依赖

使用前请确保安装必要的依赖包：

```bash
# 激活虚拟环境（如果有）
source ~/venv-tts/bin/activate

# 安装所需依赖
pip install edge-tts
```

## 使用方法

### 1. 单个文件处理脚本

#### 基本语法

```bash
python3 json_to_speech.py <输入JSON文件> [输出目录]
```

#### 示例用法

```bash
# 基本用法，使用默认输出目录 (questions-audio)
python3 json_to_speech.py questions-json/API\ 接口权限控制及常见权限设计方案.json

# 指定输出目录
python3 json_to_speech.py questions-json/JavaScript\ 事件循环机制详解.json custom-audio-output
```

### 2. 批量安全处理脚本

#### 基本语法

```bash
python3 json_to_speech_batch_safe.py <输入目录> <输出目录> [mode/custom_params] [--skip-existing] [--debug]
```

#### 预定义模式

批量处理脚本提供四种预定义模式，适应不同的处理需求：

| 模式名称 | 批次大小 | 间隔时间 | 适用场景 | 风险等级 |
|--------|---------|---------|---------|---------|
| `conservative` | 2-3个文件 | 10-20分钟 | 100+个文件的大目录 | 低 |
| `balanced` | 3-5个文件 | 5-15分钟 | 20-100个文件的中等目录 | 低 |
| `aggressive` | 5-8个文件 | 2-8分钟 | <20个文件的小目录 | 中 |
| `test` | 1个文件 | 0.5-1分钟 | 测试和调试 | 低 |

#### 自定义参数格式

```bash
custom <batch_size_min>-<batch_size_max> <interval_min>-<interval_max>
```

#### 命令行参数说明

- **输入目录**: 包含 JSON 文件的目录路径（通常为 `questions-json`）
- **输出目录**: 用于存放生成的音频文件的目录
- **模式/自定义参数**: 可选，指定处理模式或自定义批次大小和间隔时间
- `--skip-existing`: 可选，跳过已经生成的音频文件
- `--debug`: 可选，开启调试模式，显示更详细的日志信息

## 示例用法

### 使用预定义模式

```bash
# 使用默认平衡模式
python3 json_to_speech_batch_safe.py questions-json questions-audio

# 使用保守模式处理大型目录
python3 json_to_speech_batch_safe.py questions-json questions-audio conservative

# 使用激进模式快速处理小型目录
python3 json_to_speech_batch_safe.py questions-json questions-audio aggressive

# 使用测试模式进行调试
python3 json_to_speech_batch_safe.py questions-json test-output test

# 启用跳过已存在文件功能
python3 json_to_speech_batch_safe.py questions-json questions-audio balanced --skip-existing
```

### 使用自定义参数

```bash
# 自定义批次大小为2-4个文件，间隔时间为8-12分钟
python3 json_to_speech_batch_safe.py questions-json questions-audio custom 2-4 8-12

# 自定义参数并启用跳过功能
python3 json_to_speech_batch_safe.py questions-json questions-audio custom 3-6 6-10 --skip-existing
```

## 输出文件格式

转换后的音频文件将按照以下命名规则保存在指定的输出目录中：

```
<audioKey>_audio_question.mp3       # 问题语音
<audioKey>_audio_answer_simple.mp3  # 简洁答案语音
<audioKey>_audio_answer_detail.mp3  # 详细答案语音
<audioKey>_audio_answer_analysis.mp3 # 分析答案语音
```

其中 `<audioKey>` 是从 JSON 文件中提取的唯一标识符。

## 进度管理

批量处理脚本会自动保存处理进度到输出目录的 `batch_progress.json` 文件中。如果处理被中断，再次运行相同的命令将自动从上次停止的地方继续处理。

## 日志记录

批量处理脚本会将详细的处理日志保存到输出目录的 `batch_processing.log` 文件中，包括处理时间、成功/失败状态、等待时间等信息。

您可以使用以下命令实时查看日志：

```bash
tail -f <输出目录>/batch_processing.log
```

## 安全特性

批量处理脚本包含多层保护机制，避免因频繁调用 API 导致 IP 被封禁：

1. **随机间隔时间**: 每批次处理后随机等待一段时间，避免固定模式触发 API 限制
2. **小批量处理**: 每批次只处理少量文件，减少短时间内的请求数量
3. **进度保存与恢复**: 支持中断恢复，不会因意外情况丢失进度
4. **错误处理**: 单个文件处理失败不会影响整体批处理流程

## 常见问题与解决方案

### 1. 虚拟环境未激活

```bash
source ~/venv-tts/bin/activate
```

### 2. 依赖包缺失

```bash
pip install edge-tts
```

### 3. 网络连接问题
- 确保网络连接正常
- 检查是否能访问 Microsoft Edge TTS 服务
- 可以尝试更换网络环境

### 4. 音频文件生成失败
- 检查 JSON 文件格式是否正确
- 确保 JSON 文件中包含必要的字段（audioKey, question_markdown 等）
- 查看日志文件了解具体错误原因

## 性能优化建议

1. **选择合适的模式**: 根据文件数量选择对应的处理模式
2. **网络环境**: 在稳定的网络环境下运行
3. **监控进度**: 定期查看日志确保处理正常
4. **分段处理**: 对于超大规模的目录，可以考虑手动分目录处理

## 资源占用说明

- **内存**: 处理大量文件时，建议确保系统有足够的可用内存
- **磁盘空间**: 语音文件会占用一定的磁盘空间，请确保输出目录所在磁盘有足够空间
- **网络带宽**: 转换过程中需要稳定的网络连接用于调用 TTS API

## 语音质量优化

脚本默认使用高质量的中文语音（云杨、云健等）。如果需要修改语音设置，可以编辑 `json_to_speech.py` 文件中的 `preferred_voices` 列表。