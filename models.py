from sqlalchemy import Column, Integer, String, Text as SqlText, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    level = Column(String(10), nullable=False, index=True)  # N5, N4, N3, N2, N1
    category = Column(String(50), nullable=False, index=True)  # short, medium, long, info_search, article
    recommended_time_min = Column(Integer, default=3)
    content_html = Column(SqlText, nullable=False)
    translation_ru = Column(SqlText, nullable=False)
    vocabulary_json = Column(JSON, nullable=True, default=list)

    questions = relationship(
        "Question",
        back_populates="text",
        cascade="all, delete-orphan",
        order_by="Question.question_number"
    )


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
    option_explanation = Column(SqlText, nullable=False)

    question = relationship("Question", back_populates="options")

