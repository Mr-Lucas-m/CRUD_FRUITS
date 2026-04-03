#!/bin/sh
set -e

echo "Aguardando banco de dados..."
until pg_isready -h db -U fruits_user; do
  sleep 1
done

echo "Rodando migrations..."
alembic upgrade head

echo "Subindo API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000