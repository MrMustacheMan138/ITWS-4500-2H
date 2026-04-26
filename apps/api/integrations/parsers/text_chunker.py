from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    text_docs = [doc for doc in docs if doc.metadata.get("page") not in skip_pages] # Gets all the pages that have text to parse without tables

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

    Output format per chunk:
    {
        "type": "text" | "table",
        "page": int,
        "section_hint": str | None,   # best guess before LLM classification
        "content": str                # always plain text
    }
    """
    normalized = []

    for chunk in parsed.get("text_chunks", []):
        normalized.append({
            "type": "text",
            "page": chunk["page"],
            "section_hint": chunk["header"],
            "content": chunk["content"].strip()
        })

    for chunk in parsed.get("table_chunks", []):
        normalized.append({
            "type": "table",
            "page": chunk["page"],
            "section_hint": detect_header(                      # reuse header detection on flattened text
                " ".join(                                       # so tables get a section_hint too
                    cell for row in chunk["content"]
                    for cell in row if cell
                )
            ),
            "content": table_to_text(chunk["content"])
        })

    # Sort by page order so chunks flow in document order
    normalized.sort(key=lambda c: c["page"] or 0)

    return normalized