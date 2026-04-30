from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.domain.models import (
    DiagnosticBundle,
    MedicalRecord,
    TurnResult,
    UserSession,
)
from app.db.runtime import DatabaseRuntime
from app.domain.session_store import SessionNotFoundError
from app.repositories.consultation_event_repository import ConsultationEventRepository
from app.repositories.consultation_message_repository import ConsultationMessageRepository
from app.repositories.session_repository import SessionRepository
from app.services.diagnosis_service import DiagnosisService
from app.services.normalization_service import NormalizationService


class InvalidTurnError(ValueError):
    """Raised when a user turn is malformed for the current session state."""


class ConsultationService:
    def __init__(
        self,
        database_runtime: DatabaseRuntime,
        session_repository: SessionRepository,
        message_repository: ConsultationMessageRepository,
        event_repository: ConsultationEventRepository,
        normalization_service: NormalizationService,
        diagnosis_service: DiagnosisService,
    ) -> None:
        self._database_runtime = database_runtime
        self._session_repository = session_repository
        self._message_repository = message_repository
        self._event_repository = event_repository
        self._normalization_service = normalization_service
        self._diagnosis_service = diagnosis_service

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

        with self._database_runtime.session_scope() as db_session:
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
            new_entries = [session.consultation_log.entries[-1]]
            self._session_repository.save(db_session, session)
            self._message_repository.append_entries(
                db_session,
                session_id=session.session_id,
                entries=new_entries,
            )
            self._event_repository.append(
                db_session,
                session_id=session.session_id,
                event_type="session_created",
                payload={
                    "assistant_message": intro_message,
                    "disclaimer_accepted": disclaimer_accepted,
                    "state": session.state_payload(),
                },
            )
            return session

    def handle_free_text_turn(self, session_id: str, message: str) -> TurnResult:
        with self._database_runtime.session_scope() as db_session:
            session = self._session_repository.get(db_session, session_id)
            new_entries = []
            session.add_user_message(message, {"event": "free_text_symptom_input"})
            new_entries.append(session.consultation_log.entries[-1])

            normalized_input = self._normalization_service.normalize(db_session, message)
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
            new_entries.append(session.consultation_log.entries[-1])
            self._persist_session_turn(
                db_session,
                session=session,
                event_type="free_text_turn",
                new_entries=new_entries,
                event_payload={
                    "user_message": message,
                    "assistant_message": assistant_message,
                    "normalized_input": asdict(normalized_input),
                    "diagnoses": [asdict(item) for item in bundle.diagnoses],
                    "next_question": asdict(bundle.next_question) if bundle.next_question else None,
                    "red_flags": [asdict(item) for item in bundle.red_flags],
                    "explanation_trace": bundle.explanation_trace,
                    "state": session.state_payload(),
                },
            )

            return TurnResult(
                session=session,
                assistant_message=assistant_message,
                normalized_input=normalized_input,
                diagnostic_bundle=bundle,
            )

    def handle_follow_up_answer(
        self, session_id: str, question_id: str, response: str
    ) -> TurnResult:
        with self._database_runtime.session_scope() as db_session:
            session = self._session_repository.get(db_session, session_id)
            pending_question = session.pending_question

            if pending_question is None:
                raise InvalidTurnError("There is no active follow-up question for this session.")

            if pending_question.id != question_id:
                raise InvalidTurnError("The follow-up response does not match the active question.")

            response_value = response.strip().lower()
            if response_value not in {"yes", "no", "unknown"}:
                raise InvalidTurnError("Follow-up responses must be yes, no, or unknown.")

            new_entries = []
            session.add_user_message(
                response_value.capitalize(),
                {
                    "event": "follow_up_answer",
                    "question_id": question_id,
                    "target_symptom": pending_question.target_symptom,
                    "response": response_value,
                },
            )
            new_entries.append(session.consultation_log.entries[-1])
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
            new_entries.append(session.consultation_log.entries[-1])
            self._persist_session_turn(
                db_session,
                session=session,
                event_type="follow_up_turn",
                new_entries=new_entries,
                event_payload={
                    "question_id": question_id,
                    "response": response_value,
                    "assistant_message": assistant_message,
                    "diagnoses": [asdict(item) for item in bundle.diagnoses],
                    "next_question": asdict(bundle.next_question) if bundle.next_question else None,
                    "red_flags": [asdict(item) for item in bundle.red_flags],
                    "explanation_trace": bundle.explanation_trace,
                    "state": session.state_payload(),
                },
            )

            return TurnResult(
                session=session,
                assistant_message=assistant_message,
                normalized_input=None,
                diagnostic_bundle=bundle,
            )

    def _persist_session_turn(
        self,
        db_session: Any,
        *,
        session: UserSession,
        event_type: str,
        new_entries: list[Any],
        event_payload: dict[str, Any],
    ) -> None:
        self._session_repository.save(db_session, session)
        self._message_repository.append_entries(
            db_session,
            session_id=session.session_id,
            entries=new_entries,
        )
        self._event_repository.append(
            db_session,
            session_id=session.session_id,
            event_type=event_type,
            payload=event_payload,
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
        bundle = self._diagnosis_service.diagnose(request_payload)
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
