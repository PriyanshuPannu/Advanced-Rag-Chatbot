import os
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from chromadb.api.types import Metadata
from typing import List

# Persistent Chroma DB
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

            all_chunks = []
            all_metadata: List[Metadata] = []

            for doc in documents:

                page_text = doc.page_content
                page_number = doc.metadata.get("page", 0) + 1

                chunks = chunk_text(page_text)

                for i, chunk in enumerate(chunks):

                    all_chunks.append(chunk)

                    all_metadata.append({
                        "source": filename,        # pdf file name
                        "page": page_number,       # page number
                        "paragraph": i + 1         # paragraph/chunk number
                    })

            embeddings = embedding_model.encode(all_chunks).tolist()
            ids = [str(uuid.uuid4()) for _ in all_chunks]

            collection.add(
                documents=all_chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=all_metadata
            )

    print(" All PDFs ingested successfully.")


if __name__ == "__main__":
    ingest_all_pdfs()
