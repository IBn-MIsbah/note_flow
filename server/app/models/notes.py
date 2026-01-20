"""
id title content (text/json) user_id(FK user.id) created_at updated_at
relation one note many user
0 or one active lock
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import JSON, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import NoteLock, User


class Note(SQLModel, table=True):
    __tablename__ = "notes"  # type: ignore

    id: UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )
    title: str = Field(index=True)
    content: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    user_id: UUID = Field(foreign_key="users.id", index=True)
    owner: "User" = Relationship(back_populates="notes")

    locks: Optional["NoteLock"] = Relationship(back_populates="note")
    is_deleted: bool = Field(default=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
        )
    )
