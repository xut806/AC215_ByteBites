FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY docker-entrypoint.sh ./
COPY cli.py ./

RUN pip install pipenv && \
    pipenv install --system --deploy

RUN pipenv install

RUN chmod +x ./docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
