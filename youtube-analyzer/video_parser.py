"""
YouTube 视频解析模块
使用 yt-dlp 下载视频、字幕、音频、缩略图
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from config import YTDLP_CONFIG, PARSER_CONFIG, get_output_path


class VideoParser:
    """YouTube 视频解析器"""

    def __init__(self, video_url: str = None, video_id: str = None):
        self.video_url = video_url
        self.video_id = video_id
        self.output_dir = None

    def parse(self, url: str) -> Dict:
        """
        解析 YouTube 视频

        Args:
            url: YouTube 视频 URL

        Returns:
            解析结果字典
        """
        self.video_url = url
        print(f"📥 开始解析视频: {url}")

        # 1. 获取元数据
        print("📋 获取视频元数据...")
        metadata = self._get_metadata(url)
        self.video_id = metadata.get("id")
        self.output_dir = get_output_path(self.video_id, "")

        # 2. 下载素材
        print("⬇️ 下载视频素材...")
        self._download_materials(url)

        # 3. 返回解析结果
        return {
            "id": self.video_id,
            "title": metadata.get("title"),
            "description": metadata.get("description"),
            "duration": metadata.get("duration"),
            "view_count": metadata.get("view_count"),
            "upload_date": metadata.get("upload_date"),
            "thumbnail": str(get_output_path(self.video_id, "thumbnail.jpg")),
            "subtitles": str(get_output_path(self.video_id, "subtitles.vtt")),
            "audio": str(get_output_path(self.video_id, "audio.mp3")),
            "metadata_file": str(get_output_path(self.video_id, "metadata.json")),
        }

    def _get_metadata(self, url: str) -> Dict:
        """获取视频元数据"""
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            url
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            data = json.loads(result.stdout.strip())

            # 提取需要的字段
            metadata = {
                "id": data.get("id"),
                "title": data.get("title"),
                "description": data.get("description", ""),
                "duration": data.get("duration"),
                "view_count": data.get("view_count"),
                "upload_date": data.get("upload_date"),
                "uploader": data.get("uploader"),
                "thumbnail": data.get("thumbnail"),
            }

            # 保存元数据到文件
            if self.video_id:
                metadata_file = get_output_path(self.video_id, "metadata.json")
                metadata_file.parent.mkdir(parents=True, exist_ok=True)
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

            return metadata

        except subprocess.TimeoutExpired:
            raise Exception("获取元数据超时")
        except subprocess.CalledProcessError as e:
            raise Exception(f"获取元数据失败: {e.stderr}")
        except json.JSONDecodeError:
            raise Exception("解析元数据格式失败")

    def _download_materials(self, url: str) -> None:
        """下载视频素材"""
        if not self.video_id:
            raise Exception("视频 ID 未设置")

        output_template = str(get_output_path(self.video_id, "%(title)s.%(ext)s"))

        # yt-dlp 下载命令
        cmd = [
            "yt-dlp",
            # 下载设置
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs", "zh-Hans,zh-Hant,en,auto",
            "--convert-subs", "vtt",
            "--extract-audio",
            "--audio-format", PARSER_CONFIG["audio_format"],
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            # 输出设置
            "-o", output_template,
            # 格式设置
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            url
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # 10分钟超时
            )
            print(f"✅ 素材下载完成")

        except subprocess.TimeoutExpired:
            raise Exception("下载超时，请检查网络或视频是否可用")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or "未知错误"
            raise Exception(f"下载失败: {error_msg}")

    def get_audio_path(self) -> Optional[Path]:
        """获取音频文件路径"""
        if not self.video_id:
            return None

        audio_dir = get_output_path(self.video_id, "")
        if not audio_dir.exists():
            return None

        # 查找音频文件
        for ext in ["mp3", "m4a", "wav"]:
            files = list(audio_dir.glob(f"*.{ext}"))
            if files:
                return files[0]

        return None

    def get_subtitle_path(self) -> Optional[Path]:
        """获取字幕文件路径"""
        if not self.video_id:
            return None

        subtitle_file = get_output_path(self.video_id, "subtitles.vtt")
        if subtitle_file.exists():
            return subtitle_file

        # 尝试查找其他字幕文件
        subtitle_dir = get_output_path(self.video_id, "")
        vtt_files = list(subtitle_dir.glob("*.vtt"))
        if vtt_files:
            return vtt_files[0]

        return None
