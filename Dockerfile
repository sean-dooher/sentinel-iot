FROM python:3.6

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


RUN useradd --system app && \
    mkdir /app && \
    chown app:app /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY --chown=app:app ./sentinel/ /app/
ADD --chown=app:app entrypoint-*.sh /app/
COPY --chown=app:app run_tests.sh /app/
RUN mkdir /app/static
RUN chown app:app /app/static


USER app
WORKDIR /app
ENV PYTHONUNBUFFERED 1
