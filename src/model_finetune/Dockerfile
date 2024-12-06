FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel

ENV PYENV_SHELL=/bin/bash

COPY Pipfile /app/
COPY Pipfile.lock /app/

WORKDIR /app

RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --deploy && \
    mkdir -p /app && \
    mkdir -p /app/logs && \
    mkdir -p /app/finetuned_models

RUN pipenv sync

COPY eval.py /app/
COPY llama_finetune.py /app/

CMD ["python", "/app/llama_finetune.py", "--train"]