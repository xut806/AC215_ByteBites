FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
COPY fine_tune.py utils.py compare_models.py ./
COPY docker-entrypoint.sh ./
# Copy the fine-tuned model into the container
COPY finetuned_model /app/finetuned_model

RUN pip install pipenv && \
    pipenv install --system --deploy

RUN pipenv install

# Create directories for logs
RUN mkdir /app/logs

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
