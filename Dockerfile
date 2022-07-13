FROM node:14-buster

ARG USER_ID=999
ARG GROUP_ID=999

ENV USER_ID=$USER_ID
ENV GROUP_ID=$GROUP_ID


WORKDIR /home/app
COPY . ./macpepdb_web_src

RUN apt-get update -y \
    && apt-get upgrade -y \
    && groupadd -g $GROUP_ID app \
    && useradd -d /app -g $GROUP_ID -m -s /bin/bash -u $USER_ID app \
    && chown -R app:app .

USER app
WORKDIR /home/app/macpepdb_web_src

RUN yarn install

ENTRYPOINT [ "./entrypoint.sh" ]
