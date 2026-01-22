from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Note, User
from app.schema.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter()


@router.post("/", status_code=201, response_model=NoteRead)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):

    new_note = Note(
        title=note_data.title, content=note_data.content, user_id=current_user.id
    )
    try:
        session.add(new_note)
        await session.commit()
        await session.refresh(new_note)
        return new_note
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating new Note: {str(e)}",
        )


@router.get("/", status_code=200, response_model=list[NoteRead])
async def list_notes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    statement = (
        select(Note)
        .where(Note.user_id == current_user.id)
        .where(Note.is_deleted.is_(False))
        .order_by(Note.updated_at.desc())
    )
    result = await session.execute(statement=statement)
    notes = result.scalars().all()

    return notes


@router.get("/{note_id}", status_code=200, response_model=NoteRead)
async def read_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    statement = select(Note).where(Note.id == note_id)
    result = await session.execute(statement=statement)
    note = result.scalar_one_or_none()

    if not note or not note.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this note",
        )
    return note


@router.patch("/{note_id}", status_code=200)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    statement = select(Note).where(Note.id == note_id)
    result = await session.execute(statement=statement)
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note note foud."
        )
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    update_data = note_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    session.add(note)
    await session.commit()
    await session.refresh(note)

    return {"message": "Note updated successfully"}


@router.patch("/delete/{note_id}", status_code=200, response_model=dict)
async def soft_delete(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    statement = select(Note).where(Note.id == note_id)
    result = await session.execute(statement=statement)
    note = result.scalar_one_or_none()

    if not note or note.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found."
        )

    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized."
        )

    note.is_deleted = True
    session.add(note)
    try:
        await session.commit()
        return {"message": "Note moved to trash seccessfully."}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error during deletion")
