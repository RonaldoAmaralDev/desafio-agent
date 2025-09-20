"""Add prompt_id column to agents

Revision ID: 0003_add_prompt_id_agents
Revises: 0002_add_model_temperature
Create Date: 2025-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_prompt_id_agents"
down_revision = "0002_add_model_temperature"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'agents',
        sa.Column('prompt_id', sa.INTEGER(), sa.ForeignKey('prompts.id'), nullable=True)
    )

def downgrade():
    op.drop_column('agents', 'prompt_id')