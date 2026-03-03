from fastapi import FastAPI
from app.retriever import retrieve
from app.llm import generate_answer

app = FastAPI()


@app.get("/")
def root():
    return {"message": "AI Research RAG running"}


@app.post("/chat")
def chat(query: str):
    documents, metadata = retrieve(query)
    answer = generate_answer(query, documents)

    return {
        "response": answer,
        "sources": metadata
    }



