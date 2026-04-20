# Defense Guide

This guide is for your project defense, not for end users. It stays close to the real code path so you can explain the system confidently without memorizing extra theory.

## 90-Second Architecture Walkthrough

1. The frontend creates a session through `POST /api/v1/sessions`.
2. FastAPI calls `ConsultationService.create_session(...)` in [consultation_service.py](../backend/app/services/consultation_service.py).
3. Python creates a `UserSession`, stores the intro assistant message, and persists the session, messages, and event payload.
4. When the user sends free text, Python calls the Common Lisp normalizer through `LispBridge`.
5. Lisp converts raw user language into canonical symptom tokens such as `fever`, `cough`, or `runny_nose`.
6. Python stores those canonical symptoms on the `MedicalRecord`.
7. Python sends structured symptom state to Prolog through `PrologBridge`.
8. Prolog ranks possible conditions, checks red flags, and chooses the next follow-up question.
9. Python composes the assistant reply, persists the updated session state, and returns the API response to the frontend.

## Why Each Paradigm Is Necessary

- `Python OOP`
  - Owns the API, orchestration, repositories, persistence, and validation.
  - Best file to cite: [consultation_service.py](../backend/app/services/consultation_service.py)
- `Common Lisp`
  - Owns normalization only.
  - It turns human wording into canonical symbols without storing state.
  - Best files to cite: [main.lisp](../lisp/src/main.lisp), [normalizer.lisp](../lisp/src/normalizer.lisp), [lexicon.lisp](../lisp/src/lexicon.lisp)
- `Prolog`
  - Owns logical reasoning only.
  - It decides diagnoses, red flags, and follow-up questions from structured facts.
  - Best files to cite: [main.pl](../prolog/src/main.pl), [facts.pl](../prolog/src/facts.pl), [questions.pl](../prolog/src/questions.pl), [red_flags.pl](../prolog/src/red_flags.pl)

## Exact Backend Flow

### Session creation

- Route: [router.py](../backend/app/api/router.py)
- Service method: [consultation_service.py](../backend/app/services/consultation_service.py)
- What to say:
  - Python validates that the disclaimer was accepted.
  - It creates a `UserSession` with a `MedicalRecord`.
  - It adds the first assistant message.
  - It persists the session row, message row, and event row.

### Free-text turn

- Service method: [consultation_service.py](../backend/app/services/consultation_service.py)
- What to say:
  - Python stores the raw user message.
  - Lisp normalizes the text into canonical symptoms.
  - Python applies those symptoms to the medical record.
  - Python calls Prolog with confirmed, denied, and unknown symptoms.
  - Python stores the assistant response and new state.

### Follow-up turn

- Service method: [consultation_service.py](../backend/app/services/consultation_service.py)
- What to say:
  - Python verifies there is an active question.
  - Python verifies the answer belongs to that exact question.
  - It updates the symptom state as `yes`, `no`, or `unknown`.
  - Then it runs Prolog again and persists the new result.

## Common Defense Questions

### "Why is mapped phrases sometimes empty?"

- Because `matched_phrases` only records phrase-level aliases.
- Single-word matches still normalize successfully through the token dictionary.
- Example:
  - `"I am sneezing"` produces canonical symptom `sneezing`
  - but `matched_phrases` is empty because no multi-word phrase alias was needed

### "Why use canonical symptom tokens?"

- They separate user language from rule logic.
- Lisp handles messy human wording.
- Prolog receives only stable internal symbols like `painful_urination` or `runny_nose`.

### "How do you keep the three paradigms consistent?"

- Python seeds the symptom, condition, and question catalogs.
- Python also validates that:
  - Lisp canonical outputs exist in the symptom catalog
  - Prolog symptom references exist in the symptom catalog
  - Prolog questions and conditions exist in the database
- Best file to cite: [paradigm_catalog_service.py](../backend/app/services/paradigm_catalog_service.py)

### "Where is persistence handled?"

- Database models are defined in [models.py](../backend/app/db/models.py)
- SQLAlchemy session/engine setup is in [runtime.py](../backend/app/db/runtime.py)
- Repository writes happen from the service layer, mainly in [consultation_service.py](../backend/app/services/consultation_service.py)

## Short File-by-File Memory Aid

- `router.py`: HTTP in and out
- `consultation_service.py`: main business flow
- `models.py`: domain state shapes
- `lisp_bridge.py`: Python to Lisp bridge
- `prolog_bridge.py`: Python to Prolog bridge
- `main.lisp`, `normalizer.lisp`, `lexicon.lisp`: normalization pipeline
- `facts.pl`, `rules.pl`, `questions.pl`, `red_flags.pl`: logic knowledge base
- `db/models.py`: persisted schema
- `session_repository.py`, `consultation_message_repository.py`, `consultation_event_repository.py`: durable storage helpers

## Last-Minute Prep

- Practice explaining one full flow:
  - `I have a high fever and coughing`
- Practice explaining one direct-token case:
  - `I am sneezing`
- Practice explaining one urgent case:
  - `I have chest pain and trouble breathing`
- Practice explaining one follow-up cycle:
  - initial diagnosis -> follow-up question -> yes/no answer -> updated diagnosis
