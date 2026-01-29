"""add_granular_tutorial_completion

Revision ID: l7g8h9i0j1k2
Revises: k6f7g8h9i0j1
Create Date: 2024-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'l7g8h9i0j1k2'
down_revision: Union[str, None] = 'k6f7g8h9i0j1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GRANULAR_COLUMNS = [
    'tutorial_learn_completed_at',
    'tutorial_reading_lv1_completed_at',
    'tutorial_reading_lv2_completed_at',
    'tutorial_listening_lv1_completed_at',
    'tutorial_speaking_lv1_completed_at',
    'tutorial_speaking_lv2_completed_at',
]


def upgrade() -> None:
    # Add 6 new nullable DateTime columns
    for col in GRANULAR_COLUMNS:
        op.add_column('users', sa.Column(col, sa.DateTime(timezone=True), nullable=True))

    # Backfill: copy vocabulary_tutorial_completed_at into all 6 new columns
    # for users who already completed the tutorial
    op.execute(
        sa.text(
            "UPDATE users SET "
            "tutorial_learn_completed_at = vocabulary_tutorial_completed_at, "
            "tutorial_reading_lv1_completed_at = vocabulary_tutorial_completed_at, "
            "tutorial_reading_lv2_completed_at = vocabulary_tutorial_completed_at, "
            "tutorial_listening_lv1_completed_at = vocabulary_tutorial_completed_at, "
            "tutorial_speaking_lv1_completed_at = vocabulary_tutorial_completed_at, "
            "tutorial_speaking_lv2_completed_at = vocabulary_tutorial_completed_at "
            "WHERE vocabulary_tutorial_completed_at IS NOT NULL"
        )
    )


def downgrade() -> None:
    for col in GRANULAR_COLUMNS:
        op.drop_column('users', col)
