from fastapi import FastAPI
from app.retriever import retrieve
from app.llm import generate_answer
from app.database import init_db

init_db()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "AI Research RAG running"}


@app.post("/chat")
def chat(query: str):

    documents, metadata = retrieve(query)
    answer = generate_answer(query, documents)

    sources = []

    for item in metadata:
        sources.append({
            "pdf": item.get("pdf", "Unknown PDF"),
            "page": item.get("page", "Unknown")
        })

    return {
        "response": answer,
        "sources": sources
    }