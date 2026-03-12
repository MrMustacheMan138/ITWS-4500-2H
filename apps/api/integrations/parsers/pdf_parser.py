from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import fitz

def parse_file(pdf_path: str):
   doc = fitz.open(pdf_path)
   num_pages = doc.page_count

   # Pre-scan 
   with pdfplumber.open(pdf_path) as pdf:
      for i in range(0, num_pages):
         page = pdf.pages[i]
         tables = page.find_tables() # Returns a list of tables found
         extracted_table = page.extract_tables()

