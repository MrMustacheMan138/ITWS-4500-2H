"""
Unit tests for domain/curriculum/section_rules.py

Covers section lookup, keyword classification, and chunk classification
without touching the database or any AI service.
"""

import pytest

from domain.curriculum.section_rules import (
    SECTIONS,
    SECTIONS_BY_ID,
    Section,
    get_section,
    all_section_ids,
    classify_by_keywords,
    classify_chunk,
)

KNOWN_SECTION_IDS = {
    "course_schedule",
    "core_requirements",
    "specialization_paths",
    "electives",
    "credit_load",
    "faculty_expertise",
}


# ---------------------------------------------------------------------------
# Section registry
# ---------------------------------------------------------------------------

class TestSectionRegistry:
    def test_sections_list_is_not_empty(self):
        assert len(SECTIONS) > 0

    def test_all_known_section_ids_present(self):
        ids = set(all_section_ids())
        assert KNOWN_SECTION_IDS.issubset(ids)

    def test_sections_by_id_matches_sections_list(self):
        for section in SECTIONS:
            assert section.id in SECTIONS_BY_ID
            assert SECTIONS_BY_ID[section.id] is section

    def test_each_section_has_required_fields(self):
        for section in SECTIONS:
            assert section.id, f"Section missing id: {section}"
            assert section.name, f"Section missing name: {section}"
            assert section.description, f"Section missing description: {section}"

    def test_section_ids_are_unique(self):
        ids = [s.id for s in SECTIONS]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# get_section
# ---------------------------------------------------------------------------

class TestGetSection:
    def test_returns_correct_section(self):
        section = get_section("course_schedule")
        assert section is not None
        assert section.id == "course_schedule"

    def test_returns_none_for_unknown_id(self):
        assert get_section("nonexistent_section") is None

    def test_returns_none_for_empty_string(self):
        assert get_section("") is None

    @pytest.mark.parametrize("section_id", list(KNOWN_SECTION_IDS))
    def test_all_known_ids_resolve(self, section_id):
        assert get_section(section_id) is not None


# ---------------------------------------------------------------------------
# classify_by_keywords
# ---------------------------------------------------------------------------

class TestClassifyByKeywords:
    def test_schedule_keywords(self):
        result = classify_by_keywords("Students take courses in fall and spring semesters.")
        assert result == "course_schedule"

    def test_core_requirements_keywords(self):
        result = classify_by_keywords("All students must complete required core foundational courses.")
        assert result == "core_requirements"

    def test_electives_keywords(self):
        result = classify_by_keywords("Students may choose any technical elective from the list.")
        assert result == "electives"

    def test_credit_load_keywords(self):
        result = classify_by_keywords("The program requires 120 total credit hours per semester.")
        assert result == "credit_load"

    def test_faculty_keywords(self):
        result = classify_by_keywords("Our faculty hold PhD degrees and publish research papers.")
        assert result == "faculty_expertise"

    def test_returns_none_for_no_match(self):
        result = classify_by_keywords("This sentence contains no relevant terms whatsoever.")
        assert result is None

    def test_returns_none_for_empty_string(self):
        assert classify_by_keywords("") is None

    def test_highest_score_wins(self):
        # "fall semester schedule" has multiple course_schedule hits
        result = classify_by_keywords("fall semester year 1 sophomore schedule")
        assert result == "course_schedule"

    def test_case_insensitive(self):
        result = classify_by_keywords("FALL SEMESTER SPRING YEAR")
        assert result == "course_schedule"


# ---------------------------------------------------------------------------
# classify_chunk
# ---------------------------------------------------------------------------

class TestClassifyChunk:
    def test_table_with_schedule_hint(self):
        chunk = {
            "type": "table",
            "section_hint": "fall semester schedule",
            "content": "CS101 | CS201 | CS301",
        }
        assert classify_chunk(chunk) == "course_schedule"

    def test_table_with_required_hint(self):
        chunk = {
            "type": "table",
            "section_hint": "required core courses",
            "content": "Math | Physics | Chemistry",
        }
        assert classify_chunk(chunk) == "core_requirements"

    def test_table_with_elective_hint(self):
        chunk = {
            "type": "table",
            "section_hint": "optional elective courses",
            "content": "Art | Music | Drama",
        }
        assert classify_chunk(chunk) == "electives"

    def test_table_with_credit_hint(self):
        chunk = {
            "type": "table",
            "section_hint": "credit hours distribution",
            "content": "CS: 30 credits | Math: 20 credits",
        }
        assert classify_chunk(chunk) == "credit_load"

    def test_text_chunk_with_keyword_content(self):
        chunk = {
            "type": "text",
            "section_hint": None,
            "content": "Students must complete required mandatory core foundational courses in year one.",
        }
        result = classify_chunk(chunk)
        assert result == "core_requirements"

    def test_defaults_to_core_requirements_when_no_match(self):
        chunk = {
            "type": "text",
            "section_hint": None,
            "content": "Random unrelated content with no matching terms.",
        }
        result = classify_chunk(chunk)
        assert result == "core_requirements"

    def test_section_hint_boosts_classification(self):
        chunk = {
            "type": "text",
            "section_hint": "fall schedule",
            "content": "Courses are listed below.",
        }
        result = classify_chunk(chunk)
        assert result == "course_schedule"