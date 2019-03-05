# vim: set ft=dockerfile:
FROM eu.gcr.io/sapient-tracer-168309/wg-base-images/wg-docker-sanic-base:latest

WORKDIR /app

ADD ./app/requirements-server.txt /app
RUN pip install --user -r /app/requirements-server.txt

ADD ./app /app
