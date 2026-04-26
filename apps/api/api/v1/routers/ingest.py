"""
Ingest router: accepts URLs and PDF uploads, runs parsers,
saves Source + Chunk records to the database.

  POST /ingest/link  — ingest a web URL
  POST /ingest/pdf   — ingest an uploaded PDF (multipart)
"""

import json
import os
import tempfile
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Chunk, Source, User
from api.v1.deps import get_current_user
from domain.curriculum.section_rules import classify_by_keywords

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_db_chunks(source: Source, raw_chunks: list[dict]) -> list[Chunk]:
    """Convert parser output dicts into Chunk ORM objects."""
    db_chunks = []
    for idx, c in enumerate(raw_chunks):
        content = c.get("content", "")
        if not content:
            continue
        # Table content comes back as list[list[str]] — serialise to JSON string
        if c.get("type") == "table" and isinstance(content, list):
            content = json.dumps(content)
        section = classify_by_keywords(content) if c.get("type") == "text" else None
        db_chunks.append(
            Chunk(
                source_id=source.id,
                chunk_index=idx,
                text=content[:10_000],
                section=section,
                chunk_type=c.get("type", "text"),
                page_number=c.get("page"),
            )
        )
    return db_chunks


async def _persist(
    db: AsyncSession,
    user_id: int,
    program_id: int,
    source_type: str,
    source_url: Optional[str],
    file_name: Optional[str],
    all_chunks: list[dict],
) -> Source:
    """Create Source row, bulk-insert its chunks, commit, return Source."""
    source = Source(
        user_id=user_id,
        program_id=program_id,
        source_type=source_type,
        source_url=source_url,
        file_name=file_name,
        status="processing",
    )
    db.add(source)
    await db.flush()  # get source.id without a full commit

    for chunk in _build_db_chunks(source, all_chunks):
        db.add(chunk)

    # Store a quick text preview on the source row
    combined = " ".join(
        c["content"] for c in all_chunks
        if c.get("type") == "text" and isinstance(c.get("content"), str)
    )
    source.processed_text = combined[:10_000]
    source.status = "completed"

    await db.commit()
    await db.refresh(source)
    return source


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class LinkIngestRequest(BaseModel):
    program_id: int
    url: str

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("url cannot be empty")
        return v.strip()


class IngestResponse(BaseModel):
    source_id: int
    status: str
    chunks_saved: int
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/link", response_model=IngestResponse)
async def ingest_link(
    body: LinkIngestRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Fetch a URL, chunk its text, persist Source + Chunks to the DB."""
    try:
        from integrations.parsers.link_parser import parse_link
        result = parse_link(body.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    all_chunks = result.get("table_chunks", []) + result.get("text_chunks", [])

    source = await _persist(
        db=db,
        user_id=current_user.id,
        program_id=body.program_id,
        source_type="link",
        source_url=body.url,
        file_name=None,
        all_chunks=all_chunks,
    )

    return IngestResponse(
        source_id=source.id,
        status=source.status,
        chunks_saved=len(all_chunks),
        message=f"Ingested {len(all_chunks)} chunks from {body.url}",
    )


@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdf(
    program_id: int = Form(...),
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF, parse it into chunks, persist Source + Chunks to the DB."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are accepted")

    # Write to a temp file — pdf_parser needs a file path (fitz/pdfplumber)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        from integrations.parsers.pdf_parser import parse_file
        result = parse_file(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {exc}")
    finally:
        os.unlink(tmp_path)

    all_chunks = result.get("table_chunks", []) + result.get("text_chunks", [])

    source = await _persist(
        db=db,
        user_id=current_user.id,
        program_id=program_id,
        source_type="pdf",
        source_url=None,
        file_name=file.filename,
        all_chunks=all_chunks,
    )

    return IngestResponse(
        source_id=source.id,
        status=source.status,
        chunks_saved=len(all_chunks),
        message=f"Ingested {len(all_chunks)} chunks from {file.filename}",
    )
