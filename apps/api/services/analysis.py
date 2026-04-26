# services/analysis.py

import json
import os
from datetime import datetime
from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Source, Chunk, ProgramAnalysis

MIN_WORDS = 100

SECTION_WEIGHTS = {
    "course schedule":  0.30,
    "required courses": 0.25,
    "concentration":    0.25,
    "program overview": 0.15,
    "accreditation":    0.05,
}

# Section Analysis (LLM call)
async def analyze_program(program_id: int, db: AsyncSession) -> ProgramAnalysis:
    # Get or create ProgramAnalysis row
    result = await db.execute(
        select(ProgramAnalysis).where(ProgramAnalysis.program_id == program_id)
    )
    analysis = result.scalars().first()
    if not analysis:
        analysis = ProgramAnalysis(program_id=program_id, status="processing")
        db.add(analysis)
    else:
        analysis.status = "processing"
    await db.commit()
    await db.refresh(analysis)

    # Pull all chunks for this program
    chunk_result = await db.execute(
        select(Chunk)
        .join(Source, Chunk.source_id == Source.id)
        .where(Source.program_id == program_id)
        .order_by(Chunk.source_id, Chunk.chunk_index)
    )
    all_chunks = chunk_result.scalars().all()

    if not all_chunks:
        analysis.status      = "insufficient"
        analysis.analyzed_at = datetime.utcnow()
        await db.commit()
        return analysis

    # Combine all chunks into one document grouped by section
    section_texts: dict[str, list[str]] = {}
    for chunk in all_chunks:
        label = chunk.section or "general"
        if label == "general":
            continue
        section_texts.setdefault(label, []).append(chunk.text)

    if not section_texts:
        analysis.status      = "insufficient"
        analysis.analyzed_at = datetime.utcnow()
        await db.commit()
        return analysis

    # Build combined document
    combined_doc = ""
    for section_label, texts in section_texts.items():
        combined_doc += f"\n\n=== {section_label.upper()} ===\n"
        combined_doc += "\n\n".join(texts)

    if len(combined_doc.split()) < MIN_WORDS:
        analysis.status      = "insufficient"
        analysis.analyzed_at = datetime.utcnow()
        await db.commit()
        return analysis

    # Single Groq call
    sections_found = list(section_texts.keys())
    result_dict = await _call_groq(combined_doc, sections_found)

    if not result_dict or result_dict.get("insufficient"):
        analysis.status      = "insufficient"
        analysis.analyzed_at = datetime.utcnow()
        await db.commit()
        return analysis

    # Compute weighted overall score
    section_scores = result_dict.get("section_scores", {})
    overall_score = _compute_score(section_scores)

    analysis.overall_score   = overall_score
    analysis.orientation     = result_dict.get("orientation")
    analysis.overall_summary = result_dict.get("overall_summary")
    analysis.strengths       = result_dict.get("strengths")
    analysis.weaknesses      = result_dict.get("weaknesses")
    analysis.improvements    = result_dict.get("improvements")
    analysis.score_breakdown = section_scores
    analysis.status          = "complete" if overall_score else "insufficient"
    analysis.analyzed_at     = datetime.utcnow()
    await db.commit()

    return analysis

# Program Analysis (orchestrator)
async def _call_groq(combined_doc: str, sections_found: list[str]) -> dict:
    sections_str = ", ".join(sections_found)

    prompt = f"""
    You are evaluating a university academic program for rigor and quality.

    Grade each section from 1 to 100 (integers, decimals allowed).
    Determine if the program is theory-heavy, application-heavy, or balanced.

    Return ONLY valid JSON:
    {{
    "orientation": "theory-heavy | application-heavy | balanced",
    "overall_summary": "3-4 sentence summary of the program character and rigor",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "improvements": ["improvement 1", "improvement 2"],
    "section_scores": {{
        "<section_name>": 0
    }}
    }}

    Only score sections present in the document: {sections_str}
    Orientation must be exactly: "theory-heavy", "application-heavy", or "balanced"

    Program content:
    {combined_doc[:12000]}
    """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an academic program evaluator. Return only valid JSON, no markdown, no explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"insufficient": True}


def _compute_score(section_scores: dict) -> float | None:
    if not section_scores:
        return None

    total_weight = 0
    weighted_sum = 0

    for section, score in section_scores.items():
        weight = SECTION_WEIGHTS.get(section, 0.05)
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    coverage_ratio  = total_weight / sum(SECTION_WEIGHTS.values())
    raw_score       = weighted_sum / total_weight
    penalized_score = raw_score * (0.6 + 0.4 * coverage_ratio)

    return round(penalized_score, 1)