from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import GeneratedDraft
from app.schemas import DraftListItem, DraftResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[DraftListItem])
def list_history(limit: int = 20, session: Session = Depends(get_session)):
    drafts = session.exec(
        select(GeneratedDraft).order_by(GeneratedDraft.created_at.desc()).limit(limit)
    ).all()
    return drafts


@router.get("/{draft_id}", response_model=DraftResponse)
def get_history_item(draft_id: int, session: Session = Depends(get_session)):
    draft = session.get(GeneratedDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found.")
    return draft
