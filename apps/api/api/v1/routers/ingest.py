from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
from enum import Enum

router = APIRouter()


class EntryType(str, Enum):
    PDF = "pdf"
    LINK = "link"


class IngestEntry(BaseModel):
    type: EntryType
    content: str
    metadata: Optional[dict] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, value, info):
        if not value or not value.strip():
            raise ValueError("Content cannot be empty")
        return value


class IngestRequest(BaseModel):
    entries: List[IngestEntry]

    @field_validator("entries")
    @classmethod
    def validate_entries(cls, value):
        if not value:
            raise ValueError("At least one entry is required")
        return value


class IngestResult(BaseModel):
    entry_id: str
    status: Literal["success", "failed"]
    message: Optional[str] = None


class IngestResponse(BaseModel):
    results: List[IngestResult]
    total_processed: int
    successful: int
    failed: int


@router.post("", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Ingest multiple data entries (PDFs or links) for processing.
    Each entry specifies a type ('pdf' or 'link') and content.
    """
    results = []
    successful = 0
    failed = 0

    for idx, entry in enumerate(request.entries):
        entry_id = f"entry_{idx}"
        try:
            if entry.type == EntryType.PDF:
                # TODO: call pdf_processor service
                message = f"PDF queued for processing: {entry.content[:60]}"
            else:
                # TODO: call link_fetcher service
                message = f"Link queued for processing: {entry.content[:60]}"

            results.append(IngestResult(entry_id=entry_id, status="success", message=message))
            successful += 1

        except Exception as e:
            results.append(IngestResult(entry_id=entry_id, status="failed", message=str(e)))
            failed += 1

    return IngestResponse(
        results=results,
        total_processed=len(request.entries),
        successful=successful,
        failed=failed,
    )
