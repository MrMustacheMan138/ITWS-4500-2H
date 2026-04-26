# services/comparison.py
"""
Comparison engine.

Flow:
  1. Load both programs' ProgramAnalysis records (produced by services/analysis.py).
  2. If either analysis is missing / insufficient, fall back to a direct LLM
     comparison using the raw chunk text so the user still gets a result.
  3. Call Groq once with both programs' data and produce a structured JSON result
     that matches the shape expected by ResultsView.tsx:
       {
         "score_a": <0-100>,
         "score_b": <0-100>,
         "verdict": "<one-sentence verdict>",
         "section_scores": [
           {
             "section_id": "<id>",
             "score": <0-100>,          # score for program A on this section
             "score_b": <0-100>,        # score for program B on this section
             "strengths": ["..."],
             "weaknesses": ["..."]
           },
           ...
         ],
         "gaps": [
           {"title": "...", "body": "...", "cite": "..."},
           ...
         ]
       }
  4. Persist result JSON string into Comparison.comparison_results and return it.
"""

import json
import os
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from groq import Groq

from models import Comparison, Program, ProgramAnalysis, Chunk, Source
from domain.scoring.rigor_rubric import SECTION_WEIGHTS, SECTION_CRITERIA

logger = logging.getLogger(__name__)

MAX_CHUNK_CHARS = 8_000
MAX_ANALYSIS_CHARS = 6_000


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def run_comparison(comparison_id: int, db: AsyncSession) -> Comparison:
    """
    Execute the full comparison pipeline for a Comparison record.
    Updates comparison.comparison_results in-place and returns the record.
    """
    # 1. Load the comparison row
    result = await db.execute(select(Comparison).where(Comparison.id == comparison_id))
    comparison = result.scalars().first()
    if not comparison:
        raise ValueError(f"Comparison {comparison_id} not found")

    if not comparison.program_a_id or not comparison.program_b_id:
        raise ValueError("Comparison must have both program_a_id and program_b_id set")

    # 2. Load programs
    prog_a = await _get_program(comparison.program_a_id, db)
    prog_b = await _get_program(comparison.program_b_id, db)

    # 3. Gather data for each program (analysis if available, raw chunks as fallback)
    data_a = await _collect_program_data(comparison.program_a_id, db)
    data_b = await _collect_program_data(comparison.program_b_id, db)

    # 4. Run the LLM comparison
    result_dict = await _call_groq_comparison(
        name_a=f"{prog_a.institution or ''} {prog_a.name}".strip(),
        name_b=f"{prog_b.institution or ''} {prog_b.name}".strip(),
        data_a=data_a,
        data_b=data_b,
    )

    # 5. Persist
    comparison.comparison_results = json.dumps(result_dict)
    await db.commit()
    await db.refresh(comparison)

    return comparison


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _get_program(program_id: int, db: AsyncSession) -> Program:
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalars().first()
    if not program:
        raise ValueError(f"Program {program_id} not found")
    return program


async def _collect_program_data(program_id: int, db: AsyncSession) -> dict:
    """
    Return a dict with whatever we know about a program.
    Prefers a finished ProgramAnalysis; falls back to raw chunk text.
    """
    # Try to get a completed analysis
    analysis_result = await db.execute(
        select(ProgramAnalysis).where(
            ProgramAnalysis.program_id == program_id,
            ProgramAnalysis.status == "complete",
        )
    )
    analysis = analysis_result.scalars().first()

    if analysis:
        return {
            "source": "analysis",
            "overall_score": analysis.overall_score,
            "orientation": analysis.orientation,
            "overall_summary": analysis.overall_summary,
            "strengths": analysis.strengths or [],
            "weaknesses": analysis.weaknesses or [],
            "improvements": analysis.improvements or [],
            "score_breakdown": analysis.score_breakdown or {},
        }

    # Fall back to raw chunks
    chunk_result = await db.execute(
        select(Chunk)
        .join(Source, Chunk.source_id == Source.id)
        .where(Source.program_id == program_id)
        .order_by(Chunk.source_id, Chunk.chunk_index)
    )
    chunks = chunk_result.scalars().all()

    if not chunks:
        return {"source": "empty", "text": ""}

    # Build section-grouped text, capped at MAX_CHUNK_CHARS
    section_texts: dict[str, list[str]] = {}
    for chunk in chunks:
        label = chunk.section or "general"
        section_texts.setdefault(label, []).append(chunk.text)

    combined = ""
    for section_label, texts in section_texts.items():
        combined += f"\n\n=== {section_label.upper()} ===\n"
        combined += "\n\n".join(texts)
        if len(combined) >= MAX_CHUNK_CHARS:
            break

    return {"source": "chunks", "text": combined[:MAX_CHUNK_CHARS]}


def _format_program_context(name: str, data: dict) -> str:
    """Turn a program data dict into a readable block for the LLM prompt."""
    if data["source"] == "analysis":
        lines = [f"Program: {name}"]
        if data.get("overall_score") is not None:
            lines.append(f"Overall rigor score (0-100): {data['overall_score']}")
        if data.get("orientation"):
            lines.append(f"Orientation: {data['orientation']}")
        if data.get("overall_summary"):
            lines.append(f"Summary: {data['overall_summary']}")
        if data.get("strengths"):
            lines.append("Strengths: " + "; ".join(data["strengths"]))
        if data.get("weaknesses"):
            lines.append("Weaknesses: " + "; ".join(data["weaknesses"]))
        if data.get("score_breakdown"):
            breakdown = "; ".join(
                f"{k}: {v}" for k, v in data["score_breakdown"].items()
            )
            lines.append(f"Section scores: {breakdown}")
        return "\n".join(lines)

    elif data["source"] == "chunks":
        return f"Program: {name}\n\nRaw curriculum content:\n{data['text']}"

    else:
        return f"Program: {name}\n\n(No content available — program may not have been ingested yet)"


async def _call_groq_comparison(
    name_a: str,
    name_b: str,
    data_a: dict,
    data_b: dict,
) -> dict:
    """
    Call Groq once to produce the full comparison JSON.
    Returns a dict matching the ResultsView schema.
    """
    context_a = _format_program_context(name_a, data_a)
    context_b = _format_program_context(name_b, data_b)

    # Build a best-guess score baseline from existing analysis data
    baseline_a = data_a.get("overall_score") or 50
    baseline_b = data_b.get("overall_score") or 50

    # Build rubric block from domain criteria
    rubric_lines = [f"- {sid}: {desc}" for sid, desc in SECTION_CRITERIA.items()]
    rubric_block = "\n".join(rubric_lines)

    prompt = f"""You are comparing two university academic programs for curricular rigor and quality.

PROGRAM A:
{context_a}

PROGRAM B:
{context_b}

SCORING RUBRIC (use this to evaluate each section):
{rubric_block}

Your task: produce a detailed, balanced comparison. Return ONLY valid JSON (no markdown, no explanation) matching this exact schema:

{{
  "score_a": <integer 0-100, overall rigor score for program A>,
  "score_b": <integer 0-100, overall rigor score for program B>,
  "verdict": "<one concise sentence declaring which program is more rigorous and why>",
  "section_scores": [
    {{
      "section_id": "<snake_case section name>",
      "score": <integer 0-100 for program A on this section>,
      "score_b": <integer 0-100 for program B on this section>,
      "strengths": ["<strength of program A in this section>"],
      "weaknesses": ["<weakness of program A in this section>"]
    }}
  ],
  "gaps": [
    {{
      "title": "<short gap title>",
      "body": "<2-3 sentence explanation of the gap between the two programs>",
      "cite": "<which program this gap applies to, e.g. 'Program B lacks...'>"
    }}
  ]
}}

Rules:
- score_a baseline hint: {baseline_a} (adjust based on your analysis)
- score_b baseline hint: {baseline_b} (adjust based on your analysis)
- Produce section_scores for at least 3-5 meaningful curriculum sections found in the content
- Produce 3-5 gaps that highlight the most important structural differences
- Be specific and cite concrete curriculum evidence where possible
- section_id values must be lowercase with underscores (e.g. "core_requirements", "course_schedule")
- Scores must be integers
"""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert academic program evaluator. "
                    "Return only valid JSON, no markdown fences, no explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Groq returned invalid JSON: %s\nRaw: %s", e, raw[:500])
        # Return a fallback result so the page still renders something
        result = _fallback_result(name_a, name_b, data_a, data_b)

    # Ensure required keys exist
    result.setdefault("score_a", int(baseline_a))
    result.setdefault("score_b", int(baseline_b))
    result.setdefault("verdict", f"Comparison between {name_a} and {name_b} complete.")
    result.setdefault("section_scores", [])
    result.setdefault("gaps", [])

    return result


def _fallback_result(name_a: str, name_b: str, data_a: dict, data_b: dict) -> dict:
    """
    Minimal structured result when the LLM call fails or returns unparseable JSON.
    Uses available analysis scores if present, otherwise defaults to 50.
    """
    score_a = int(data_a.get("overall_score") or 50)
    score_b = int(data_b.get("overall_score") or 50)

    winner = name_a if score_a >= score_b else name_b
    verdict = (
        f"{winner} scores higher on overall curriculum rigor "
        f"({max(score_a, score_b)} vs {min(score_a, score_b)})."
    )

    section_scores = []
    breakdown_a = data_a.get("score_breakdown") or {}
    breakdown_b = data_b.get("score_breakdown") or {}
    all_sections = set(breakdown_a.keys()) | set(breakdown_b.keys())

    for sec in all_sections:
        sa = int(breakdown_a.get(sec, 50) * 10)  # analysis stores 0-10, convert to 0-100
        sb = int(breakdown_b.get(sec, 50) * 10)
        section_scores.append({
            "section_id": sec.lower().replace(" ", "_"),
            "score": sa,
            "score_b": sb,
            "strengths": [],
            "weaknesses": [],
        })

    gaps = []
    weaknesses_a = data_a.get("weaknesses") or []
    weaknesses_b = data_b.get("weaknesses") or []
    for w in weaknesses_a[:2]:
        gaps.append({"title": f"{name_a}: Area for improvement", "body": w, "cite": name_a})
    for w in weaknesses_b[:2]:
        gaps.append({"title": f"{name_b}: Area for improvement", "body": w, "cite": name_b})

    return {
        "score_a": score_a,
        "score_b": score_b,
        "verdict": verdict,
        "section_scores": section_scores,
        "gaps": gaps,
    }