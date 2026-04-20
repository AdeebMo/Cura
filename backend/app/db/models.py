from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONValue, UTCDateTime, utc_now


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    alias: Mapped[str] = mapped_column(String(80), nullable=False)
    age_group: Mapped[str] = mapped_column(String(32), nullable=False)
    sex: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vitals: Mapped[dict[str, object]] = mapped_column(JSONValue, default=dict, nullable=False)
    confirmed_symptoms: Mapped[list[str]] = mapped_column(JSONValue, default=list, nullable=False)
    denied_symptoms: Mapped[list[str]] = mapped_column(JSONValue, default=list, nullable=False)
    unknown_symptoms: Mapped[list[str]] = mapped_column(JSONValue, default=list, nullable=False)
    pending_question: Mapped[dict[str, object] | None] = mapped_column(JSONValue, nullable=True)
    asked_question_ids: Mapped[list[str]] = mapped_column(JSONValue, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        index=True,
    )

    messages: Mapped[list["ConsultationMessageModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConsultationMessageModel.ordinal",
    )
    events: Mapped[list["ConsultationEventModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConsultationEventModel.created_at",
    )


class ConsultationMessageModel(Base):
    __tablename__ = "consultation_messages"
    __table_args__ = (
        UniqueConstraint("session_id", "ordinal", name="uq_consultation_messages_session_ordinal"),
        Index("ix_consultation_messages_session_ordinal", "session_id", "ordinal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_metadata: Mapped[dict[str, object]] = mapped_column(
        "metadata_json",
        JSONValue,
        default=dict,
        nullable=False,
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now, nullable=False)

    session: Mapped[SessionModel] = relationship(back_populates="messages")


class ConsultationEventModel(Base):
    __tablename__ = "consultation_events"
    __table_args__ = (Index("ix_consultation_events_session_created", "session_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONValue, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now, nullable=False)

    session: Mapped[SessionModel] = relationship(back_populates="events")


class SymptomCatalogModel(Base):
    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    body_system: Mapped[str] = mapped_column(String(80), nullable=False)
    intake_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    is_red_flag_candidate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ConditionCatalogModel(Base):
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    condition_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class QuestionCatalogModel(Base):
    __tablename__ = "question_catalog"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    target_symptom: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
