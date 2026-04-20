"""initial catalog and session schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260420_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("alias", sa.String(length=80), nullable=False),
        sa.Column("age_group", sa.String(length=32), nullable=False),
        sa.Column("sex", sa.String(length=32), nullable=True),
        sa.Column("vitals", sa.JSON(), nullable=False),
        sa.Column("confirmed_symptoms", sa.JSON(), nullable=False),
        sa.Column("denied_symptoms", sa.JSON(), nullable=False),
        sa.Column("unknown_symptoms", sa.JSON(), nullable=False),
        sa.Column("pending_question", sa.JSON(), nullable=True),
        sa.Column("asked_question_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_updated_at", "sessions", ["updated_at"], unique=False)

    op.create_table(
        "consultation_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "ordinal", name="uq_consultation_messages_session_ordinal"),
    )
    op.create_index(
        "ix_consultation_messages_session_ordinal",
        "consultation_messages",
        ["session_id", "ordinal"],
        unique=False,
    )

    op.create_table(
        "consultation_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_consultation_events_session_created",
        "consultation_events",
        ["session_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "symptoms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("canonical_key", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("body_system", sa.String(length=80), nullable=False),
        sa.Column("intake_priority", sa.Integer(), nullable=False),
        sa.Column("is_red_flag_candidate", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canonical_key"),
    )
    op.create_index("ix_symptoms_canonical_key", "symptoms", ["canonical_key"], unique=True)

    op.create_table(
        "conditions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("condition_key", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("condition_key"),
    )
    op.create_index("ix_conditions_condition_key", "conditions", ["condition_key"], unique=True)

    op.create_table(
        "question_catalog",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("target_symptom", sa.String(length=80), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_question_catalog_target_symptom", "question_catalog", ["target_symptom"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_question_catalog_target_symptom", table_name="question_catalog")
    op.drop_table("question_catalog")
    op.drop_index("ix_conditions_condition_key", table_name="conditions")
    op.drop_table("conditions")
    op.drop_index("ix_symptoms_canonical_key", table_name="symptoms")
    op.drop_table("symptoms")
    op.drop_index("ix_consultation_events_session_created", table_name="consultation_events")
    op.drop_table("consultation_events")
    op.drop_index("ix_consultation_messages_session_ordinal", table_name="consultation_messages")
    op.drop_table("consultation_messages")
    op.drop_index("ix_sessions_updated_at", table_name="sessions")
    op.drop_table("sessions")
