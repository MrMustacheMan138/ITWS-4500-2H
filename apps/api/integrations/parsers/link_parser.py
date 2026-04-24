"""
Link parser: fetches a URL, extracts readable text, and returns chunks
in the same shape as pdf_parser so downstream consumers don't care about
the source type.
"""
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from urllib.parse import urlparse

# Mirrors KNOWN_HEADERS in pdf_parser.py — keywords that hint at a section
KNOWN_HEADERS = [
    "fall", "spring", "required", "courses", "focus track",
    "depth", "breadth", "electives", "prerequisites", "credit",
    "concentration", "major", "minor", "capstone",
]


def is_valid_url(url: str) -> bool:
    """Validate that the string is a well-formed http(s) URL."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def detect_header(text: str) -> str | None:
    """Return the first known header keyword found in the chunk, if any."""
    lower = text.lower()
    for header in KNOWN_HEADERS:
        if header in lower:
            return header
    return None


def parse_link(url: str) -> dict:
    """
    Fetch a web page and return its text chunks.

    Returns the same shape as parse_file() in pdf_parser.py so both sources
    feed into the same downstream pipeline.

    Raises:
        ValueError: if the URL is malformed.
        RuntimeError: if the fetch fails or the page has no extractable text.
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    if not docs or not any(doc.page_content.strip() for doc in docs):
        raise RuntimeError(f"No text content found at {url}")

    # Same splitter settings as text_chunker.py for consistency
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    text_chunks = [
        {
            "type": "text",
            "page": None,          # web pages don't have page numbers
            "content": chunk.page_content,
            "header": detect_header(chunk.page_content),
            "source_url": url,
        }
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    return {
        "table_chunks": [],        # TODO: extract HTML tables in a later pass
        "text_chunks": text_chunks,
    }