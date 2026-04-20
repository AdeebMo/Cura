import json
import shutil
import tempfile
from pathlib import Path

from app.core.config import Settings
from app.domain.session_store import InMemorySessionStore
from app.integrations.lisp_bridge import LispBridge
from app.integrations.prolog_bridge import PrologBridge
from app.repositories.consultation_log_repository import ConsultationLogRepository
from app.services.consultation_service import ConsultationService


def build_service(log_directory: Path) -> ConsultationService:
    project_root = Path(__file__).resolve().parents[2]
    test_settings = Settings(
        project_root=project_root,
        backend_root=project_root / "backend",
    )
    return ConsultationService(
        session_store=InMemorySessionStore(),
        lisp_bridge=LispBridge(test_settings),
        prolog_bridge=PrologBridge(test_settings),
        log_repository=ConsultationLogRepository(log_directory / "consultations.jsonl", test_settings),
    )


def test_service_tracks_session_state_across_a_follow_up_turn() -> None:
    project_root = Path(__file__).resolve().parents[2]
    temp_dir = Path(tempfile.mkdtemp(dir=project_root / "backend"))

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


def test_service_records_reasoning_metadata_and_snapshot() -> None:
    project_root = Path(__file__).resolve().parents[2]
    temp_dir = Path(tempfile.mkdtemp(dir=project_root / "backend"))

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

        service.log_session_snapshot(
            turn.session,
            "free_text_turn",
            {"assistant_message": turn.assistant_message},
        )

        snapshot_path = temp_dir / "consultations.jsonl"
        payload = json.loads(snapshot_path.read_text(encoding="utf-8").strip())
        assert payload["event_type"] == "free_text_turn"
        assert payload["context"]["assistant_message"] == turn.assistant_message
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
