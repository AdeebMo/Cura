from __future__ import annotations

from app.core.config import settings
from app.db.runtime import DatabaseRuntime
from app.integrations.lisp_bridge import LispBridge
from app.repositories import (
    ConditionCatalogRepository,
    QuestionCatalogRepository,
    SymptomCatalogRepository,
)
from app.services.normalization_service import NormalizationService
from app.services.paradigm_catalog_service import (
    ParadigmCatalogValidationService,
    PrologCatalogInspector,
)


def main() -> None:
    database_runtime = DatabaseRuntime(settings)
    database_runtime.initialize_schema()
    validator = ParadigmCatalogValidationService(
        SymptomCatalogRepository(),
        ConditionCatalogRepository(),
        QuestionCatalogRepository(),
        NormalizationService(LispBridge(settings), SymptomCatalogRepository()),
        PrologCatalogInspector(settings),
    )

    with database_runtime.session_scope() as db_session:
        validator.validate(db_session)

    print("Python, Common Lisp, Prolog, and database catalogs are aligned.")


if __name__ == "__main__":
    main()
