from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, get_current_user
from models import User

router = APIRouter()


class SourceResponse(BaseModel):
    id: str
    type: str
    content: str
    metadata: Optional[dict] = None


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all ingested sources for the current user."""
    # TODO: query sources from database once Source model is added
    return []


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a source by ID."""
    # TODO: implement deletion once Source model is added
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not yet implemented")