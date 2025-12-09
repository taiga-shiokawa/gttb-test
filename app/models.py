from datetime import datetime
from typing import Optional

from sqlalchemy import Text, UniqueConstraint
from sqlmodel import Column, Field, SQLModel


class GeneratedDraft(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("owner", "repo", "pr_number", name="uq_pr"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    pr_url: str = Field(index=True)
    owner: str
    repo: str
    pr_number: int
    pr_title: Optional[str] = None
    generated_title: Optional[str] = None
    markdown: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
