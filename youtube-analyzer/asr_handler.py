"""
语音识别模块 (ASR)
使用 MiniMax Speech API 进行语音转文字
"""

import requests
from pathlib import Path
from typing import Optional
from config import API_CONFIG, get_output_path


class ASRHandler:
    """语音识别处理器"""

    def __init__(self):
        self.api_key = API_CONFIG["minimax"]["api_key"]
        self.model = API_CONFIG["minimax"]["asr_model"]
        self.endpoint = API_CONFIG["minimax"]["asr_endpoint"]
        self._check_api_key()

    def _check_api_key(self):
        """检查 API Key"""
        if not self.api_key:
            raise ValueError(
                "MiniMax API Key 未配置！\n"
                "请设置环境变量 MINIMAX_API_KEY"
            )

    def transcribe(self, audio_path: Path, video_id: str) -> str:
        """
        将音频转换为文字

        Args:
            audio_path: 音频文件路径
            video_id: 视频 ID

        Returns:
            转录文本
        """
        if not audio_path or not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        print(f"🎤 开始语音识别: {audio_path.name}")

        # TODO: MiniMax ASR API 调用
        # API 端点和参数待确认
        #
        # 参考调用方式（待完成）:
        #
        # url = f"{self.endpoint}/v1/audio/transcriptions"
        # headers = {
        #     "Authorization": f"Bearer {self.api_key}"
        # }
        # files = {
        #     "file": open(audio_path, "rb"),
        #     "model": (None, self.model),
        # }
        # response = requests.post(url, headers=headers, files=files)
        # result = response.json()
        # return result.get("text", "")

        raise NotImplementedError(
            "MiniMax ASR API 调用尚未实现！\n"
            "需要确认:\n"
            "1. ASR API 端点\n"
            "2. 请求参数格式\n"
            "3. 返回格式\n"
            "请在 MiniMax 控制台获取 API 文档后补充。"
        )

    def transcribe_with_srt(self, audio_path: Path, video_id: str) -> tuple[str, Path]:
        """
        将音频转换为文字（带时间戳）

        Args:
            audio_path: 音频文件路径
            video_id: 视频 ID

        Returns:
            (转录文本, SRT文件路径)
        """
        # TODO: 实现带时间戳的转录
        text = self.transcribe(audio_path, video_id)

        # 保存转录文本
        transcript_file = get_output_path(video_id, "transcript.txt")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(text)

        return text, transcript_file


# 全局 ASR 处理器实例
_asr_handler: Optional[ASRHandler] = None

def get_asr_handler() -> ASRHandler:
    """获取 ASR 处理器实例"""
    global _asr_handler
    if _asr_handler is None:
        _asr_handler = ASRHandler()
    return _asr_handler
