from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PullRequestFile(BaseModel):
    filename: str
    status: Optional[str] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    patch: Optional[str] = None


class PullRequestComment(BaseModel):
    user: Optional[str] = None
    body: str
    path: Optional[str] = None
    position: Optional[int] = None


class PullRequestData(BaseModel):
    title: str
    body: Optional[str] = None
    diff: Optional[str] = None
    files: List[PullRequestFile] = Field(default_factory=list)
    comments: List[PullRequestComment] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    pr_url: str


class DraftResponse(BaseModel):
    id: int
    pr_url: str
    owner: str
    repo: str
    pr_number: int
    pr_title: Optional[str] = None
    generated_title: Optional[str] = None
    markdown: str
    created_at: datetime

    class Config:
        orm_mode = True


class DraftListItem(BaseModel):
    id: int
    pr_url: str
    pr_title: Optional[str] = None
    generated_title: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
