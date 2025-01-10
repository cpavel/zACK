FROM python:3.11.4-bullseye

WORKDIR /install

RUN apt update && apt install sudo
RUN pip install --upgrade pip

# Static files for install only. You can use /app mapped to local host for development and updates
ADD . /install/

# ENV sectionis defined for build phase only, you can ovveride it for run phase in docker-compose.yml
# Required to make install script running
ENV TERM xterm-256color

# DJANGO DB settings for data and /admin
ENV RUNNING_ENVIRONMENT dev
ENV DB_HOST db
ENV DB_USER admin
# Password must be complex, otherwise createsuperuser will fail silently
ENV DB_PASSWORD a1234567-B
# Postgres initial superuser credentials
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

ENV CELERY_BROKER_URL "redis://redis:6379/0"
ENV CELERY_RESULT_BACKEND "redis://redis:6379/0"


RUN bin/install --no-input --skip-db

WORKDIR /app

RUN chmod +x /install/docker/backend/server-entrypoint.sh
RUN chmod +x /install/docker/backend/worker-entrypoint.sh
