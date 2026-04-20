from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, settings
from app.db.runtime import DatabaseRuntime
from app.integrations.lisp_bridge import LispBridge
from app.integrations.prolog_bridge import PrologBridge
from app.repositories import (
    ConditionCatalogRepository,
    ConsultationEventRepository,
    ConsultationLogRepository,
    ConsultationMessageRepository,
    QuestionCatalogRepository,
    SessionRepository,
    SymptomCatalogRepository,
)
from app.services.consultation_service import ConsultationService
from app.services.diagnosis_service import DiagnosisService
from app.services.normalization_service import NormalizationService
from app.services.paradigm_catalog_service import (
    CatalogBootstrapService,
    ParadigmCatalogValidationService,
    PrologCatalogInspector,
)


def build_consultation_service(runtime_settings: Settings = settings) -> ConsultationService:
    database_runtime = DatabaseRuntime(runtime_settings)
    if runtime_settings.auto_initialize_database:
        database_runtime.initialize_schema()

    session_repository = SessionRepository()
    message_repository = ConsultationMessageRepository()
    event_repository = ConsultationEventRepository()
    symptom_catalog_repository = SymptomCatalogRepository()
    condition_catalog_repository = ConditionCatalogRepository()
    question_catalog_repository = QuestionCatalogRepository()
    normalization_service = NormalizationService(
        LispBridge(runtime_settings),
        symptom_catalog_repository,
    )
    diagnosis_service = DiagnosisService(PrologBridge(runtime_settings))
    prolog_catalog_inspector = PrologCatalogInspector(runtime_settings)
    catalog_bootstrap_service = CatalogBootstrapService(
        symptom_catalog_repository,
        condition_catalog_repository,
        question_catalog_repository,
        prolog_catalog_inspector,
    )
    validation_service = ParadigmCatalogValidationService(
        symptom_catalog_repository,
        condition_catalog_repository,
        question_catalog_repository,
        normalization_service,
        prolog_catalog_inspector,
    )

    with database_runtime.session_scope() as db_session:
        catalog_bootstrap_service.seed_catalogs(db_session)
        if runtime_settings.validate_paradigms_on_startup:
            validation_service.validate(db_session)

    return ConsultationService(
        database_runtime=database_runtime,
        session_repository=session_repository,
        message_repository=message_repository,
        event_repository=event_repository,
        normalization_service=normalization_service,
        diagnosis_service=diagnosis_service,
        log_repository=ConsultationLogRepository(repo_settings=runtime_settings),
    )


@lru_cache(maxsize=1)
def get_consultation_service() -> ConsultationService:
    return build_consultation_service(settings)
