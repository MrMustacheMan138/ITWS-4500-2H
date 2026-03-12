from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
from enum import Enum

router = APIRouter()

class EntryType(str, Enum):
   PDF = "pdf"
   LINK = "link"
   
class IngestEntry(BaseModel):
   type: EntryType
   content: str # URL for link, base64 for pdf, or file path
   metadata: Optional[dict] = None

   @field_validator('content')
   @classmethod
   def validate_content(cls, value, info):
      if not value or not value.strip():
         raise ValueError('Content cannot be empty')
      return value

class IngestRequest(BaseModel):
   entries: List[IngestEntry]

   @field_validator('entries')
   @classmethod
   def validate_entries(cls, value):
      if not value:
         raise ValueError('At least one entry is required')
      return value

class IngestResult(BaseModel):
   entry_id: str
   status: Literal["success", "failed"]
   message: Optional[str] = None


class IngestResponse(BaseModel):
   # Response format
   results: List[IngestResult]
   total_process: int
   successful: int
   failed: int

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
   """
   Ingest multiple data entries (PDFs, links, or images) for processing

   Each entry is marked as:
   - type: 'pdf', 'link'
   - content: URL for links, base64-encoded data for files, or file path
   - metadata: Optional additional information
   """
   
   result = []
   successful = 0
   failed = 0

   for idx, entry in enumerate(request.entries):
      entry_id = f"entry_{idx}"
      if entry.type == "pdf":
         # Call an imported function to chunk out the PDF into sections and pass it through to the LLM
      else:
         # Call an imported function to go through the contents that the URL leads to

      
