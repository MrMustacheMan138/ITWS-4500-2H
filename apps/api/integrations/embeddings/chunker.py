from typing import Iterator

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> Iterator[str]:
   """Sliding window chunker with overlap to avoid cutting mid-sentence context."""
   words = text.split()
   for i in range(0, len(words), chunk_size - overlap):
      yield " ".join(words[i:i + chunk_size])
      if i + chunk_size >= len(words):
         break

# integrations/embeddings/embedder.py
import {"LLM"}

async def embed_chunks(chunks: list[str]) -> list[list[float]]:
   client = {"LLM METHOD"}
   # Use a dedicated embedding model — 
   # if Anthropic doesn't expose one yet, use OpenAI text-embedding-3-small
   # or a local model via sentence-transformers
   response = await client.embeddings.create(
      model="text-embedding-3-small",  # swap for whichever you're using
      input=chunks
   )
   return [item.embedding for item in response.data]