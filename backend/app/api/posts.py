"""Pending scheduled-post review and publishing actions."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services import posting_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["posts"])


class PollResponse(BaseModel):
    question: str
    options: list[str]
    poll_type: str
    is_anonymous: bool
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None


class ScheduledPostResponse(BaseModel):
    id: str
    channel_id: str
    channel_name: str
    content: str
    poll: Optional[PollResponse] = None
    status: Literal["pending", "published", "rejected", "generating", "publishing", "failed"]
    scheduled_for: datetime
    created_at: datetime
    published_at: Optional[datetime] = None


@router.get("/pending", response_model=list[ScheduledPostResponse])
async def get_pending_posts(current_user: UserModel = Depends(get_current_user)):
    return await posting_service.list_pending_posts(str(current_user.id))


@router.post("/{post_id}/approve", response_model=ScheduledPostResponse)
async def approve_post(post_id: str, current_user: UserModel = Depends(get_current_user)):
    try:
        return await posting_service.decide_post(post_id, str(current_user.id), approve=True)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Could not publish approved scheduled post %s", post_id)
        raise HTTPException(status_code=502, detail="Telegram could not publish this post. It remains available for review.") from exc


@router.post("/{post_id}/decline", response_model=ScheduledPostResponse)
async def decline_post(post_id: str, current_user: UserModel = Depends(get_current_user)):
    try:
        return await posting_service.decide_post(post_id, str(current_user.id), approve=False)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
