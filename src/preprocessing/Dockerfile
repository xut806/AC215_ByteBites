FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY data_preprocessing.py ./
COPY docker-entrypoint.sh ./

RUN pip install pipenv && \
    pipenv install --system --deploy

# Install dependencies from Pipfile
RUN pipenv install

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
