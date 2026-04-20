from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.domain.models import DiagnosticBundle, TurnResult, UserSession
from app.domain.session_store import InMemorySessionStore, SessionNotFoundError
from app.integrations.lisp_bridge import LispBridge, LispBridgeError
from app.integrations.prolog_bridge import PrologBridge, PrologBridgeError
from app.repositories.consultation_log_repository import ConsultationLogRepository
from app.schemas.api import (
    CreateSessionRequest,
    CreateSessionResponse,
    TurnResponse,
    UserTurnRequest,
)
from app.services.consultation_service import ConsultationService, InvalidTurnError

router = APIRouter(prefix="/api/v1", tags=["consultation"])

session_store = InMemorySessionStore()
log_repository = ConsultationLogRepository()
consultation_service = ConsultationService(
    session_store=session_store,
    lisp_bridge=LispBridge(),
    prolog_bridge=PrologBridge(),
    log_repository=log_repository,
)


def _session_state(session: UserSession) -> dict[str, object]:
    return session.state_payload()


def _turn_payload(result: TurnResult) -> dict[str, object]:
    return {
        "assistant_message": result.assistant_message,
        "normalized_input": asdict(result.normalized_input) if result.normalized_input else None,
        "diagnoses": [asdict(item) for item in result.diagnostic_bundle.diagnoses],
        "next_question": (
            asdict(result.diagnostic_bundle.next_question)
            if result.diagnostic_bundle.next_question
            else None
        ),
        "red_flags": [asdict(item) for item in result.diagnostic_bundle.red_flags],
        "explanation_trace": result.diagnostic_bundle.explanation_trace,
        "state": _session_state(result.session),
    }


def _turn_log_context(result: TurnResult) -> dict[str, object]:
    return {
        "assistant_message": result.assistant_message,
        "normalized_input": asdict(result.normalized_input) if result.normalized_input else None,
        "diagnoses": [asdict(item) for item in result.diagnostic_bundle.diagnoses],
        "next_question": (
            asdict(result.diagnostic_bundle.next_question)
            if result.diagnostic_bundle.next_question
            else None
        ),
        "red_flags": [asdict(item) for item in result.diagnostic_bundle.red_flags],
        "explanation_trace": result.diagnostic_bundle.explanation_trace,
    }


@router.post("/sessions", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    background_tasks: BackgroundTasks,
) -> CreateSessionResponse:
    try:
        session = consultation_service.create_session(
            alias=request.alias,
            age_group=request.age_group,
            sex=request.sex,
            vitals=request.vitals.model_dump(exclude_none=True),
            disclaimer_accepted=request.disclaimer_accepted,
        )
    except InvalidTurnError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    assistant_message = session.consultation_log.entries[-1].message
    background_tasks.add_task(
        consultation_service.log_session_snapshot,
        session,
        "session_created",
        {"assistant_message": assistant_message},
    )
    return CreateSessionResponse(
        session_id=session.session_id,
        assistant_message=assistant_message,
        state=_session_state(session),
    )


@router.post("/sessions/{session_id}/turns", response_model=TurnResponse)
def create_turn(
    session_id: str,
    request: UserTurnRequest,
    background_tasks: BackgroundTasks,
) -> TurnResponse:
    try:
        if request.type == "free_text":
            if not request.message:
                raise InvalidTurnError("A free-text turn requires a message.")
            result = consultation_service.handle_free_text_turn(session_id, request.message)
            event_type = "free_text_turn"
        else:
            if not request.question_id or not request.response:
                raise InvalidTurnError("A follow-up turn requires question_id and response.")
            result = consultation_service.handle_follow_up_answer(
                session_id,
                request.question_id,
                request.response,
            )
            event_type = "follow_up_turn"
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found") from exc
    except (InvalidTurnError, LispBridgeError, PrologBridgeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    background_tasks.add_task(
        consultation_service.log_session_snapshot,
        result.session,
        event_type,
        _turn_log_context(result),
    )
    return TurnResponse(**_turn_payload(result))
