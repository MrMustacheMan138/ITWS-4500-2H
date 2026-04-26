"""
Program management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated, Optional, List
from database import get_db
from models import Program, User, ProgramAnalysis
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
    result = await db.execute(select(Program).where(Program.user_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=ProgramResponse)
async def create_program(program_data: ProgramCreate, db: DbSession, current_user: CurrentUser):
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
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalars().first()
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(program)
    await db.commit()


@router.get("/{program_id}/analysis")
async def get_program_analysis(
    program_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    result = await db.execute(
        select(Program).where(
            Program.id == program_id,
            Program.user_id == current_user.id,
        )
    )
    program = result.scalars().first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    result = await db.execute(
        select(ProgramAnalysis).where(ProgramAnalysis.program_id == program_id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this program")

    return {
        "program_id":      program_id,
        "program_name":    program.name,
        "institution":     program.institution,
        "status":          analysis.status,
        "overall_score":   analysis.overall_score,
        "orientation":     analysis.orientation,
        "overall_summary": analysis.overall_summary,
        "strengths":       analysis.strengths,
        "weaknesses":      analysis.weaknesses,
        "improvements":    analysis.improvements,
        "score_breakdown": analysis.score_breakdown,
        "analyzed_at":     str(analysis.analyzed_at) if analysis.analyzed_at else None,
    }