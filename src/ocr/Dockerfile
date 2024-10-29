FROM python:3.11-slim

# Install essential system packages for Python and pipenv (to avoid build errors)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY ocr_ner.py ./
COPY docker-entrypoint.sh ./

RUN pip install pipenv && \
    pipenv install --system --deploy

# Install dependencies from Pipfile
RUN pipenv install

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
