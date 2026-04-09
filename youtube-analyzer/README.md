# YouTube Video Analyzer

YouTube 视频解析工具，输入关键词或 URL，自动化解析视频并生成 AI 摘要与知识点。

## 功能特性

- 🔍 **关键词搜索** - 输入关键词搜索 YouTube 视频
- 📺 **视频解析** - 下载元数据、字幕、音频、缩略图
- 🎤 **语音转文字** - 使用 MiniMax ASR API 转录音频
- 🤖 **AI 摘要** - 使用 MiniMax LLM 生成摘要和关键知识点
- 📁 **多格式输出** - JSON、元数据、文字稿、字幕、音频、缩略图

## 技术栈

- Claude Code Skills（调度层）
- yt-dlp（视频下载）
- MiniMax ASR（语音转文字）
- MiniMax LLM（AI 摘要）

## 项目结构

```
youtube-analyzer/
├── __init__.py
├── main.py              # 主入口
├── config.py            # 配置文件
├── video_search.py      # 视频搜索
├── video_parser.py      # 视频解析
├── asr_handler.py       # ASR 处理
├── ai_summarizer.py     # AI 摘要
├── requirements.txt     # 依赖
└── output/              # 输出目录
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

### 1. 设置 API Key

```bash
export MINIMAX_API_KEY="your_api_key_here"
```

或创建 `.env` 文件：

```
MINIMAX_API_KEY=your_api_key_here
```

### 2. 安装 yt-dlp

```bash
pip install yt-dlp
```

## 使用方法

### 命令行模式

```bash
# 搜索视频
python main.py search "Claude Code 教程"

# 选择视频解析
python main.py select 1

# 直接解析 URL
python main.py parse https://www.youtube.com/watch?v=xxx

# 查看输出文件
python main.py output
```

### Claude Code Skill 模式

```bash
# 搜索
/yta search Claude Code 教程

# 解析
/yta parse https://www.youtube.com/watch?v=xxx

# 选择
/yta select 1
```

## 输出内容

解析完成后，输出以下文件：

```
output/[video_id]/
├── metadata.json      # 元数据
├── subtitles.vtt      # 字幕文件
├── audio.mp3          # 音频文件
├── thumbnail.jpg      # 缩略图
├── transcript.txt     # 文字稿
├── summary.md         # AI 摘要
└── key_points.md      # 关键知识点
```

## 待完成

- [x] 项目框架搭建
- [ ] MiniMax ASR API 集成
- [ ] MiniMax LLM API 集成
- [ ] Claude Code Skill 完整实现
- [ ] 单元测试

## License

MIT
