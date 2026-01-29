from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class OptionSchema(BaseModel):
    index: int
    word_id: str
    translation: str
    image_url: Optional[str] = None


class NextReviewSchema(BaseModel):
    """下次複習等待時間（答對/答錯兩種情境）"""
    correct_wait_seconds: int
    correct_is_mastered: bool
    incorrect_wait_seconds: int


class ExerciseSchema(BaseModel):
    word_id: str
    type: str
    options: List[OptionSchema]
    correct_index: Optional[int] = None
    next_review: Optional[NextReviewSchema] = None


class ExerciseWithWordSchema(ExerciseSchema):
    word: str
    translation: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    pool: str


class WordDetailSchema(BaseModel):
    id: str
    word: str
    translation: str
    sentence: Optional[str] = None
    sentence_zh: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None


class WordDetailWithPoolSchema(WordDetailSchema):
    pool: str


class AnswerSchema(BaseModel):
    word_id: str
    correct: bool
    exercise_type: str
    user_answer: Optional[str] = None
    response_time_ms: Optional[int] = None


class AnswerResultSchema(BaseModel):
    word_id: str
    correct: bool
    previous_pool: str
    new_pool: str
    next_available_time: datetime
