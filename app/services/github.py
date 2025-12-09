import logging
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas import PullRequestComment, PullRequestData, PullRequestFile

logger = logging.getLogger(__name__)
settings = get_settings()


class GitHubClient:
    def __init__(self, token: str | None = settings.github_token, base_url: str = settings.github_api_base):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers: Dict[str, str] = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
            self.headers["X-GitHub-Api-Version"] = "2022-11-28"

    async def _get(self, url: str, headers: Dict[str, str] | None = None, params: Dict[str, Any] | None = None):
        merged_headers = {**self.headers, **(headers or {})}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=merged_headers, params=params)

        if response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            logger.warning("GitHub authentication failed: %s", response.text)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GitHub authentication failed.")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull request not found.")
        if response.is_error:
            logger.error("GitHub API error %s: %s", response.status_code, response.text)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="GitHub API error.")
        return response

    async def fetch_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = await self._get(url)
        return response.json()

    async def fetch_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = await self._get(url, params={"per_page": 100})
        return response.json()

    async def fetch_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        response = await self._get(url, params={"per_page": 100})
        return response.json()

    async def fetch_diff(self, owner: str, repo: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = await self._get(url, headers={"Accept": "application/vnd.github.v3.diff"})
        return response.text

    async def get_pull_request_bundle(self, owner: str, repo: str, pr_number: int) -> PullRequestData:
        pr_json = await self.fetch_pull_request(owner, repo, pr_number)
        files_json = await self.fetch_files(owner, repo, pr_number)
        comments_json = await self.fetch_comments(owner, repo, pr_number)
        diff_text = await self.fetch_diff(owner, repo, pr_number)

        pr_files = [
            PullRequestFile(
                filename=item.get("filename"),
                status=item.get("status"),
                additions=item.get("additions"),
                deletions=item.get("deletions"),
                patch=item.get("patch"),
            )
            for item in files_json
        ]
        pr_comments = [
            PullRequestComment(
                user=(comment.get("user") or {}).get("login"),
                body=comment.get("body") or "",
                path=comment.get("path"),
                position=comment.get("position"),
            )
            for comment in comments_json
        ]
        return PullRequestData(
            title=pr_json.get("title") or "",
            body=pr_json.get("body"),
            diff=diff_text,
            files=pr_files,
            comments=pr_comments,
        )
