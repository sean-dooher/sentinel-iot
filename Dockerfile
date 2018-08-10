FROM node:8-alpine as react-pkg
RUN mkdir /sentinel
COPY sentinel/webpack.config.js sentinel/.babelrc /sentinel/
COPY sentinel/package.json sentinel/package-lock.json /sentinel/
RUN cd /sentinel && npm install
COPY sentinel/assets /sentinel/assets
RUN cd /sentinel && npm run build

FROM python:3.6-alpine

ARG user_id=1000

RUN adduser -D -u $user_id sentinel && \
    mkdir /sentinel && \
    chown sentinel:sentinel /sentinel

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /sentinel/requirements.txt
RUN pip install -r /sentinel/requirements.txt

COPY --chown=sentinel:sentinel ./sentinel/ /sentinel/
COPY --chown=sentinel:sentinel entrypoint-*.sh /entry/
COPY --chown=sentinel:sentinel run_tests.sh /sentinel/
COPY --from=react-pkg /sentinel/assets/bundles/main.js /sentinel/assets/bundles/main.js
RUN mkdir /sentinel/static && chown sentinel:sentinel /sentinel/static
RUN mkdir /sentinel/reports && chown sentinel:sentinel /sentinel/reports

USER sentinel
WORKDIR /sentinel
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
ENV PYTHONUNBUFFERED 1
