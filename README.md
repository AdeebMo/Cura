# Cura

Cura is an educational, rule-based symptom triage and diagnostic assistant for non-emergency use.

This repository is intentionally split by paradigm:

- `backend/`: Python + FastAPI orchestration and OOP session management
- `lisp/`: Common Lisp symptom normalization with pure functional transformations
- `prolog/`: SWI-Prolog rule engine for diagnosis, follow-up questions, and red flags
- `frontend/`: React + Tailwind premium chat-style interface

## Current Scope

The first vertical slice is intentionally small and defensible:

- Conditions: `common_cold`, `influenza`, `allergy`
- Symptom normalization through Lisp
- Stateful consultation flow through Python classes
- Rule-based diagnosis and next-question inference through Prolog
- Modern frontend shell with intake, chat, and session sidebar

## Architecture

- `UserSession` coordinates the consultation lifecycle.
- `MedicalRecord` stores confirmed, denied, and unknown symptoms plus basic vitals.
- `ConsultationLog` stores the conversational transcript and decision trace.
- Lisp converts free-text symptom descriptions into canonical symptom tokens.
- Prolog evaluates those tokens against a small medical rule base and suggests the next best follow-up question.

The system is educational only and deliberately avoids medical certainty.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn app.main:app --reload
```

The backend expects:

- `sbcl`
- `swipl`

Both are invoked as subprocesses by Python.

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

Environment check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-env.ps1
```

