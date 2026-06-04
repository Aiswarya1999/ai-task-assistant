from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, init_db, get_db
from .models import Base, Task, User
from .services.pii_service import scrubber
from .services.ai_service import generate_task_summary

tags_metadata = [
    {"name": "Security", "description": "Local PII Scrubbing System"},
    {"name": "Tasks", "description": "AI-Powered Task Management"},
]

app = FastAPI(
    title="Secure AI Task Assistant",
    description="Enterprise-grade local PII-Scrubbing & Automated Task Creation Pipeline",
    version="1.0.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
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

@app.get("/", include_in_schema=False) 
async def root():
    return {"message": "Task Backend Operational"}

@app.get("/test-pii", tags=["Security"], summary="Preview Local PII Scrubber")
async def test_pii(text: str):
    clean_text = scrubber.clean_text(text)
    return {"original": text, "scrubbed": clean_text}

@app.post("/tasks/auto", tags=["Tasks"], summary="Create Sanitized Task via AI")
def create_smart_task(note: str = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        # Step 1: Clean text locally using regex patterns
        clean_note = scrubber.clean_text(note)
        
        # Step 2: Request professional title via direct REST API call
        ai_title = generate_task_summary(clean_note)
        
        # Step 3: Persist safely to PostgreSQL database
        new_task = Task(title=ai_title, description=clean_note, user_id=1)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        print(f"❌ Pipeline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))