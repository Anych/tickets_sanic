FROM python:3.10-slim

COPY ../../requirements.txt /tmp/requirements.txt
COPY ../../migrations/migrate /bin/migrate
COPY ../../migrations/makemigrations /bin/makemigrations

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt
ENV TZ=Asia/Almaty
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 /usr/local/bin/dbmate
RUN chmod +x /usr/local/bin/dbmate

RUN useradd -m -d /proj -s /bin/bash app
WORKDIR /proj
COPY . /proj
RUN chown -R app:app /proj/*

USER app
