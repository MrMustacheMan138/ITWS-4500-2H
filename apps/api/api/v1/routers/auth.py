from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Annotated

from database import get_db
from models import User
from core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


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


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignupResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: str

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: DbSession):
    """
    Login endpoint: authenticate user with email and password.
    """
    # Queries the table
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    # Verifies
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    token = create_access_token({"sub": str(user.id)})
    return LoginResponse(
        id=user.id, 
        email=user.email, 
        name=user.name, 
        role=user.role, 
        access_token=token, 
        token_type="bearer"
    )
    


@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: SignupRequest, db: DbSession):
    """
    Signup endpoint: create a new user account.
    """
    result = await db.execute(select(User).where(User.email == user_data.email))
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
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Repopulates new_user with db generated fields like id, created_at

    return SignupResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        created_at=new_user.created_at
    )
