import json
import ollama

from app.retriever import retrieve
from app.llm import generate_answer


JUDGE_MODEL = "qwen2:1.5b"


questions = [
    "What is transformer architecture?",
    "What is self attention in transformers?",
    "What is BERT used for?",
    "What problem do transformers solve compared to RNNs?",
    "What is the purpose of positional encoding?"
]


def judge_llm(question, answer, context):

    prompt = f"""
You are evaluating a Retrieval Augmented Generation (RAG) system.

Score the following metrics from 0 to 1.

Metrics:
1. faithfulness — Is the answer supported by the context?
2. answer_relevance — Does the answer properly answer the question?
3. context_relevance — Is the retrieved context useful for the question?

Return ONLY valid JSON like this:
{{"faithfulness":0.8,"answer_relevance":0.9,"context_relevance":0.85}}

Question:
{question}

Context:
{context}

Answer:
{answer}
"""

    response = ollama.chat(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    result = response["message"]["content"].strip()

    return json.loads(result)


def run_evaluation():

    faith_scores = []
    answer_scores = []
    context_scores = []

    for q in questions:

        print("Evaluating:", q)

        docs, _ = retrieve(q)

        answer = generate_answer(q, docs)

        context = "\n\n".join(docs)

        scores = judge_llm(q, answer, context)

        faith_scores.append(scores["faithfulness"])
        answer_scores.append(scores["answer_relevance"])
        context_scores.append(scores["context_relevance"])

    print("\nFinal Scores")

    print("Faithfulness:", round(sum(faith_scores)/len(faith_scores), 3))
    print("Answer Relevance:", round(sum(answer_scores)/len(answer_scores), 3))
    print("Context Relevance:", round(sum(context_scores)/len(context_scores), 3))


if __name__ == "__main__":
    run_evaluation()