# Secure AI Task & Document Assistant (RAG Backend)

A containerized, privacy-first backend architecture engineered with **FastAPI** and **PostgreSQL (`pgvector`)** to manage corporate workflows and securely query unstructured PDF documentation using **Retrieval-Augmented Generation (RAG)**. 

This system implements strict **"Privacy-by-Design"** principles, dynamically sanitizing Personally Identifiable Information (PII) using natural language processing (NLP) before database storage or third-party Large Language Model (LLM) processing, ensuring architectural alignment with data compliance frameworks like **GDPR**.

---

## 🛡️ Core Architecture & Security Features

- **Privacy-by-Design Ingestion Layer:** Uses **Microsoft Presidio** alongside specialized **SpaCy NLP** pipelines to identify, flag, and redact sensitive user information (names, emails, locations, and financial metadata) dynamically at runtime.
- **Model-Agnostic Abstraction:** Engineered with an interchangeable API routing structure capable of instantly switching the underlying LLM provider (e.g., from OpenAI to **Google Gemini 1.5 / Embedding-2**) via an OpenAI-compatible gateway to prevent vendor lock-in and enhance system availability.
- **High-Dimensional Vector Indexes:** Integrates a PostgreSQL instance equipped with the **`pgvector`** extension to handle text chunk vectorization, indexing, and low-latency semantic proximity matching using **Cosine Distance** formulas.
- **Containerized DevSecOps Lifecycle:** Orchestrated from scratch with **Docker & Docker Compose**, fully decoupling application environments from persistent database stores for reproducible and isolated production deployments.
- **Enterprise API Storefront:** Features a custom-tailored, security-hardened FastAPI Swagger UI mapping distinct corporate boundaries (*Security, Tasks, Documents*) using semantic route summaries and obfuscating default underlying JSON database schemas.

---

## 🔄 End-to-End Data Pipeline

1. **Document Ingress:** Raw text strings are extracted from file streams (e.g., PDFs via `PyMuPDF`).
2. **PII Sanitization:** The data stream passes through the custom `PIIScrubber` engine where sensitive tokens are overwritten with semantic fallback placeholders (e.g., `[REDACTED_PERSON]`).
3. **Vector Vectorization:** The anonymized text block is compiled into high-dimensional embeddings ($768$ or $1536$ elements depending on model mapping).
4. **pgvector Storage:** Redacted context blocks and vector arrays are stored together inside the PostgreSQL layer using explicit database bounds.
5. **Contextual Synthesis (RAG):** User queries run semantic lookups across the vector table $\rightarrow$ the top 3 high-affinity context blocks are retrieved $\rightarrow$ the target LLM synthesizes an contextual response strictly isolated from unredacted source PII data.

---

## 🛠️ Technological Specifications

- **Language Runtime:** Python 3.11+
- **Framework Ecosystem:** FastAPI, SQLAlchemy ORM, Pydantic v2
- **Persistent Storage:** PostgreSQL 17 + `pgvector`
- **NLP & Data Parsing:** Microsoft Presidio, SpaCy (`en_core_web_lg`), PyMuPDF (`fitz`)
- **Virtualization Infrastructure:** Docker & Docker Compose

---

## 🚀 Step-by-Step Installation & Deployment

### 1. Clone the Project
```bash
git clone [https://github.com/Aiswarya1999/ai-task-assistant.git](https://github.com/Aiswarya1999/ai-task-assistant.git)
cd ai-task-assistant
