# services/ingestion.py

import os
import json
import logging
from google import genai
from google.genai import types
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models import Source, Chunk
from integrations.parsers.pdf_parser import parse_file
from integrations.parsers.link_parser import parse_link
from integrations.parsers.text_chunker import normalize_chunks
from domain.curriculum.section_rules import SECTIONS, classify_by_keywords

logger = logging.getLogger(__name__)

# Canonical section IDs — kept in sync with domain/curriculum/section_rules.py
VALID_SECTIONS = [s.id for s in SECTIONS]

# Gemini client — supports both env var names used across the codebase
_GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")


# ---------------------------------------------------------------------------
# LLM Section Classifier
# ---------------------------------------------------------------------------

async def organize_text(raw_text: str) -> dict[str, str]:
    """
    Send raw extracted text to Gemini.
    Returns a dict mapping canonical section_id -> cleaned text.

    Section IDs match domain/curriculum/section_rules.py exactly so that
    SECTION_WEIGHTS in analysis.py and comparison.py can look them up.
    """
    prompt = f"""
    You are organizing raw university program document text into structured sections.

    Extract and organize the content into these sections (only include sections that have content):
    - "course_schedule": year-by-year plans, semester layouts, course sequences
    - "core_requirements": required/mandatory course lists, credit requirements, foundation courses
    - "specialization_paths": tracks, concentrations, focus areas, depth options
    - "electives": free or technical electives, optional course lists
    - "credit_load": total credit hours, per-semester load, credit distribution
    - "faculty_expertise": faculty research areas, credentials, industry backgrounds, academic expertise

    Return ONLY valid JSON, no markdown:
    {{
    "course_schedule": "all relevant text here...",
    "core_requirements": "all relevant text here...",
    "specialization_paths": "all relevant text here...",
    "electives": "all relevant text here...",
    "credit_load": "all relevant text here..."
    "faculty_expertise": "all relevant text here..."
    }}

    Only include keys where content exists. Set missing sections to null.

    Document:
    {raw_text[:8000]}
    """

    client = genai.Client(api_key=_GEMINI_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a document organizer. "
                "Return only valid JSON, no markdown, no explanation."
            )
        ),
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        sections = json.loads(raw)
        return {k: v for k, v in sections.items() if v and k in VALID_SECTIONS}
    except json.JSONDecodeError:
        logger.warning(
            "Gemini returned invalid JSON for section organization; "
            "falling back to keyword classifier"
        )
        return {}


# ---------------------------------------------------------------------------
# Keyword-based fallback classifier
# ---------------------------------------------------------------------------

def _organize_by_keywords(raw_text: str) -> dict[str, str]:
    """
    Cheap keyword-based fallback used when Gemini is unavailable or returns
    invalid JSON. Uses domain/curriculum/section_rules.classify_by_keywords().
    """
    section_id = classify_by_keywords(raw_text)
    if section_id:
        return {section_id: raw_text}
    # Safe default: dump everything into core_requirements
    return {"core_requirements": raw_text}


# ---------------------------------------------------------------------------
# Source Processor
# ---------------------------------------------------------------------------

async def process_source(
    source: Source,
    path_or_url: str,
    db: AsyncSession,
    section_override: Optional[str] = None,
) -> None:
    """
    Parse a source file or URL, organize the text into canonical sections,
    and save as Chunk rows.

    Pipeline: parse -> (LLM organize | keyword fallback) -> save chunks
    """
    try:
        logger.debug(
            "process_source called for source_id=%s type=%s",
            source.id,
            source.source_type,
        )

        if source.source_type == "pdf":
            # parse_file already returns normalized chunks: [{"content": ..., ...}]
            raw_chunks = parse_file(path_or_url)

        elif source.source_type == "link":
            # parse_link returns the raw dict; normalize_chunks flattens it to
            # the same format as parse_file so downstream code is identical
            raw_chunks = normalize_chunks(parse_link(path_or_url))

        elif source.source_type == "image":
            # OCR is explicitly out of scope for this project version
            source.status = "failed"
            source.error_message = "Image OCR is not supported in this version."
            await db.commit()
            return

        else:
            raw_chunks = []

        if not raw_chunks:
            source.status = "failed"
            source.error_message = "No content could be extracted from this source."
            await db.commit()
            return

        # Combine all raw chunks into one text block for the LLM organizer
        full_text = "\n\n".join(c["content"] for c in raw_chunks)

        # Store a preview of the raw text on the source row
        source.processed_text = full_text[:10_000]

        if section_override:
            # Skip LLM — label everything as the override section
            logger.debug("section_override=%r; skipping LLM organization", section_override)
            organized = {section_override: full_text}
        else:
            # Use Gemini to organize into canonical sections
            logger.debug("calling organize_text for source_id=%s", source.id)
            organized = await organize_text(full_text)

            # Fall back to keyword classifier if Gemini returns nothing useful
            if not organized:
                logger.warning(
                    "organize_text returned nothing for source_id=%s; "
                    "using keyword fallback",
                    source.id,
                )
                organized = _organize_by_keywords(full_text)

        if not organized:
            source.status = "failed"
            source.error_message = "Could not organize document into sections."
            await db.commit()
            return

        # Persist one Chunk per section
        for i, (section_label, section_text) in enumerate(organized.items()):
            db.add(
                Chunk(
                    source_id=source.id,
                    chunk_index=i,
                    text=section_text,
                    section=section_label,
                    chunk_type="text",
                    page_number=None,
                )
            )

        source.status = "processed"
        await db.commit()

    except Exception as e:
        source.status = "failed"
        source.error_message = str(e)
        await db.commit()
        raise