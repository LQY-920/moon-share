"""
YouTube Video Analyzer 主入口
整合搜索、解析、ASR、AI摘要的完整流程
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict

from config import PROJECT_ROOT, OUTPUT_DIR, ensure_api_key
from video_search import VideoSearcher, get_searcher
from video_parser import VideoParser
from asr_handler import get_asr_handler
from ai_summarizer import get_summarizer


class YouTubeAnalyzer:
    """YouTube 视频分析器"""

    def __init__(self):
        self.searcher = get_searcher()
        self.current_videos: List[Dict] = []
        self.current_selection: List[Dict] = []
        self.parse_results: Dict[str, Dict] = {}

    def search(self, keyword: str) -> List[Dict]:
        """
        搜索 YouTube 视频

        Args:
            keyword: 搜索关键词

        Returns:
            视频列表
        """
        videos = self.searcher.search(keyword)
        self.current_videos = videos

        # 为每个视频生成 AI 概述
        self._add_ai_overview(videos)

        # 展示结果
        self._display_videos(videos)

        return videos

    def _add_ai_overview(self, videos: List[Dict]):
        """为搜索结果添加 AI 概述"""
        print("\n🤖 正在生成 AI 概述...")

        try:
            # 暂时跳过 ASR，直接用 yt-dlp 获取的描述生成概述
            for video in videos:
                # yt-dlp 搜索结果中没有完整描述，跳过或使用默认值
                video["ai_overview"] = "点击选择查看详情"
        except Exception as e:
            print(f"⚠️ AI 概述生成失败: {e}")

    def _display_videos(self, videos: List[Dict]):
        """展示视频列表"""
        if not videos:
            print("未找到相关视频")
            return

        print("\n" + "="*80)
        print(f"{'编号':<6}{'标题':<35}{'时长':<8}{'观看数':<10}{'AI概述'}")
        print("="*80)

        for i, video in enumerate(videos, 1):
            title = video["title"]
            if len(title) > 33:
                title = title[:30] + "..."

            print(f"[{i:<4}] {title:<35} {video['duration']:<8} {video['view_count']:<10} {video.get('ai_overview', '')[:20]}")

        print("="*80)
        print(f"\n📌 输入 /yta select <编号> 选择视频进行解析")
        print(f"   例如: /yta select 1   (解析第1个视频)")
        print(f"        /yta select 1,3  (解析第1和第3个视频)")

    def select(self, selection: str) -> List[Dict]:
        """
        选择视频进行解析

        Args:
            selection: 选择字符串，如 "1" 或 "1,3"

        Returns:
            选中的视频列表
        """
        indices = []
        for s in selection.split(","):
            s = s.strip()
            if s.isdigit():
                idx = int(s) - 1
                if 0 <= idx < len(self.current_videos):
                    indices.append(idx)

        if not indices:
            print("❌ 无效的选择，请输入正确的编号")
            return []

        self.current_selection = [self.current_videos[i] for i in indices]
        print(f"\n✅ 已选择 {len(self.current_selection)} 个视频")

        # 开始解析
        for video in self.current_selection:
            self._parse_video(video)

        return self.current_selection

    def _parse_video(self, video: Dict):
        """解析单个视频"""
        video_id = video["id"]
        url = video["url"]

        print(f"\n{'='*60}")
        print(f"📺 正在解析: {video['title']}")
        print(f"{'='*60}")

        try:
            # 1. 解析视频（下载素材）
            print("\n[1/4] 📋 获取视频信息...")
            parser = VideoParser()
            result = parser.parse(url)
            self.parse_results[video_id] = result

            # 2. 获取音频路径
            print("\n[2/4] 🎤 查找音频文件...")
            audio_path = parser.get_audio_path()

            if audio_path and audio_path.exists():
                # 3. 语音转文字
                print("\n[3/4] 🔄 语音转文字...")
                asr = get_asr_handler()
                transcript, transcript_file = asr.transcribe_with_srt(audio_path, video_id)
                self.parse_results[video_id]["transcript_file"] = str(transcript_file)
                self.parse_results[video_id]["transcript"] = transcript
                print(f"✅ 文字稿已生成: {transcript_file}")
            else:
                print("⚠️ 未找到音频文件，跳过语音转文字")
                transcript = ""

            # 4. AI 摘要
            if transcript:
                print("\n[4/4] 🤖 生成 AI 摘要...")
                summarizer = get_summarizer()
                summary_result = summarizer.summarize(transcript, video_id, result)
                self.parse_results[video_id]["summary"] = summary_result["summary"]
                self.parse_results[video_id]["key_points"] = summary_result["key_points"]
                self.parse_results[video_id]["overview"] = summary_result["overview"]
            else:
                print("⚠️ 无文字稿，跳过 AI 摘要")

            print(f"\n✅ 解析完成: {video['title']}")
            self._display_result(video_id)

        except NotImplementedError as e:
            print(f"\n⚠️ {str(e)}")
            print("请配置 API Key 后重试")
        except Exception as e:
            print(f"\n❌ 解析失败: {str(e)}")

    def _display_result(self, video_id: str):
        """展示解析结果"""
        result = self.parse_results.get(video_id)
        if not result:
            return

        print(f"\n{'='*60}")
        print(f"📺 解析结果")
        print(f"{'='*60}")
        print(f"标题: {result.get('title', 'N/A')}")
        print(f"时长: {result.get('duration', 'N/A')}")
        print(f"观看数: {result.get('view_count', 'N/A')}")

        if result.get("summary"):
            print(f"\n📝 AI 摘要:")
            print(f"{result['summary'][:500]}...")

        if result.get("key_points"):
            print(f"\n📚 关键知识点:")
            print(result["key_points"][:300])

        print(f"\n📁 文件已保存至: {OUTPUT_DIR / video_id}")

    def parse_url(self, url: str):
        """
        直接解析指定 URL

        Args:
            url: YouTube 视频 URL
        """
        print(f"🔗 直接解析模式: {url}")

        video = {
            "id": "direct",
            "url": url,
            "title": "直接解析"
        }

        self.current_selection = [video]
        self._parse_video(video)

    def display_output(self, video_id: str = None):
        """显示输出文件"""
        if video_id:
            output_dir = OUTPUT_DIR / video_id
        else:
            # 显示最新的输出
            dirs = list(OUTPUT_DIR.glob("*"))
            if dirs:
                output_dir = max(dirs, key=lambda p: p.stat().st_mtime)
            else:
                print("暂无输出文件")
                return

        print(f"\n📁 输出目录: {output_dir}")

        if not output_dir.exists():
            print("目录不存在")
            return

        files = list(output_dir.glob("*"))
        if not files:
            print("目录为空")
            return

        print("\n文件列表:")
        for f in files:
            size = f.stat().st_size
            if size > 1024 * 1024:
                size_str = f"{size / 1024 / 1024:.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"  📄 {f.name:<30} {size_str}")


# 全局分析器实例
_analyzer: Optional[YouTubeAnalyzer] = None

def get_analyzer() -> YouTubeAnalyzer:
    """获取分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = YouTubeAnalyzer()
    return _analyzer


# CLI 入口
def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py search <关键词>")
        print("  python main.py parse <YouTube_URL>")
        print("  python main.py select <编号>")
        print("  python main.py output [视频ID]")
        sys.exit(1)

    command = sys.argv[1].lower()
    analyzer = get_analyzer()

    if command == "search":
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
            sys.exit(1)
        analyzer.search(sys.argv[2])

    elif command == "parse":
        if len(sys.argv) < 3:
            print("请提供 YouTube URL")
            sys.exit(1)
        analyzer.parse_url(sys.argv[2])

    elif command == "select":
        if len(sys.argv) < 3:
            print("请提供选择的编号")
            sys.exit(1)
        analyzer.select(sys.argv[2])

    elif command == "output":
        video_id = sys.argv[2] if len(sys.argv) > 2 else None
        analyzer.display_output(video_id)

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
