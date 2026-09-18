# ResumeAI

**An AI-powered resume and career assessment platform.**

ResumeAI has two connected experiences built on one analysis engine:

1. **Career Assessment (candidate-facing)** — a job seeker uploads their resume, describes the
   role they're targeting, completes a short communication & grammar challenge, and unlocks a
   full AI career report: ATS score, overall resume rating, role recommendations, skill-gap
   analysis and a prioritised improvement plan.
2. **Recruiter Screening (recruiter-facing)** — upload many resumes against one job and get a
   ranked, explainable candidate list. Available at `/recruiter`.

Every score traces back to something measurable in the resume text and the job description.
ResumeAI is a **decision-support tool** — it never makes a hiring decision, and all
recommendations are clearly labelled as AI-generated.

---

## The candidate flow

```
LANDING PAGE
   ↓
LOGIN / REGISTER
   ↓
WELCOME TRANSITION  (~1.8s, skipped under prefers-reduced-motion)
   ↓
RESUME UPLOAD + TARGET JOB DESCRIPTION
   ↓
"Analyze My Resume"  →  resume parsed, analysis computed and STORED (but locked)
   ↓
COMMUNICATION + GRAMMAR ASSESSMENT   (5 questions, feedback after each answer)
   ↓
COMMUNICATION SCORE CALCULATED
   ↓
CAREER REPORT REVEALED
   ├── ATS score (6 explained factors)
   ├── Overall resume rating (7 categories)
   ├── Job match score
   ├── Communication score
   ├── Strengths & weaknesses
   ├── Role recommendations
   ├── Skill gap analysis
   └── Improvement plan (with before/after from your own resume)
```

**The gate is enforced server-side, not just in the UI.** `GET /career/reports/{id}` returns
**403** until the assessment is complete, and the assessment endpoint never sends correct
answers or explanations to the client until an answer has been submitted — so the answers
can't be read from the network tab or React state.

---

## Features

- **Recruiter dashboard** — total candidates, processed resumes, shortlisted count, average match score, and processing status at a glance.
- **Resume parsing** — PDF, DOCX, and TXT. Extracts name, email, phone, location, education, work experience, years of experience, projects, certifications, and job titles. A malformed resume fails gracefully without affecting the rest of a batch.
- **Job description analysis** — extracts required skills, preferred skills, required experience, education requirement, keywords, and responsibilities from pasted JD text.
- **AI matching engine** — combines TF-IDF/cosine similarity, sentence-transformer semantic similarity (with automatic fallback to TF-IDF if the model can't load), skill matching, experience matching, education matching, and keyword matching into a configurable weighted 0–100 score.
- **Candidate ranking** — sortable, filterable ranking per job with match score, matching/missing skills, and a recommendation tier (Strong / Good / Potential / Low Match).
- **Explainable AI** — every analysis includes a strengths list, a gaps list, and a natural-language summary, so no score is a black box.
- **Candidate comparison** — select 2–3 candidates and compare them side by side.
- **Analytics** — score distribution, recommendation breakdown, top skills, and processing stats, per job.
- **Resume & job management** — full CRUD, re-analysis, download, and duplicate detection.
- **Dark/light mode**, responsive layout, loading/empty/error states, and toast notifications throughout.

---

## Architecture

```
resumeai/
├── backend/                 FastAPI application
│   ├── app/
│   │   ├── api/              Route handlers (auth, jobs, resumes, analysis)
│   │   ├── models/            SQLAlchemy ORM models
│   │   ├── schemas/           Pydantic request/response schemas
│   │   ├── services/          Orchestration: parsing pipeline, analysis pipeline
│   │   ├── ml/                 The actual AI: resume/JD parsers, skill extractor,
│   │   │                       skills taxonomy, and the matching engine
│   │   ├── utils/              Security, file handling, JSON helpers
│   │   ├── database/          SQLAlchemy session/engine
│   │   ├── config.py           Settings (env-driven)
│   │   └── main.py             App entrypoint, middleware, error handlers
│   ├── seed_demo_data.py       Seeds a demo recruiter, job, and 5 sample candidates
│   └── requirements.txt
│
└── frontend/                 React + Vite + Tailwind SPA
    └── src/
        ├── pages/              Dashboard, Jobs, Job detail, Resume library, Candidate detail, Auth
        ├── components/         Reusable UI: score ring, comparison table, analytics charts, etc.
        ├── context/            Auth + theme (dark/light) context
        └── services/api.js     Axios client
```

**Data flow:** a resume is uploaded once and stored independently of any job.
Analyzing a resume against a job creates a `ResumeAnalysis` row linking the two,
so the same resume can be scored against multiple jobs without re-uploading it.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Recharts, Axios |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| AI / ML | scikit-learn (TF-IDF, cosine similarity), sentence-transformers, regex-based NLP |
| Resume parsing | PyMuPDF (PDF), python-docx (DOCX) |
| Database | SQLite (dev) — PostgreSQL-ready via `DATABASE_URL` |
| Auth | JWT (python-jose) + bcrypt password hashing |
| Docs | FastAPI's built-in Swagger UI / OpenAPI |

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit SECRET_KEY before deploying anywhere real
```

**Environment variables** (`backend/.env`):

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret — **change this in production** | dev value |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./resumeai.db` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173,http://localhost:3000` |
| `MAX_FILE_SIZE_MB` | Max resume upload size | `10` |
| `USE_SEMANTIC_MODEL` | Enable sentence-transformers semantic scoring | `true` |
| `SEMANTIC_MODEL_NAME` | Hugging Face model name | `all-MiniLM-L6-v2` |
| `WEIGHT_SKILLS` / `WEIGHT_EXPERIENCE` / `WEIGHT_SEMANTIC` / `WEIGHT_EDUCATION` / `WEIGHT_KEYWORDS` | Default scoring weights (sum to 1.0) | `0.40 / 0.25 / 0.20 / 0.10 / 0.05` |

See `backend/.env.example` for the full list.

### Database setup

The database is created automatically on first run (SQLite file, or your configured
PostgreSQL database) — there's no separate migration step needed for a fresh install.
To point at PostgreSQL instead of SQLite, set:

```
DATABASE_URL=postgresql://user:password@host:5432/resumeai
```

and add `psycopg2-binary` to `requirements.txt`.

### Seed demo data (recommended for a first run)

```bash
cd backend
python seed_demo_data.py
```

This creates a demo recruiter (`demo@resumeai.com` / `demopassword123`), one job
description, and five genuinely different sample candidates, fully analyzed —
so the dashboard is useful the moment you log in.

### Running the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend setup

```bash
cd frontend
npm install
cp .env.example .env    # VITE_API_URL should point at your backend
```

### Running the frontend

```bash
npm run dev
```

Visit http://localhost:5173 and log in with the demo account, or register a new one.

---

## API reference

Full interactive documentation is auto-generated at `/docs`. Key endpoints:

```
POST   /auth/register
POST   /auth/login
GET    /auth/me

--- Candidate career flow ---
POST   /career/reports                                (multipart: file + job_description)
GET    /career/reports                                list your reports
GET    /career/reports/{report_id}                    403 until assessment complete
DELETE /career/reports/{report_id}
GET    /career/reports/{report_id}/assessment         questions WITHOUT answers
POST   /career/reports/{report_id}/assessment/answer  {question_id, option_id} -> feedback
POST   /career/reports/{report_id}/assessment/complete  unlocks the report

--- Recruiter screening ---
POST   /jobs
GET    /jobs
GET    /jobs/{job_id}
PUT    /jobs/{job_id}
DELETE /jobs/{job_id}

POST   /resumes/upload           (multipart, accepts multiple files)
GET    /resumes
GET    /resumes/{resume_id}
GET    /resumes/{resume_id}/download
POST   /resumes/{resume_id}/reprocess
DELETE /resumes/{resume_id}

POST   /analysis/{resume_id}/{job_id}
GET    /analysis/{resume_id}/{job_id}

GET    /jobs/{job_id}/candidates
GET    /jobs/{job_id}/ranking
POST   /jobs/{job_id}/compare
GET    /jobs/{job_id}/analytics
```

All endpoints except `/auth/register` and `/auth/login` require a
`Authorization: Bearer <token>` header.

---

## Deployment

### Backend (Render, Railway, Fly.io, etc.)
1. Set `DATABASE_URL` to a managed PostgreSQL instance.
2. Set a strong, random `SECRET_KEY`.
3. Set `CORS_ORIGINS` to your deployed frontend URL.
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel, Netlify, etc.)
1. Build command: `npm run build`
2. Output directory: `dist`
3. Set `VITE_API_URL` to your deployed backend URL.

---

## Error handling

The system is designed so that one bad input never takes down the app:

- Unsupported file types, oversized files, empty files, and encrypted/scanned PDFs are caught and reported per-file during a batch upload.
- A failed resume parse is recorded on the `Resume` row (`parse_status="failed"`, with a message) rather than raising — the rest of the batch keeps processing.
- Analyzing a resume that hasn't been successfully parsed returns a clear `422` instead of crashing.
- Global FastAPI exception handlers catch validation errors, database errors, and any unhandled exception, returning a clean JSON error instead of a stack trace.
- Duplicate resume uploads (matched by file hash) are detected and flagged rather than silently re-processed.

---

---

## Running the tests

Two end-to-end suites run against the real ASGI app, database and ML pipeline:

```bash
cd backend
source venv/bin/activate
python test_full_suite.py    # 61 checks: career flow, gating, validation, recruiter regression
python test_career_flow.py   # focused walkthrough of the candidate flow
```

## Future improvements

- Real-time collaborative notes and tags on candidates
- Bulk actions (analyze/delete/export in bulk)
- Interview scheduling integration
- Configurable scoring weights exposed in the UI per job
- Support for scanned/image-only PDFs via OCR
- Multi-recruiter teams and role-based access control
- Candidate-facing status page / email notifications
- Export ranked shortlist to CSV/PDF

---

## Screenshots

_Add screenshots of the dashboard, job detail/ranking view, candidate detail page,
and analytics tab here once you have the app running locally._

---

## License

MIT — built as a portfolio/freelance demonstration project.
