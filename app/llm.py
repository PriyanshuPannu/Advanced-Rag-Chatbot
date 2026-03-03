import ollama


def generate_answer(query, context_chunks):
    if not context_chunks:
        return "No relevant context found in the papers."

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are an AI research assistant.

Answer the question using ONLY the context provided from research papers.
If the answer is not found in the context, say:
"The answer is not available in the provided papers."

Provide a clear and technical explanation.

Context:
{context}

Question:
{query}

Answer:
"""

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]