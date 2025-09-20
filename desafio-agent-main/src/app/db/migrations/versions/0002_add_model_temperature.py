"""Add model and temperature columns to agents

Revision ID: 0002_add_model_temperature
Revises: 0001_initial
Create Date: 2025-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_model_temperature"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('agents', sa.Column('model', sa.String(), nullable=False, server_default='gpt-3.5'))
    op.add_column('agents', sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7'))

def downgrade():
    op.drop_column('agents', 'temperature')
    op.drop_column('agents', 'model')