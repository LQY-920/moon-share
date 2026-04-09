"""
YouTube 视频搜索模块
使用 yt-dlp 搜索 YouTube 视频
"""

import json
import subprocess
from typing import List, Dict, Optional
from config import SEARCH_CONFIG, get_output_path


class VideoSearcher:
    """YouTube 视频搜索器"""

    def __init__(self):
        self.max_results = SEARCH_CONFIG["max_results"]
        self.fields = SEARCH_CONFIG["fields"]

    def search(self, keyword: str) -> List[Dict]:
        """
        搜索 YouTube 视频

        Args:
            keyword: 搜索关键词

        Returns:
            视频信息列表
        """
        print(f"🔍 正在搜索: {keyword}")

        # yt-dlp 搜索命令
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(title)s|%(duration)s|%(view_count)s|%(upload_date)s|%(id)s|%(url)s",
            f"ytsearch{self.max_results}:{keyword}",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )

            videos = self._parse_search_results(result.stdout)
            print(f"✅ 找到 {len(videos)} 个视频")
            return videos

        except subprocess.TimeoutExpired:
            raise Exception("搜索超时，请重试")
        except subprocess.CalledProcessError as e:
            raise Exception(f"搜索失败: {e.stderr}")
        except Exception as e:
            raise Exception(f"搜索异常: {str(e)}")

    def _parse_search_results(self, raw_output: str) -> List[Dict]:
        """解析搜索结果"""
        videos = []
        lines = raw_output.strip().split('\n')

        for line in lines:
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) < 6:
                continue

            title, duration, view_count, upload_date, video_id, url = parts[:6]

            # 格式化时长
            duration_str = self._format_duration(int(duration) if duration.isdigit() else 0)

            # 格式化观看数
            view_str = self._format_count(int(view_count) if view_count.isdigit() else 0)

            # 格式化日期
            date_str = self._format_date(upload_date)

            videos.append({
                "id": video_id,
                "title": title,
                "duration": duration_str,
                "view_count": view_str,
                "upload_date": date_str,
                "url": url,
            })

        return videos

    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if seconds >= 3600:
            return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"
        return f"{seconds // 60}:{seconds % 60:02d}"

    def _format_count(self, count: int) -> str:
        """格式化观看数"""
        if count >= 100000000:
            return f"{count / 100000000:.1f}亿"
        if count >= 10000:
            return f"{count / 10000:.1f}万"
        return str(count)

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return date_str

    def display_results(self, videos: List[Dict]) -> None:
        """展示搜索结果"""
        if not videos:
            print("未找到相关视频")
            return

        print("\n" + "="*80)
        print(f"{'编号':<6}{'标题':<40}{'时长':<10}{'观看数':<10}{'发布日期'}")
        print("="*80)

        for i, video in enumerate(videos, 1):
            title = video["title"][:38] + ".." if len(video["title"]) > 40 else video["title"]
            print(f"[{i:<4}] {title:<40} {video['duration']:<10} {video['view_count']:<10} {video['upload_date']}")

        print("="*80)
        print(f"\n输入 /yta select <编号> 选择视频进行解析")
        print(f"例如: /yta select 1")


# 全局搜索器实例
_searcher: Optional[VideoSearcher] = None

def get_searcher() -> VideoSearcher:
    """获取搜索器实例"""
    global _searcher
    if _searcher is None:
        _searcher = VideoSearcher()
    return _searcher
