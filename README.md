# ⚡ FormFill AI — Autonomous Form Filling Web Platform & FastAPI Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-45BA4B?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Sentence-Transformers](https://img.shields.io/badge/Sentence--Transformers-MiniLM--L6-FF6F00?style=for-the-badge)](https://www.sbert.net/)
[![License](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)](LICENSE)

An end-to-end **Web Application Platform & FastAPI Backend System** that automatically ingests candidate documents (Resumes, Marksheets, Certificates), extracts canonical profile facts, semantically matches form fields using deep learning embeddings, and executes automated form filling on **Live Google Forms**, **Web Forms**, and **PDF Application Documents** via Playwright headless browser automation.

---

## 🚀 Key Features

* **⚡ Live Form Auto-Fill Sandbox**: Input any live Google Form or web link, trigger Playwright automated browser filling, view real-time field match matrices, and preview live browser screenshots.
* **👤 Extracted AI Profile Vault**: Ingests resumes/marksheets (PDF, DOCX, TXT) and stores canonical facts (Name, Email, Phone, DOB, Education, Experience, Skills) with confidence scores.
* **📄 Static PDF Form Filler**: Overlays extracted profile entities onto static PDF application forms and generates downloadable filled PDF documents.
* **🛠️ Modular Model & API Hub**: Built-in REST API endpoints with clear hooks for deep learning / NER model teammates to plug in custom trained weights (`core/extractor.py` & `POST /api/match-fields`).
* **🎨 Classy Glassmorphic Dashboard**: SaaS-grade web interface mounted at root `/` (`index.html`, `style.css`, `app.js`).

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────────────────────────────────────┐
                                  │            Web Application Platform UI                   │
                                  │   (index.html | style.css | app.js - Glassmorphism UI)   │
                                  └────────────────────────────┬─────────────────────────────┘
                                                               │ HTTP REST API
                                                               ▼
                                  ┌──────────────────────────────────────────────────────────┐
                                  │                   FastAPI Backend Core                   │
                                  │                (main.py / backend/app.py)                │
                                  └──────────────┬──────────────────────────┬────────────────┘
                                                 │                          │
                        ┌────────────────────────┴───┐          ┌───────────┴────────────────────────┐
                        │   Playwright Form Engine   │          │   ML/DL Matcher & Entity Engine    │
                        │      (core/browser.py)     │          │        (core/extractor.py)         │
                        └────────────────────────────┘          └────────────────────────────────────┘
```

---

## 🛠️ Teammate Integration Guide (Deep Learning / NER)

This codebase provides clean, decoupled hooks for team members developing custom NER or deep learning field matching models:

1. **Document Entity Extraction**:
   Modify `extract_structured_profile()` in [`core/extractor.py`](file:///c:/Users/John/OneDrive/Documents/Desktop/dl%20project/core/extractor.py) to load custom spaCy, HuggingFace, or PyTorch NER model weights.

2. **Semantic Field Matcher API**:
   The endpoint `POST /api/match-fields` accepts raw form questions and invokes [`core/field_matcher.py`](file:///c:/Users/John/OneDrive/Documents/Desktop/dl%20project/core/field_matcher.py), which uses cosine similarity over `sentence-transformers/all-MiniLM-L6-v2`.

---

## 💻 Quick Start & Running Locally

### Option A: One-Click Execution (Windows)
Double-click the **`run.bat`** file in the project root folder.

### Option B: Command Line

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Start Server**:
   ```bash
   python main.py
   ```

3. **Access in Web Browser**:
   * **Web Application UI**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
   * **Interactive API Documentation (Swagger)**: [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

---

## 📡 REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/upload-document` | Ingests PDF/DOCX/TXT resume or marksheet and saves extracted entities to DB |
| `GET` | `/api/profile` | Returns all canonical user facts stored in the Profile Vault |
| `POST` | `/api/match-fields` | Matches detected form questions against canonical facts using cosine similarity |
| `POST` | `/api/fill-form` | Triggers Playwright engine to fill live Google Forms and returns browser screenshot preview |
| `POST` | `/api/fill-and-export-pdf` | Overlays extracted profile facts onto static PDF application forms and exports filled PDF |

---

## 📂 Repository Structure

```text
├── automation/
│   ├── playwright_filler.py    # Playwright browser form filling engine
│   └── pdf_filler.py           # PyPDF form overlay & exporter
├── backend/
│   ├── app.py                  # FastAPI application routes
│   ├── database.py             # SQLite database connection & session
│   ├── models.py               # SQLAlchemy ORM models
│   └── schemas.py              # Pydantic request/response schemas
├── core/
│   ├── extractor.py            # Document text parsing & entity extractor (Teammate hook)
│   ├── field_matcher.py        # Sentence-Transformers semantic field matcher
│   └── ingestion.py            # PDF/DOCX file text ingestion
├── index.html                  # Web platform HTML layout
├── style.css                   # Glassmorphic dark cyber design system
├── app.js                      # Web platform JS dynamic DOM & API interactions
├── main.py                     # Entry point server script (uvicorn)
├── run.bat                     # One-click Windows launcher
└── requirements.txt            # Python dependencies
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
