#!/bin/sh
set -e

echo "Esperando banco de dados em $DATABASE_HOST:$DATABASE_PORT..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 1
done
echo "Banco de dados disponível!"

cd /app

export PYTHONPATH=/app/src

echo "Rodando migrations Alembic..."
alembic -c /app/alembic.ini upgrade head
echo "Migrations aplicadas com sucesso!"

echo "Iniciando FastAPI..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000