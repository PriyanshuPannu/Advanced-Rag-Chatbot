import os
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from typing import List, Dict
from chromadb.api.types import Metadata
from typing import List

# Persistent Chroma DB
import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(name="research_papers")

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)


def ingest_all_pdfs(data_folder="data"):
    for filename in os.listdir(data_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_folder, filename)
            print(f"Ingesting: {filename}")

            loader = PyMuPDFLoader(file_path)
            documents = loader.load()

            full_text = "\n".join([doc.page_content for doc in documents])
            chunks = chunk_text(full_text)

            embeddings = embedding_model.encode(chunks).tolist()

            ids = [str(uuid.uuid4()) for _ in chunks]

            metadata: List[Metadata] = [{"source": str(filename)} for _ in chunks]

            collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadata
            )

    print("✅ All PDFs ingested successfully.")


if __name__ == "__main__":
    ingest_all_pdfs()