# vim: set ft=dockerfile:

FROM python:3.7-alpine as base

MAINTAINER Sebastiaan Van Hoecke

FROM base as builder

RUN apk --update add gcc musl-dev make libuv git

COPY app/requirements.txt /requirements.txt

RUN mkdir /install

WORKDIR /install

RUN pip install --compile --install-option="--prefix=/install" --upgrade --ignore-installed -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local

COPY app /app

WORKDIR /app
VOLUME /app

RUN addgroup -S -g 1000 user && adduser -S -u 1000 -D -G user user
RUN chown -R user:user /app

USER user

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--access-logfile", "-", "--error-logfile", "-", "--workers=1", "-b", ":5000", "app:app", "--worker-class", "sanic.worker.GunicornWorker"]
