import json
import shutil
import tempfile
from pathlib import Path

from app.bootstrap import build_consultation_service
from app.core.config import Settings


def build_service(work_directory: Path):
    project_root = Path(__file__).resolve().parents[2]
    test_settings = Settings(
        project_root=project_root,
        backend_root=work_directory,
        database_url=f"sqlite+pysqlite:///{(work_directory / 'cura-test.db').as_posix()}",
    )
    return build_consultation_service(test_settings)


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

        snapshot_path = temp_dir / "data" / "consultations.jsonl"
        payload = json.loads(snapshot_path.read_text(encoding="utf-8").strip())
        assert payload["event_type"] == "free_text_turn"
        assert payload["context"]["assistant_message"] == turn.assistant_message
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_service_persists_session_state_across_service_instances() -> None:
    project_root = Path(__file__).resolve().parents[2]
    temp_dir = Path(tempfile.mkdtemp(dir=project_root / "backend"))

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
