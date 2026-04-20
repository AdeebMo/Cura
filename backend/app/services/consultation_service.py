from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.domain.models import (
    DiagnosticBundle,
    FollowUpQuestion,
    MedicalRecord,
    NormalizedInput,
    TurnResult,
    UserSession,
)
from app.domain.session_store import InMemorySessionStore, SessionNotFoundError
from app.integrations.lisp_bridge import LispBridge
from app.integrations.prolog_bridge import PrologBridge
from app.repositories.consultation_log_repository import ConsultationLogRepository


class InvalidTurnError(ValueError):
    """Raised when a user turn is malformed for the current session state."""


class ConsultationService:
    def __init__(
        self,
        session_store: InMemorySessionStore,
        lisp_bridge: LispBridge,
        prolog_bridge: PrologBridge,
        log_repository: ConsultationLogRepository,
    ) -> None:
        self._session_store = session_store
        self._lisp_bridge = lisp_bridge
        self._prolog_bridge = prolog_bridge
        self._log_repository = log_repository

    def create_session(
        self,
        *,
        alias: str,
        age_group: str,
        sex: str | None,
        vitals: dict[str, Any],
        disclaimer_accepted: bool,
    ) -> UserSession:
        if not disclaimer_accepted:
            raise InvalidTurnError("The educational-use disclaimer must be accepted first.")

        session = UserSession(
            medical_record=MedicalRecord(alias=alias, age_group=age_group, sex=sex, vitals=vitals)
        )
        intro_message = (
            "Thanks. I can help with an educational symptom-triage conversation for non-emergency use. "
            "Tell me what symptoms you are experiencing, and I will translate that into a rule-based assessment."
        )
        session.add_assistant_message(
            intro_message,
            {"event": "session_created", "disclaimer_accepted": disclaimer_accepted},
        )
        return self._session_store.save(session)

    def handle_free_text_turn(self, session_id: str, message: str) -> TurnResult:
        session = self._session_store.get(session_id)
        session.add_user_message(message, {"event": "free_text_symptom_input"})

        normalized_input = self._lisp_bridge.normalize(message)
        session.medical_record.confirm_symptoms(normalized_input.canonical_symptoms)

        bundle = self._run_diagnostic_cycle(session)
        assistant_message = self._compose_assistant_message(bundle)
        session.add_assistant_message(
            assistant_message,
            {
                "event": "diagnostic_update",
                "normalized_symptoms": normalized_input.canonical_symptoms,
                "unknown_terms": normalized_input.unknown_terms,
                "red_flags": [flag.id for flag in bundle.red_flags],
                "decision_trace": bundle.explanation_trace,
                "diagnoses": [asdict(item) for item in bundle.diagnoses],
                "next_question": asdict(bundle.next_question) if bundle.next_question else None,
            },
        )
        self._session_store.save(session)

        return TurnResult(
            session=session,
            assistant_message=assistant_message,
            normalized_input=normalized_input,
            diagnostic_bundle=bundle,
        )

    def handle_follow_up_answer(
        self, session_id: str, question_id: str, response: str
    ) -> TurnResult:
        session = self._session_store.get(session_id)
        pending_question = session.pending_question

        if pending_question is None:
            raise InvalidTurnError("There is no active follow-up question for this session.")

        if pending_question.id != question_id:
            raise InvalidTurnError("The follow-up response does not match the active question.")

        response_value = response.strip().lower()
        if response_value not in {"yes", "no", "unknown"}:
            raise InvalidTurnError("Follow-up responses must be yes, no, or unknown.")

        session.add_user_message(
            response_value.capitalize(),
            {
                "event": "follow_up_answer",
                "question_id": question_id,
                "target_symptom": pending_question.target_symptom,
                "response": response_value,
            },
        )
        session.medical_record.set_symptom_state(pending_question.target_symptom, response_value)
        session.set_pending_question(None)

        bundle = self._run_diagnostic_cycle(session)
        assistant_message = self._compose_assistant_message(bundle)
        session.add_assistant_message(
            assistant_message,
            {
                "event": "diagnostic_update",
                "question_id": question_id,
                "response": response_value,
                "red_flags": [flag.id for flag in bundle.red_flags],
                "decision_trace": bundle.explanation_trace,
                "diagnoses": [asdict(item) for item in bundle.diagnoses],
                "next_question": asdict(bundle.next_question) if bundle.next_question else None,
            },
        )
        self._session_store.save(session)

        return TurnResult(
            session=session,
            assistant_message=assistant_message,
            normalized_input=None,
            diagnostic_bundle=bundle,
        )

    def log_session_snapshot(
        self,
        session: UserSession,
        event_type: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        self._log_repository.append(
            {
                "event_type": event_type,
                "context": context or {},
                "session": session.state_payload(),
            }
        )

    def _run_diagnostic_cycle(self, session: UserSession) -> DiagnosticBundle:
        request_payload = {
            "demographics": {
                "age_group": session.medical_record.age_group,
                "sex": session.medical_record.sex,
            },
            "vitals": session.medical_record.vitals,
            "confirmed_symptoms": sorted(session.medical_record.confirmed_symptoms),
            "denied_symptoms": sorted(session.medical_record.denied_symptoms),
            "unknown_symptoms": sorted(session.medical_record.unknown_symptoms),
            "asked_question_ids": sorted(session.asked_question_ids),
        }
        bundle = self._prolog_bridge.diagnose(request_payload)
        session.set_pending_question(bundle.next_question)
        return bundle

    def _compose_assistant_message(self, bundle: DiagnosticBundle) -> str:
        message_parts: list[str] = []

        if bundle.red_flags:
            triggers = ", ".join(flag.trigger.replace("_", " ") for flag in bundle.red_flags)
            message_parts.append(
                "A safety warning was triggered by "
                f"{triggers}. This educational assistant cannot assess emergencies, so urgent clinical evaluation is recommended."
            )

        if bundle.diagnoses:
            top = bundle.diagnoses[0]
            message_parts.append(
                f"My current leading rule-based match is {top.condition.replace('_', ' ')} "
                f"with {top.rule_strength} support. {top.explanation}"
            )
            if len(bundle.diagnoses) > 1:
                alternatives = ", ".join(
                    diagnosis.condition.replace("_", " ") for diagnosis in bundle.diagnoses[1:]
                )
                message_parts.append(f"Other plausible rule-based matches are {alternatives}.")
        else:
            message_parts.append(
                "I do not have enough structured evidence for a likely rule-based match yet."
            )

        if bundle.next_question:
            message_parts.append(bundle.next_question.prompt)
        else:
            message_parts.append(
                "I have enough information for this first-pass summary, but this remains educational and non-diagnostic."
            )

        return " ".join(message_parts)


__all__ = [
    "ConsultationService",
    "InvalidTurnError",
    "SessionNotFoundError",
]
