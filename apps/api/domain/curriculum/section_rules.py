"""
Curriculum section definitions.

Each section represents a distinct aspect of a curriculum that we want
to analyze separately. Chunks get classified into one of these sections
(via embedding similarity or LLM classification), then scored per-section
against the rigor rubric.

The `description` field is what gets embedded for similarity matching
against incoming chunks — keep it detailed.

The `keywords` field provides a cheap fallback when embeddings aren't
available (useful for tests and dev mode).
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Section:
    id: str              # Stable ID used in DB + prompts
    name: str            # Human-readable label for the UI
    description: str     # Used for embedding-based classification
    keywords: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Curriculum Sections
# ---------------------------------------------------------------------------

SECTIONS: list[Section] = [
    Section(
        id="course_schedule",
        name="Course Schedule",
        description=(
            "The semester-by-semester plan of courses, including fall and spring "
            "offerings, course numbers, credit hours per term, and sequencing."
        ),
        keywords=["fall", "spring", "semester", "schedule", "year 1", "sophomore", "junior", "senior"],
    ),
    Section(
        id="core_requirements",
        name="Core Requirements",
        description=(
            "Required foundational courses every student must complete. Includes "
            "math prerequisites, intro sequences, and mandatory core courses."
        ),
        keywords=["required", "core", "mandatory", "foundation", "must complete"],
    ),
    Section(
        id="specialization_paths",
        name="Specialization Paths",
        description=(
            "Optional tracks, concentrations, or focus areas. Covers how many "
            "specializations are offered and how deep each track is."
        ),
        keywords=["concentration", "track", "focus area", "specialization", "depth"],
    ),
    Section(
        id="electives",
        name="Electives",
        description=(
            "Free or technical electives and optional course lists available "
            "to students outside of required coursework."
        ),
        keywords=["elective", "optional", "free choice", "technical elective"],
    ),
    Section(
        id="credit_load",
        name="Credit Load",
        description=(
            "Total credit hours required, per-semester load, and credit "
            "distribution across the program."
        ),
        keywords=["credit hours", "credits", "total units", "credit load", "per semester"],
    ),
    Section(
    id="faculty_expertise",
    name="Faculty Expertise",
    description=(
        "Faculty research areas, industry experience, credentials, and academic "
        "backgrounds relevant to the program's field. Indicates the depth of "
        "expertise available to students."
    ),
    keywords=["faculty", "professor", "research", "phd", "industry experience", "expertise", "lab", "publications"],
    ),
]



# Fast lookup by id
SECTIONS_BY_ID: dict[str, Section] = {s.id: s for s in SECTIONS}


def get_section(section_id: str) -> Section | None:
    """Return a Section by its id, or None if not found."""
    return SECTIONS_BY_ID.get(section_id)


def all_section_ids() -> list[str]:
    """Return the list of all known section ids."""
    return [s.id for s in SECTIONS]

<<<<<<< HEAD
def classify_by_keywords(text: str) -> str | None:
    """
    Score-based keyword classifier. Counts keyword hits per section
    and returns the section with the highest score.
    Returns None if no keywords match at all.
    """
    lower = text.lower()
    scores: dict[str, int] = {}
    for section in SECTIONS:
        score = sum(1 for kw in section.keywords if kw in lower)
        if score > 0:
            scores[section.id] = score
    if not scores:
        return None
    return max(scores, key=lambda k: scores[k])

def classify_chunk(chunk: dict) -> str:
    """
    Classify a single normalized chunk into a section.
    Uses the section_hint (detected header) as a strong prior,
    then falls back to scored keyword matching on the content.
    
    chunk expected keys: content (str), section_hint (str | None), type (str)
    """
    # Tables describing schedules/courses are almost always course_schedule
    if chunk.get("type") == "table":
        hint = (chunk.get("section_hint") or "").lower()
        if any(kw in hint for kw in ["fall", "spring", "semester", "schedule", "year"]):
            return "course_schedule"
        if any(kw in hint for kw in ["required", "core", "mandatory"]):
            return "core_requirements"
        if any(kw in hint for kw in ["elective", "optional"]):
            return "electives"
        if any(kw in hint for kw in ["credit", "credits", "units"]):
            return "credit_load"

    # Use the section_hint from text_chunker as a head start
    hint = chunk.get("section_hint") or ""
    combined = f"{hint}\n{chunk.get('content', '')}"
    return classify_by_keywords(combined) or "core_requirements"
=======

def classify_by_keywords(text: str) -> str | None:
    """
    Cheap keyword-based classifier. Returns the id of the first matching
    section, or None if no keywords match.

    This is a fallback for when embeddings aren't available. Real
    classification should use embedding similarity against Section.description.
    """
    lower = text.lower()
    for section in SECTIONS:
        if any(kw in lower for kw in section.keywords):
            return section.id
    return None
>>>>>>> 906d83372dcd30abc521974d9acddd112012a1d3
