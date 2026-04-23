from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import fitz
from text_chunker import chunk_pages

KNOWN_HEADERS = ["fall", "spring", "required", "courses", "focus track", "depth", "breadth", "electives"] # Fill with headers that are commonly associated with important parts

def is_relevant_table(table: list[list[str]]) -> bool:
   if not table or not table[0]:
      return False
   header_row = [cell.lower() for cell in table[0] if cell] # Traverse through top row
   return any(keyword in " ".join(header_row) for keyword in KNOWN_HEADERS) # 

def parse_file(pdf_path: str) -> dict:
   doc = fitz.open(pdf_path)
   num_pages = doc.page_count

   table_chunks = []
   table_pages = set()

   # Pre-scan 
   with pdfplumber.open(pdf_path) as pdf:
      for i in range(num_pages):
         page = pdf.pages[i]
         tables = page.extract_tables()
         if tables:
            table_pages.add(i)
            for table in tables: # Processing single table
               if is_relevant_table(table):
                  table_chunks.append({
                     "type":"table",
                     "page": i,
                     "content": table # Raw list[list[str]]
                  })
      
   text_chunks = chunk_pages(pdf_path, skip_pages=table_pages) # Currently skips pages just if they have a table in it.
   # If a table takes up half a page and the other half contains actual text, it gets skipped. Will determine a fix later

   return {
      "table_chunks" : table_chunks,
      "text_chunks": text_chunks
   }


