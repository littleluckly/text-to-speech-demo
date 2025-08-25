# 安全批量 TTS 处理工具

这套工具可以安全地将大量 Markdown 问答内容转换为音频，避免频繁调用 edge-tts API 导致 IP 被封禁。

## 📁 文件说明

### 核心脚本

- **`question_to_speech.py`** - 基础 TTS 转换脚本（单次处理）
- **`question_to_speech_batch_safe.py`** - 安全批量处理脚本
- **`batch_tts.sh`** - 便捷启动脚本（推荐使用）

### 输入文件

- **`vue_questions-md-format.md`** - 小文件示例（推荐用于测试）
- **`vue_questions-md-format_uuid.md`** - 大文件示例（生产使用需谨慎）

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source ~/venv-tts/bin/activate

# 确认依赖已安装
pip install edge-tts markdown
```

### 2. 选择处理模式

#### 🐌 保守模式（推荐用于大文件）

```bash
./batch_tts.sh conservative large_questions.md output
```

- 每批处理：2-3 个问题
- 间隔时间：10-20 分钟
- 适用场景：100+问题的大文件
- 优点：最大程度避免 API 限制

#### ⚖️ 平衡模式（默认推荐）

```bash
./batch_tts.sh balanced vue_questions.md output
```

- 每批处理：3-5 个问题
- 间隔时间：5-15 分钟
- 适用场景：中等规模文件（20-100 个问题）
- 优点：平衡处理速度和安全性

#### ⚡ 激进模式（小文件快速处理）

```bash
./batch_tts.sh aggressive small_questions.md output
```

- 每批处理：5-8 个问题
- 间隔时间：2-8 分钟
- 适用场景：小文件（<20 个问题）
- 优点：处理速度快

#### 🧪 测试模式（调试用）

```bash
./batch_tts.sh test vue_questions-md-format.md test_output
```

- 每批处理：1 个问题
- 间隔时间：0.5-1 分钟
- 适用场景：测试和调试
- 优点：快速验证功能

#### 🔧 自定义模式

```bash
./batch_tts.sh custom questions.md output 2-4 8-12
```

- 自定义批次大小和间隔时间
- 格式：`批次大小范围 间隔时间范围（分钟）`

## 📊 输出结构

处理完成后，输出目录包含：

```
output/
├── batch_processing.log       # 详细日志文件
├── batch_progress.json        # 进度和状态记录
├── 285acd89_q0001/            # 问题1目录（ID前缀_问题编号）
│   ├── 285acd89_audio_simple.mp3      # ID前缀_简答音频
│   ├── 285acd89_audio_question.mp3    # ID前缀_问题音频
│   ├── 285acd89_audio_analysis.mp3    # ID前缀_解析音频
│   └── 285acd89_meta.json             # ID前缀_元数据文件
├── 0ccadea6_q0002/            # 问题2目录
│   └── ...
└── ...
```

### 文件命名规则

- **目录命名**：`{ID前缀}_q{4位编号}` （例：`285acd89_q0001`）
- **音频文件**：`{ID前缀}_{type}.mp3` （例：`285acd89_audio_simple.mp3`）
- **元数据文件**：`{ID前缀}_meta.json` （例：`285acd89_meta.json`）
- **ID 前缀**：取原始 ID 的前 8 位字符，无 ID 时使用 `q0001` 格式

### 命名优势

- **快速识别**：通过 ID 前缀快速定位问题
- **避免冲突**：每个问题的 ID 是唯一的，确保文件名不重复
- **批量管理**：在处理大量问题时更容易管理和查找
- **兼容性**：保留问题编号作为备用标识

## ⚙️ 高级功能

### 1. 进度恢复

处理可以随时中断，再次运行会自动从上次停止的地方继续：

```bash
# 处理被中断后，重新运行相同命令即可继续
./batch_tts.sh balanced questions.md output
```

### 2. 实时监控

查看处理日志：

```bash
# 实时查看日志
tail -f output/batch_processing.log

# 查看进度
cat output/batch_progress.json
```

### 3. 直接使用 Python 脚本

如果不想使用 Shell 脚本，可以直接调用 Python 脚本：

```bash
# 基本用法
python3 question_to_speech_batch_safe.py input.md output

# 自定义参数
python3 question_to_speech_batch_safe.py input.md output 3-5 5-15
```

## 🛡️ 安全特性

### API 保护机制

1. **随机间隔**：批次间随机等待，模拟人工操作
2. **小批量处理**：避免短时间内大量请求
3. **进度保存**：支持中断恢复，不会丢失进度
4. **错误处理**：单个问题失败不影响整体处理

### 推荐配置

根据文件大小选择合适的模式：

| 问题数量 | 推荐模式     | 预估时间  | 风险等级 |
| -------- | ------------ | --------- | -------- |
| 1-10     | aggressive   | 30 分钟内 | 低       |
| 10-50    | balanced     | 1-3 小时  | 低       |
| 50-100   | balanced     | 3-8 小时  | 中       |
| 100+     | conservative | 8+小时    | 低       |

## 📝 源文件格式要求

### 支持的 Markdown 格式

```markdown
---
id: 285acd89-b79b-49e6-8425-5d60d5101233
type: choice
difficulty: easy
tags: [vue, lifecycle]
---

## **题目：** 这里是问题内容

## **✅ 精简答案：**

这里是精简答案内容

**📘 详细解析：**

这里是详细解析内容

---
```

### 关键要素

- YAML frontmatter（包含 id、type、difficulty、tags）
- 题目部分（`## **题目：**`）
- 精简答案部分（`## **✅ 精简答案：**`）
- 详细解析部分（`**📘 详细解析：**`）
- 问题间用 `---` 分隔

## ❓ 常见问题

### Q: 如何估算处理时间？

A: 脚本启动时会显示预估时间，也可以用以下公式：

- 保守模式：`问题数量 × 15分钟 ÷ 2.5`
- 平衡模式：`问题数量 × 10分钟 ÷ 4`
- 激进模式：`问题数量 × 5分钟 ÷ 6.5`

### Q: 处理被中断了怎么办？

A: 重新运行相同的命令，脚本会自动从上次停止的地方继续。

### Q: 如何修改语音设置？

A: 编辑 `question_to_speech.py` 文件中的 `preferred_voices` 列表。

### Q: 处理失败的问题怎么办？

A: 查看 `batch_progress.json` 中的 `failed_questions` 字段，可以手动处理失败的问题。

## 🔧 故障排除

1. **虚拟环境未激活**

   ```bash
   source ~/venv-tts/bin/activate
   ```

2. **依赖包缺失**

   ```bash
   pip install edge-tts markdown
   ```

3. **网络连接问题**

   - 确保网络连接正常
   - 可以尝试更换网络环境

4. **磁盘空间不足**
   - 清理输出目录中的旧文件
   - 确保有足够的磁盘空间存储音频文件

## 📈 性能优化建议

1. **选择合适的模式**：根据文件大小选择对应的处理模式
2. **网络环境**：在稳定的网络环境下运行
3. **分段处理**：超大文件可以考虑手动分割后分别处理
4. **监控进度**：定期查看日志确保处理正常
