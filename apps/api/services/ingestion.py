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
from domain.curriculum.section_rules import SECTIONS, classify_chunk

logger = logging.getLogger(__name__)

VALID_SECTIONS = [s.id for s in SECTIONS]
_GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")


async def organize_text(raw_text: str) -> dict[str, str]:
    prompt = f"""
    You are organizing raw university program document text into structured sections.

    Extract and organize the content into these sections:
    - "course_schedule"
    - "core_requirements"
    - "specialization_paths"
    - "electives"
    - "credit_load"
    - "faculty_expertise"

    Return ONLY valid JSON, no markdown.

    Only include keys where content exists. Set missing sections to null.

    Document:
    {raw_text[:8000]}
    """
    try:
        client = genai.Client(api_key=_GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Return only valid JSON, no markdown, no explanation."
            ),
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        sections = json.loads(raw)
        return {k: v for k, v in sections.items() if v and k in VALID_SECTIONS}

    except Exception as e:
        logger.warning("Gemini organize_text failed (%s); using keyword fallback", e)
        return {}


def _organize_by_keywords(raw_chunks: list[dict]) -> dict[str, str]:
    buckets: dict[str, list[str]] = {}

    for chunk in raw_chunks:
        content = (chunk.get("content") or "").strip()
        if not content:
            continue

        section_id = classify_chunk(chunk)
        buckets.setdefault(section_id, []).append(content)

    return {
        section_id: "\n\n".join(texts)
        for section_id, texts in buckets.items()
        if texts
    }


async def process_source(
    source: Source,
    path_or_url: str,
    db: AsyncSession,
    section_override: Optional[str] = None,
) -> None:
    try:
        logger.debug(
            "process_source called for source_id=%s type=%s",
            source.id,
            source.source_type,
        )

        if source.source_type == "pdf":
            raw_chunks = parse_file(path_or_url)

        elif source.source_type == "link":
            raw_chunks = normalize_chunks(parse_link(path_or_url))

        elif source.source_type == "image":
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

        full_text = "\n\n".join(c["content"] for c in raw_chunks)
        source.processed_text = full_text[:10_000]

        if section_override:
            logger.debug("section_override=%r; skipping LLM organization", section_override)
            organized = {section_override: full_text}
        else:
            logger.debug("calling organize_text for source_id=%s", source.id)
            organized = await organize_text(full_text)

            if not organized:
                logger.warning(
                    "organize_text returned nothing for source_id=%s; using keyword fallback",
                    source.id,
                )
                organized = _organize_by_keywords(raw_chunks)

        if not organized:
            source.status = "failed"
            source.error_message = "Could not organize document into sections."
            await db.commit()
            return

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