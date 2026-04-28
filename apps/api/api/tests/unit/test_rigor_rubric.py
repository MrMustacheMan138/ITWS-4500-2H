"""
Unit tests for domain/scoring/rigor_rubric.py

Tests scoring math, prompt building, and weight validation.
"""

import pytest

from domain.scoring.rigor_rubric import (
    SECTION_WEIGHTS,
    SECTION_CRITERIA,
    SectionScore,
    RigorResult,
    compute_overall_score,
    build_section_prompt,
    validate_weights,
)


# ---------------------------------------------------------------------------
# Weight validation
# ---------------------------------------------------------------------------

class TestWeightConfiguration:
    def test_weights_sum_to_one(self):
        total = sum(SECTION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-6, f"Weights sum to {total}, expected 1.0"

    def test_all_weights_are_positive(self):
        for section_id, weight in SECTION_WEIGHTS.items():
            assert weight > 0, f"Section '{section_id}' has non-positive weight {weight}"

    def test_validate_weights_returns_true(self):
        assert validate_weights() is True

    def test_criteria_exist_for_every_weighted_section(self):
        for section_id in SECTION_WEIGHTS:
            assert section_id in SECTION_CRITERIA, f"No criteria for '{section_id}'"

    def test_criteria_strings_are_non_empty(self):
        for section_id, criteria in SECTION_CRITERIA.items():
            assert criteria.strip(), f"Empty criteria for '{section_id}'"


# ---------------------------------------------------------------------------
# compute_overall_score
# ---------------------------------------------------------------------------

class TestComputeOverallScore:
    def test_all_sections_perfect_score(self):
        scores = [
            SectionScore(section_id=sid, score=100.0, strengths=[], weaknesses=[])
            for sid in SECTION_WEIGHTS
        ]
        result = compute_overall_score(scores)
        assert result == 100.0

    def test_all_sections_zero_score(self):
        scores = [
            SectionScore(section_id=sid, score=0.0, strengths=[], weaknesses=[])
            for sid in SECTION_WEIGHTS
        ]
        result = compute_overall_score(scores)
        assert result == 0.0

    def test_empty_scores_returns_zero(self):
        assert compute_overall_score([]) == 0.0

    def test_single_section_returns_its_score(self):
        scores = [SectionScore(section_id="core_requirements", score=80.0, strengths=[], weaknesses=[])]
        result = compute_overall_score(scores)
        assert result == 80.0

    def test_unknown_section_is_skipped(self):
        scores = [
            SectionScore(section_id="nonexistent_section", score=100.0, strengths=[], weaknesses=[]),
            SectionScore(section_id="core_requirements", score=50.0, strengths=[], weaknesses=[]),
        ]
        result = compute_overall_score(scores)
        # Only core_requirements (weight 0.30) contributes; renormalized => 50.0
        assert result == 50.0

    def test_weighted_average_is_correct(self):
        # course_schedule (0.25) = 80, core_requirements (0.30) = 100
        # others zero
        scores = [
            SectionScore(section_id="course_schedule", score=80.0, strengths=[], weaknesses=[]),
            SectionScore(section_id="core_requirements", score=100.0, strengths=[], weaknesses=[]),
        ]
        result = compute_overall_score(scores)
        total_w = 0.25 + 0.30
        expected = round((0.25 * 80.0 + 0.30 * 100.0) / total_w, 1)
        assert result == expected

    def test_result_is_rounded_to_one_decimal(self):
        scores = [SectionScore(section_id="course_schedule", score=66.666, strengths=[], weaknesses=[])]
        result = compute_overall_score(scores)
        assert result == round(result, 1)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# build_section_prompt
# ---------------------------------------------------------------------------

class TestBuildSectionPrompt:
    def test_contains_section_id(self):
        prompt = build_section_prompt("core_requirements", ["some content"])
        assert "core_requirements" in prompt

    def test_contains_chunks(self):
        prompt = build_section_prompt("electives", ["Elective course list here"])
        assert "Elective course list here" in prompt

    def test_multiple_chunks_are_joined(self):
        prompt = build_section_prompt("electives", ["chunk A", "chunk B"])
        assert "chunk A" in prompt
        assert "chunk B" in prompt

    def test_empty_chunks_shows_placeholder(self):
        prompt = build_section_prompt("electives", [])
        assert "no content" in prompt.lower()

    def test_contains_json_schema_hint(self):
        prompt = build_section_prompt("electives", ["some content"])
        assert "score" in prompt.lower()
        assert "strengths" in prompt.lower()
        assert "weaknesses" in prompt.lower()

    def test_criteria_injected_for_known_section(self):
        prompt = build_section_prompt("course_schedule", ["content"])
        criteria = SECTION_CRITERIA["course_schedule"]
        # Criteria text (or meaningful part of it) should appear
        assert "rigorous" in prompt.lower() or "sequence" in prompt.lower()