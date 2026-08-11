from ingest import model, collection
from config import TOP_K

def retrieve(query, k=TOP_K, sources=None):
    q_emb = model.encode([query]).tolist()
    where = {"source": {"$in": sources}} if sources else None
    res = collection.query(query_embeddings=q_emb, n_results=k, where=where)
    if not res["documents"] or not res["documents"][0]:
        return []
    return [
        {"text": d, "source": m["source"], "page": m["page"]}
        for d, m in zip(res["documents"][0], res["metadatas"][0])
    ]