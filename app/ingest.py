import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from config import *

model = SentenceTransformer(EMBED_MODEL)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(COLLECTION)

def pdf_to_pages(path):
    reader = PdfReader(path)
    return [(i + 1, p.extract_text() or "") for i, p in enumerate(reader.pages)]

def chunk(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    step = max(1, size - overlap)
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + size])
        start += step
    return [c for c in out if c.strip()]

def ingest(path, doc_name, batch_size=64):
    ids, texts, metas = [], [], []
    for page_no, page_text in pdf_to_pages(path):
        for j, c in enumerate(chunk(page_text)):
            ids.append(f"{doc_name}-p{page_no}-c{j}")
            texts.append(c)
            metas.append({"source": doc_name, "page": page_no})

    if not texts:
        raise ValueError("no extractable text (scanned PDF? needs OCR)")

    for i in range(0, len(texts), batch_size):
        sl = slice(i, i + batch_size)
        collection.upsert(
            ids=ids[sl], documents=texts[sl],
            embeddings=model.encode(texts[sl]).tolist(), metadatas=metas[sl]
        )
    return len(texts)