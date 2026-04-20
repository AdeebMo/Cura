from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


def stable_sorted(values: set[str]) -> list[str]:
    return sorted(values)


@dataclass(slots=True)
class MatchedPhrase:
    source: str
    canonical: str


@dataclass(slots=True)
class NormalizedInput:
    canonical_symptoms: list[str]
    matched_phrases: list[MatchedPhrase] = field(default_factory=list)
    unknown_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DiagnosisResult:
    condition: str
    rule_strength: str
    matched_symptoms: list[str]
    missing_symptoms: list[str]
    conflicting_symptoms: list[str]
    explanation: str


@dataclass(slots=True)
class SafetyAlert:
    id: str
    severity: str
    message: str
    trigger: str


@dataclass(slots=True)
class FollowUpQuestion:
    id: str
    prompt: str
    target_symptom: str
    rationale: str


@dataclass(slots=True)
class DiagnosticBundle:
    diagnoses: list[DiagnosisResult] = field(default_factory=list)
    next_question: FollowUpQuestion | None = None
    red_flags: list[SafetyAlert] = field(default_factory=list)
    explanation_trace: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ConsultationEntry:
    role: str
    message: str
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


@dataclass(slots=True)
class ConsultationLog:
    entries: list[ConsultationEntry] = field(default_factory=list)

    def append(self, role: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        self.entries.append(
            ConsultationEntry(role=role, message=message, metadata=metadata or {})
        )

    def to_dict(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self.entries]


@dataclass(slots=True)
class MedicalRecord:
    alias: str
    age_group: str
    sex: str | None = None
    vitals: dict[str, Any] = field(default_factory=dict)
    confirmed_symptoms: set[str] = field(default_factory=set)
    denied_symptoms: set[str] = field(default_factory=set)
    unknown_symptoms: set[str] = field(default_factory=set)

    def confirm_symptoms(self, symptoms: list[str]) -> None:
        for symptom in symptoms:
            self.confirmed_symptoms.add(symptom)
            self.denied_symptoms.discard(symptom)
            self.unknown_symptoms.discard(symptom)

    def set_symptom_state(self, symptom: str, response: str) -> None:
        self.confirmed_symptoms.discard(symptom)
        self.denied_symptoms.discard(symptom)
        self.unknown_symptoms.discard(symptom)

        if response == "yes":
            self.confirmed_symptoms.add(symptom)
        elif response == "no":
            self.denied_symptoms.add(symptom)
        else:
            self.unknown_symptoms.add(symptom)

    def state_payload(self) -> dict[str, Any]:
        return {
            "alias": self.alias,
            "age_group": self.age_group,
            "sex": self.sex,
            "vitals": self.vitals,
            "confirmed_symptoms": stable_sorted(self.confirmed_symptoms),
            "denied_symptoms": stable_sorted(self.denied_symptoms),
            "unknown_symptoms": stable_sorted(self.unknown_symptoms),
        }


@dataclass(slots=True)
class UserSession:
    medical_record: MedicalRecord
    consultation_log: ConsultationLog = field(default_factory=ConsultationLog)
    session_id: str = field(default_factory=lambda: str(uuid4()))
    asked_question_ids: set[str] = field(default_factory=set)
    pending_question: FollowUpQuestion | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def add_user_message(self, message: str, metadata: dict[str, Any] | None = None) -> None:
        self.consultation_log.append("user", message, metadata)
        self.touch()

    def add_assistant_message(
        self, message: str, metadata: dict[str, Any] | None = None
    ) -> None:
        self.consultation_log.append("assistant", message, metadata)
        self.touch()

    def set_pending_question(self, question: FollowUpQuestion | None) -> None:
        self.pending_question = question
        if question:
            self.asked_question_ids.add(question.id)
        self.touch()

    def state_payload(self) -> dict[str, Any]:
        return {
            **self.medical_record.state_payload(),
            "session_id": self.session_id,
            "asked_question_ids": stable_sorted(self.asked_question_ids),
            "pending_question": asdict(self.pending_question) if self.pending_question else None,
            "consultation_history": self.consultation_log.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(slots=True)
class TurnResult:
    session: UserSession
    assistant_message: str
    normalized_input: NormalizedInput | None
    diagnostic_bundle: DiagnosticBundle

