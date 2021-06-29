FROM node:14-buster

WORKDIR /app

COPY ./macpepdb_web_frontend /app

RUN yarn install

ENTRYPOINT [ "./entrypoint.sh" ]
