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
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# LLM Section Classifier
VALID_SECTIONS = [
    "course schedule",
    "required courses",
    "concentration",
    "program overview",
    "accreditation",
]

async def organize_text(raw_text: str) -> dict[str, str]:
    """
    Send raw extracted text to Gemini flash-lite.
    Returns a dict mapping section name → cleaned text.
    """
    prompt = f"""
    You are organizing raw university program document text into sections.

    Extract and organize the content into these sections (only include sections that have content):
    - "course schedule": year-by-year plans, semester layouts, course sequences
    - "required courses": core/required course lists, credit requirements  
    - "concentration": tracks, specializations, electives, focus areas
    - "program overview": program description, learning outcomes, goals
    - "accreditation": accrediting bodies, standards, certifications

    Return ONLY valid JSON, no markdown:
    {{
    "course schedule": "all relevant text here...",
    "required courses": "all relevant text here...",
    "concentration": "all relevant text here...",
    "program overview": "all relevant text here...",
    "accreditation": "all relevant text here..."
    }}

    Only include keys where content exists. If a section has no content set its value to null.

    Document:
    {raw_text[:8000]}
    """

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_1"))
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a document organizer. Return only valid JSON, no markdown, no explanation."
        )
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        sections = json.loads(raw)
        return {k: v for k, v in sections.items() if v}
    except json.JSONDecodeError:
        return {}


# Source Processor
async def process_source(
    source: Source,
    path_or_url: str,
    db: AsyncSession,
    section_override: Optional[str] = None
) -> None:
    """
    Parse a source file, organize text into sections, save as chunks.
    """
    try:
        logger.debug("process_source called for source_id=%s type=%s", source.id, source.source_type)

        if source.source_type == "pdf":
            raw_chunks = parse_file(path_or_url)
        elif source.source_type == "link":
            raw_chunks = await _fetch_and_chunk_link(path_or_url)
        elif source.source_type == "image":
            raw_chunks = await _ocr_image(path_or_url)
        else:
            raw_chunks = []

        if not raw_chunks:
            source.status = "failed"
            source.error_message = "No content could be extracted from this source."
            await db.commit()
            return

        # Combine all raw chunks into one text block
        full_text = "\n\n".join(c["content"] for c in raw_chunks)

        # Store raw preview on source
        source.processed_text = full_text[:10_000]

        if section_override:
            # Skip LLM organization — label everything as the override section
            logger.debug("section_override=%r; skipping LLM organization", section_override)
            organized = {section_override: full_text}
        else:
            # Use Gemini to organize into sections
            logger.debug("calling organize_text for source_id=%s", source.id)
            organized = await organize_text(full_text)

        if not organized:
            source.status = "failed"
            source.error_message = "Could not organize document into sections."
            await db.commit()
            return

        # Save one chunk per section
        for i, (section_label, section_text) in enumerate(organized.items()):
            db.add(Chunk(
                source_id=source.id,
                chunk_index=i,
                text=section_text,
                section=section_label,
                chunk_type="text",
                page_number=None,
            ))

        source.status = "processed"
        await db.commit()

    except Exception as e:
        source.status = "failed"
        source.error_message = str(e)
        await db.commit()
        raise

# Stubs for future source types

async def _fetch_and_chunk_link(url: str) -> list[dict]:
    """
    Fetch a URL, strip HTML tags, return normalized chunks
    in the same format as parse_file().
    """
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; CurriculumBot/1.0)"
            })
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.text, "lxml")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Try to find the main content area first
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find(id="content") or
        soup.find(class_="content") or
        soup.find(id="main") or
        soup.body
    )

    if not main:
        raise ValueError("Could not extract content from page.")

    # Extract clean text
    text = main.get_text(separator="\n", strip=True)

    # Remove blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    if len(clean_text.split()) < 50:
        raise ValueError("Page has insufficient text content.")

    # Return in same format as parse_file()
    return [{"content": clean_text, "type": "text", "page": None}]


async def _ocr_image(path: str) -> list[dict]:
    """Run OCR on an image and return normalized chunks. NOT GOING TO IMPLEMENT FOR PROJECT. MAYBE FUTURE WORK"""
    # TODO: implement with pytesseract or LLM vision
    return []