from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import GeneratedDraft
from app.schemas import DraftResponse, GenerateRequest
from app.services.blog_generator import BlogGenerator, extract_title_from_markdown
from app.services.github import GitHubClient
from app.services.llm import LLMClient
from app.utils import parse_github_pr_url

router = APIRouter(prefix="/api", tags=["generate"])

github_client = GitHubClient()
blog_generator = BlogGenerator(LLMClient())


@router.post("/generate", response_model=DraftResponse)
async def generate_draft(payload: GenerateRequest, session: Session = Depends(get_session)):
    owner, repo, pr_number = parse_github_pr_url(payload.pr_url)
    pr_data = await github_client.get_pull_request_bundle(owner, repo, pr_number)
    markdown = await blog_generator.generate(pr_data)
    generated_title = extract_title_from_markdown(markdown)

    existing = session.exec(
        select(GeneratedDraft).where(
            GeneratedDraft.owner == owner,
            GeneratedDraft.repo == repo,
            GeneratedDraft.pr_number == pr_number,
        )
    ).first()

    if existing:
        existing.markdown = markdown
        existing.generated_title = generated_title
        existing.pr_title = pr_data.title
        existing.pr_url = payload.pr_url
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    draft = GeneratedDraft(
        pr_url=payload.pr_url,
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        pr_title=pr_data.title,
        generated_title=generated_title,
        markdown=markdown,
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft
