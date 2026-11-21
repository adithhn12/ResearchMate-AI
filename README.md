# ResearchMate AI — AI-Powered Literature Review & Research Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6600?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

An end-to-end, full-stack academic research platform that empowers students, researchers, and scientists to ingest multiple peer-reviewed papers, interact with them using grounded multi-document Retrieval Augmented Generation (RAG), compare research methodologies, analyze literature gaps, and generate publication-ready structured literature reviews with Word (.docx) and PDF export.

---

## 🌟 Key Features

### 1. 📊 Research Dashboard & Intelligence
- Metrics on total papers, projects, AI inquiries, comparisons, and literature reviews.
- **Recharts Data Visualizations**:
  - Publication year distribution bar chart.
  - Document ingestion and vector indexing status breakdown (Indexed, Processing, Failed).
- Interactive research activity stream and recent uploads list with status badges.

### 2. 📚 Research Paper Library
- Multi-file PDF upload with automated text extraction, chunking, and embedding indexing.
- Automatic bibliographic metadata extraction: Title, Authors, Abstract, Publication Year, and Keywords.
- Search and filter by publication year, keywords, and processing status.
- Detailed modal view for inspecting full abstract, chunk count, and metadata.
- Multi-project organization with per-project isolation.

### 3. 🤖 AI Research Assistant (Multi-Doc RAG)
- **Traditional RAG Pipeline**:
  `PDF Upload → Text Extraction (PyMuPDF) → Chunking (Sliding Window) → Embeddings (all-MiniLM-L6-v2) → ChromaDB → Similarity Retrieval → Gemini Synthesis`
- Conversation threads with persistent message history.
- Grounded citations: every claim explicitly references `[Paper Title, p. X]`.
- Clickable citation cards: click any citation to view the exact retrieved textual snippet from the paper.
- Target inquiry scope: search across all papers in a project or filter to specific papers.

### 4. ⚖️ Research Paper Comparison Matrix
- Select 2 or more research papers to cross-evaluate in an aligned matrix table.
- Multi-dimensional comparison across 9 academic axes:
  1. Research Objectives
  2. Methodologies & Frameworks
  3. Algorithms & Models
  4. Datasets & Benchmarks
  5. Evaluation Metrics
  6. Results & Empirical Findings
  7. Strengths & Novelty
  8. Limitations & Constraints
  9. Future Research Directions
- Executive comparative synthesis summarizing trade-offs and domain impact.
- Persistent comparison history with reload and delete options.

### 5. 🔍 Research Gap & Limitation Analyzer
- Deep extraction of explicit constraints stated by authors across the corpus.
- Cross-paper recurring academic challenges identification.
- AI-inferred unexplored opportunities and methodological blind spots.
- Actionable future research proposals with supporting papers and page references.
- Filter between *Explicit Author Limitations* and *AI Inferred Research Gaps*.

### 6. 📝 Automated Literature Review Generator & Export
- Automated 8-section academic review synthesis:
  1. Introduction
  2. Background and Related Work
  3. Thematic Literature Analysis
  4. Comparison of Existing Approaches
  5. Research Limitations
  6. Research Gaps & Open Problems
  7. Conclusion & Future Outlook
  8. Formatted References (APA Style)
- In-place editing: edit any section directly in the browser and save updates.
- **Export Capabilities**:
  - **DOCX**: Formatted Microsoft Word document (`python-docx`).
  - **PDF**: Publication-ready styled PDF document (`ReportLab`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic |
| **PDF Processing** | PyMuPDF (fitz) |
| **Embeddings** | HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`) via ChromaDB ONNX |
| **Vector Database** | ChromaDB (Persistent directory storage) |
| **LLM & Reasoning**| Google Gemini API (`gemini-flash-lite-latest`, `gemini-3.8-flash`) |
| **Database** | SQLite + SQLAlchemy |
| **Document Export**| `python-docx` (Word) and `ReportLab` (PDF) |
| **Authentication** | JWT (PyJWT) + Salted PBKDF2 Password Hashing |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Environment Configuration
The backend loads configuration from `.env` in the project root:
```ini
# Gemini API Key (keep private)
GEMINI_API_KEY=your_gemini_api_key

# Model (Default: gemini-flash-lite-latest, with automatic fallbacks)
GEMINI_MODEL=gemini-flash-lite-latest

# Application Security
SECRET_KEY=researchmate-ai-super-secret-key-2026
```

### 3. Backend Setup & Startup
```powershell
# Navigate to backend
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API docs will be live at: `http://localhost:8000/docs`

### 4. Frontend Setup & Startup
In a separate terminal:
```powershell
# Navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```
The React frontend will be live at: `http://localhost:5173`

---

## 🧪 Testing

### Run Automated Unit & Integration Tests
```powershell
cd backend
python -m pytest tests -v
```

### Run End-to-End Verification Pipeline
```powershell
python verify_e2e.py
```
This tests:
- User authentication & project creation.
- Multi-paper PDF ingestion and PyMuPDF text parsing.
- `all-MiniLM-L6-v2` embedding generation & ChromaDB vector indexing.
- Multi-document RAG retrieval with citation verification.
- Cross-paper comparison table generation.
- Research gap extraction with limitation distinction.
- 8-section literature review generation.
- Real DOCX & PDF file generation and binary streaming.

---

## 🌐 Production Deployment Guide

ResearchMate AI is architected for seamless production deployment with a decoupled frontend and backend:

### Architecture
- **Frontend**: Deployed on **Vercel** as a high-performance Single Page Application (SPA).
- **Backend**: Deployed on **Render** (or Railway/AWS) as a containerized FastAPI service.
- **Persistent Data & Vectors**: Hosted on a **Render Persistent Disk** mounted at `/var/data` ensuring SQLite data, ChromaDB vector embeddings, and uploaded PDFs survive redeployments, restarts, and instance reboots.

---

### A. Deploy Backend to Render

1. **Connect Repository**:
   - Push your repository to GitHub or GitLab.
   - Go to the [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Blueprint** (or **Web Service**).
   - If using Render Blueprint, Render automatically detects `render.yaml`.

2. **Manual Web Service Configuration** (if not using blueprint):
   - **Environment**: `Python`
   - **Root Directory**: Leave blank (repository root)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter or higher (required for persistent disk).

3. **Attach Persistent Storage (Critical)**:
   - In your Render Web Service settings, navigate to **Disks** → **Add Disk**.
   - **Name**: `researchmate-storage`
   - **Mount Path**: `/var/data`
   - **Size**: 10 GB or higher.
   - *This ensures your SQLite database (`/var/data/researchmate.db`), ChromaDB collections (`/var/data/chroma_data`), and uploaded PDFs (`/var/data/uploaded_papers`) remain fully persistent across restarts and redeployments!*

4. **Set Environment Variables on Render**:
   | Variable | Value / Description |
   |---|---|
   | `GEMINI_API_KEY` | Your Google Gemini API Key from Google AI Studio |
   | `GEMINI_MODEL` | `gemini-flash-lite-latest` (or `gemini-3.8-flash`) |
   | `DATA_DIR` | `/var/data` |
   | `SECRET_KEY` | Generate a strong random string (e.g. `openssl rand -hex 32`) |
   | `CORS_ORIGINS` | Your Vercel frontend domain (e.g. `https://researchmate-ai.vercel.app,http://localhost:5173`) or `*` |
   | `PYTHON_VERSION`| `3.12.0` |

---

### B. Deploy Frontend to Vercel

1. **Import Project into Vercel**:
   - Go to [Vercel](https://vercel.com/) and click **Add New** → **Project**.
   - Select your GitHub repository.
   - Set **Root Directory** to `frontend`.
   - Vercel automatically detects the **Vite** framework preset.

2. **Configure Environment Variables on Vercel**:
   | Variable | Value |
   |---|---|
   | `VITE_API_URL` | Your Render Backend URL (e.g. `https://researchmate-api.onrender.com`) |

3. **SPA Routing**:
   - The included `frontend/vercel.json` automatically handles SPA rewrites so that page reloads on deep links (e.g. `/assistant`, `/library`) resolve properly to `index.html`.

4. **Deploy**:
   - Click **Deploy**. Vercel will build and launch your responsive academic SaaS interface!

---

## 📁 Project Architecture

```
ResearchMate AI/
├── .env                       # Existing Gemini API key & secrets
├── .env.example               # Template environment configuration
├── .gitignore                 # Standard git ignore definitions
├── README.md                  # Complete documentation
├── create_sample_papers.py    # Generates realistic sample research papers
├── verify_e2e.py              # Full end-to-end integration test runner
├── sample_papers/             # Generated academic PDFs for testing
│   ├── multi_doc_rag_synthesis.pdf
│   ├── lightweight_embeddings_evaluation.pdf
│   └── multiagent_literature_review.pdf
│
├── backend/                   # Python FastAPI Backend
│   ├── requirements.txt       # Python dependencies
│   ├── tests/                 # Automated test suite
│   │   ├── test_document_processing.py
│   │   ├── test_vector_and_rag.py
│   │   └── test_api.py
│   └── app/
│       ├── __init__.py
│       ├── main.py            # FastAPI entrypoint, CORS, routes
│       ├── config.py          # Environment settings & directories
│       ├── database.py        # SQLAlchemy engine and session
│       ├── models.py          # SQLAlchemy ORM models
│       ├── schemas.py         # Pydantic schemas
│       ├── auth.py            # JWT authentication & PBKDF2 hashing
│       ├── services/
│       │   ├── pdf_service.py      # PyMuPDF extraction, chunking, metadata
│       │   ├── vector_store.py     # ChromaDB & all-MiniLM-L6-v2 indexing
│       │   ├── gemini_service.py   # Grounded RAG, comparisons, gap analyzer, reviews
│       │   └── export_service.py   # python-docx and reportlab generators
│       └── routers/
│           ├── auth.py             # Login, register, demo login, user info
│           ├── projects.py         # Project management
│           ├── papers.py           # Upload, list, search, filter, delete papers
│           ├── chat.py             # Grounded RAG chat sessions & citations
│           ├── compare.py          # Methodology comparison matrix
│           ├── research_gaps.py    # Limitations & research gap extraction
│           ├── literature_reviews.py # 8-section review generation & export
│           └── analytics.py        # Dashboard metrics & chart distributions
│
└── frontend/                  # React + Vite Frontend
    ├── package.json           # Dependencies: react, tailwind, recharts, lucide
    ├── vite.config.js         # Vite proxy setup to backend (:8000)
    ├── tailwind.config.js     # Academic navy & subtle blue design palette
    └── src/
        ├── api/client.js      # Axios client with JWT interceptor & API endpoints
        ├── contexts/
        │   ├── AuthContext.jsx     # Authentication state & demo access
        │   ├── ProjectContext.jsx  # Active project selection & management
        │   └── ThemeContext.jsx    # Dark/light theme toggle
        ├── components/
        │   ├── Sidebar.jsx         # Persistent navigation & project selector
        │   ├── Navbar.jsx          # Top header & quick actions
        │   ├── Modal.jsx           # Reusable academic dialog
        │   └── UploadModal.jsx     # Multi-file PDF drag-and-drop uploader
        ├── pages/
        │   ├── Dashboard.jsx       # Analytics, Recharts, recent uploads & timeline
        │   ├── Library.jsx         # Paper cards, search, filter, metadata drawer
        │   ├── Assistant.jsx       # Multi-doc RAG chat with clickable citations
        │   ├── Comparison.jsx      # 9-dimension structured comparison matrix
        │   ├── GapAnalyzer.jsx     # Explicit limitations vs AI inferred gaps
        │   ├── LiteratureReview.jsx# 8-section editor, DOCX/PDF export
        │   └── Auth.jsx            # Modern login/registration & instant demo access
        ├── App.jsx            # Root application layout
        └── index.css          # Tailwind directives & styles
```
