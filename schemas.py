from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ==========================================
# 1. Catalog / List Schemas
# ==========================================

class TextListItemSchema(BaseModel):
    id: int
    title: str
    level: str
    category: str
    source_exam: Optional[str] = None
    is_nhk: bool = False
    recommended_time_min: int
    question_count: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. Strict Anti-Cheat Reading Schemas
# (No is_correct, explanations, translations, or evidence IDs)
# ==========================================

class OptionReadSchema(BaseModel):
    id: int
    option_number: int
    option_text: str

    model_config = ConfigDict(from_attributes=True)


class QuestionReadSchema(BaseModel):
    id: int
    question_number: int
    question_text: str
    options: List[OptionReadSchema]

    model_config = ConfigDict(from_attributes=True)


class TextReadSchema(BaseModel):
    id: int
    title: str
    level: str
    category: str
    source_exam: Optional[str] = None
    is_nhk: bool = False
    recommended_time_min: int
    content_html: str
    questions: List[QuestionReadSchema]

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. Submission Schemas
# ==========================================

class AnswerSubmissionSchema(BaseModel):
    question_id: int
    selected_option_id: int


class SubmitPayloadSchema(BaseModel):
    answers: List[AnswerSubmissionSchema]
    time_spent_sec: Optional[int] = None


# ==========================================
# 4. Analysis / Post-Submit Schemas
# ==========================================

class OptionAnalysisSchema(BaseModel):
    id: int
    option_number: int
    option_text: str
    is_correct: bool
    option_explanation: str
    was_selected: bool

    model_config = ConfigDict(from_attributes=True)


class QuestionAnalysisSchema(BaseModel):
    id: int
    question_number: int
    question_text: str
    general_explanation: str
    evidence_span_id: Optional[str] = None
    is_user_correct: bool
    selected_option_id: Optional[int] = None
    correct_option_id: int
    options: List[OptionAnalysisSchema]

    model_config = ConfigDict(from_attributes=True)


class VocabularyItemSchema(BaseModel):
    word: str
    furigana: str
    translation: str


class TextAnalysisSchema(BaseModel):
    id: int
    title: str
    level: str
    category: str
    source_exam: Optional[str] = None
    is_nhk: bool = False
    recommended_time_min: int
    content_html: str
    translation_ru: str
    vocabulary: List[VocabularyItemSchema]
    total_questions: int
    correct_count: int
    score_percent: float
    time_spent_sec: Optional[int] = None
    questions: List[QuestionAnalysisSchema]

    model_config = ConfigDict(from_attributes=True)
