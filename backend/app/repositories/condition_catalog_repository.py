from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ConditionCatalogModel


@dataclass(frozen=True, slots=True)
class ConditionSeed:
    condition_key: str
    display_name: str
    active: bool = True
    notes: str | None = None


class ConditionCatalogRepository:
    def condition_keys(self, db_session: Session) -> set[str]:
        statement = select(ConditionCatalogModel.condition_key)
        return {row[0] for row in db_session.execute(statement)}

    def seed(self, db_session: Session, items: Iterable[ConditionSeed]) -> None:
        existing = {
            row.condition_key: row
            for row in db_session.execute(select(ConditionCatalogModel)).scalars()
        }
        for item in items:
            row = existing.get(item.condition_key)
            if row is None:
                row = ConditionCatalogModel(condition_key=item.condition_key)
                db_session.add(row)

            row.display_name = item.display_name
            row.active = item.active
            row.notes = item.notes
