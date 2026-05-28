import os
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_task_summary(description: str):
    """Summarizes a note into a short title using Gemini."""
    try:
        prompt = f"Summarize this note into a 3-5 word task title. Return ONLY the title: {description}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Summary Error: {e}")
        return "New AI Task"

def get_embedding(text: str):
    print(f"DEBUG: Attempting Gemini embedding for: {text[:30]}...")
    try:
        # 2026 Standard: Use 'text-embedding-005' or 'gemini-embedding-001'
        # These models provide the best 768-dimension vectors
        result = genai.embed_content(
            model="models/text-embedding-005",
            content=text,
            task_type="retrieval_document"
        )
        print("DEBUG: Gemini Embedding successful!")
        return result['embeddings'][0]['values'] if 'embeddings' in result else result['embedding']
    except Exception as e:
        # CHECK YOUR DOCKER TERMINAL FOR THIS PRINT:
        print(f"DEBUG REAL ERROR: {e}") 
        
        # Fallback to the classic model if 005 is not yet in your region
        try:
            print("DEBUG: Trying fallback to embedding-001...")
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e2:
            print(f"DEBUG Critical Failure: {e2}")
            return None

def get_answer_from_context(question: str, context_chunks: list):
    """RAG: Answers a question using the retrieved database chunks."""
    context_text = "\n\n".join([chunk.content for chunk in context_chunks])
    
    prompt = f"""
    You are a secure assistant. Use the provided context to answer the question accurately.
    If the answer is not in the context, say 'I don't know based on the documents provided.'
    
    Context:
    {context_text}
    
    Question: {question}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"