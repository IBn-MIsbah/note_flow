from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import create_access_token as cat
from app.core.security import create_refresh_token as crt
from app.core.security import set_auth_cookeis as sac
from app.core.security import verify_password, decode_refresh_token as drt
from app.models import User
from app.schema import LoginInput, UserResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", status_code=200, response_model=dict)
async def login(
    login_data: LoginInput, response: Response, session: AsyncSession = Depends(get_db)
):
    try:
        statemet = select(User).where(User.email == login_data.email)
        result = await session.execute(statement=statemet)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Email not found."
            )

        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password",
            )

        access_token = cat(user.id)
        refresh_token = crt(user.id)
        sac(access_token=access_token, refresh_token=refresh_token, response=response)

        return {"message": "Logged in successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
        )

@router.get('/me', status_code=200, response_model=UserResponse)
async def read_me(current_user:User = Depends(get_current_user)):
    return current_user

@router.post('/refresh-token', status_code=204)
async def refresh_token(request:Request, response:Response, session:AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session Expired. Please Login to continue."
        )
    
    user_id=await drt(refresh_token=refresh_token)
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_access_token = cat(user.id)
    new_refresh_token = crt(user.id)
    sac(access_token=new_access_token, refresh_token=new_refresh_token, response=response)

    return None
