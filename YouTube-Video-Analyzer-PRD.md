# YouTube Video Analyzer - Product Spec

## 1. 产品定位

**产品名称**: YouTube Video Analyzer
**一句话说明**: 输入关键词或 YouTube URL，自动化解析视频并生成 AI 摘要与知识点

**解决什么问题**:
- 快速从 YouTube 视频中提取内容，无需完整观看
- 将视频内容转化为可用的文字素材
- 支持多平台内容创作（公众号、抖音、小红书、朋友圈）

**核心技术栈**:
- Claude Code Skills（调度层 + 交互界面）
- yt-dlp（视频下载 + YouTube 搜索）
- 豆包 ASR API（语音转文字）
- 智谱 glm-4（AI 摘要 + 关键信息提取）

---

## 2. 核心功能

### 2.1 视频搜索模式

| 功能 | 说明 |
|------|------|
| 关键词搜索 | 输入关键词，yt-dlp 搜索 YouTube 视频 |
| 视频列表展示 | 显示标题、时长、观看数、AI 概述 |
| 视频选择 | 用户从列表中选择一个或多个视频 |
| URL 直解析 | 输入 YouTube URL，直接解析指定视频 |

**搜索结果展示字段**:
- 标题
- 时长
- 观看数
- AI 简要概述（50字以内）

### 2.2 视频解析功能

| 功能 | 说明 |
|------|------|
| 元数据提取 | 标题、描述、时长、观看数、发布时间 |
| 字幕下载 | 自动字幕 / 手动上传的字幕 |
| 音频提取 | 提取音频流（用于 ASR 转录） |
| 缩略图下载 | 下载视频封面图 |
| 语音转文字 | 豆包 ASR API 转录视频音频 |
| AI 摘要 | glm-4 生成视频内容摘要 |
| 关键信息提取 | 主题、知识点、语速、风格分析 |

### 2.3 输出内容

解析完成后，输出以下文件/内容：

```
output/
├── metadata.json          # 元数据（标题、描述、时长、观看数、发布时间）
├── subtitles.vtt          # 字幕文件（WebVTT格式）
├── audio.mp3              # 音频文件
├── thumbnail.jpg          # 缩略图
├── transcript.txt         # 文字稿（ASR结果）
├── summary.md             # AI摘要
└── key_points.md          # 关键知识点
```

---

## 3. 用户流程

### 3.1 关键词搜索流程

```
用户输入关键词
    ↓
yt-dlp 搜索 YouTube（返回视频列表）
    ↓
展示视频列表：标题 + 时长 + 观看数 + AI概述
    ↓
用户选择视频（单选或多选）
    ↓
进入解析流程
```

### 3.2 URL 直解析流程

```
用户输入 YouTube URL
    ↓
验证 URL 格式
    ↓
进入解析流程
```

### 3.3 完整解析流程

```
yt-dlp 下载素材
├── 视频元数据
├── 字幕文件
├── 音频流
└── 缩略图
    ↓
豆包 ASR API 语音转文字
    ↓
glm-4 AI 摘要 + 关键信息提取
    ↓
输出结构化结果
```

---

## 4. 技术架构

### 4.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skill                      │
│                    （调度层 + 交互界面）                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     Python 脚本层                         │
│  ├── video_search.py    （yt-dlp 搜索）                  │
│  ├── video_parser.py    （yt-dlp 下载 + 解析）           │
│  ├── asr_handler.py     （豆包 ASR 调用）                │
│  └── ai_summarizer.py   （glm-4 摘要生成）               │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                       外部 API                            │
│  ├── YouTube（yt-dlp 访问）                              │
│  ├── 豆包 ASR API（语音转文字）                          │
│  └── 智谱 glm-4 API（AI 摘要）                           │
└─────────────────────────────────────────────────────────┘
```

### 4.2 模块职责

| 模块 | 职责 |
|------|------|
| `skill.yaml` | Skill 配置，定义命令和参数 |
| `main.py` | 主入口，协调各模块 |
| `video_search.py` | yt-dlp 搜索功能 |
| `video_parser.py` | yt-dlp 下载和素材解析 |
| `asr_handler.py` | 豆包 ASR API 调用 |
| `ai_summarizer.py` | glm-4 API 调用 |
| `output_formatter.py` | 结果格式化输出 |

### 4.3 API 配置

```yaml
# skill.yaml
apis:
  doubao_asr:
    endpoint: "https://ark.cn-beijing.volces.com/api/v3/audio/transcription"
    model: "doubbao-s2-32k"

  zhipu_glm4:
    endpoint: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    model: "glm-4"
```

---

## 5. AI 能力配置

### 5.1 豆包 ASR

| 配置项 | 值 |
|--------|-----|
| 模型 | doubbao-s2-32k |
| 用途 | 语音转文字 |
| 输入 | 音频文件（mp3/m4a/wav） |
| 输出 | 文字稿（.txt） |

### 5.2 智谱 glm-4

| 配置项 | 值 |
|--------|-----|
| 模型 | glm-4 |
| 用途 | AI 摘要生成、关键信息提取 |
| 输入 | 文字稿 |
| 输出 | AI 摘要（.md）、关键知识点（.md） |

---

## 6. Skill 实现思路

### 6.1 命令设计

```bash
# 关键词搜索
/yta search <关键词>

# URL 解析
/yta parse <YouTube_URL>

# 交互式选择（搜索后）
/yta select <视频编号>
```

### 6.2 交互流程

```
用户: /yta search Claude Code 教程
Skill:
  1. 调用 video_search.py 搜索
  2. 返回视频列表：
     [1] Claude Code 入门教程 (15:32) - 10.2万观看
         AI概述: 介绍Claude Code基本用法...
     [2] Claude Code 高级技巧 (22:15) - 5.6万观看
         AI概述: 深入讲解Skills和Hooks...
     [3] ...
用户: /yta select 1
Skill:
  1. 调用 video_parser.py 解析视频
  2. 调用 asr_handler.py 转录
  3. 调用 ai_summarizer.py 生成摘要
  4. 返回完整结果
```

### 6.3 输出格式化

解析完成后，以结构化方式展示：

```
✅ 解析完成

📺 视频信息
标题: xxx
时长: 15:32
观看数: 10.2万
发布: 2024-01-15

📝 AI 摘要
[摘要内容...]

📚 关键知识点
1. xxx
2. xxx
3. xxx

📁 文件已保存至 output/[video_id]/
├── metadata.json
├── subtitles.vtt
├── audio.mp3
├── thumbnail.jpg
├── transcript.txt
├── summary.md
└── key_points.md
```

---

## 7. 注意事项

### 7.1 YouTube 下载限制
- 部分视频可能因版权或地区限制无法下载
- 字幕取决于视频是否有自动字幕

### 7.2 API 成本
- 豆包 ASR：按实际使用量计费
- 智谱 glm-4：按 token 计费
- 建议添加用量监控

### 7.3 错误处理
- 网络超时重试机制
- API 失败降级策略
- 用户中断处理

---

## 8. 待补充

- [ ] 豆包 ASR API Key 配置
- [ ] 智谱 glm-4 API Key 配置
- [ ] 输出目录路径配置
- [ ] 多语言支持（是否需要翻译功能）
- [ ] 批量处理（一次解析多个视频）
