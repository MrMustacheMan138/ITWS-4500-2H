from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from database import get_db
from models import User
from core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignupResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str


class LogoutRequest(BaseModel):
    """Placeholder for logout - in practice, token invalidation is handled client-side"""
    pass


class LogoutResponse(BaseModel):
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login endpoint: authenticate user with email and password.
    
    TODO: Implement:
    1. Query User table for user with matching email
    2. Verify password using verify_password(credentials.password, user.hashed_password)
    3. If verification fails, raise HTTPException(status_code=401, detail="Invalid credentials")
    4. Generate JWT token using create_access_token({"sub": user.email, "user_id": user.id})
    5. Return access_token and token_type
    """
    # Placeholder implementation
    return {
        "access_token": "dummy_token_replace_me",
        "token_type": "bearer"
    }


@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: SignupRequest, db: AsyncSession = Depends(get_db)):
    """
    Signup endpoint: create a new user account.
    
    TODO: Implement:
    1. Check if user with email already exists: 
       result = await db.execute(select(User).where(User.email == user_data.email))
       existing_user = result.scalars().first()
       if existing_user: raise HTTPException(status_code=400, detail="Email already registered")
    2. Hash password using hashed_pw = get_password_hash(user_data.password)
    3. Create new User instance with email, full_name, hashed_password
    4. db.add(new_user)
       await db.commit()
       await db.refresh(new_user)
    5. Return user data in SignupResponse format
    """
    raise HTTPException(status_code=501, detail="Signup endpoint not yet implemented")


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout endpoint: invalidate user session.
    
    Note: With JWT tokens, logout is typically handled client-side by removing the token.
    This endpoint can be used for server-side token blacklisting (optional).
    
    TODO: Implement:
    1. If implementing token blacklist: add token to redis/cache with expiration
    2. For now, just acknowledge logout and let client remove token
    """
    return {"message": "Logged out successfully"}