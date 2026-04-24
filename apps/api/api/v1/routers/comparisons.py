"""
Comparison endpoints.

Minimal placeholder handlers for creating and retrieving comparison records.
Detailed comparison logic should be implemented later in service/domain layers.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated, Optional, List

from database import get_db
from models import Comparison, User
from api.v1.deps import get_current_user


router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class ComparisonCreate(BaseModel):
    title: str
    program_a_id: Optional[int] = None
    program_b_id: Optional[int] = None


class ComparisonResponse(BaseModel):
    id: int
    user_id: int
    title: str
    program_a_id: Optional[int]
    program_b_id: Optional[int]
    comparison_results: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ComparisonResponse])
async def get_comparisons(db: DbSession, current_user: CurrentUser):
    """Return all comparisons for the current user."""
    result = await db.execute(select(Comparison).where(Comparison.user_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=ComparisonResponse)
async def create_comparison(
    comparison_data: ComparisonCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a placeholder comparison record for later processing."""
    new_comparison = Comparison(
        user_id=current_user.id,
        title=comparison_data.title,
        program_a_id=comparison_data.program_a_id,
        program_b_id=comparison_data.program_b_id,
        comparison_results=None,
    )
    db.add(new_comparison)
    await db.commit()
    await db.refresh(new_comparison)
    return new_comparison


@router.get("/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(comparison_id: int, db: DbSession, current_user: CurrentUser):
    """Get one comparison by id."""
    result = await db.execute(select(Comparison).where(Comparison.id == comparison_id))
    comparison = result.scalars().first()
    if comparison is None:
        raise HTTPException(status_code=404, detail="Comparison not found")
    if comparison.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return comparison
