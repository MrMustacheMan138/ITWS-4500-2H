from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

SECTION_HEADERS = []

def chunk_pages(pdf_path: str, skip_pages: set[int]) -> list[dict]:
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load() # Loads the document into docs

    text_docs = [doc for doc in docs if doc.metadata.get("page" not in skip_pages)] # Gets all the pages that have text to parse without tables

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(text_docs)

    return [
        # Returns chunk entries that are sectioned off by their detected headers
        {
            "type": "text",
            "page": chunk.metadata.get("page"),
            "content": chunk.page_content,
            "header": detect_header(chunk.page_content)
        }
        for chunk in chunks
    ]

def detect_header(text: str) -> str | None:
    lower = text.lower()
    for header in SECTION_HEADERS:
        if header in lower:
            return header
    return None
