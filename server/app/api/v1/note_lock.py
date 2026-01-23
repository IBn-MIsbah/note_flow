from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Note, NoteLock, User

router = APIRouter()


@router.post("/{note_id}/lock", status_code=200, response_model=dict)
async def acquire_lock(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not foud."
        )

    statement = select(NoteLock).where(NoteLock.note_id == note_id)
    result = await session.execute(statement=statement)
    lock = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    lock_duration = timedelta(seconds=100)

    if lock:
        if lock.expires_at > now and lock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Note is currently being edited by another user",
            )
        lock.user_id = current_user.id
        lock.expires_at = now + lock_duration
    else:
        lock = NoteLock(
            note_id=note_id, user_id=current_user.id, expires_at=now + lock_duration
        )

    session.add(lock)
    await session.commit()

    return {"status": "locked", "expires_at": lock.expires_at}
