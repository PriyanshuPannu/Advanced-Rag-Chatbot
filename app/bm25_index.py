import chromadb
from rank_bm25 import BM25Okapi

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="research_papers")


def load_bm25():

    data = collection.get(include=["documents", "metadatas"])

    docs = data.get("documents") or []
    metas = data.get("metadatas") or []

    tokenized_corpus = [doc.split() for doc in docs]

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25, docs, metas