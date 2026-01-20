from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import create_access_token as cat
from app.core.security import create_refresh_token as crt
from app.core.security import hash_password
from app.core.security import set_auth_cookeis as sac
from app.models import User
from app.schema import UserCreate, UserResponse

router = APIRouter()


@router.post("/", status_code=201, response_model=UserResponse)
async def register(
    user_data: UserCreate, response: Response, session: AsyncSession = Depends(get_db)
):
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement=statement)
    exist_user = result.scalar_one_or_none()

    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is alredy in use."
        )

    try:
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email, name=user_data.name, hashed_password=hashed_password
        )

        access_token = cat(new_user.id)
        refresh_token = crt(new_user.id)

        sac(access_token=access_token, refresh_token=refresh_token, response=response)

        session.add(new_user)
        await session.commit()
        await session.refresh()
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering new user: {str(e)}",
        )
