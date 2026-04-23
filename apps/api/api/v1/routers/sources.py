"""
Source management endpoints: CRUD operations for data sources.

Sources represent individual documents/links that make up a program.
Examples: PDF syllabus, course handbook link, image of degree requirements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import Source, User
from api.v1.deps import get_current_user

router = APIRouter()


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
    program_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all sources for the current user.
    
    Query Parameters:
        program_id: Filter by program ID (optional)
        status: Filter by status - "pending", "processing", "completed", "failed" (optional)
    
    TODO: Implement:
    1. Build query: query = select(Source).where(Source.user_id == current_user.id)
    2. If program_id provided: query = query.where(Source.program_id == program_id)
    3. If status provided: query = query.where(Source.status == status)
    4. Execute: result = await db.execute(query)
    5. Return: result.scalars().all()
    """
    raise HTTPException(status_code=501, detail="GET /sources not yet implemented")


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific source by ID.
    
    TODO: Implement:
    1. Query source: result = await db.execute(select(Source).where(Source.id == source_id))
    2. Fetch: source = result.scalars().first()
    3. If not found: raise HTTPException(status_code=404, detail="Source not found")
    4. Verify ownership: if source.user_id != current_user.id: raise HTTPException(403, "Not authorized")
    5. Return source
    """
    raise HTTPException(status_code=501, detail="GET /sources/{id} not yet implemented")


@router.post("/", response_model=SourceResponse)
async def create_source(
    source_data: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new source.
    
    The source will be created with status="pending" and queued for processing.
    
    TODO: Implement:
    1. Create new Source instance with:
       - user_id=current_user.id
       - program_id=source_data.program_id
       - source_type=source_data.source_type
       - source_url=source_data.source_url
       - file_name=source_data.file_name
       - status="pending"
       - metadata=source_data.metadata
    2. db.add(new_source)
    3. await db.commit()
    4. await db.refresh(new_source)
    5. TODO: Trigger async task to process source (see services/ layer)
    6. Return new_source in SourceResponse format
    """
    raise HTTPException(status_code=501, detail="POST /sources not yet implemented")


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a source.
    
    Note: Only user who created the source can update it.
    
    TODO: Implement:
    1. Fetch source: result = await db.execute(select(Source).where(Source.id == source_id))
    2. Verify ownership: if source.user_id != current_user.id: raise HTTPException(403, "Not authorized")
    3. Update fields if provided:
       - if source_data.source_type: source.source_type = source_data.source_type
       - if source_data.source_url: source.source_url = source_data.source_url
       - etc. (only update non-None fields)
    4. await db.commit()
    5. await db.refresh(source)
    6. Return updated source
    """
    raise HTTPException(status_code=501, detail="PUT /sources/{id} not yet implemented")


@router.delete("/{source_id}", status_code=204)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a source.
    
    Note: Only user who created the source can delete it.
    
    TODO: Implement:
    1. Fetch source: result = await db.execute(select(Source).where(Source.id == source_id))
    2. Verify ownership: if source.user_id != current_user.id: raise HTTPException(403, "Not authorized")
    3. Delete: await db.delete(source)
    4. await db.commit()
    5. Return 204 No Content (FastAPI handles this automatically)
    """
    raise HTTPException(status_code=501, detail="DELETE /sources/{id} not yet implemented")
