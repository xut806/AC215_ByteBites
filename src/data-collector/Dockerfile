FROM python:3.11-slim

ARG DEBIAN_PACKAGES="build-essential git curl wget"

ENV DEBIAN_FRONTEND=noninteractive

ENV PYENV_SHELL=/bin/bash

ENV PYTHONUNBUFFERED=1

RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get install -y --no-install-recommends apt-transport-https ca-certificates gnupg curl && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv  && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-sdk -y

USER app
WORKDIR /app

ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

ADD --chown=app:app . /app

ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]