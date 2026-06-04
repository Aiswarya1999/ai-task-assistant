# 🛡️ Secure AI Task Assistant

A zero-trust, full-stack application engineered to intercept, identify, and scrub localized Personally Identifiable Information (PII) before routing sanitized payloads to third-party Large Language Model (LLM) APIs. Built for secure enterprise task creation and smart scheduling automation without data leakage.

## 🚀 Key Features

* **Zero-Trust PII Interception Layer**: Uses high-performance regular expressions inside the local runtime environment to strip names, emails, and phone numbers (`<PERSON>`, `<EMAIL>`, `<PHONE_NUMBER>`) before data crosses any network boundaries.
* **Lightweight Asynchronous API**: Powered by FastAPI, featuring fully decoupled schema evaluation, relational database persistence, and cross-origin resource sharing (CORS).
* **Dockerized Sandbox Architecture**: Containerized database management and server isolation via Docker Compose to ensure local configuration stability and fast deployments.
* **Proactive Security Strategy**: Includes a complete architectural STRIDE Threat Model evaluating application attack surfaces and boundaries.

---

## 🛠️ Tech Stack

* **Frontend Dashboard**: Streamlit (Python)
* **Backend Framework**: FastAPI (Python)
* **Database Engine**: PostgreSQL (SQLAlchemy ORM)
* **AI Orchestration**: Direct Google Gemini REST API Integration

---

## 🏁 Quick Start & Deployment

### 1. Configure Local Environment Settings
Create a `.env` file inside your `backend/` directory to store your credentials securely:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=postgresql://user:password@db:5432/assistant_db
