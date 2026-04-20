from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import ConsultationEventModel


class ConsultationEventRepository:
    def append(
        self,
        db_session: Session,
        *,
        session_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        db_session.add(
            ConsultationEventModel(
                session_id=session_id,
                event_type=event_type,
                payload=payload,
            )
        )
