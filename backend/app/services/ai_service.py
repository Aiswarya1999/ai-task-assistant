import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_task_summary(scrubbed_text: str) -> str:
    """Generates a concise task title via direct REST API call."""
    if not GEMINI_API_KEY:
        return "New AI Task (API Key Missing)"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"Generate a short, professional task title (maximum 6 words) for the following items. No quotes:\n\n{scrubbed_text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
    return "New AI Task"


def get_embedding(text: str):
    """Generates text vector embeddings via direct REST API call."""
    if not GEMINI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text}]},
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()["embedding"]["values"]
    except Exception as e:
        print(f"Embedding API Error: {e}")
    return None


def get_answer_from_context(question: str, context_chunks) -> str:
    """Asks Gemini to answer a question using retrieved context via direct REST API call."""
    if not GEMINI_API_KEY:
        return "AI Assistant offline."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    combined_context = "\n---\n".join([chunk.content for chunk in context_chunks])
    prompt = f"Context:\n{combined_context}\n\nQuestion: {question}\n\nAnswer:"

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"QA API Error: {e}")
    return "Error generating response."
