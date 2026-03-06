import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.bm25_index import load_bm25

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="research_papers")

bm25, bm25_docs, bm25_metas = load_bm25()


def retrieve(query: str, top_k: int = 20, final_k: int = 5):

    query_embedding = embedding_model.encode(query).tolist()

    dense_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = dense_results.get("documents")
    metadatas = dense_results.get("metadatas")

    dense_docs = documents[0] if documents else []
    dense_metas = metadatas[0] if metadatas else []

    tokenized_query = query.split()

    bm25_scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:top_k]

    bm25_docs_top = [bm25_docs[i] for i in top_indices]
    bm25_metas_top = [bm25_metas[i] for i in top_indices]

    combined_docs = dense_docs + bm25_docs_top
    combined_metas = dense_metas + bm25_metas_top

    seen = set()
    unique_docs = []
    unique_metas = []

    for doc, meta in zip(combined_docs, combined_metas):
        if doc not in seen:
            seen.add(doc)
            unique_docs.append(doc)
            unique_metas.append(meta)

    pairs = [(query, doc) for doc in unique_docs]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(unique_docs, unique_metas, scores),
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