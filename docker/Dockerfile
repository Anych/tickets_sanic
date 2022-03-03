FROM python:3.10-slim

RUN pip install --upgrade pip

COPY requirements/ /tmp/requirements

RUN pip install --no-cache-dir -r /tmp/requirements/dev.txt
ENV TZ=Asia/Almaty
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 /usr/local/bin/dbmate
RUN chmod +x /usr/local/bin/dbmate

RUN useradd -m -d /proj -s /bin/bash app
COPY . /proj
WORKDIR /proj
RUN chown -R app:app /proj/*
USER app
