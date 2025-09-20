"""export/import setup: ensure prompts table and agents.prompt_id

Revision ID: 0003_export_import_setup
Revises: 0002_create_users_and_agent
Create Date: 2025-09-20 12:40:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# Revisões
revision = "0003_export_import_setup"
down_revision = "0002_create_users_and_agent"
branch_labels = None
depends_on = None


def _has_table(conn, name: str) -> bool:
    insp = sa.inspect(conn)
    return insp.has_table(name)


def _has_column(conn, table: str, column: str) -> bool:
    insp: Inspector = sa.inspect(conn)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols


def _fk_exists(conn, table: str, fk_name: str) -> bool:
    insp: Inspector = sa.inspect(conn)
    fks = insp.get_foreign_keys(table)
    for fk in fks:
        if fk.get("name") == fk_name:
            return True
    return False


def upgrade() -> None:
    conn = op.get_bind()

    # 1) TABLE: prompts
    if not _has_table(conn, "prompts"):
        op.create_table(
            "prompts",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("agent_id", sa.Integer(), nullable=True, index=True),
            sa.Column("name", sa.String(length=150), nullable=True),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
        )
        # FK prompts.agent_id -> agents.id (opcional/nullable)
        op.create_foreign_key(
            "fk_prompts_agent_id_agents",
            "prompts",
            "agents",
            ["agent_id"],
            ["id"],
            ondelete="SET NULL",
        )
    else:
        # garante colunas essenciais se a tabela já existir
        if not _has_column(conn, "prompts", "agent_id"):
            op.add_column("prompts", sa.Column("agent_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_prompts_agent_id_agents",
                "prompts",
                "agents",
                ["agent_id"],
                ["id"],
                ondelete="SET NULL",
            )
        if not _has_column(conn, "prompts", "name"):
            op.add_column("prompts", sa.Column("name", sa.String(length=150), nullable=True))
        if not _has_column(conn, "prompts", "description"):
            op.add_column("prompts", sa.Column("description", sa.String(length=255), nullable=True))
        if not _has_column(conn, "prompts", "content"):
            op.add_column("prompts", sa.Column("content", sa.Text(), nullable=False))

        # garante índice em agent_id (se o dialect suportar easily)
        # alguns backends não retornam índices via inspector com facilidade;
        # se já existir, Postgres ignora criação duplicada por nome diferente.
        op.create_index("ix_prompts_agent_id", "prompts", ["agent_id"], unique=False)

    # 2) COLUMN: agents.prompt_id (FK -> prompts.id)
    if not _has_column(conn, "agents", "prompt_id"):
        op.add_column("agents", sa.Column("prompt_id", sa.Integer(), nullable=True))

    # cria FK se ainda não existir
    if not _fk_exists(conn, "agents", "fk_agents_prompt_id_prompts"):
        op.create_foreign_key(
            "fk_agents_prompt_id_prompts",
            "agents",
            "prompts",
            ["prompt_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    conn = op.get_bind()

    # remove FK agents.prompt_id -> prompts.id
    if _fk_exists(conn, "agents", "fk_agents_prompt_id_prompts"):
        op.drop_constraint("fk_agents_prompt_id_prompts", "agents", type_="foreignkey")

    # remove coluna prompt_id de agents (se existir)
    if _has_column(conn, "agents", "prompt_id"):
        op.drop_column("agents", "prompt_id")

    # remove FK prompts.agent_id -> agents.id
    # nome pode variar se já existia; tentamos o padrão criado acima.
    if _fk_exists(conn, "prompts", "fk_prompts_agent_id_agents"):
        op.drop_constraint("fk_prompts_agent_id_agents", "prompts", type_="foreignkey")

    # drop index (se existir) e tabela prompts
    try:
        op.drop_index("ix_prompts_agent_id", table_name="prompts")
    except Exception:
        pass

    if _has_table(conn, "prompts"):
        op.drop_table("prompts")