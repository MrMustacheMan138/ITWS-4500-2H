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
        id="course schedule",
        name="Course Schedule",
        description=(
            "The semester-by-semester plan of courses, including fall and spring "
            "offerings, course numbers, credit hours per term, and sequencing. "
            "Covers what a typical student takes each semester."
        ),
        keywords=["fall", "spring", "semester", "schedule", "year 1", "sophomore", "junior", "senior", "first year", "second year"],
    ),
    Section(
        id="required courses",
        name="Required Courses",
        description=(
            "Required foundational courses that every student in the program must "
            "complete. Includes math prerequisites, intro sequences, and core "
            "discipline courses with no substitution allowed."
        ),
        keywords=["required", "core", "mandatory", "prerequisite", "foundation", "credit hours", "credits"],
    ),
    Section(
        id="concentration",
        name="Concentration",
        description=(
            "Optional tracks, concentrations, focus areas, or depth options. "
            "Covers how many specializations are offered, what each consists of, "
            "and how selective or deep each track is."
        ),
        keywords=["concentration", "track", "focus area", "specialization", "depth", "breadth", "elective"],
    ),
    Section(
        id="program overview",
        name="Program Overview",
        description=(
            "General program description, learning outcomes, faculty expertise, "
            "research opportunities, and professional development components. "
            "Indicates the program's pedagogical orientation."
        ),
        keywords=["learning outcomes", "faculty", "program goals", "description", "research", "internship", "career"],
    ),
    Section(
        id="accreditation",
        name="Accreditation",
        description=(
            "Accrediting bodies, standards, certifications, and outcome tracking. "
            "Indicates the external validation of program quality."
        ),
        keywords=["accreditation", "abet", "standards", "certifications", "accredited"],
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