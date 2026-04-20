from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import ConsultationMessageModel
from app.domain.models import ConsultationEntry


class ConsultationMessageRepository:
    def append_entries(
        self,
        db_session: Session,
        *,
        session_id: str,
        entries: list[ConsultationEntry],
    ) -> None:
        if not entries:
            return

        next_ordinal = self._next_ordinal(db_session, session_id)
        for offset, entry in enumerate(entries):
            db_session.add(
                ConsultationMessageModel(
                    session_id=session_id,
                    role=entry.role,
                    message=entry.message,
                    payload_metadata=dict(entry.metadata),
                    ordinal=next_ordinal + offset,
                    created_at=entry.timestamp,
                )
            )

    def _next_ordinal(self, db_session: Session, session_id: str) -> int:
        statement: Select[tuple[int | None]] = select(
            func.max(ConsultationMessageModel.ordinal)
        ).where(ConsultationMessageModel.session_id == session_id)
        max_ordinal = db_session.execute(statement).scalar_one()
        if max_ordinal is None:
            return 0
        return max_ordinal + 1
