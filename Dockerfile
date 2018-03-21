FROM python:3.6

RUN useradd --system app && \
    mkdir /app && \
    chown app:app /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY --chown=app:app ./sentinel/ /app/
ADD --chown=app:app entrypoint-*.sh /app/
RUN mkdir /app/static
RUN chown app:app /app/static

VOLUME ["/app"]
USER app
WORKDIR /app
ENV PYTHONUNBUFFERED 1
