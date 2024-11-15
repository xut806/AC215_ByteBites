FROM python:3.10-slim-buster
ENV PYENV_SHELL=/bin/bash

COPY Pipfile /app/
COPY Pipfile.lock /app/
COPY llama_finetune.py /app/

WORKDIR /app

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --deploy && \
    mkdir -p /app

RUN pipenv sync

ENTRYPOINT ["python", "/app/llama_finetune.py"]