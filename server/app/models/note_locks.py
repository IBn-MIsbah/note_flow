"""id note_id(FK notes.id unique) user_id(FK user.id) created_at expires_at"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import Note, User


class NoteLock(SQLModel, table=True):
    __tablename__ = "note_locks"  # type: ignore

    id: UUID = Field(index=True, primary_key=True, default_factory=uuid.uuid4)
    note_id: UUID = Field(foreign_key="notes.id", unique=True)
    user_id: UUID = Field(foreign_key="users.id")

    expires_at: datetime = Field(index=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    note: "Note" = Relationship(back_populates="locks")
    user: "User" = Relationship(back_populates="locks")
