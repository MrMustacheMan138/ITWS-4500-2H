"""
Source management endpoints: CRUD operations for data sources.

Sources represent individual documents/links that make up a program.
Examples: PDF syllabus, course handbook link, image of degree requirements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, DateTime
from pydantic import BaseModel
from typing import List, Optional, Annotated

from database import get_db
from models import Source, User
from api.v1.deps import get_current_user

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# ============================================================================
# Pydantic Schemas
# ============================================================================

class SourceCreate(BaseModel):
    """Schema for creating a new source."""
    program_id: int
    source_type: str  # "pdf", "link", "image", "text"
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    metadata: Optional[str] = None  # JSON-formatted metadata


class SourceUpdate(BaseModel):
    """Schema for updating a source."""
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    status: Optional[str] = None  # "pending", "processing", "completed", "failed"
    metadata: Optional[str] = None


class SourceResponse(BaseModel):
    """Schema for source response data."""
    id: int
    user_id: int
    program_id: int
    source_type: str
    source_url: Optional[str]
    file_name: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.get("/", response_model=List[SourceResponse])
async def get_sources(
    db: DbSession, 
    current_user: CurrentUser,
    program_id: Optional[int] = None, 
    status: Optional[str] = None
    ):
    """
    Get all sources for the current user.
    
    Query Parameters:
        program_id: Filter by program ID (optional)
        status: Filter by status - "pending", "processing", "completed", "failed" (optional)
    """
    query = select(Source).where(Source.user_id == current_user.id)

    if program_id is not None:
        query = query.where(Source.program_id == program_id)
    if status is not None:
        query = query.where(Source.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Get a specific source by ID.
    """

    # Query
    result = await db.execute(select(Source).where(Source.id == source_id))
    # Fetch
    source = result.scalars().first()
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return source

@router.post("/", response_model=SourceResponse)
async def create_source(
    source_data: SourceCreate,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Create a new source.
    
    The source will be created with status="pending" and queued for processing.
    """
    new_source = Source(
        user_id=current_user.id,
        program_id=source_data.program_id,
        source_type=source_data.source_type,
        source_url=source_data.source_url,
        file_name=source_data.file_name,
        status="pending",
        source_metadata=source_data.metadata
    )

    db.add(new_source)
    
    await db.commit()
    await db.refresh(new_source)

    # Later on, TODO: Trigger async task to process source (see services/ layer)

    return new_source
    

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Update a source.
    
    Note: Only user who created the source can update it.
    """
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()

    if source is None:
        raise HTTPException(404, "Source not found")

    if source.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    if source_data.source_type is not None:
        source.source_type = source_data.source_type
    if source_data.source_url is not None:
        source.source_url = source_data.source_url
    
    await db.commit()
    await db.refresh(source)

    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: int,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Delete a source.
    
    Note: Only user who created the source can delete it.
    """

    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()

    if source is None:
        raise HTTPException(404, "Source not found")

    if source.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    await db.delete(source)
    await db.commit()

