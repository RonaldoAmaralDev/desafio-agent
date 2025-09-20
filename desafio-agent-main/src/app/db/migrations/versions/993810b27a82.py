from alembic import op
import sqlalchemy as sa
from sqlalchemy import select, insert, delete, and_
from datetime import datetime
import bcrypt

# Revisões
revision = "993810b27a82"
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

    if admin_row is not None:  # já existe
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
    # Criar agente Ollama
    # -------------------
    now = datetime.utcnow()

    exists = conn.execute(
        select(sa.literal(1)).select_from(agents).where(
            and_(
                agents.c.name == "Ollama Local",
                agents.c.model == "llama3"
            )
        ).limit(1)
    ).first()

    if exists is None:  # não existe ainda
        conn.execute(
            insert(agents).values(
                name="Ollama Local",
                description="Agente local usando Ollama (Llama 3).",
                provider="ollama",
                model="llama3",
                base_url="http://ollama:11434",
                temperature=0.0,
                active=True,
                owner_id=admin_id,  # 🔗 vincula ao admin
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

    # Remover agente
    conn.execute(
        delete(agents).where(
            and_(
                agents.c.name == "Ollama Local",
                agents.c.model == "llama3"
            )
        )
    )

    # Remover admin
    conn.execute(
        delete(users).where(users.c.email == "admin@example.com")
    )
