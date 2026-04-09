"""
YouTube Video Analyzer 配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# API 配置 - 待补充
API_CONFIG = {
    "minimax": {
        # MiniMax API Key - 待补充
        "api_key": os.getenv("MINIMAX_API_KEY", ""),
        # MiniMax LLM 模型
        "llm_model": "MiniMax-M2.7",
        # MiniMax ASR 模型 - 待确认
        "asr_model": "speech-02-turbo",
        # LLM API 端点
        "llm_endpoint": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        # ASR API 端点 - 待确认
        "asr_endpoint": "https://api.minimax.chat/v1/audio/v1",
    }
}

# yt-dlp 配置
YTDLP_CONFIG = {
    # 下载格式偏好
    "format_preference": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    # 字幕格式
    "subtitle_format": "vtt",
    # 输出模板
    "output_template": str(OUTPUT_DIR / "%(id)s" / "%(title)s.%(ext)s"),
}

# 搜索配置
SEARCH_CONFIG = {
    # 最多返回视频数
    "max_results": 10,
    # 搜索结果字段
    "fields": ["title", "duration", "view_count", "upload_date"],
}

# 解析配置
PARSER_CONFIG = {
    # 需要下载的内容
    "download_items": ["metadata", "subtitles", "audio", "thumbnail"],
    # 音频格式
    "audio_format": "mp3",
}

def get_output_path(video_id: str, filename: str) -> Path:
    """获取输出文件路径"""
    video_dir = OUTPUT_DIR / video_id
    video_dir.mkdir(parents=True, exist_ok=True)
    return video_dir / filename

def ensure_api_key():
    """检查 API Key 是否已配置"""
    if not API_CONFIG["minimax"]["api_key"]:
        raise ValueError(
            "MiniMax API Key 未配置！\n"
            "请在 config.py 中设置 MINIMAX_API_KEY 环境变量，"
            "或在环境变量中配置。"
        )
