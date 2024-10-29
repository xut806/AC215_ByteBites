FROM python:3.11-slim

# Install essential system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY ocr_ner.py ./
COPY extract_ingredients.py ./
COPY docker-entrypoint.sh ./

RUN pip install pipenv && \
    pipenv install --system --deploy

# Install dependencies from Pipfile
RUN pipenv install

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
