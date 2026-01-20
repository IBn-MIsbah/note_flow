"""
id email password_hash name created_at updated_at
one user many notes
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import Note, NoteLock


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: Optional[str] = Field(index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str = Field()
    notes: List["Note"] = Relationship(back_populates="owner")
    locks: List["NoteLock"] = Relationship(back_populates="user")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
        )
    )
