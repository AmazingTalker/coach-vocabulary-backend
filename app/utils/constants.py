from datetime import timezone, timedelta
from enum import Enum
from typing import Dict, Optional

# Timezone used for daily boundary calculations (e.g. "today's learned count").
# All "today" references in the codebase should use this timezone.
APP_TIMEZONE = timezone(timedelta(hours=8))  # UTC+8

class PoolType(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


class ExerciseType(str, Enum):
    READING_LV1 = "reading_lv1"
    READING_LV2 = "reading_lv2"
    LISTENING_LV1 = "listening_lv1"
    SPEAKING_LV1 = "speaking_lv1"
    SPEAKING_LV2 = "speaking_lv2"


# Pool wait times in seconds
POOL_WAIT_TIMES: Dict[str, int] = {
    "P1": 10 * 60,              # 10 minutes
    "P2": 20 * 60 * 60,         # 20 hours
    "P3": 44 * 60 * 60,         # 44 hours
    "P4": 68 * 60 * 60,         # 68 hours
    "P5": 164 * 60 * 60,        # 164 hours
    "R_REVIEW": 10 * 60,        # R pool review phase: 10 minutes
    "R_PRACTICE": 20 * 60 * 60, # R pool practice phase: 20 hours
}

# Pool exercise type mapping
POOL_EXERCISE_TYPES: Dict[str, ExerciseType] = {
    "P1": ExerciseType.READING_LV1,
    "P2": ExerciseType.LISTENING_LV1,
    "P3": ExerciseType.SPEAKING_LV1,
    "P4": ExerciseType.READING_LV2,
    "P5": ExerciseType.SPEAKING_LV2,
    "R1": ExerciseType.READING_LV1,
    "R2": ExerciseType.LISTENING_LV1,
    "R3": ExerciseType.SPEAKING_LV1,
    "R4": ExerciseType.READING_LV2,
    "R5": ExerciseType.SPEAKING_LV2,
}

# Pool progression: what pool to move to when answered correctly
POOL_CORRECT_NEXT: Dict[str, str] = {
    "P1": "P2",
    "P2": "P3",
    "P3": "P4",
    "P4": "P5",
    "P5": "P6",
    "R1": "P1",
    "R2": "P2",
    "R3": "P3",
    "R4": "P4",
    "R5": "P5",
}

# Pool regression: what pool to move to when answered incorrectly
POOL_INCORRECT_NEXT: Dict[str, str] = {
    "P1": "R1",
    "P2": "R2",
    "P3": "R3",
    "P4": "R4",
    "P5": "R5",
    "R1": "R1",  # Stay in R pool
    "R2": "R2",
    "R3": "R3",
    "R4": "R4",
    "R5": "R5",
}

# R pool to P pool mapping
R_TO_P_POOL: Dict[str, str] = {
    "R1": "P1",
    "R2": "P2",
    "R3": "P3",
    "R4": "P4",
    "R5": "P5",
}

# Exercise type order for practice mode
EXERCISE_TYPE_ORDER = [
    ExerciseType.READING_LV1,
    ExerciseType.READING_LV2,
    ExerciseType.LISTENING_LV1,
    ExerciseType.SPEAKING_LV1,
    ExerciseType.SPEAKING_LV2,
]

# Limits
DAILY_LEARN_LIMIT = 50
P1_UPCOMING_LIMIT = 10
PRACTICE_MIN_WORDS = 5
PRACTICE_SESSION_SIZE = 5
REVIEW_MIN_WORDS = 3
REVIEW_MAX_WORDS = 5
LEARN_SESSION_SIZE = 5
OPTIONS_COUNT = 4
