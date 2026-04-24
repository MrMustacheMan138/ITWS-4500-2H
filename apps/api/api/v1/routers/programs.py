"""
Program management endpoints.

This file provides minimal placeholder CRUD handlers so the frontend can
integrate against stable endpoints while implementation is in progress.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated, Optional, List

from database import get_db
from models import Program, User
from api.v1.deps import get_current_user


router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class ProgramCreate(BaseModel):
    name: str
    description: Optional[str] = None
    institution: Optional[str] = None


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    institution: Optional[str] = None


class ProgramResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    institution: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProgramResponse])
async def get_programs(db: DbSession, current_user: CurrentUser):
    """Return all programs for the current user."""
    result = await db.execute(select(Program).where(Program.user_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=ProgramResponse)
async def create_program(program_data: ProgramCreate, db: DbSession, current_user: CurrentUser):
    """Create a program placeholder record."""
    new_program = Program(
        user_id=current_user.id,
        name=program_data.name,
        description=program_data.description,
        institution=program_data.institution,
    )
    db.add(new_program)
    await db.commit()
    await db.refresh(new_program)
    return new_program


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(program_id: int, db: DbSession, current_user: CurrentUser):
    """Get a specific program by id."""
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalars().first()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return program


@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update program fields (placeholder behavior)."""
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalars().first()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if program_data.name is not None:
        program.name = program_data.name
    if program_data.description is not None:
        program.description = program_data.description
    if program_data.institution is not None:
        program.institution = program_data.institution

    await db.commit()
    await db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=204)
async def delete_program(program_id: int, db: DbSession, current_user: CurrentUser):
    """Delete a program and linked sources through model cascade."""
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalars().first()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(program)
    await db.commit()
