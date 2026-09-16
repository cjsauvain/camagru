FROM python:3.14-slim

WORKDIR /app

COPY ./src ./src

ENV PYTHONPATH=/app/src

RUN useradd --create-home camagru \
    && mkdir /app/data \
    && chown -R camagru /app/data

USER camagru

EXPOSE 8080

CMD [ "python", "-m", "camagru" ]