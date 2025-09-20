#!/bin/bash
set -e

echo "🚨 ATENÇÃO: Isso vai resetar completamente o banco de dados (container: postgres-db)!"
echo "Pressione Ctrl+C para cancelar ou aguarde 5 segundos..."
sleep 5

# Derruba containers e remove volumes (inclui os dados do Postgres)
echo "🛑 Derrubando containers e apagando volumes..."
docker compose down -v

# Remove também o diretório de dados local (montado no volume ./pgdata)
echo "🗑️ Limpando diretório ./pgdata..."
sudo rm -rf ./pgdata

# Sobe containers novamente em segundo plano
echo "🚀 Subindo containers..."
docker compose up -d --build

# Aguarda o Postgres ficar pronto
echo "⏳ Aguardando Postgres inicializar..."
until docker exec postgres-db pg_isready -U postgres > /dev/null 2>&1; do
  sleep 2
done

echo "✅ Postgres está pronto!"

# Marca banco como na versão inicial
echo "📌 Rodando alembic stamp..."
docker exec agent-api alembic stamp 0001_initial

# Aplica migrations até o head
echo "📌 Rodando alembic upgrade head..."
docker exec agent-api alembic upgrade head

echo "🎉 Banco resetado com sucesso!"
