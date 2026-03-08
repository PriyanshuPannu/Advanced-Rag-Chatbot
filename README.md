🤖ARPA — AI Research Paper Assistant

Retrieval-Augmented Generation (RAG) chatbot that answers questions about AI research papers stored locally as PDFs.

ARPA retrieves relevant research paper sections using hybrid search, then generates grounded answers using a local LLM via Ollama.

The project includes a Streamlit interface, persistent chat history, and LLM-as-a-Judge evaluation to measure RAG performance.

Features:
```
Chat with AI research papers
Hybrid retrieval (Dense + BM25)
Cross-encoder reranking for improved search quality
ChromaDB vector database
Local LLM inference using Ollama (phi3)
Streamlit UI with conversation history
Delete chat functionality
Source citation with PDF page numbers
LLM-as-a-Judge evaluation pipeline
```

##Screenshots##

Query Response:

<br>
<img width="1919" height="969" alt="query-response" src="https://github.com/user-attachments/assets/6d89508e-d9c2-4447-9067-df1c0adee255" />

<br>
<br>

Conversation history:

<br>
<img width="1916" height="968" alt="Convo-history" src="https://github.com/user-attachments/assets/9e9b625a-80de-4f83-a23b-db9868f03185" />



Architecture:
```
User Question
      │
      ▼
Streamlit UI
      │
      ▼
FastAPI Backend
      │
      ▼
Retriever
 ├── Dense Search (ChromaDB + BGE Embeddings)
 ├── Sparse Search (BM25)
 └── Cross-Encoder Reranking
      │
      ▼
Top Relevant Context Chunks
      │
      ▼
Ollama LLM (phi3)
      │
      ▼
Generated Answer
      │
      ▼
Displayed in Streamlit UI
```
Evaluation Pipeline:
```
Question
   │
   ▼
Retriever
   │
   ▼
Context
   │
   ▼
Generator LLM (phi3)
   │
   ▼
Answer
   │
   ▼
Judge LLM (qwen2)
   │
   ▼
Evaluation Scores
```
Metrics:
```
Faithfulness

Answer Relevance

Context Relevance
```

Tech Stack:
```
Backend:
FastAPI,
Uvicorn

Retrieval:
ChromaDB
Sentence Transformers
BGE Embeddings (bge-small-en-v1.5)
BM25 (rank-bm25)
Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)

LLM:
Ollama
Phi-3

Frontend:
Streamlit

Evaluation:
LLM-as-a-Judge (local model via Ollama)
```

Installation:
```
Clone the repository
git clone https://github.com/yourusername/rag_chatbot.git
cd rag_chatbot
```
Create virtual environment
```
python -m venv .venv
```
Activate:
```
Windows

.venv\Scripts\activate
```
Mac / Linux
```
source .venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Run Ollama:
```
Install Ollama and pull the model:
```
```
ollama pull phi3
Run the Application
```
Start backend:
```
uvicorn main:app --reload
```
Start Streamlit UI:
```
streamlit run ui.py
```
Run Evaluation:
```
python -m app.llm_judge_eval
```
Example output:
```
Faithfulness: 0.92
Answer Relevance: 0.91
Context Relevance: 0.93
```
With small datasets, averages can look very high and small models like qwen2:1.5b tend to score generously.

Future Improvements:
```
Streaming responses

Better chunking strategies

Multi-document indexing

Docker deployment
```
