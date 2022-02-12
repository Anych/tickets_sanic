FROM python:3.10-slim

COPY ../../requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd -m -d /proj -s /bin/bash app
WORKDIR /proj
COPY .. /proj
RUN chown -R app:app /proj/*

USER app