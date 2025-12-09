from textwrap import shorten
from typing import List, Optional

from app.schemas import PullRequestComment, PullRequestData, PullRequestFile


def _summarize_files(files: List[PullRequestFile]) -> str:
    lines: List[str] = []
    for file in files[:15]:
        summary = f"- {file.filename} (+{file.additions or 0}/-{file.deletions or 0}, {file.status or 'modified'})"
        if file.patch:
            snippet = shorten(file.patch.replace("\n", " "), width=220, placeholder=" ...")
            summary += f" | patch: {snippet}"
        lines.append(summary)
    return "\n".join(lines) if lines else "No file summary available."


def _summarize_comments(comments: List[PullRequestComment]) -> str:
    lines: List[str] = []
    for comment in comments[:15]:
        author = comment.user or "someone"
        location = f" ({comment.path})" if comment.path else ""
        snippet = shorten(comment.body.replace("\n", " "), width=180, placeholder=" ...")
        lines.append(f"- {author}{location}: {snippet}")
    return "\n".join(lines) if lines else "No review comments."


def _truncate_block(text: str | None, limit: int = 4000) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else f"{text[:limit]}... [truncated]"


def extract_title_from_markdown(markdown: str) -> Optional[str]:
    for line in markdown.splitlines():
        if line.strip().startswith("#"):
            return line.lstrip("#").strip()
    return None


class BlogGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def _build_messages(self, pr: PullRequestData) -> List[dict]:
        files_summary = _summarize_files(pr.files)
        comments_summary = _summarize_comments(pr.comments)
        diff_excerpt = _truncate_block(pr.diff, limit=6000)
        body_excerpt = _truncate_block(pr.body, limit=2000)

        system_prompt = (
            "あなたはCTOの代わりにテックブログの下書きを作る技術広報ライターです。"
            "出力はMarkdownのみ。"
            "構成は以下を必ず含めてください:\n"
            "1) タイトル案を2〜3件\n"
            "2) 見出し構成 (箇条書き)\n"
            "3) 本文: 背景, 技術的課題, 解決策の方針, 実装のポイント, まとめ(学び・今後の課題)\n"
            "読者はエンジニア。簡潔かつ具体的に書き、数字や指標があれば活用してください。"
        )

        user_prompt = (
            f"PRタイトル: {pr.title}\n"
            f"PR本文:\n{body_excerpt or 'なし'}\n\n"
            f"変更ファイル概要:\n{files_summary}\n\n"
            f"レビューコメント:\n{comments_summary}\n\n"
            f"Diff抜粋:\n{diff_excerpt or 'diff取得なし'}\n\n"
            "上記をもとにテックブログ下書きを作成してください。"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    async def generate(self, pr: PullRequestData) -> str:
        messages = self._build_messages(pr)
        return await self.llm_client.generate(messages)
