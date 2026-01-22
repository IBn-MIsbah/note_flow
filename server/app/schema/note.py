from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    title: str
    content: Optional[Dict[str, Any]] = None


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: UUID

    user_id: UUID

    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
