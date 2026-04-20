from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class VitalsModel(BaseModel):
    temperature_c: float | None = None
    pain_severity: int | None = Field(default=None, ge=0, le=10)
    hydration_status: Literal["normal", "reduced", "poor"] | None = None


class CreateSessionRequest(BaseModel):
    alias: str = Field(min_length=1, max_length=80)
    age_group: Literal["child", "teen", "adult", "older_adult"]
    sex: Literal["female", "male", "other", "prefer_not_to_say"] | None = None
    vitals: VitalsModel = Field(default_factory=VitalsModel)
    disclaimer_accepted: bool


class ConsultationEntryModel(BaseModel):
    role: str
    message: str
    timestamp: str
    metadata: dict[str, object] = Field(default_factory=dict)


class MatchedPhraseModel(BaseModel):
    source: str
    canonical: str


class NormalizedInputModel(BaseModel):
    canonical_symptoms: list[str] = Field(default_factory=list)
    matched_phrases: list[MatchedPhraseModel] = Field(default_factory=list)
    unknown_terms: list[str] = Field(default_factory=list)


class DiagnosisResultModel(BaseModel):
    condition: str
    rule_strength: str
    matched_symptoms: list[str] = Field(default_factory=list)
    missing_symptoms: list[str] = Field(default_factory=list)
    conflicting_symptoms: list[str] = Field(default_factory=list)
    explanation: str


class SafetyAlertModel(BaseModel):
    id: str
    severity: str
    message: str
    trigger: str


class FollowUpQuestionModel(BaseModel):
    id: str
    prompt: str
    target_symptom: str
    rationale: str


class SessionStateModel(BaseModel):
    session_id: str
    alias: str
    age_group: str
    sex: str | None = None
    vitals: dict[str, object] = Field(default_factory=dict)
    confirmed_symptoms: list[str] = Field(default_factory=list)
    denied_symptoms: list[str] = Field(default_factory=list)
    unknown_symptoms: list[str] = Field(default_factory=list)
    asked_question_ids: list[str] = Field(default_factory=list)
    pending_question: FollowUpQuestionModel | None = None
    consultation_history: list[ConsultationEntryModel] = Field(default_factory=list)
    created_at: str
    updated_at: str


class CreateSessionResponse(BaseModel):
    session_id: str
    assistant_message: str
    state: SessionStateModel


class UserTurnRequest(BaseModel):
    type: Literal["free_text", "follow_up_answer"]
    message: str | None = None
    question_id: str | None = None
    response: Literal["yes", "no", "unknown"] | None = None


class TurnResponse(BaseModel):
    assistant_message: str
    normalized_input: NormalizedInputModel | None = None
    diagnoses: list[DiagnosisResultModel] = Field(default_factory=list)
    next_question: FollowUpQuestionModel | None = None
    red_flags: list[SafetyAlertModel] = Field(default_factory=list)
    explanation_trace: list[str] = Field(default_factory=list)
    state: SessionStateModel

