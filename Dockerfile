FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY /docker/entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Копируем остальной код
COPY . .

EXPOSE 8080

# Указываем entrypoint.sh как точку входа (теперь в корне)
ENTRYPOINT ["/entrypoint.sh"]