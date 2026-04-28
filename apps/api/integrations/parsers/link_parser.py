"""
Link parser: fetches a URL, extracts readable text, and returns chunks
in the same shape as pdf_parser so downstream consumers don't care about
the source type.
"""
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from urllib.parse import urlparse

KNOWN_HEADERS = [
    "fall", "spring", "required", "courses", "focus track",
    "depth", "breadth", "electives", "prerequisites", "credit",
    "concentration", "major", "minor", "capstone",
]

# Tags that are never curriculum content
NOISE_TAGS = ['nav', 'footer', 'header', 'script', 'style', 'noscript', 'iframe']

# CSS class/id fragments that indicate boilerplate
NOISE_PATTERNS = ['nav', 'footer', 'header', 'menu', 'sidebar', 'breadcrumb',
                  'cookie', 'banner', 'popup', 'modal', 'alert', 'search']


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def detect_header(text: str) -> str | None:
    lower = text.lower()
    for header in KNOWN_HEADERS:
        if header in lower:
            return header
    return None


def _extract_clean_text(url: str) -> str:
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()

    for tag in soup.find_all(True):
        try:
            tag_classes = " ".join(tag.get("class") or [])
            tag_id = tag.get("id") or ""
            combined = f"{tag_classes} {tag_id}".lower()
            if any(pattern in combined for pattern in NOISE_PATTERNS):
                tag.decompose()
        except Exception:
            continue

    main = soup.find("main") or soup.find(id="main") or soup.find(id="content")
    target = main or soup.find("body") or soup.find("html") or soup

    return " ".join((target.get_text(separator=" ") if target else "").split())


def parse_link(url: str) -> dict:
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        text = _extract_clean_text(url)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    if not text.strip():
        raise RuntimeError(f"No text content found at {url}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([text])

    text_chunks = [
        {
            "type": "text",
            "page": None,
            "content": chunk.page_content,
            "header": detect_header(chunk.page_content),
            "source_url": url,
        }
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    return {
        "table_chunks": [],
        "text_chunks": text_chunks,
    }