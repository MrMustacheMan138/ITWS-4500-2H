import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

SECTION_HEADERS = [
    "course schedule",
    "required courses",
    "electives",
    "concentration",
    "focus track",
    "learning outcomes",
    "faculty",
    "accreditation",
]


def chunk_pages(pdf_path: str, skip_pages: set[int]) -> list[dict]:
    """
    Load a PDF and split it into chunks, skipping pages whose relevant tables
    were already captured separately.
    """
    try:
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
    except Exception as e:
        logger.warning("PyMuPDFLoader failed for %s: %s", pdf_path, e)
        return []

    # Filter out pages that we've already captured as tables.
    # Note: PyMuPDFLoader page indices are 0-based, matching pdfplumber.
    text_docs = [
        doc for doc in docs
        if doc.metadata.get("page") not in skip_pages
        and (doc.page_content or "").strip()
    ]

    if not text_docs:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(text_docs)

    return [
        {
            "type": "text",
            "page": chunk.metadata.get("page"),
            "content": chunk.page_content,
            "header": detect_header(chunk.page_content),
        }
        for chunk in chunks
        if (chunk.page_content or "").strip()
    ]


def detect_header(text: str) -> str | None:
    lower = text.lower()
    for header in SECTION_HEADERS:
        if header in lower:
            return header
    return None


def table_to_text(table: list[list[str]]) -> str:
    """Flattens a raw table (list of rows) into a readable string."""
    if not table:
        return ""
    headers = [h or "" for h in table[0]]
    rows = table[1:]
    lines = []
    for row in rows:
        pairs = [f"{h}: {v}" for h, v in zip(headers, row) if h and v]
        if pairs:
            lines.append(" | ".join(pairs))
    return "\n".join(lines)


def normalize_chunks(parsed: dict) -> list[dict]:
    """
    Takes the raw output from parse_file() and returns a unified
    flat list of chunks ready for the LLM classifier and embedder.
    """
    normalized = []

    for chunk in parsed.get("text_chunks", []):
        content = (chunk.get("content") or "").strip()
        if not content:
            continue
        normalized.append({
            "type": "text",
            "page": chunk.get("page"),
            "section_hint": chunk.get("header"),
            "content": content,
        })

    for chunk in parsed.get("table_chunks", []):
        flat_text = table_to_text(chunk["content"])
        if not flat_text.strip():
            continue
        normalized.append({
            "type": "table",
            "page": chunk.get("page"),
            "section_hint": detect_header(
                " ".join(
                    cell for row in chunk["content"]
                    for cell in row if cell
                )
            ),
            "content": flat_text,
        })

    # Sort by page order so chunks flow in document order
    normalized.sort(key=lambda c: c["page"] if c["page"] is not None else 0)

    return normalized