import streamlit as st
import requests

st.title("📚 AI Research Paper Assistant (RAG)")

query = st.text_input("Ask a question about the research papers:")

if st.button("Submit"):
    if query:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            params={"query": query}
        )

        if response.status_code == 200:
            data = response.json()

            st.write("### 🧠 Answer")
            st.write(data["response"])

            st.write("### 📄 Sources")
            for src in data["sources"]:
                st.write(f"- {src}")
        else:
            st.error("API Error")




            