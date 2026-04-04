#!/bin/sh
set -e

echo "Aguardando banco de dados estar pronto..."
until pg_isready -h db -U fruits_user; do
  echo "  banco ainda não está pronto, aguardando..."
  sleep 2
done

echo "Rodando migrations (alembic upgrade head)..."
alembic upgrade head

echo "Subindo a API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000