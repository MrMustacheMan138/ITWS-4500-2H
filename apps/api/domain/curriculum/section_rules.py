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