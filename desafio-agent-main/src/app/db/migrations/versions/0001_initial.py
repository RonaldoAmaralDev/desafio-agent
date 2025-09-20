"""Initial migration with execution_costs

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Tabela de usuários
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True)
    )

    # Tabela de agentes
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('temperature', sa.Float(), server_default="0.0"),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('base_url', sa.String(255), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    )

    # Tabela de prompts (aponta para agents)
    op.create_table(
        'prompts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('version', sa.String(50), server_default="1.0"),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True)
    )

    # Tabela de execuções
    op.create_table(
        'executions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('input', sa.String(), nullable=False),
        sa.Column('output', sa.String(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )

    # Tabela de custos por execução
    op.create_table(
        'execution_costs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('execution_id', sa.Integer(), sa.ForeignKey('executions.id'), nullable=False),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )

    # Tabela de workflows
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('steps', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True)
    )


def downgrade():
    # Ordem inversa ao upgrade
    op.drop_table('workflows')
    op.drop_table('execution_costs')
    op.drop_table('executions')
    op.drop_table('prompts')
    op.drop_table('agents')
    op.drop_table('users')