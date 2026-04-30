import shutil
import tempfile
from pathlib import Path

from app.core.config import Settings
from app.db.runtime import DatabaseRuntime
from app.integrations.lisp_bridge import LispBridge
from app.integrations.prolog_bridge import PrologBridge
from app.repositories.condition_catalog_repository import ConditionCatalogRepository
from app.repositories.consultation_event_repository import ConsultationEventRepository
from app.repositories.consultation_message_repository import ConsultationMessageRepository
from app.repositories.question_catalog_repository import QuestionCatalogRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.symptom_catalog_repository import SymptomCatalogRepository
from app.services.consultation_service import ConsultationService, InvalidTurnError
from app.services.diagnosis_service import DiagnosisService
from app.services.normalization_service import NormalizationService
from app.services.paradigm_catalog_service import (
    CatalogBootstrapService,
    ParadigmCatalogValidationService,
    PrologCatalogInspector,
)

def build_service(work_directory: Path) -> ConsultationService:
    project_root = Path(__file__).resolve().parents[2]
    database_name = f"cura_test_{work_directory.name}"
    test_settings = Settings(
        project_root=project_root,
        backend_root=project_root / "backend",
        database_url=(
            f"sqlite+pysqlite:///file:{database_name}?mode=memory&cache=shared&uri=true"
        ),
    )
    database_runtime = DatabaseRuntime(test_settings)
    database_runtime.initialize_schema()

    session_repository = SessionRepository()
    message_repository = ConsultationMessageRepository()
    event_repository = ConsultationEventRepository()
    symptom_catalog_repository = SymptomCatalogRepository()
    condition_catalog_repository = ConditionCatalogRepository()
    question_catalog_repository = QuestionCatalogRepository()
    normalization_service = NormalizationService(
        LispBridge(test_settings),
        symptom_catalog_repository,
    )
    diagnosis_service = DiagnosisService(PrologBridge(test_settings))
    inspector = PrologCatalogInspector(test_settings)

    with database_runtime.session_scope() as db_session:
        CatalogBootstrapService(
            symptom_catalog_repository,
            condition_catalog_repository,
            question_catalog_repository,
            inspector,
        ).seed_catalogs(db_session)
        ParadigmCatalogValidationService(
            symptom_catalog_repository,
            condition_catalog_repository,
            question_catalog_repository,
            normalization_service,
            inspector,
        ).validate(db_session)

    return ConsultationService(
        database_runtime=database_runtime,
        session_repository=session_repository,
        message_repository=message_repository,
        event_repository=event_repository,
        normalization_service=normalization_service,
        diagnosis_service=diagnosis_service,
    )


def test_service_tracks_session_state_across_a_follow_up_turn() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        service = build_service(temp_dir)
        session = service.create_session(
            alias="Ava",
            age_group="adult",
            sex="female",
            vitals={"temperature_c": 38.6},
            disclaimer_accepted=True,
        )

        initial_turn = service.handle_free_text_turn(
            session.session_id,
            "I have a high fever and coughing.",
        )

        assert "fever" in initial_turn.session.medical_record.confirmed_symptoms
        assert initial_turn.diagnostic_bundle.next_question is not None

        follow_up_turn = service.handle_follow_up_answer(
            session.session_id,
            initial_turn.diagnostic_bundle.next_question.id,
            "yes",
        )

        asked_symptom = initial_turn.diagnostic_bundle.next_question.target_symptom
        assert asked_symptom in follow_up_turn.session.medical_record.confirmed_symptoms
        assert follow_up_turn.diagnostic_bundle.next_question is not None
        assert (
            follow_up_turn.diagnostic_bundle.next_question.id
            != initial_turn.diagnostic_bundle.next_question.id
        )
        assert len(follow_up_turn.session.consultation_log.entries) >= 5
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_records_reasoning_metadata() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        service = build_service(temp_dir)
        session = service.create_session(
            alias="Noor",
            age_group="adult",
            sex="female",
            vitals={"temperature_c": 38.1},
            disclaimer_accepted=True,
        )

        turn = service.handle_free_text_turn(
            session.session_id,
            "I have painful urination and frequent urination.",
        )
        assistant_metadata = turn.session.consultation_log.entries[-1].metadata

        assert assistant_metadata["decision_trace"]
        assert assistant_metadata["diagnoses"][0]["condition"] == "urinary_tract_infection"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_persists_session_state_across_service_instances() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        first_service = build_service(temp_dir)
        session = first_service.create_session(
            alias="Zayd",
            age_group="adult",
            sex="male",
            vitals={"temperature_c": 38.4},
            disclaimer_accepted=True,
        )
        initial_turn = first_service.handle_free_text_turn(
            session.session_id,
            "I have fever, cough, and a sore throat.",
        )

        second_service = build_service(temp_dir)
        follow_up_turn = second_service.handle_follow_up_answer(
            session.session_id,
            initial_turn.diagnostic_bundle.next_question.id,
            "yes",
        )

        assert follow_up_turn.session.session_id == session.session_id
        assert len(follow_up_turn.session.consultation_log.entries) >= 5
        assert follow_up_turn.session.pending_question is not None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_rejects_session_without_disclaimer() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        service = build_service(temp_dir)

        try:
            service.create_session(
                alias="Sara",
                age_group="adult",
                sex="female",
                vitals={},
                disclaimer_accepted=False,
            )
        except InvalidTurnError as exc:
            assert "disclaimer" in str(exc).lower()
        else:
            raise AssertionError("Expected disclaimer validation to fail.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_flags_red_flag_symptoms_and_preserves_direct_token_matches() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        service = build_service(temp_dir)
        session = service.create_session(
            alias="Lina",
            age_group="adult",
            sex="female",
            vitals={},
            disclaimer_accepted=True,
        )

        turn = service.handle_free_text_turn(
            session.session_id,
            "I am sneezing and I have chest pain and trouble breathing.",
        )

        assert "sneezing" in turn.normalized_input.canonical_symptoms
        assert turn.normalized_input.matched_phrases
        assert {flag.id for flag in turn.diagnostic_bundle.red_flags} >= {
            "chest_pain",
            "difficulty_breathing",
        }
        assert "urgent clinical evaluation" in turn.assistant_message.lower()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_rejects_follow_up_for_the_wrong_question() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="cura-test-"))
    try:
        service = build_service(temp_dir)
        session = service.create_session(
            alias="Omar",
            age_group="adult",
            sex="male",
            vitals={"temperature_c": 38.5},
            disclaimer_accepted=True,
        )
        turn = service.handle_free_text_turn(
            session.session_id,
            "I have fever and cough.",
        )

        try:
            service.handle_follow_up_answer(session.session_id, "q_not_the_real_question", "yes")
        except InvalidTurnError as exc:
            assert "does not match" in str(exc).lower()
        else:
            raise AssertionError("Expected mismatched follow-up validation to fail.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
