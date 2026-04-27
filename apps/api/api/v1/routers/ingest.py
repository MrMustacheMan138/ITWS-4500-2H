import os
import shutil
import tempfile
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, Source, Program
from api.v1.deps import get_current_user
from services.ingestion import process_source
from services.analysis import analyze_program

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class SourceResult(BaseModel):
    source_id: int
    file_name: Optional[str]
    source_type: str
    status: str
    error: Optional[str] = None

class IngestResponse(BaseModel):
    program_id: int
    sources_processed: int
    sources_failed: int
    sources: list[SourceResult]
    analysis_status: str  # "complete" | "insufficient" | "failed"

# Ingest Endpoint

@router.post("/", response_model=IngestResponse)
async def ingest_sources(
    program_id: Annotated[int, Form()],
    db: DbSession,
    current_user: CurrentUser,
    files: list[UploadFile] = File(default=[]),
    links: Annotated[Optional[str], Form()] = None,
    section_override: Annotated[Optional[str], Form()] = None, 
):
    """
    Upload files and/or links for a program and run the full pipeline:
    parse -> chunk -> classify -> analyze -> score

    Form fields:
        program_id  : which program these sources belong to (required)
        files       : one or more PDF uploads (optional)
        links       : comma-separated URLs (optional)
    """

    # Verify program exists and belongs to this user
    result = await db.execute(
        select(Program).where(
            Program.id == program_id,
            Program.user_id == current_user.id
        )
    )
    program = result.scalars().first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    source_results: list[SourceResult] = []

    # 1. Process uploaded files
    for upload in files:
        if not upload.filename:
            continue

        source_type = _detect_file_type(upload.filename)

        # Create the Source row immediately so we have an ID
        source = Source(
            user_id=current_user.id,
            program_id=program_id,
            source_type=source_type,
            file_name=upload.filename,
            status="processing",
        )
        db.add(source)
        await db.commit()
        await db.refresh(source)

        tmp_path = None
        try:
            # Write upload to a temp file so parsers can open it from disk
            suffix = os.path.splitext(upload.filename)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(upload.file, tmp)
                tmp_path = tmp.name

            await process_source(source, tmp_path, db, section_override=section_override)
            await db.refresh(source)

            if source.status == "failed":
                source_results.append(SourceResult(
                    source_id=source.id,
                    file_name=upload.filename,
                    source_type=source_type,
                    status="failed",
                    error="Processing failed",
                ))
            else:
                source_results.append(SourceResult(
                    source_id=source.id,
                    file_name=upload.filename,
                    source_type=source_type,
                    status=source.status,
                ))

        except Exception as e:
            print("Process failed...")
            source_results.append(SourceResult(
                source_id=source.id,
                file_name=upload.filename,
                source_type=source_type,
                status="failed",
                error=str(e),
            ))

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    # 2. Process links
    if links:
        for url in [u.strip() for u in links.split(",") if u.strip()]:
            source = Source(
                user_id=current_user.id,
                program_id=program_id,
                source_type="link",
                source_url=url,
                status="processing",
            )
            db.add(source)
            await db.commit()
            await db.refresh(source)

            try:
                await process_source(source, url, db, section_override=section_override)
                source_results.append(SourceResult(
                    source_id=source.id,
                    file_name=None,
                    source_type="link",
                    status=source.status,
                ))
            except Exception as e:
                source_results.append(SourceResult(
                    source_id=source.id,
                    file_name=None,
                    source_type="link",
                    status="failed",
                    error=str(e),
                ))

    # 3. Bail if nothing got through
    successful = [s for s in source_results if s.status == "processed"]
    failed     = [s for s in source_results if s.status == "failed"]

    if not successful:
        raise HTTPException(
            status_code=422,
            detail="No sources were processed successfully. Check your files or links."
        )

    # 4. Run program-level analysis once all sources are done
    try:
        analysis = await analyze_program(program_id, db)
        analysis_status = analysis.status
    except Exception as e:
        print(f"DEBUG: analyze_program FAILED: {e}")
        analysis_status = "failed"

    return IngestResponse(
        program_id=program_id,
        sources_processed=len(successful),
        sources_failed=len(failed),
        sources=source_results,
        analysis_status=analysis_status,
    )


# Helpers

def _detect_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[-1].lower()
    return {
        ".pdf":  "pdf",
        ".png":  "image",
        ".jpg":  "image",
        ".jpeg": "image",
        ".webp": "image",
    }.get(ext, "file")