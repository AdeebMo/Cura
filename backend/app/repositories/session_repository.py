from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import SessionModel
from app.domain.models import ConsultationEntry, ConsultationLog, FollowUpQuestion, MedicalRecord, UserSession
from app.domain.session_store import SessionNotFoundError


def _coerce_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class SessionRepository:
    def get(self, db_session: Session, session_id: str) -> UserSession:
        row = db_session.get(SessionModel, session_id)
        if row is None:
            raise SessionNotFoundError(session_id)
        return self._to_domain(row)

    def save(self, db_session: Session, session: UserSession) -> UserSession:
        row = db_session.get(SessionModel, session.session_id)
        if row is None:
            row = SessionModel(id=session.session_id)
            db_session.add(row)

        row.alias = session.medical_record.alias
        row.age_group = session.medical_record.age_group
        row.sex = session.medical_record.sex
        row.vitals = dict(session.medical_record.vitals)
        row.confirmed_symptoms = sorted(session.medical_record.confirmed_symptoms)
        row.denied_symptoms = sorted(session.medical_record.denied_symptoms)
        row.unknown_symptoms = sorted(session.medical_record.unknown_symptoms)
        row.pending_question = asdict(session.pending_question) if session.pending_question else None
        row.asked_question_ids = sorted(session.asked_question_ids)
        row.status = "active"
        row.created_at = _coerce_datetime(session.created_at)
        row.updated_at = _coerce_datetime(session.updated_at)
        db_session.flush()
        return session

    def _to_domain(self, row: SessionModel) -> UserSession:
        pending_question = None
        if row.pending_question:
            pending_question = FollowUpQuestion(**row.pending_question)

        consultation_log = ConsultationLog(
            entries=[
                ConsultationEntry(
                    role=message.role,
                    message=message.message,
                    timestamp=_coerce_datetime(message.created_at),
                    metadata=dict(message.payload_metadata or {}),
                )
                for message in sorted(row.messages, key=lambda item: item.ordinal)
            ]
        )
        session = UserSession(
            session_id=row.id,
            medical_record=MedicalRecord(
                alias=row.alias,
                age_group=row.age_group,
                sex=row.sex,
                vitals=dict(row.vitals or {}),
                confirmed_symptoms=set(row.confirmed_symptoms or []),
                denied_symptoms=set(row.denied_symptoms or []),
                unknown_symptoms=set(row.unknown_symptoms or []),
            ),
            consultation_log=consultation_log,
            asked_question_ids=set(row.asked_question_ids or []),
            pending_question=pending_question,
            created_at=_coerce_datetime(row.created_at),
            updated_at=_coerce_datetime(row.updated_at),
        )
        return session
