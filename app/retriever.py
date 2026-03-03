import chromadb
from sentence_transformers import SentenceTransformer

import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection("research_papers")

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


from typing import List, Tuple, Any

def retrieve(query: str, top_k: int = 5) -> Tuple[List[str], List[Any]]:
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents")
    metadatas = results.get("metadatas")

    if not documents or not metadatas:
        return [], []

    return documents[0], metadatas[0]