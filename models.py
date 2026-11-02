from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text as SqlText, Boolean,
    ForeignKey, JSON, Float, DateTime, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from database import Base


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    level = Column(String(10), nullable=False, index=True)  # N5, N4, N3, N2, N1
    category = Column(String(50), nullable=False, index=True)  # short, medium, long, info_search, article
    source_exam = Column(String(100), nullable=True)  # e.g., "JLPT 2022.12 N3", "NHK News Easy"
    is_nhk = Column(Boolean, default=False, nullable=False)
    recommended_time_min = Column(Integer, default=3)
    content_html = Column(SqlText, nullable=False)
    translation_ru = Column(SqlText, nullable=False)
    vocabulary_json = Column(JSON, nullable=True, default=list)

    # Stream & Quality Extensions
    origin = Column(String(30), default="archive", nullable=False)  # archive, ai_generated, parametric, pdf_import
    verification_status = Column(String(30), default="expert_reviewed", nullable=False)  # expert_reviewed, auto_verified, unverified
    profile_key = Column(String(80), nullable=True, index=True)  # e.g. "N3:short:detail:1:S"
    topic_tags = Column(JSON, nullable=True, default=list)
    content_hash = Column(String(64), nullable=True, index=True)
    difficulty_vector = Column(JSON, nullable=True, default=dict)
    novelty_report = Column(JSON, nullable=True, default=dict)
    report_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    questions = relationship(
        "Question",
        back_populates="text",
        cascade="all, delete-orphan",
        order_by="Question.question_number"
    )
    user_states = relationship("UserTextState", back_populates="text", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="text", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(SqlText, nullable=False)
    general_explanation = Column(SqlText, nullable=False)
    evidence_span_id = Column(String(100), nullable=True)

    text = relationship("Text", back_populates="questions")
    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Option.option_number"
    )


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_number = Column(Integer, nullable=False)
    option_text = Column(SqlText, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    trap_type = Column(String(50), nullable=True)
    option_explanation = Column(SqlText, nullable=False)

    question = relationship("Question", back_populates="options")


class TaskSlot(Base):
    """
    Активный слот в потоке заданий пользователя.
    На каждый профиль сложности у пользователя поддерживается фиксированное количество слотов (по умолчанию 3).
    """
    __tablename__ = "task_slots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, nullable=False, default="default-user")
    profile_key = Column(String(80), index=True, nullable=False)
    position = Column(Integer, nullable=False)  # 1, 2, 3
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="SET NULL"), nullable=True)
    state = Column(String(20), default="active", nullable=False)  # active, in_progress, placeholder
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    text = relationship("Text")

    __table_args__ = (
        UniqueConstraint("user_id", "profile_key", "position", name="uq_user_profile_slot"),
    )


class UserTextState(Base):
    """
    Состояние прохождения конкретного текста конкретным пользователем.
    """
    __tablename__ = "user_text_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, nullable=False, default="default-user")
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), index=True, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, in_progress, solved
    perfect = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    solved_at = Column(DateTime, nullable=True)
    attempts_count = Column(Integer, default=0, nullable=False)
    best_score = Column(Float, default=0.0, nullable=False)
    last_score = Column(Float, default=0.0, nullable=False)
    last_answers = Column(JSON, nullable=True)
    error_question_ids = Column(JSON, nullable=True, default=list)

    text = relationship("Text", back_populates="user_states")

    __table_args__ = (
        UniqueConstraint("user_id", "text_id", name="uq_user_text_state"),
    )


class Attempt(Base):
    """
    Зафиксированная попытка сдачи задания (с идемпотентным ключом против гонок).
    """
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, nullable=False, default="default-user")
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), index=True, nullable=False)
    answers = Column(JSON, nullable=False)
    score = Column(Float, nullable=False)
    mode = Column(String(20), default="first", nullable=False)  # first, retry, retry_errors
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    text = relationship("Text", back_populates="attempts")


class GenerationJob(Base):
    """
    Задача генерации и аудита качества контента.
    """
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True)
    profile_key = Column(String(80), index=True, nullable=False)
    provider = Column(String(30), default="parametric", nullable=False)  # parametric, ollama, llm_api
    status = Column(String(20), default="completed", nullable=False)  # queued, in_progress, completed, failed, budget_exceeded
    cost_usd = Column(Float, default=0.0, nullable=False)
    error_log = Column(SqlText, nullable=True)
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

