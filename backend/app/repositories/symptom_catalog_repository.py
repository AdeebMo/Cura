from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.symptom_catalog import SymptomSeed
from app.db.models import SymptomCatalogModel


class SymptomCatalogRepository:
    def canonical_keys(self, db_session: Session) -> set[str]:
        statement = select(SymptomCatalogModel.canonical_key)
        return {row[0] for row in db_session.execute(statement)}

    def seed(self, db_session: Session, items: Iterable[SymptomSeed]) -> None:
        existing = {
            row.canonical_key: row
            for row in db_session.execute(select(SymptomCatalogModel)).scalars()
        }
        for item in items:
            row = existing.get(item.canonical_key)
            if row is None:
                row = SymptomCatalogModel(canonical_key=item.canonical_key)
                db_session.add(row)

            row.display_name = item.display_name
            row.body_system = item.body_system
            row.intake_priority = item.intake_priority
            row.is_red_flag_candidate = item.is_red_flag_candidate
            row.active = item.active
