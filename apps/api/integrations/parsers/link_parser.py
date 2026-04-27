"""
Link parser: fetches a URL with Playwright (full JS execution), extracts
readable text via BeautifulSoup, and returns chunks in the same shape as
pdf_parser so downstream consumers don't care about the source type.

Playwright is used instead of a simple requests/WebBaseLoader fetch so that
pages that rely on JavaScript to render their DOM (SPAs, React course
catalogs, etc.) are fully loaded before we extract text.
"""

from urllib.parse import urlparse

from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWN_HEADERS = [
    "fall", "spring", "required", "courses", "focus track",
    "depth", "breadth", "electives", "prerequisites", "credit",
    "concentration", "major", "minor", "capstone",
]


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


def _extract_text_from_html(html: str) -> str:
    """Strip scripts, styles, nav boilerplate and return clean readable text."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    # Prefer main content container if present
    main = soup.find("main") or soup.find(id="main") or soup.find(class_="main-content")
    root = main if main else soup.body or soup

    return root.get_text(separator="\n", strip=True)


async def parse_link(url: str) -> dict:
    """
    Fetch a web page with full JS execution via Playwright (headless Chromium)
    and return its text chunks.

    Returns the same shape as parse_file() in pdf_parser.py.

    Raises:
        ValueError: if the URL is malformed.
        RuntimeError: if the fetch fails or the page has no extractable text.
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        from playwright.async_api import async_playwright  # local import keeps startup fast

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = await browser.new_page()

            # networkidle waits for JS-heavy pages to finish rendering
            await page.goto(url, wait_until="networkidle", timeout=30_000)

            html = await page.content()
            await browser.close()

    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url} with Playwright: {e}") from e

    text = _extract_text_from_html(html)

    if not text.strip():
        raise RuntimeError(f"No text content found at {url}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    raw_chunks = splitter.split_text(text)

    text_chunks = [
        {
            "type": "text",
            "page": None,
            "content": chunk,
            "header": detect_header(chunk),
            "source_url": url,
        }
        for chunk in raw_chunks
        if chunk.strip()
    ]

    return {
        "table_chunks": [],
        "text_chunks": text_chunks,
    }