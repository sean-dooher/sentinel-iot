FROM node:8-alpine as react-pkg
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh dumb-init
USER node
COPY --chown=node:node sentinel/webpack.config.js sentinel/.babelrc /sentinel/
COPY --chown=node:node sentinel/package.json sentinel/package-lock.json /sentinel/
RUN cd /sentinel && npm install
COPY --chown=node:node sentinel/assets /sentinel/assets
RUN cd /sentinel && npm run build
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

FROM python:3.6-alpine
ARG user_id=1000

RUN adduser -D -u $user_id sentinel && \
    mkdir /sentinel && \
    chown sentinel:sentinel /sentinel

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN apk update && apk add dumb-init postgresql-dev postgresql-client gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt /sentinel/requirements.txt
RUN pip install -r /sentinel/requirements.txt

COPY --chown=sentinel:sentinel ./sentinel/ /sentinel/
COPY --chown=sentinel:sentinel config/entrypoint-*.sh /entry/
COPY --chown=sentinel:sentinel run_tests.sh /sentinel/
COPY --from=react-pkg /sentinel/assets/bundles/main.js /sentinel/assets/bundles/main.js
COPY --from=react-pkg /sentinel/webpack-stats.json /sentinel


RUN mkdir -p /static && chown sentinel:sentinel /static
RUN mkdir -p /reports && chown sentinel:sentinel /reports

USER sentinel
WORKDIR /sentinel
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
