ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-alpine as poetry-base

ARG POETRY_VERSION=1.5.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    apk del \
        gcc \
        musl-dev \
        libffi-dev

FROM poetry-base as app-env

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-interaction --no-cache --no-root --without dev

FROM python:${PYTHON_VERSION}-alpine as app

ENV PATH="/app/.venv/bin:$PATH" \
    PARSER_WORKING_DIR=/data \
    PARSER_HOST=0.0.0.0 \
    PARSER_PORT=80

WORKDIR /app

COPY --from=app-env /app/.venv /app/.venv

COPY . /app

RUN mkdir -p /data

EXPOSE 80

CMD ["python3", "-m", "clash_parser"]
