"""add_exercise_session_id_to_events

Revision ID: j5e6f7g8h9i0
Revises: i4d5e6f7g8h9
Create Date: 2024-01-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'j5e6f7g8h9i0'
down_revision: Union[str, None] = 'i4d5e6f7g8h9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('exercise_session_id', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_events_exercise_session_id'), 'events', ['exercise_session_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_events_exercise_session_id'), table_name='events')
    op.drop_column('events', 'exercise_session_id')
