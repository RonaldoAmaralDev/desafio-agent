from alembic import op
import sqlalchemy as sa
from sqlalchemy import select, insert, delete, and_, or_
from uuid import uuid4
from datetime import datetime

# Revisões
revision = "993810b27a82_seed_add_default_ollama_agent"
down_revision = "0003_add_prompt_id_agents"
branch_labels = None
depends_on = None


def _get_agents_table(conn):
    metadata = sa.MetaData()
    metadata.reflect(bind=conn, only=("agents",))
    if "agents" not in metadata.tables:
        return None
    return metadata.tables["agents"]


def upgrade() -> None:
    conn = op.get_bind()
    agents = _get_agents_table(conn)
    if agents is None:
        return

    cols = agents.c.keys()

    exists_filters = []
    if "name" in cols:
        exists_filters.append(agents.c.name == "Ollama Local")
    if "provider" in cols and "model" in cols:
        exists_filters.append(and_(agents.c.provider == "ollama", agents.c.model == "llama3"))

    already = False
    if exists_filters:
        row = conn.execute(
            select(sa.literal(1)).select_from(agents).where(or_(*exists_filters)).limit(1)
        ).first()
        already = row is not None

    if already:
        return

    row = {}
    now = datetime.utcnow()

    if "id" in cols:
        row["id"] = str(uuid4())
    if "name" in cols:
        row["name"] = "Ollama Local"
    if "provider" in cols:
        row["provider"] = "ollama"
    if "model" in cols:
        row["model"] = "llama3"
    if "base_url" in cols:
        row["base_url"] = "http://ollama:11434"
    if "temperature" in cols:
        row["temperature"] = 0.0
    if "active" in cols:
        row["active"] = True
    if "description" in cols:
        row["description"] = "Agente local usando Ollama (Llama 3)."
    if "created_at" in cols:
        row["created_at"] = now
    if "updated_at" in cols:
        row["updated_at"] = now

    conn.execute(insert(agents).values(**row))


def downgrade() -> None:
    conn = op.get_bind()
    agents = _get_agents_table(conn)
    if agents is None:
        return

    cols = agents.c.keys()
    conds = []
    if "name" in cols:
        conds.append(agents.c.name == "Ollama Local")
    if "provider" in cols and "model" in cols:
        conds.append(and_(agents.c.provider == "ollama", agents.c.model == "llama3"))

    if conds:
        conn.execute(delete(agents).where(or_(*conds)))