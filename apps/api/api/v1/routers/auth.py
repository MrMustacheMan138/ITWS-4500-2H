from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Annotated
from datetime import datetime

from database import get_db
from models import User
from core.auth import verify_password, get_password_hash, create_access_token

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_admin: bool
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignupResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: DbSession):
    email = credentials.email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    token = create_access_token({"sub": str(user.id)})

    return LoginResponse(
        id=user.id,
        email=user.email,
        name=user.full_name,
        is_admin=user.is_admin,
        access_token=token,
        token_type="bearer"
    )


@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: SignupRequest, db: DbSession):
    email = user_data.email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(user_data.password) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot exceed 72 characters"
        )

    hashed_pw = get_password_hash(user_data.password)

    new_user = User(
        email=email,
        full_name=user_data.full_name,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return SignupResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.full_name,
        created_at=new_user.created_at
    )