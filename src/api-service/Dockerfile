FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /app/

#RUN pip install pipenv && pipenv sync --system
RUN pip install pipenv && pipenv install --system --deploy

RUN pip install torch==2.0.1+cpu torchvision==0.15.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

#COPY . /app
COPY --chown=root:root . /app
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]