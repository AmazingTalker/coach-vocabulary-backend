from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.common import (
    WordDetailWithPoolSchema,
    ExerciseSchema,
    AnswerSchema,
    AnswerResultSchema,
)


class ReviewSessionResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    words: List[WordDetailWithPoolSchema]
    exercises: List[ExerciseSchema]


class ReviewCompleteRequest(BaseModel):
    word_ids: List[str]
    answers: List[AnswerSchema]


class ReviewCompleteResponse(BaseModel):
    success: bool
    words_completed: int
    next_practice_time: datetime


class ReviewSubmitRequest(BaseModel):
    answers: List[AnswerSchema]


class ReviewSummary(BaseModel):
    correct_count: int
    incorrect_count: int
    returned_to_p: int


class ReviewSubmitResponse(BaseModel):
    success: bool
    results: List[AnswerResultSchema]
    summary: ReviewSummary
