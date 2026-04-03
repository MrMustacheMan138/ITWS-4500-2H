from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User

#from @/core/auth.py import hashpassword

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str = Field(alias="confirmPassword")


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == credentials.email))
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    display_name = user.name.strip() or user.email

    return LoginResponse(
        id=user.id,
        email=user.email,
        name=display_name,
        role=user.role,
        access_token=f"user-{user.id}",
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    normalized_name = payload.name.strip()
    if len(normalized_name) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")

    existing_user = await db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=normalized_name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RegisterResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
    )

@router.get("/me", response_model=)
