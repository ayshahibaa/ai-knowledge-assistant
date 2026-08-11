import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODELS = [
    m.strip()
    for m in os.getenv("GROQ_MODELS", "").split(",")
    if m.strip()
]
EMBED_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
COLLECTION = "docs"
CHUNK_SIZE = 800      # characters
CHUNK_OVERLAP = 150
TOP_K = 5