"""Users API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services import user_service
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: str
    telegram_id: int
    first_name: str
    last_name: str | None
    username: str | None
    photo_url: str | None
    language_code: str
    display_name: str


class UpdateLanguageRequest(BaseModel):
    language_code: str


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return _to_response(current_user)


@router.patch("/me/language", response_model=UserResponse)
async def update_language(
    body: UpdateLanguageRequest,
    current_user: UserModel = Depends(get_current_user),
):
    updated = await user_service.update_user_language(
        str(current_user.id), body.language_code
    )
    return _to_response(updated)


def _to_response(user: UserModel) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        photo_url=user.photo_url,
        language_code=user.language_code,
        display_name=user.display_name,
    )
