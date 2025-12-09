import re
from typing import Tuple

from fastapi import HTTPException, status

PR_URL_PATTERN = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)",
    re.IGNORECASE,
)


def parse_github_pr_url(pr_url: str) -> Tuple[str, str, int]:
    match = PR_URL_PATTERN.match(pr_url.strip())
    if not match:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid GitHub PR URL.")
    owner = match.group("owner")
    repo = match.group("repo")
    number = int(match.group("number"))
    return owner, repo, number
