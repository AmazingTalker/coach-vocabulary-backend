import random
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.word import Word
from app.repositories.word_repository import WordRepository
from app.schemas.tutorial import (
    VocabularyTutorialResponse,
    TutorialStepSchema,
    TutorialCompleteResponse,
    TutorialItemType,
    TutorialItemSchema,
    TutorialStatusResponse,
    TutorialCompleteRequest,
)
from app.schemas.common import OptionSchema, WordDetailSchema
from app.utils.constants import ExerciseType

router = APIRouter(prefix="/api/tutorial", tags=["tutorial"])

# Tutorial words configuration
TARGET_WORD = "apple"
DISTRACTOR_WORDS = ["banana", "grape", "mango"]

# Tutorial exercise types in order
TUTORIAL_EXERCISE_TYPES = [
    ExerciseType.READING_LV1,
    ExerciseType.READING_LV2,
    ExerciseType.LISTENING_LV1,
    ExerciseType.SPEAKING_LV1,
    ExerciseType.SPEAKING_LV2,
]

# Mapping from TutorialItemType to user model column name
TUTORIAL_TYPE_COLUMN_MAP = {
    "learn": "tutorial_learn_completed_at",
    "reading_lv1": "tutorial_reading_lv1_completed_at",
    "reading_lv2": "tutorial_reading_lv2_completed_at",
    "listening_lv1": "tutorial_listening_lv1_completed_at",
    "speaking_lv1": "tutorial_speaking_lv1_completed_at",
    "speaking_lv2": "tutorial_speaking_lv2_completed_at",
}

# Ordered list of tutorial item types (learn first, then exercises)
TUTORIAL_ITEM_ORDER = [
    TutorialItemType.LEARN,
    TutorialItemType.READING_LV1,
    TutorialItemType.READING_LV2,
    TutorialItemType.LISTENING_LV1,
    TutorialItemType.SPEAKING_LV1,
    TutorialItemType.SPEAKING_LV2,
]

# Mapping from TutorialItemType to ExerciseType (learn has no exercise)
TUTORIAL_ITEM_EXERCISE_MAP = {
    TutorialItemType.READING_LV1: ExerciseType.READING_LV1,
    TutorialItemType.READING_LV2: ExerciseType.READING_LV2,
    TutorialItemType.LISTENING_LV1: ExerciseType.LISTENING_LV1,
    TutorialItemType.SPEAKING_LV1: ExerciseType.SPEAKING_LV1,
    TutorialItemType.SPEAKING_LV2: ExerciseType.SPEAKING_LV2,
}


def build_tutorial_options(
    correct_word: Word,
    distractor_words: List[Word],
) -> tuple[List[OptionSchema], int]:
    """
    Build randomized options for a tutorial step.

    Returns:
        tuple: (options list, correct_index)
    """
    all_words = distractor_words + [correct_word]
    random.shuffle(all_words)

    correct_index = next(
        i for i, w in enumerate(all_words) if w.id == correct_word.id
    )

    options = []
    for i, word in enumerate(all_words):
        options.append(OptionSchema(
            index=i,
            word_id=str(word.id),
            translation=word.translation,
            image_url=word.image_url,
        ))

    return options, correct_index


def _fetch_tutorial_words(db: Session):
    """Fetch target word and distractor words for tutorial."""
    word_repo = WordRepository(db)

    target_word = word_repo.get_by_word(TARGET_WORD)
    if not target_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tutorial word '{TARGET_WORD}' not found in database"
        )

    distractor_words = []
    for word_name in DISTRACTOR_WORDS:
        word = word_repo.get_by_word(word_name)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tutorial word '{word_name}' not found in database"
            )
        distractor_words.append(word)

    return target_word, distractor_words


def _build_word_detail(target_word: Word) -> WordDetailSchema:
    """Build WordDetailSchema from a Word model."""
    return WordDetailSchema(
        id=str(target_word.id),
        word=target_word.word,
        translation=target_word.translation,
        sentence=target_word.sentence,
        sentence_zh=target_word.sentence_zh,
        image_url=target_word.image_url,
        audio_url=target_word.audio_url,
    )


@router.get("/status", response_model=TutorialStatusResponse)
def get_tutorial_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the tutorial status with per-item completion tracking.

    Returns the target word and 6 tutorial items (learn + 5 exercises)
    with their completion status and exercise step details.
    """
    target_word, distractor_words = _fetch_tutorial_words(db)
    word_detail = _build_word_detail(target_word)
    target_word_id = str(target_word.id)

    items = []
    step_number = 0
    for item_type in TUTORIAL_ITEM_ORDER:
        col_name = TUTORIAL_TYPE_COLUMN_MAP[item_type.value]
        completed_at = getattr(current_user, col_name)

        if item_type == TutorialItemType.LEARN:
            # Learn step has no exercise
            items.append(TutorialItemSchema(
                type=item_type.value,
                completed=completed_at is not None,
                completed_at=completed_at,
                step=None,
            ))
        else:
            step_number += 1
            exercise_type = TUTORIAL_ITEM_EXERCISE_MAP[item_type]

            if exercise_type in [ExerciseType.SPEAKING_LV1, ExerciseType.SPEAKING_LV2]:
                step = TutorialStepSchema(
                    step=step_number,
                    word_id=target_word_id,
                    type=exercise_type.value,
                    options=[],
                    correct_index=None,
                )
            else:
                options, correct_index = build_tutorial_options(target_word, distractor_words)
                step = TutorialStepSchema(
                    step=step_number,
                    word_id=target_word_id,
                    type=exercise_type.value,
                    options=options,
                    correct_index=correct_index,
                )

            items.append(TutorialItemSchema(
                type=item_type.value,
                completed=completed_at is not None,
                completed_at=completed_at,
                step=step,
            ))

    return TutorialStatusResponse(
        word=word_detail,
        items=items,
    )


@router.post("/complete", response_model=TutorialCompleteResponse)
def complete_tutorial_item(
    request: TutorialCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a single tutorial item as completed.

    Accepts a tutorial item type and sets the corresponding
    completion timestamp if not already set.
    """
    col_name = TUTORIAL_TYPE_COLUMN_MAP[request.type.value]
    existing = getattr(current_user, col_name)

    if existing is not None:
        return TutorialCompleteResponse(success=True, completed_at=existing)

    now = datetime.now(timezone.utc)
    setattr(current_user, col_name, now)
    db.commit()

    return TutorialCompleteResponse(success=True, completed_at=now)


@router.get("/vocabulary", response_model=VocabularyTutorialResponse)
def get_vocabulary_tutorial(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the vocabulary tutorial session.

    Returns a tutorial with 5 exercise steps using "apple" as the target word
    and "banana", "grape", "mango" as distractors.
    """
    target_word, distractor_words = _fetch_tutorial_words(db)
    target_word_id = str(target_word.id)
    word_detail = _build_word_detail(target_word)

    # Build tutorial steps
    steps = []
    for i, exercise_type in enumerate(TUTORIAL_EXERCISE_TYPES):
        # Speaking exercises don't have options
        if exercise_type in [ExerciseType.SPEAKING_LV1, ExerciseType.SPEAKING_LV2]:
            step = TutorialStepSchema(
                step=i + 1,
                word_id=target_word_id,
                type=exercise_type.value,
                options=[],
                correct_index=None,
            )
        else:
            options, correct_index = build_tutorial_options(target_word, distractor_words)
            step = TutorialStepSchema(
                step=i + 1,
                word_id=target_word_id,
                type=exercise_type.value,
                options=options,
                correct_index=correct_index,
            )
        steps.append(step)

    return VocabularyTutorialResponse(
        word=word_detail,
        steps=steps,
    )


@router.post("/vocabulary/complete", response_model=TutorialCompleteResponse)
def complete_vocabulary_tutorial(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark the vocabulary tutorial as completed.

    Sets the vocabulary_tutorial_completed_at timestamp for the current user.
    Also sets all 6 granular tutorial completion columns if not already set.
    """
    now = datetime.now(timezone.utc)

    current_user.vocabulary_tutorial_completed_at = now

    # Also set all granular columns if not already set
    for col_name in TUTORIAL_TYPE_COLUMN_MAP.values():
        if getattr(current_user, col_name) is None:
            setattr(current_user, col_name, now)

    db.commit()

    return TutorialCompleteResponse(success=True, completed_at=now)
