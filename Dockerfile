# Logminer reproducible runtime for article-1 artifact checks.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LOGMINER_API_HOST=0.0.0.0 \
    LOGMINER_API_PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-container.txt requirements-container.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-container.txt

COPY src src
COPY scripts scripts
COPY docs docs
COPY web web
COPY requirements.txt requirements.txt
COPY requirements-ai.txt requirements-ai.txt

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--app-dir", "src/logminer", "--host", "0.0.0.0", "--port", "8000"]
