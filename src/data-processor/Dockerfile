FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYENV_SHELL=/bin/bash
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y curl apt-transport-https ca-certificates gnupg lsb-release openssh-client

# Add the Google Cloud SDK repository
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

RUN apt-get update && \
    apt-get install -y google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin jq

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.11 python3-pip && \
    pip install pipenv

RUN useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    # mkdir -p /persistent && \
    # chown app:app /persistent && \
    chown app:app /app

USER app
WORKDIR /app

ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

RUN pipenv install --system --deploy && python -m pip list

ADD --chown=app:app . /app
ADD --chown=app:app secrets/data-service-account.json /app/secrets/data-service-account.json
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]
