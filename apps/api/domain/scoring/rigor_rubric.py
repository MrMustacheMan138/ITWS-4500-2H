"""
Rigor scoring rubric.

Defines how each curriculum section contributes to the overall rigor score,
and the criteria used by the LLM to evaluate a single section.

Flow at comparison time:
    1. Chunks are grouped by section (see section_rules.py).
    2. For each section, the LLM is given the chunks + the criteria here and
       returns a section_score in [0, 100] plus strengths/weaknesses.
    3. The overall score is a weighted sum of section scores using SECTION_WEIGHTS.
"""
from dataclasses import dataclass

from domain.curriculum.section_rules import all_section_ids


# ---------------------------------------------------------------------------
# Section weights — must sum to 1.0
# ---------------------------------------------------------------------------
# These weights reflect how much each section contributes to the final rigor
# score. Tune as the team converges on what "rigor" means for this product.

SECTION_WEIGHTS = {
    "course schedule":  0.30,
    "required courses": 0.25,
    "concentration":    0.25,
    "program overview": 0.15,
    "accreditation":    0.05,
}



# ---------------------------------------------------------------------------
# Per-section scoring criteria
# ---------------------------------------------------------------------------
# These strings are injected into the LLM prompt when scoring each section.
# They tell the model what "more rigorous" looks like for that specific section.

SECTION_CRITERIA: dict[str, str] = {
    "course_schedule": (
        "More rigorous programs have dense, well-sequenced schedules with "
        "advanced courses appearing earlier. Light semesters with mostly "
        "electives are less rigorous."
    ),
    "core_requirements": (
        "More rigorous programs require a broad, deep set of core courses "
        "(e.g., theory, systems, math) with no easy substitutions. Programs "
        "with very few required core courses are less rigorous."
    ),
    "specialization_paths": (
        "More rigorous programs offer multiple deep specialization tracks, "
        "each with several required advanced courses. Programs with one "
        "shallow track or no tracks at all are less rigorous."
    ),
    "electives": (
        "More rigorous programs require technical/advanced electives from an "
        "approved list of challenging courses. Programs that allow any course "
        "to count as an elective are less rigorous."
    ),
    "credit_load": (
        "More rigorous programs require a higher total credit count and a "
        "heavier typical per-semester load in the major. Programs with low "
        "total credits or light per-semester loads are less rigorous."
    ),
    "capstone_research": (
        "More rigorous programs require a substantive capstone, thesis, or "
        "research experience. Programs with no capstone requirement or only "
        "a brief group project are less rigorous."
    ),
    "grading_assessment": (
        "More rigorous programs enforce higher minimum GPAs in the major, "
        "proctored exams, and strict grading policies. Lenient grading, "
        "pass/fail options for core courses, and low minimum grades reduce rigor."
    ),
    "prerequisites_policy": (
        "More rigorous programs have long, strictly-enforced prerequisite "
        "chains. Programs where advanced courses can be taken without "
        "building on earlier courses are less rigorous."
    ),
}


# ---------------------------------------------------------------------------
# Score container
# ---------------------------------------------------------------------------

@dataclass
class SectionScore:
    section_id: str
    score: float              # 0 – 100
    strengths: list[str]
    weaknesses: list[str]


@dataclass
class RigorResult:
    overall_score: float      # 0 – 100, weighted average of section scores
    section_scores: list[SectionScore]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_overall_score(section_scores: list[SectionScore]) -> float:
    """
    Weighted average of section scores, rounded to 1 decimal.

    Missing sections are skipped and the remaining weights are renormalized
    so the final number is always on the same 0–100 scale.
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for s in section_scores:
        weight = SECTION_WEIGHTS.get(s.section_id, 0.0)
        if weight <= 0:
            continue
        total_weight += weight
        weighted_sum += weight * s.score

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 1)


def build_section_prompt(section_id: str, chunks: list[str]) -> str:
    """
    Build the prompt to send to the LLM for scoring a single section.

    The returned string gets passed as the user message. The LLM is
    expected to reply with JSON containing score, strengths, weaknesses.
    """
    criteria = SECTION_CRITERIA.get(section_id, "")
    joined = "\n\n---\n\n".join(chunks) if chunks else "(no content found for this section)"

    return (
        f"You are scoring the '{section_id}' section of a university curriculum.\n\n"
        f"RUBRIC:\n{criteria}\n\n"
        f"CONTENT:\n{joined}\n\n"
        f"Respond with JSON matching this schema exactly:\n"
        f'{{"score": <0-100>, "strengths": ["..."], "weaknesses": ["..."]}}'
    )


def validate_weights() -> bool:
    """Sanity check: section weights should cover all sections and sum to ~1.0."""
    known = set(all_section_ids())
    weighted = set(SECTION_WEIGHTS.keys())
    if known != weighted:
        return False
    return abs(sum(SECTION_WEIGHTS.values()) - 1.0) < 1e-6
