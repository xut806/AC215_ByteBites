FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY rag.py ./
COPY docker-entrypoint.sh ./

RUN pip install pipenv && \
    pipenv install --system --deploy

RUN pipenv install

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
