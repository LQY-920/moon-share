"""
AI 摘要生成模块
使用 MiniMax LLM API 生成视频摘要和关键知识点
"""

import requests
import json
from pathlib import Path
from typing import Dict, Optional
from config import API_CONFIG, get_output_path


class AISummarizer:
    """AI 摘要生成器"""

    def __init__(self):
        self.api_key = API_CONFIG["minimax"]["api_key"]
        self.model = API_CONFIG["minimax"]["llm_model"]
        self.endpoint = API_CONFIG["minimax"]["llm_endpoint"]
        self._check_api_key()

    def _check_api_key(self):
        """检查 API Key"""
        if not self.api_key:
            raise ValueError(
                "MiniMax API Key 未配置！\n"
                "请设置环境变量 MINIMAX_API_KEY"
            )

    def summarize(self, text: str, video_id: str, metadata: Dict = None) -> Dict[str, str]:
        """
        生成 AI 摘要和关键知识点

        Args:
            text: 视频文字稿
            video_id: 视频 ID
            metadata: 视频元数据（可选）

        Returns:
            {
                "summary": AI 摘要,
                "key_points": 关键知识点,
                "overview": 简要概述（用于搜索结果展示）
            }
        """
        if not text:
            raise ValueError("文字稿不能为空")

        print(f"🤖 开始 AI 摘要生成...")

        # 构建提示词
        system_prompt = """你是一个专业的视频内容分析助手。请根据提供的文字稿，生成：
1. 内容摘要（200-300字）
2. 关键知识点（5-10个要点）
3. 一句话概述（50字以内，用于搜索结果展示）

请用中文输出，格式如下：
## 摘要
[你的摘要]

## 关键知识点
1. [要点1]
2. [要点2]
...

## 一句话概述
[50字以内]"""

        user_prompt = f"视频文字稿：\n{text[:15000]}"  # 限制输入长度

        # 调用 MiniMax LLM API
        result = self._call_llm(system_prompt, user_prompt)

        # 解析结果
        summary, key_points, overview = self._parse_result(result, text[:500])

        # 保存到文件
        self._save_outputs(video_id, summary, key_points)

        return {
            "summary": summary,
            "key_points": key_points,
            "overview": overview
        }

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 MiniMax LLM API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # 解析返回内容
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]

            raise Exception(f"API 返回格式异常: {result}")

        except requests.exceptions.Timeout:
            raise Exception("LLM API 调用超时")
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API 调用失败: {str(e)}")

    def _parse_result(self, result: str, fallback_text: str) -> tuple:
        """解析 LLM 返回结果"""
        summary = ""
        key_points = ""
        overview = ""

        # 简单解析 - 实际应该用更健壮的解析方式
        lines = result.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("## 摘要"):
                current_section = "summary"
            elif line.startswith("## 关键知识点"):
                current_section = "key_points"
            elif line.startswith("## 一句话概述"):
                current_section = "overview"
            elif line and current_section:
                if current_section == "summary":
                    summary += line + "\n"
                elif current_section == "key_points":
                    key_points += line + "\n"
                elif current_section == "overview":
                    overview += line

        # 如果解析失败，使用 fallback
        if not summary:
            summary = result[:1000] if len(result) > 1000 else result
        if not key_points:
            key_points = "1. 内容见摘要"
        if not overview:
            overview = fallback_text[:50] + "..."

        return summary.strip(), key_points.strip(), overview.strip()

    def _save_outputs(self, video_id: str, summary: str, key_points: str):
        """保存输出文件"""
        # 保存摘要
        summary_file = get_output_path(video_id, "summary.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"# AI 摘要\n\n{summary}\n\n---\n\n# 关键知识点\n\n{key_points}")

        print(f"✅ 摘要已保存: {summary_file}")

    def generate_overview(self, text: str) -> str:
        """生成简短概述（用于搜索结果）"""
        if not text:
            return "暂无概述"

        system_prompt = "请用50字以内的一句话概括以下内容的核心主题："
        user_prompt = text[:1000]

        try:
            result = self._call_llm(system_prompt, user_prompt)
            return result.strip()[:50]
        except:
            return text[:50] + "..."


# 全局 AI 摘要器实例
_summarizer: Optional[AISummarizer] = None

def get_summarizer() -> AISummarizer:
    """获取 AI 摘要器实例"""
    global _summarizer
    if _summarizer is None:
        _summarizer = AISummarizer()
    return _summarizer
