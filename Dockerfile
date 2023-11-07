#FROM python:2-alpine
FROM python:alpine3.17
LABEL maintainer="NapalmZ (https://github.com/napalmz)"

ENV LANG=C.UTF-8
ENV TZ=Europe/Rome

RUN apk --no-cache update \
    && apk --no-cache upgrade \
    && apk add --no-cache \
        tzdata gcc g++

COPY ./apcupsd-influxdb-exporter.py /apcupsd-influxdb-exporter.py
RUN pip install apcaccess influxdb influxdb-client

CMD ["python", "/apcupsd-influxdb-exporter.py"]
