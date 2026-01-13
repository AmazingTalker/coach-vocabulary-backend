"""add_answer_history_table

Revision ID: f1a2b3c4d5e6
Revises: e93a64b3bb48
Create Date: 2024-01-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e93a64b3bb48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'answer_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word', sa.String(length=100), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('exercise_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('pool', sa.String(length=10), nullable=False),
        sa.Column('user_answer', sa.String(length=200), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answer_history_user_id'), 'answer_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_answer_history_word_id'), 'answer_history', ['word_id'], unique=False)
    op.create_index(op.f('ix_answer_history_source'), 'answer_history', ['source'], unique=False)
    op.create_index(op.f('ix_answer_history_pool'), 'answer_history', ['pool'], unique=False)
    op.create_index(op.f('ix_answer_history_created_at'), 'answer_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_answer_history_created_at'), table_name='answer_history')
    op.drop_index(op.f('ix_answer_history_pool'), table_name='answer_history')
    op.drop_index(op.f('ix_answer_history_source'), table_name='answer_history')
    op.drop_index(op.f('ix_answer_history_word_id'), table_name='answer_history')
    op.drop_index(op.f('ix_answer_history_user_id'), table_name='answer_history')
    op.drop_table('answer_history')
