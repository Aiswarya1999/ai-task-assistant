# 🗺️ Application Threat Model - STRIDE : Secure AI Task Assistant

## 🎯 1. System Scope & Boundaries

Defining the operational boundaries ensures a focused evaluation of attack surfaces and outlines the precise limits of security control ownership.

### A. In-Scope Components
The security posture of the following locally containerized microservices is entirely managed within this deployment framework:
* **Streamlit Frontend Dashboard**: The user interface layer executing local session logic and initiating network requests to the backend API.
* **FastAPI Backend Pipeline**: The core application logic layer hosting the custom deterministic Regex PII Scrubbing engine and API route handlers.
* **PostgreSQL Database Storage**: The relational persistence layer tracking user task records, timestamps, and localized metadata.
* **Internal Network Loops**: Inter-container communication isolated via custom Docker network bridges.

### B. Out-of-Scope Components
The following external dependencies are functionally required but fall outside the direct security control boundary of this application:
* **External LLM Cloud Infrastructure**: The remote Google Gemini REST API endpoints responsible for text processing. Security here relies entirely on upstream TLS channels and vendor compliance.
* **Host Operating System Security**: The physical host machine's kernel security, local network firewalls, and Docker daemon runtime configurations.
* **Client-Side Browsers**: Endpoint vulnerabilities, browser extension injections, or local cross-site scripting (XSS) executions on the user's machine.

### C. Data Assets & Classification
| Data Asset | Classification | Handling Rules |
| :--- | :--- | :--- |
| **Raw User Input Note** | **Confidential / PII** | Must *never* persist to disk or cross the internal trust boundary in plain text. |
| **Sanitized Task Description** | **Internal** | Permitted to persist in local PostgreSQL and transit securely across outbound HTTPS. |
| **Gemini API Key** | **Secret** | Must be confined strictly to host environment variables; completely blocked from version control. |

---

## 📊 Data Flow Diagram (DFD)

The diagram below maps the journey of a task note through our internal infrastructure layers and across the network trust boundary.

```mermaid
graph TD
    %% Define Nodes
    UserApp["👤 User Browser / Client UI"]
    Frontend["🎨 Streamlit Frontend<br>(Container)"]
    Backend["⚙️ FastAPI Backend<br>(Container)"]
    Scrubber["🛡️ Regex PII Filter Layer<br>(In-Memory Processing)"]
    Database[("💾 PostgreSQL DB<br>(Container)")]
    GeminiAPI["🤖 External Gemini API<br>(Cloud Infrastructure)"]

    %% Data Flow Connections
    UserApp -->|1. Input Messy Note| Frontend
    Frontend -->|2. POST Request /tasks/auto| Backend
    
    subgraph Local_Docker_Environment [Internal Trust Boundary]
        Backend -->|3. Evaluate Plaintext| Scrubber
        Scrubber -->|4. Return Tokenized String| Backend
        Backend -->|5. SQL INSERT Sanitized Data| Database
    end

    Backend == 6. HTTPS Outbound TLS ==> GeminiAPI
    GeminiAPI -.->|7. Generate Title Payload| Backend
    Backend -->|8. Render Secured Task| UserApp

    %% Styling and Themes
    style Local_Docker_Environment fill:#111625,stroke:#3870FF,stroke-width:2px,stroke-dasharray: 5 5
    style Scrubber fill:#1b3a24,stroke:#4CAF50,stroke-width:2px
    style GeminiAPI fill:#2d1a4d,stroke:#9C27B0,stroke-width:1px
    style Database fill:#1c2d3d,stroke:#00BCD4,stroke-width:1px

## 🛑 3. Threat Enumeration (STRIDE Matrix)

We systematically analyze each element of the application against the six STRIDE threat categories to expose architectural vulnerabilities and document their corresponding security controls.

### A. Spoofing (Identity Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T1.1** | An attacker spoof-impersonates a valid user session or bypasses local client routing to hit backend infrastructure. | Unauthorized data injection into database entities. | FastAPI Backend | **Low Risk / Acceptable**: System runs in an isolated local container network loop. Frontend-to-backend calls map directly over specified host endpoints. |

### B. Tampering (Data Integrity Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T2.1** | Adversary executes a Man-in-the-Middle (MitM) attack to alter plaintext strings on their way to the external LLM processor. | Manipulation of target metrics or poisoned model outputs returned to client UI. | Outbound Network Boundary | **Mitigated**: Outbound API transit requests are strongly bound to secure, encrypted TLS standard pathways (`HTTPS`). |
| **T2.2** | An unauthorized local process gains write access to the PostgreSQL data volume on the host. | Corrupt task definitions, structural database integrity failure. | PostgreSQL Volume | **Mitigated**: PostgreSQL data directories are explicitly managed via root-restricted Docker-managed storage volumes (`postgres_data`). |

### C. Repudiation (Audit Trail Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T3.1** | A user claims a highly sensitive action item or task reminder was generated maliciously by the system rather than by them. | Inability to track accountability or trace operational system history. | Relational Database | **Mitigated**: The database scheme automatically couples every newly indexed row with system-generated timestamps (`created_at`) and links back to explicit user keys. |

### D. Information Disclosure (Confidentiality Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T4.1** | **CRITICAL ARCHITECTURAL RISK**: Plaintext notes containing corporate email, keys, or phone sequences leak to multi-tenant third-party AI models. | Compliance breaches (GDPR, CCPA), enterprise intellectual property leaks. | Outbound Request Body | **Mitigated**: **Primary Core Control**. The custom `PIIScrubber` runtime completely runs *in-memory* inside the local trust boundary, parsing and stripping names/phones/emails *before* the JSON payload is constructed for network transit. |
| **T4.2** | Application error stack traces throw raw sensitive strings into public console logging systems during a pipeline failure. | Exposure of environmental data details to container log-watchers. | FastAPI Error Handlers | **Mitigated**: Explicit application endpoint logic wraps processes inside strict `try/except` code containment wrappers to handle and obscure lower-level diagnostic exceptions. |

### E. Denial of Service (Availability Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T5.1** | A script rapidly floods the `/tasks/auto` route with massive text requests, causing CPU exhaustion. | Memory pool failures or application crashes for legitimate users. | Uvicorn Server Runtime | **Mitigated**: Stripping out massive machine learning libraries like SpaCy and native model binaries minimizes memory usage, ensuring high base operational speed. *(See Security Roadmap for upcoming rate-limiting implementations).* |

### F. Elevation of Privilege (Authorization Threats)
| ID | Threat Scenario | Impact | Targeted Component | Mitigation Status |
| :--- | :--- | :--- | :--- | :--- |
| **T6.1** | Public version control scanning tools discover hardcoded third-party API configurations or local data storage passwords. | Complete lateral environment compromise of target database records and API billing pools. | Git Version Control | **Mitigated**: Global environment secrets are separated entirely from the codebase, stored inside a dedicated local `.env` setup that is explicitly restricted via `.gitignore`. |

## 📊 4. Threat Prioritization & Risk Ranking

To effectively allocate engineering resources, threats are evaluated using a standard Risk Matrix calculated by cross-referencing **Impact Severity** with **Exploitation Probability**.

### A. Risk Evaluation Matrix
* **Critical/High**: Requires immediate architectural mitigation before deployment.
* **Medium**: Requires planned remediation within a standard development cycle.
* **Low**: Risk is identified, monitored, and accepted within current constraints.

### B. Prioritized Threat Registry

| Rank | Threat ID | Threat Category | Description | Impact | Probability | Overall Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **T4.1** | Information Disclosure | Plaintext PII leak to external multi-tenant cloud APIs. | Crucial | High | 🔴 **CRITICAL** |
| **2** | **T6.1** | Elevation of Privilege | Environmental API keys or DB secrets leaked via Git repository. | High | Medium | 🟠 **HIGH** |
| **3** | **T2.1** | Tampering | Man-in-the-Middle intercepting outbound API packets. | High | Low | 🟡 **MEDIUM** |
| **4** | **T5.1** | Denial of Service | API endpoint flooded with text payloads, crashing Uvicorn. | Medium | Medium | 🟡 **MEDIUM** |
| **5** | **T4.2** | Information Disclosure | Sensitive strings leaking into system console logs on crash. | Medium | Low | 🟢 **LOW** |
| **6** | **T2.2** | Tampering | Malicious local process accessing raw PostgreSQL storage volumes. | High | Very Low | 🟢 **LOW** |

---

## 🏁 5. Vulnerability Remediation Status & Verification

Based on the prioritization registry above, here is how the engineering architecture addresses each threat rank:

### 🟥 Priority 1: PII Leakage (T4.1) - RESOLVED
* **Remediation Action**: Built a zero-trust runtime handler using Python's native `re` module. It enforces string parsing and structure masking directly inside the server's local RAM buffer before compiling any external request bodies.
* **Verification**: Confirmed via Streamlit visualizer panel that strings containing structural target values like `8844775599` are perfectly substituted to `<PHONE_NUMBER>` locally.

### 🟧 Priority 2: Secret Exposure (T6.1) - RESOLVED
* **Remediation Action**: Decoupled database connection string properties and the `GEMINI_API_KEY` entirely from the code footprint. Isolated them into a standalone local `.env` configuration template.
* **Verification**: Confirmed that the global `.gitignore` tracking layer completely blocks `.env` from passing into staged version snapshots.

### 🟨 Priority 3 & 4: Transit Integrity & Resource Abuse (T2.1, T5.1) - PARTIALLY MITIGATED
* **Remediation Action**: Bound outbound REST traffic to encrypted TLS pipes (`HTTPS`). Dropping bloated NLP modules (SpaCy) minimized the container footprint, making the API process highly performant.
* **Remaining Action Item**: Implement a local API gateway limit handler (like `slowapi` or an Nginx container proxy) to drop incoming request bursts exceeding 60 calls per minute from a single IP signature.

## 🔄 6. Continuous Validation & Iteration Lifecycle

Security is a moving target. To ensure that our implemented mitigations remain effective over time and do not suffer from regression during future code changes, the system follows a continuous validation and iteration loop.

### A. Automated Validation Strategy
To validate that the `PIIScrubber` never fails to intercept confidential data strings, we implement automated unit test assertions within our local CI/CD pipeline environment.

```python
# test_security_pipeline.py
import pytest
from app.services.pii_service import scrubber

def test_pii_scrubbing_validation():
    # 1. Arrange a malicious/messy plaintext payload string
    malicious_input = "Call Alice immediately at 9876543210 or email secret@something.com"
    
    # 2. Act: Run the string through our local trust boundary filter
    sanitized_output = scrubber.clean_text(malicious_input)
    
    # 3. Assert: Verify that absolutely zero raw PII leaks into the final string
    assert "9876543210" not in sanitized_output
    assert "secret@something.com" not in sanitized_output
    assert "<PHONE_NUMBER>" in sanitized_output
    assert "<EMAIL>" in sanitized_output