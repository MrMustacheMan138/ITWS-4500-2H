from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from services.chat_service import chatbot

router = APIRouter(prefix="/chat", tags=["chat"])

# Pydantic models for request/response validation
class ChatTurn(BaseModel):
    role: Literal["user", "model"]
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatTurn] | None = None

class ChatResponse(BaseModel):
    reply: str

# Main chat endpoint
@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    reply = await chatbot(
        message=payload.message,
        history=[t.model_dump() for t in (payload.history or [])],
    )

    # Wrap reply in response model
    return ChatResponse(reply=reply)
