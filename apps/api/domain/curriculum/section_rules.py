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
            "offerings, course numbers, credit hours per term, and sequencing. "
            "Covers what a typical student takes each semester."
        ),
        keywords=["fall", "spring", "semester", "schedule", "year 1", "sophomore", "junior", "senior"],
    ),
    Section(
        id="core_requirements",
        name="Core Requirements",
        description=(
            "Required foundational courses that every student in the program must "
            "complete. Includes math prerequisites, intro sequences, and core "
            "discipline courses with no substitution allowed."
        ),
        keywords=["required", "core", "mandatory", "prerequisite", "foundation"],
    ),
    Section(
        id="specialization_paths",
        name="Specialization Paths",
        description=(
            "Optional tracks, concentrations, focus areas, or depth options. "
            "Covers how many specializations are offered, what each consists of, "
            "and how selective or deep each track is."
        ),
        keywords=["concentration", "track", "focus area", "specialization", "depth", "breadth"],
    ),
    Section(
        id="electives",
        name="Electives",
        description=(
            "Free electives, technical electives, and non-core course choices. "
            "Includes the number of elective credits required, restrictions on "
            "what counts, and availability of advanced electives."
        ),
        keywords=["elective", "optional", "free choice", "approved list"],
    ),
    Section(
        id="credit_load",
        name="Credit Load & Hours",
        description=(
            "Total credit hours required to graduate, typical credit load per "
            "semester, and credit distribution across subject areas. Also covers "
            "any minimum/maximum credit constraints per term."
        ),
        keywords=["credit hour", "units", "credits", "total credits", "credit load"],
    ),
    Section(
        id="capstone_research",
        name="Capstone & Research",
        description=(
            "Senior design projects, capstone courses, thesis requirements, "
            "undergraduate research opportunities, and independent study options. "
            "Indicates the degree to which the program requires substantive "
            "project or research work."
        ),
        keywords=["capstone", "senior design", "thesis", "research", "independent study", "project"],
    ),
    Section(
        id="grading_assessment",
        name="Grading & Assessment",
        description=(
            "Grading policies, minimum GPA requirements, exam structures, and "
            "assessment methods. Indicates the academic standards enforced on "
            "students throughout the program."
        ),
        keywords=["gpa", "grading", "minimum grade", "exam", "assessment", "pass/fail"],
    ),
    Section(
        id="prerequisites_policy",
        name="Prerequisites Policy",
        description=(
            "How prerequisites are enforced, which courses require what, and the "
            "depth of the prerequisite chains. A program with long, strict "
            "prerequisite chains is typically more rigorous."
        ),
        keywords=["prerequisite", "pre-req", "corequisite", "required before"],
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