from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_current_user
from database import get_db
from models import User
from services.chat_service import chatbot

router = APIRouter(tags=["chat"])


class ChatTurn(BaseModel):
    role: Literal["user", "model"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatTurn] | None = None
    comparison_id: int | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    reply = await chatbot(
        message=payload.message,
        history=[t.model_dump() for t in (payload.history or [])],
        db=db,
        user_id=current_user.id,
        comparison_id=payload.comparison_id,
    )

    return ChatResponse(reply=reply)