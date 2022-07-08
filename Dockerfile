FROM node:14-buster

ARG USER_ID=999
ARG GROUP_ID=999

ENV USER_ID=$USER_ID
ENV GROUP_ID=$GROUP_ID

COPY ./macpepdb_web_frontend /app
WORKDIR /app

RUN apt-get update -y && apt-get install -y sudo \
    && groupadd -g $GROUP_ID app \
    && useradd -d /app -g $GROUP_ID -G sudo -m -s /bin/bash -u $USER_ID app \
    && chown -R app:app /app

USER app

RUN yarn install

ENTRYPOINT [ "./entrypoint.sh" ]
