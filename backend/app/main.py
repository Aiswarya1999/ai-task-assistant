from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import fitz  # PyMuPDF

from .database import engine, init_db, get_db
from .models import Base, Task, DocumentChunk, User
from .schemas import TaskCreate
from .services.pii_service import scrubber
from .services.ai_service import (
    generate_task_summary, 
    get_embedding, 
    get_answer_from_context
)

# 1. Define Metadata for the UI groups
tags_metadata = [
    {"name": "Security", "description": "PII Scrubbing & System Health"},
    {"name": "Tasks", "description": "AI-Powered Task Management"},
    {"name": "Documents", "description": "RAG-based PDF Intelligence"},
]

# 2. Initialize App with Clean UI settings
app = FastAPI(
    title="Secure AI Assistant",
    description="Enterprise-grade PII-Scrubbing & Document Intelligence System",
    version="1.0.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # Hides the 'Schemas' section
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from .database import SessionLocal
    init_db()
    db = SessionLocal()
    if not db.query(User).filter(User.id == 1).first():
        dummy_user = User(id=1, email="test@example.com", hashed_password="fake")
        db.add(dummy_user)
        db.commit()
    db.close()

# --- ROUTES WITH TAGS ---

@app.get("/", include_in_schema=False) # Hides the root from Swagger entirely
async def root():
    return {"message": "Backend Live"}

@app.get("/test-pii", tags=["Security"], summary="1. Privacy Check (PII Scrubber)", description="Test how the system automatically removes sensitive data like names, emails, and phone numbers.")
async def test_pii(text: str):
    clean_text = scrubber.clean_text(text)
    return {"original": text, "scrubbed": clean_text}

@app.post("/tasks/auto", tags=["Tasks"], summary="2. Create Task via AI", description="Enter a messy note; the AI will scrub it for privacy and generate a professional task title automatically.")
def create_smart_task(note: str = Body(..., embed=True), db: Session = Depends(get_db)):
    clean_note = scrubber.clean_text(note)
    ai_title = generate_task_summary(clean_note)
    new_task = Task(title=ai_title, description=clean_note, user_id=1)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.post("/documents/upload", tags=["Documents"], summary="3. Upload & Index Document (PDF)",
          description="Upload a PDF. The system will read it, scrub private info, and 'learn' the content for future questions.")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    pdf_doc = fitz.open(stream=content, filetype="pdf")
    raw_text = "".join([page.get_text() for page in pdf_doc])
    clean_text = scrubber.clean_text(raw_text)
    vector = get_embedding(clean_text)

    if not vector:
        raise HTTPException(status_code=500, detail="AI Embedding failed.")

    new_doc = DocumentChunk(content=clean_text, embedding=vector, user_id=1)
    db.add(new_doc)
    db.commit()
    return {"status": "Success", "filename": file.filename}

@app.post("/chat", tags=["Documents"], summary="4. Chat with your Knowledge Base",
          description="Ask questions about your uploaded documents. The AI uses 'Retrieved Context' to give accurate, private answers.")
def chat_with_docs(question: str = Body(..., embed=True), db: Session = Depends(get_db)):
    question_vector = get_embedding(question)
    if not question_vector:
        raise HTTPException(status_code=500, detail="Vectorization failed.")
    
    results = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(question_vector)
    ).limit(3).all()
    
    if not results:
        return {"answer": "No documents found."}

    answer = get_answer_from_context(question, results)
    return {"answer": answer}