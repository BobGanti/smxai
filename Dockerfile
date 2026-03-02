# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (libgomp1 is commonly needed for xgboost on slim images)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

# Install deps and prove gunicorn exists during build
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -r /app/requirements.txt \
 && python -m gunicorn --version

# Copy the rest of the app
COPY . /app

# Cloud Run default
ENV PORT=8080
EXPOSE 8080

# Start via module so PATH issues can't break it
CMD ["sh", "-c", "python -m gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 300 --graceful-timeout 60 --keep-alive 120 app:app"]