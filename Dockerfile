FROM python:3.10-slim
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app

RUN useradd -m -d /proj -s /bin/bash app
COPY . /proj
WORKDIR /proj
RUN chown -R app:app /proj/*
USER app
