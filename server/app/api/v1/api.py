from fastapi import APIRouter

from app.api.v1 import auth, note, user

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(note.router, prefix="/notes", tags=["notes"])
