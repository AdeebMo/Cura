from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import QuestionCatalogModel


@dataclass(frozen=True, slots=True)
class QuestionSeed:
    id: str
    target_symptom: str
    prompt: str
    rationale: str
    priority: int
    active: bool = True


class QuestionCatalogRepository:
    def question_ids(self, db_session: Session) -> set[str]:
        statement = select(QuestionCatalogModel.id)
        return {row[0] for row in db_session.execute(statement)}

    def seed(self, db_session: Session, items: Iterable[QuestionSeed]) -> None:
        existing = {
            row.id: row for row in db_session.execute(select(QuestionCatalogModel)).scalars()
        }
        for item in items:
            row = existing.get(item.id)
            if row is None:
                row = QuestionCatalogModel(id=item.id)
                db_session.add(row)

            row.target_symptom = item.target_symptom
            row.prompt = item.prompt
            row.rationale = item.rationale
            row.priority = item.priority
            row.active = item.active
