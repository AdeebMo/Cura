# Cura

Cura is an educational, rule-based symptom triage and diagnostic assistant for non-emergency use.

This repository is intentionally split by paradigm:

- `backend/`: Python + FastAPI orchestration and OOP session management
- `lisp/`: Common Lisp symptom normalization with pure functional transformations
- `prolog/`: SWI-Prolog rule engine for diagnosis, follow-up questions, and red flags
- `frontend/`: React + Tailwind premium chat-style interface

The backend now persists consultation state and medical catalogs in SQLAlchemy-managed tables, while keeping Common Lisp as the live normalization engine and Prolog as the rule-based reasoning engine.

## Current Scope

The current vertical slice is intentionally small and defensible:

- Persistent sessions, messages, and diagnostic turn artifacts
- Conditions: `common_cold`, `influenza`, `allergy`, `covid_like_viral_infection`, `migraine`, `food_poisoning`, `strep_throat`, `bronchitis`, `urinary_tract_infection`, `dehydration`
- Symptom normalization through Common Lisp
- Stateful consultation flow and repositories through Python classes
- Rule-based diagnosis and next-question inference through Prolog
- Modern frontend shell with intake, chat, and session sidebar

## Architecture

- `UserSession` coordinates the consultation lifecycle.
- `MedicalRecord` stores confirmed, denied, and unknown symptoms plus basic vitals.
- `ConsultationLog` stores the conversational transcript in-memory while Python repositories persist the durable state.
- Common Lisp converts free-text symptom descriptions into canonical symptom tokens and matched phrases.
- Prolog evaluates those tokens against the medical rule base and suggests the next best follow-up question.
- Postgres is the target database, with Alembic migrations and seeded symptom/condition/question catalogs.

The system is educational only and deliberately avoids medical certainty.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
docker compose up -d postgres
$env:CURA_DATABASE_URL="postgresql+psycopg://cura:cura@localhost:5432/cura"
alembic upgrade head
python -m app.cli.seed_catalog
uvicorn app.main:app --reload
```

The backend expects:

- `sbcl`
- `swipl`
- `Postgres 16+` for the target persisted setup

Both are invoked as subprocesses by Python.

If you want a zero-config local fallback while developing, omit `CURA_DATABASE_URL` and the backend will use `backend/cura.db`.

## Frontend Setup

Node.js is required for the frontend shell:

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` if the backend is not running at `http://localhost:8000`.

## Verification

Backend tests:

```powershell
cd backend
pytest
```

Catalog validation:

```powershell
cd backend
python -m app.cli.validate_paradigms
```

Environment check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-env.ps1
```
