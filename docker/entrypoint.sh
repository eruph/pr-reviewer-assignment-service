#!/bin/bash

set -e

sleep 10

echo "Начало миграции"
poetry run alembic upgrade head

echo "Старт приложения"
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

echo "Entrypoint отработал"
