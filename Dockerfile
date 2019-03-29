# vim: set ft=dockerfile:
FROM eu.gcr.io/sapient-tracer-168309/wg-base-images/qa/wg-docker-sanic-base:latest

WORKDIR /app

ADD ./app/requirements-server.txt /app
USER user
RUN pip install --user -r /app/requirements-server.txt

ADD ./app /app
