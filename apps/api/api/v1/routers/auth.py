from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    # TODO: Implement actual authentication logic
    return {
        "access_token": "dummy_token",
        "token_type": "bearer"
    }