import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# Load embedding model (for query embedding)
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Load cross-encoder reranker
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Connect to Chroma
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("research_papers")


def retrieve(query: str, top_k: int = 20, final_k: int = 5):
    # Step 1: Embed query
    query_embedding = embedding_model.encode(query).tolist()

    # Step 2: Retrieve top_k from vector DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents")
    metadatas = results.get("metadatas")

    if not documents or not metadatas:
        return [], []

    docs = documents[0]
    metas = metadatas[0]

    # Step 3: Rerank using cross-encoder
    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)

    # Step 4: Sort by score descending
    ranked = sorted(zip(docs, metas, scores), key=lambda x: x[2], reverse=True)

    # Step 5: Select top final_k
    top_ranked = ranked[:final_k]

    final_docs = [item[0] for item in top_ranked]
    final_metas = [item[1] for item in top_ranked]

    return final_docs, final_metas