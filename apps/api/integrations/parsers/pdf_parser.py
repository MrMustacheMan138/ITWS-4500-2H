from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import fitz
import logging
from integrations.parsers.text_chunker import chunk_pages, normalize_chunks

logger = logging.getLogger(__name__)

# Headers commonly associated with curriculum-relevant tables
KNOWN_HEADERS = [
    "fall", "spring", "required", "courses", "focus track",
    "depth", "breadth", "electives", "credit", "credits",
    "semester", "year", "course code", "course number",
]


def is_relevant_table(table: list[list[str]]) -> bool:
    """Return True if the table's header row contains a curriculum keyword."""
    if not table or not table[0]:
        return False
    header_row = [(cell or "").lower() for cell in table[0]]
    joined = " ".join(header_row)
    return any(keyword in joined for keyword in KNOWN_HEADERS)


def parse_file(pdf_path: str) -> list[dict]:
    """
    Parse a PDF and return normalized chunks.

    Strategy:
      1. Scan every page with pdfplumber; collect ONLY relevant tables.
      2. Only skip a page during text chunking if at least one table on that
         page was deemed relevant. Pages whose tables are all irrelevant
         (often layout artifacts in modern PDFs) keep their text.
      3. Always run text chunking — even if zero tables were found.
      4. As a final safety net, if the combined output is empty, fall back
         to chunking ALL pages so we never silently drop the whole document.
    """
    table_chunks: list[dict] = []
    pages_with_relevant_tables: set[int] = set()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables() or []
                except Exception as e:
                    logger.warning("pdfplumber.extract_tables failed on page %d: %s", i, e)
                    tables = []

                page_had_relevant = False
                for table in tables:
                    if is_relevant_table(table):
                        page_had_relevant = True
                        table_chunks.append({
                            "type": "table",
                            "page": i,
                            "content": table,
                        })

                if page_had_relevant:
                    pages_with_relevant_tables.add(i)

    except Exception as e:
        # If pdfplumber blows up entirely, fall through to PyMuPDF text extraction
        logger.warning("pdfplumber.open failed for %s: %s", pdf_path, e)

    # Run text chunking on all pages except those whose relevant tables we already captured
    text_chunks = chunk_pages(pdf_path, skip_pages=pages_with_relevant_tables)

    # Safety net: if we somehow extracted nothing, retry with no skipped pages
    if not text_chunks and not table_chunks:
        logger.warning(
            "parse_file produced 0 chunks for %s; retrying without page skipping",
            pdf_path,
        )
        text_chunks = chunk_pages(pdf_path, skip_pages=set())

    return normalize_chunks({
        "table_chunks": table_chunks,
        "text_chunks": text_chunks,
    })