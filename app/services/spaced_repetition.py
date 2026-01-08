from datetime import datetime, timedelta, timezone
from typing import Optional

from app.utils.constants import (
    POOL_WAIT_TIMES,
    POOL_CORRECT_NEXT,
    POOL_INCORRECT_NEXT,
    POOL_EXERCISE_TYPES,
    R_TO_P_POOL,
    ExerciseType,
)


def get_next_available_time(pool: str, is_review_phase: bool = False) -> datetime:
    """Calculate the next available time based on pool type."""
    now = datetime.now(timezone.utc)

    if pool.startswith("R"):
        if is_review_phase:
            wait_seconds = POOL_WAIT_TIMES["R_REVIEW"]
        else:
            wait_seconds = POOL_WAIT_TIMES["R_PRACTICE"]
    elif pool in POOL_WAIT_TIMES:
        wait_seconds = POOL_WAIT_TIMES[pool]
    else:
        # P0 or P6 - no wait time
        return now

    return now + timedelta(seconds=wait_seconds)


def get_exercise_type(pool: str) -> Optional[ExerciseType]:
    """Get the exercise type for a given pool."""
    return POOL_EXERCISE_TYPES.get(pool)


def process_correct_answer(current_pool: str) -> tuple[str, datetime, bool]:
    """
    Process a correct answer and return the new pool, next available time,
    and whether it's in review phase.

    Returns:
        tuple: (new_pool, next_available_time, is_in_review_phase)
    """
    new_pool = POOL_CORRECT_NEXT.get(current_pool, current_pool)

    # If moving from R pool to P pool, use the P pool's wait time
    if current_pool.startswith("R") and new_pool.startswith("P"):
        next_time = get_next_available_time(new_pool)
        return new_pool, next_time, False

    # Regular P pool progression
    if new_pool == "P6":
        # Mastered - no next available time needed
        return new_pool, datetime.now(timezone.utc), False

    next_time = get_next_available_time(new_pool)
    return new_pool, next_time, False


def process_incorrect_answer(current_pool: str) -> tuple[str, datetime, bool]:
    """
    Process an incorrect answer and return the new pool, next available time,
    and whether it's in review phase.

    Returns:
        tuple: (new_pool, next_available_time, is_in_review_phase)
    """
    new_pool = POOL_INCORRECT_NEXT.get(current_pool, current_pool)

    # Moving to R pool or staying in R pool - enter review phase
    is_in_review_phase = True
    next_time = get_next_available_time(new_pool, is_review_phase=True)

    return new_pool, next_time, is_in_review_phase


def complete_review_phase(pool: str) -> tuple[datetime, bool]:
    """
    Complete the review phase and move to practice phase.

    Returns:
        tuple: (next_available_time, is_in_review_phase)
    """
    # After review, wait 20 hours for practice
    next_time = get_next_available_time(pool, is_review_phase=False)
    return next_time, False


def is_p_pool(pool: str) -> bool:
    """Check if the pool is a P pool (P0-P6)."""
    return pool.startswith("P")


def is_r_pool(pool: str) -> bool:
    """Check if the pool is an R pool (R1-R5)."""
    return pool.startswith("R")


def get_corresponding_p_pool(r_pool: str) -> Optional[str]:
    """Get the corresponding P pool for an R pool."""
    return R_TO_P_POOL.get(r_pool)
