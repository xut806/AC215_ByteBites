# # Base image
# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Copy the project files into the container
# COPY . .

# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgl1-mesa-glx \
#     libglib2.0-0 && \
#     python3.11-venv \
#     python3-pip \
#     libffi-dev \
#     libssl-dev \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     curl \
#     gnupg \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # Install Python packages
# RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --deploy

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8080/health || exit 1

# # Run the application
# CMD ["uvicorn", "cli:app", "--host", "0.0.0.0", "--port", "8080"]


# base image (non-GPU )
FROM python:3.11-slim

# Install system dependencies required for image processing

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3.11-venv \
    python3-pip \
    libffi-dev \
    libssl-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*


# Create and activate virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# Install Pipenv in virtual environment
RUN pip install pipenv

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
ENV PYTHONPATH="/app:$PYTHONPATH"

# Copy project files into the container
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN PIPENV_IGNORE_VIRTUALENVS=1
RUN pipenv install --deploy --ignore-pipfile


# Copy application code (but not .env)
COPY . .


# Health check
## TODO: don't rely on hardcoded port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["pipenv", "run", "uvicorn", "cli:app", "--host", "0.0.0.0", "--port", "8080"]
