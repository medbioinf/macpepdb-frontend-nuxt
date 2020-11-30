FROM python:3.7.7-buster
LABEL maintainer="dirk.winkelhardt@gmail.com"

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update -y && apt-get install -y yarn libev-dev

WORKDIR /usr/src/trypperdb_web

COPY . .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && yarn install \
    && yarn build-prod \
    && rm -r node_modules \
    && chmod 755 ./entrypoint.sh

ENV TRYPPERDB_ENV production

ENTRYPOINT [ "./entrypoint.sh" ]
