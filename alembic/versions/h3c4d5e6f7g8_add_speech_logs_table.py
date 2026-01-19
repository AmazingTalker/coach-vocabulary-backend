"""add_speech_logs_table

Revision ID: h3c4d5e6f7g8
Revises: g2b3c4d5e6f7
Create Date: 2024-01-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'h3c4d5e6f7g8'
down_revision: Union[str, None] = 'g2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'speech_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('word', sa.String(length=100), nullable=False),
        sa.Column('recording_path', sa.String(length=500), nullable=False),
        sa.Column('native_transcript', sa.String(length=500), nullable=True),
        sa.Column('cloud_transcript', sa.String(length=500), nullable=True),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_speech_logs_user_id'), 'speech_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_speech_logs_word_id'), 'speech_logs', ['word_id'], unique=False)
    op.create_index(op.f('ix_speech_logs_platform'), 'speech_logs', ['platform'], unique=False)
    op.create_index(op.f('ix_speech_logs_created_at'), 'speech_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_speech_logs_created_at'), table_name='speech_logs')
    op.drop_index(op.f('ix_speech_logs_platform'), table_name='speech_logs')
    op.drop_index(op.f('ix_speech_logs_word_id'), table_name='speech_logs')
    op.drop_index(op.f('ix_speech_logs_user_id'), table_name='speech_logs')
    op.drop_table('speech_logs')
