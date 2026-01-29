from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import ExerciseSchema, WordDetailSchema


class TutorialStepSchema(ExerciseSchema):
    step: int


class VocabularyTutorialResponse(BaseModel):
    word: WordDetailSchema
    steps: List[TutorialStepSchema]


class TutorialCompleteResponse(BaseModel):
    success: bool
    completed_at: Optional[datetime] = None


class TutorialItemType(str, Enum):
    LEARN = "learn"
    READING_LV1 = "reading_lv1"
    READING_LV2 = "reading_lv2"
    LISTENING_LV1 = "listening_lv1"
    SPEAKING_LV1 = "speaking_lv1"
    SPEAKING_LV2 = "speaking_lv2"


class TutorialItemSchema(BaseModel):
    type: str
    completed: bool
    completed_at: Optional[datetime] = None
    step: Optional[TutorialStepSchema] = None


class TutorialStatusResponse(BaseModel):
    word: WordDetailSchema
    items: List[TutorialItemSchema]


class TutorialCompleteRequest(BaseModel):
    type: TutorialItemType
