"""
Unit tests for integrations/parsers/ utilities.

Tests URL validation, header detection, table flattening, and chunk
normalization — all pure Python logic that doesn't hit disk or network.
"""

import pytest

from integrations.parsers.link_parser import is_valid_url, detect_header as link_detect_header
from integrations.parsers.text_chunker import (
    detect_header as text_detect_header,
    table_to_text,
    normalize_chunks,
)
from api.v1.routers.ingest import _detect_file_type


# ---------------------------------------------------------------------------
# URL validation
# ---------------------------------------------------------------------------

class TestIsValidUrl:
    @pytest.mark.parametrize("url", [
        "https://www.rpi.edu/catalog",
        "http://cs.mit.edu/programs",
        "https://example.com",
        "http://localhost:8080/path",
    ])
    def test_valid_urls(self, url):
        assert is_valid_url(url) is True

    @pytest.mark.parametrize("url", [
        "",
        "not-a-url",
        "ftp://example.com",
        "//example.com",
        "example.com",
        "http://",
        "javascript:alert(1)",
    ])
    def test_invalid_urls(self, url):
        assert is_valid_url(url) is False


# ---------------------------------------------------------------------------
# Header detection (link_parser)
# ---------------------------------------------------------------------------

class TestLinkDetectHeader:
    def test_detects_fall(self):
        assert link_detect_header("Fall semester course list") == "fall"

    def test_detects_spring(self):
        assert link_detect_header("Spring semester offerings") == "spring"

    def test_detects_required(self):
        assert link_detect_header("Required courses for the major") == "required"

    def test_detects_credit(self):
        assert link_detect_header("Credit hours per course") == "credit"

    def test_returns_none_for_no_match(self):
        assert link_detect_header("This sentence has no matching terms.") is None

    def test_returns_none_for_empty(self):
        assert link_detect_header("") is None

    def test_case_insensitive(self):
        assert link_detect_header("ELECTIVES available") == "electives"


# ---------------------------------------------------------------------------
# Header detection (text_chunker)
# ---------------------------------------------------------------------------

class TestTextDetectHeader:
    def test_detects_course_schedule(self):
        assert text_detect_header("Course schedule for fall") == "course schedule"

    def test_detects_electives(self):
        assert text_detect_header("List of electives available") == "electives"

    def test_detects_faculty(self):
        assert text_detect_header("Faculty research interests") == "faculty"

    def test_returns_none_for_no_match(self):
        assert text_detect_header("Random unrelated content here.") is None

    def test_returns_none_for_empty(self):
        assert text_detect_header("") is None


# ---------------------------------------------------------------------------
# table_to_text
# ---------------------------------------------------------------------------

class TestTableToText:
    def test_basic_table(self):
        table = [
            ["Course", "Credits", "Semester"],
            ["CS101", "3", "Fall"],
            ["CS201", "4", "Spring"],
        ]
        result = table_to_text(table)
        assert "CS101" in result
        assert "3" in result
        assert "Fall" in result
        assert "CS201" in result

    def test_empty_table_returns_empty_string(self):
        assert table_to_text([]) == ""

    def test_header_only_table_returns_empty(self):
        # No data rows, so nothing to emit
        table = [["Course", "Credits"]]
        result = table_to_text(table)
        assert result == ""

    def test_rows_with_none_cells_handled(self):
        table = [
            ["Course", "Credits"],
            [None, "3"],
            ["CS101", None],
            ["CS201", "4"],
        ]
        result = table_to_text(table)
        # Only the fully paired row should appear
        assert "CS201" in result

    def test_pipe_delimiter_used(self):
        table = [
            ["A", "B"],
            ["x", "y"],
        ]
        result = table_to_text(table)
        assert "|" in result


# ---------------------------------------------------------------------------
# normalize_chunks
# ---------------------------------------------------------------------------

class TestNormalizeChunks:
    def test_text_chunks_included(self):
        parsed = {
            "text_chunks": [
                {"content": "Introduction to algorithms.", "page": 1, "header": None}
            ],
            "table_chunks": [],
        }
        result = normalize_chunks(parsed)
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["content"] == "Introduction to algorithms."

    def test_table_chunks_converted_to_text(self):
        parsed = {
            "text_chunks": [],
            "table_chunks": [
                {
                    "content": [["Course", "Credits"], ["CS101", "3"]],
                    "page": 2,
                }
            ],
        }
        result = normalize_chunks(parsed)
        assert len(result) == 1
        assert result[0]["type"] == "table"
        assert "CS101" in result[0]["content"]

    def test_empty_content_chunks_are_filtered(self):
        parsed = {
            "text_chunks": [
                {"content": "", "page": 1, "header": None},
                {"content": "  ", "page": 2, "header": None},
                {"content": "Valid content.", "page": 3, "header": None},
            ],
            "table_chunks": [],
        }
        result = normalize_chunks(parsed)
        assert len(result) == 1
        assert result[0]["content"] == "Valid content."

    def test_chunks_sorted_by_page(self):
        parsed = {
            "text_chunks": [
                {"content": "Page 5 content.", "page": 5, "header": None},
                {"content": "Page 1 content.", "page": 1, "header": None},
                {"content": "Page 3 content.", "page": 3, "header": None},
            ],
            "table_chunks": [],
        }
        result = normalize_chunks(parsed)
        pages = [c["page"] for c in result]
        assert pages == sorted(pages)

    def test_none_page_treated_as_zero(self):
        parsed = {
            "text_chunks": [
                {"content": "No page.", "page": None, "header": None},
                {"content": "Page 2.", "page": 2, "header": None},
            ],
            "table_chunks": [],
        }
        result = normalize_chunks(parsed)
        # Should not raise; None page treated as 0
        assert len(result) == 2

    def test_empty_input(self):
        result = normalize_chunks({"text_chunks": [], "table_chunks": []})
        assert result == []


# ---------------------------------------------------------------------------
# _detect_file_type (ingest router helper)
# ---------------------------------------------------------------------------

class TestDetectFileType:
    @pytest.mark.parametrize("filename,expected", [
        ("syllabus.pdf", "pdf"),
        ("course_catalog.PDF", "pdf"),
        ("photo.png", "image"),
        ("scan.jpg", "image"),
        ("photo.jpeg", "image"),
        ("image.webp", "image"),
        ("data.csv", "file"),
        ("document.docx", "file"),
        ("archive.zip", "file"),
        ("unknown", "file"),
    ])
    def test_file_type_detection(self, filename, expected):
        assert _detect_file_type(filename) == expected