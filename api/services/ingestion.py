import os
from typing import List
from django.db import transaction
from api.models import Document, DocumentChunk

CHUNK_SIZE = 1500  # characters
EMBEDDING_DIM = 768

def _read_file_text(path: str) -> str:
    """Basic text reader; extend later for PDF/DOCX via unstructured."""
    ext = os.path.splitext(path)[1].lower()
    if ext in {'.txt', '.md', '.py', '.js', '.ts', '.json', '.csv'}:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return ""  # unsupported yet


def _chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] if text else []


def _embed_chunks(chunks: List[str]) -> List[List[float]]:
    # Placeholder zero embeddings; replace with real Gemini embeddings later.
    return [[0.0] * EMBEDDING_DIM for _ in chunks]


def process_document(document: Document) -> None:
    """Parse, chunk, embed, store chunks, and update status."""
    raw_text = _read_file_text(document.file.path)
    if not raw_text.strip():
        document.status = 'failed'
        document.save(update_fields=['status'])
        return
    chunks = _chunk_text(raw_text)
    embeddings = _embed_chunks(chunks)
    with transaction.atomic():
        objs = [DocumentChunk(document=document, chunk_text=c, embedding=e) for c, e in zip(chunks, embeddings)]
        DocumentChunk.objects.bulk_create(objs, batch_size=100)
        document.status = 'ready'
        document.save(update_fields=['status'])
