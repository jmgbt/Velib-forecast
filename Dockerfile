FROM python:3.8.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1

ENV AIRFLOW_HOME=/app/airflow

WORKDIR $AIRFLOW_HOME

RUN apt-get update && apt-get install curl -y

COPY scripts scripts
RUN chmod +x scripts/entrypoint.sh
RUN chmod +x scripts/init_connections.sh

COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --only main
