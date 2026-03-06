import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="research_papers")


def retrieve(query: str, top_k: int = 20, final_k: int = 5):

    query_embedding = embedding_model.encode(query).tolist()

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

    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(docs, metas, scores),
        key=lambda x: x[2],
        reverse=True
    )

    top_ranked = ranked[:final_k]

    final_docs = []
    grouped_sources = {}

    for doc, meta, score in top_ranked:

        source = meta.get("source", "Unknown PDF")
        page = meta.get("page", "Unknown")

        if source not in grouped_sources:
            grouped_sources[source] = set()

        grouped_sources[source].add(page)

        final_docs.append(doc)

    final_metas = []

    for pdf, pages in grouped_sources.items():

        page_list = sorted(list(pages))
        page_text = ", ".join([str(p) for p in page_list])

        final_metas.append({
            "pdf": pdf,
            "page": page_text
        })

    return final_docs, final_metas