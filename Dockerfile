FROM python:3.8.10-slim

#Do not use env as this would persist after the build and would impact your containers, children images

ARG DEBIAN_FRONTEND=noninteractive

# force the stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED 1

ENV  AIRFLOW_HOME=/app/airflow
WORKDIR $AIRFLOW_HOME

COPY scripts/entrypoint.sh  ./
RUN chmod +x /app/airflow/entrypoint.sh

COPY poetry.lock ./
COPY pyproject.toml ./

RUN apt-get update \
    && apt-get -y upgrade \
    && pip install --no-cache-dir poetry \
    && poetry install \
    && apt-get clean \

ENTRYPOINT ["poetry", "run" ]
