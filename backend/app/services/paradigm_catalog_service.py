from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.data import SYMPTOM_CATALOG
from app.repositories.condition_catalog_repository import ConditionCatalogRepository, ConditionSeed
from app.repositories.question_catalog_repository import QuestionCatalogRepository, QuestionSeed
from app.repositories.symptom_catalog_repository import SymptomCatalogRepository
from app.services.normalization_service import NormalizationService


def _humanize_key(value: str) -> str:
    return value.replace("_", " ").title()


def _parse_atom_list(raw_values: str) -> list[str]:
    return [item.strip() for item in raw_values.split(",") if item.strip()]


@dataclass(frozen=True, slots=True)
class PrologCatalogSnapshot:
    symptom_keys: set[str]
    condition_seeds: tuple[ConditionSeed, ...]
    question_seeds: tuple[QuestionSeed, ...]

    @property
    def condition_keys(self) -> set[str]:
        return {item.condition_key for item in self.condition_seeds}

    @property
    def question_ids(self) -> set[str]:
        return {item.id for item in self.question_seeds}


class PrologCatalogInspector:
    _disease_pattern = re.compile(
        r"^disease\((?P<condition>[a-z_]+), \[(?P<required>[a-z_, ]*)\], "
        r"\[(?P<supportive>[a-z_, ]*)\], \[(?P<contra>[a-z_, ]*)\]\)\.$"
    )
    _question_pattern = re.compile(
        r'^follow_up_question\((?P<symptom>[a-z_]+), (?P<question_id>[a-z_]+), '
        r'"(?P<prompt>.*?)", "(?P<rationale>.*?)", (?P<priority>\d+)\)\.$'
    )
    _red_flag_pattern = re.compile(
        r'^red_flag_symptom\((?P<symptom>[a-z_]+), (?P<severity>[a-z_]+), "(?P<message>.*)"\)\.$'
    )
    _derived_red_flag_ids = {"severe_dehydration"}

    def __init__(self, inspector_settings: Settings = settings) -> None:
        self._settings = inspector_settings

    def inspect(self) -> PrologCatalogSnapshot:
        symptom_keys: set[str] = set()
        condition_seeds: list[ConditionSeed] = []
        question_seeds: list[QuestionSeed] = []

        facts_path = self._settings.project_root / "prolog" / "src" / "facts.pl"
        for raw_line in facts_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue

            match = self._disease_pattern.match(line)
            if match is None:
                continue

            required = _parse_atom_list(match.group("required"))
            supportive = _parse_atom_list(match.group("supportive"))
            contra = _parse_atom_list(match.group("contra"))
            symptom_keys.update(required)
            symptom_keys.update(supportive)
            symptom_keys.update(contra)
            condition_key = match.group("condition")
            condition_seeds.append(
                ConditionSeed(
                    condition_key=condition_key,
                    display_name=_humanize_key(condition_key),
                    notes="Seeded from the Prolog disease rule base.",
                )
            )

        questions_path = self._settings.project_root / "prolog" / "src" / "questions.pl"
        for raw_line in questions_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue

            match = self._question_pattern.match(line)
            if match is None:
                continue

            target_symptom = match.group("symptom")
            symptom_keys.add(target_symptom)
            question_seeds.append(
                QuestionSeed(
                    id=match.group("question_id"),
                    target_symptom=target_symptom,
                    prompt=match.group("prompt"),
                    rationale=match.group("rationale"),
                    priority=int(match.group("priority")),
                )
            )

        red_flags_path = self._settings.project_root / "prolog" / "src" / "red_flags.pl"
        for raw_line in red_flags_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue

            match = self._red_flag_pattern.match(line)
            if match is None:
                continue

            symptom = match.group("symptom")
            if symptom not in self._derived_red_flag_ids:
                symptom_keys.add(symptom)

        return PrologCatalogSnapshot(
            symptom_keys=symptom_keys,
            condition_seeds=tuple(condition_seeds),
            question_seeds=tuple(question_seeds),
        )


class ParadigmCatalogError(RuntimeError):
    """Raised when the Python, Lisp, and Prolog catalogs drift apart."""


class CatalogBootstrapService:
    def __init__(
        self,
        symptom_catalog_repository: SymptomCatalogRepository,
        condition_catalog_repository: ConditionCatalogRepository,
        question_catalog_repository: QuestionCatalogRepository,
        prolog_catalog_inspector: PrologCatalogInspector,
    ) -> None:
        self._symptom_catalog_repository = symptom_catalog_repository
        self._condition_catalog_repository = condition_catalog_repository
        self._question_catalog_repository = question_catalog_repository
        self._prolog_catalog_inspector = prolog_catalog_inspector

    def seed_catalogs(self, db_session: Session) -> PrologCatalogSnapshot:
        snapshot = self._prolog_catalog_inspector.inspect()
        self._symptom_catalog_repository.seed(db_session, SYMPTOM_CATALOG)
        self._condition_catalog_repository.seed(db_session, snapshot.condition_seeds)
        self._question_catalog_repository.seed(db_session, snapshot.question_seeds)
        db_session.flush()
        return snapshot


class ParadigmCatalogValidationService:
    def __init__(
        self,
        symptom_catalog_repository: SymptomCatalogRepository,
        condition_catalog_repository: ConditionCatalogRepository,
        question_catalog_repository: QuestionCatalogRepository,
        normalization_service: NormalizationService,
        prolog_catalog_inspector: PrologCatalogInspector,
    ) -> None:
        self._symptom_catalog_repository = symptom_catalog_repository
        self._condition_catalog_repository = condition_catalog_repository
        self._question_catalog_repository = question_catalog_repository
        self._normalization_service = normalization_service
        self._prolog_catalog_inspector = prolog_catalog_inspector

    def validate(self, db_session: Session) -> None:
        prolog_snapshot = self._prolog_catalog_inspector.inspect()
        lisp_symptom_keys = self._normalization_service.canonical_inventory()
        db_symptom_keys = self._symptom_catalog_repository.canonical_keys(db_session)
        db_condition_keys = self._condition_catalog_repository.condition_keys(db_session)
        db_question_ids = self._question_catalog_repository.question_ids(db_session)

        errors: list[str] = []

        missing_lisp_keys = sorted(lisp_symptom_keys - db_symptom_keys)
        if missing_lisp_keys:
            errors.append(
                "Missing DB symptom seeds for Lisp canonical keys: " + ", ".join(missing_lisp_keys)
            )

        missing_prolog_symptoms = sorted(prolog_snapshot.symptom_keys - db_symptom_keys)
        if missing_prolog_symptoms:
            errors.append(
                "Missing DB symptom seeds for Prolog symptom references: "
                + ", ".join(missing_prolog_symptoms)
            )

        missing_conditions = sorted(prolog_snapshot.condition_keys - db_condition_keys)
        if missing_conditions:
            errors.append(
                "Missing DB condition seeds for Prolog conditions: " + ", ".join(missing_conditions)
            )

        missing_questions = sorted(prolog_snapshot.question_ids - db_question_ids)
        if missing_questions:
            errors.append(
                "Missing DB question seeds for Prolog follow-up questions: "
                + ", ".join(missing_questions)
            )

        if errors:
            raise ParadigmCatalogError(" | ".join(errors))
