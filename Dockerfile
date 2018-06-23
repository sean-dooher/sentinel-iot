FROM python:3.6

ARG user_id=1000

RUN useradd -u $user_id --system sentinel && \
    mkdir /sentinel && \
    chown sentinel:sentinel /sentinel

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN wget -O /usr/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64
RUN chmod +x /usr/bin/dumb-init

COPY requirements.txt /sentinel/requirements.txt
RUN pip install -r /sentinel/requirements.txt

COPY --chown=sentinel:sentinel ./sentinel/ /sentinel/
COPY --chown=sentinel:sentinel entrypoint-*.sh /entry/
COPY --chown=sentinel:sentinel run_tests.sh /sentinel/
RUN mkdir /sentinel/static
RUN chown sentinel:sentinel /sentinel/static


USER sentinel
WORKDIR /sentinel
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
ENV PYTHONUNBUFFERED 1
