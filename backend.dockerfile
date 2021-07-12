FROM python:3.8.8-buster
LABEL maintainer="dirk.winkelhardt@gmail.com"

WORKDIR /app

COPY ./macpepdb_web_backend /app/macpepdb_web_backend
COPY ./macpepdb_web_backend/entrypoint.sh /app/
COPY Pipfile /app
COPY Pipfile.lock /app
COPY config.yaml /app
COPY config.production.yaml /app

RUN apt-get update -y && apt-get install -y libev-dev \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --system --skip-lock \
    && chmod 755 ./entrypoint.sh

ENV MACPEPDB_WEB_ENV production

ENTRYPOINT [ "./entrypoint.sh" ]
