# Cura Backend

FastAPI orchestration layer for the Cura educational diagnostic assistant.

This package owns:

- OOP session and consultation state
- SQLAlchemy repositories and durable persistence
- subprocess bridges to Common Lisp and SWI-Prolog
- API contracts for the React frontend
- seeding and cross-paradigm validation

## Runtime Responsibilities

- `Python OOP`
  - API routing
  - transaction boundaries
  - session/message/event repositories
  - state transitions and validation
- `Common Lisp`
  - free-text cleanup
  - synonym mapping
  - canonical symptom normalization
- `Prolog`
  - diagnosis ranking
  - safety warning inference
  - follow-up question selection

## Database Tables

- `sessions`
- `consultation_messages`
- `consultation_events`
- `symptoms`
- `conditions`
- `question_catalog`

## Useful Commands

```powershell
cd backend
pip install -e .[dev]
alembic upgrade head
python -m app.cli.seed_catalog
python -m app.cli.validate_paradigms
pytest
```
