from __future__ import annotations

from app.core.config import settings
from app.db.runtime import DatabaseRuntime
from app.repositories import (
    ConditionCatalogRepository,
    QuestionCatalogRepository,
    SymptomCatalogRepository,
)
from app.services.paradigm_catalog_service import CatalogBootstrapService, PrologCatalogInspector


def main() -> None:
    database_runtime = DatabaseRuntime(settings)
    database_runtime.initialize_schema()

    bootstrap_service = CatalogBootstrapService(
        SymptomCatalogRepository(),
        ConditionCatalogRepository(),
        QuestionCatalogRepository(),
        PrologCatalogInspector(settings),
    )

    with database_runtime.session_scope() as db_session:
        snapshot = bootstrap_service.seed_catalogs(db_session)

    print(
        "Seeded symptom, condition, and question catalogs "
        f"({len(snapshot.symptom_keys)} Prolog symptoms, "
        f"{len(snapshot.condition_seeds)} conditions, "
        f"{len(snapshot.question_seeds)} questions)."
    )


if __name__ == "__main__":
    main()
