from alembic import op
import sqlalchemy as sa
from sqlalchemy import select, insert, delete, and_
from datetime import datetime
import bcrypt
import os

# Revisões
revision = "0002_create_users_and_agent"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _get_table(conn, name: str):
    metadata = sa.MetaData()
    metadata.reflect(bind=conn, only=(name,))
    return metadata.tables.get(name)


def upgrade() -> None:
    conn = op.get_bind()
    users = _get_table(conn, "users")
    agents = _get_table(conn, "agents")

    if users is None or agents is None:
        return

    # -------------------
    # Criar/pegar admin
    # -------------------
    admin_row = conn.execute(
        select(users.c.id).where(users.c.email == "admin@example.com")
    ).first()

    if admin_row is not None:
        admin_id = admin_row[0]
    else:
        result = conn.execute(
            insert(users).values(
                name="Admin",
                email="admin@example.com",
                password=bcrypt.hashpw(
                    "admin123".encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")
            ).returning(users.c.id)
        )
        admin_id = result.scalar()

    # -------------------
    # Criar agentes
    # -------------------
    now = datetime.utcnow()

    # Agente Ollama
    exists_ollama = conn.execute(
        select(sa.literal(1)).select_from(agents).where(
            and_(
                agents.c.name == "Ollama",
                agents.c.model == "llama3"
            )
        ).limit(1)
    ).first()

    if exists_ollama is None:
        conn.execute(
            insert(agents).values(
                name="Ollama",
                description="Agente local usando Ollama (Llama 3).",
                provider="ollama",
                model="llama3",
                base_url="http://ollama:11434",
                temperature=0.0,
                active=True,
                owner_id=admin_id,
                created_at=now,
                updated_at=now
            )
        )

    # Agente OpenAI GPT
    exists_openai = conn.execute(
        select(sa.literal(1)).select_from(agents).where(
            and_(
                agents.c.name == "OpenAI GPT",
                agents.c.model == "gpt-4o"
            )
        ).limit(1)
    ).first()

    if exists_openai is None:
        conn.execute(
            insert(agents).values(
                name="OpenAI GPT",
                description="Agente remoto usando API da OpenAI.",
                provider="openai",
                model="gpt-4o",
                base_url="https://api.openai.com/v1",
                temperature=0.7,
                active=True,
                owner_id=admin_id,
                created_at=now,
                updated_at=now
            )
        )

def downgrade() -> None:
    conn = op.get_bind()
    users = _get_table(conn, "users")
    agents = _get_table(conn, "agents")

    if users is None or agents is None:
        return

    # Remover agentes
    conn.execute(
        delete(agents).where(
            and_(
                agents.c.name == "Ollama",
                agents.c.model == "llama3"
            )
        )
    )
    conn.execute(
        delete(agents).where(
            and_(
                agents.c.name == "OpenAI GPT",
                agents.c.model == "gpt-4o"
            )
        )
    )

    # Remover admin
    conn.execute(
        delete(users).where(users.c.email == "admin@example.com")
    )
