"""
User MongoDB document model.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return cls(str(v))
        if isinstance(v, str) and ObjectId.is_valid(v):
            return cls(v)
        raise ValueError(f"Invalid ObjectId: {v}")


class UserModel(BaseModel):
    """Represents a row in the `users` MongoDB collection."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    telegram_id: int                        # Telegram user ID (unique)
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None          # Telegram @username
    photo_url: Optional[str] = None         # Telegram profile image
    language_code: str = "en"              # Preferred language

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @property
    def display_name(self) -> str:
        parts = [self.first_name]
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)
