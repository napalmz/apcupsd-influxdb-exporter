FROM python:2-alpine
LABEL maintainer="NapalmZ (https://github.com/napalmz)"

ENV LANG=C.UTF-8
ENV TZ=Europe/Rome

RUN apk --no-cache update \
    && apk --no-cache upgrade \
    && apk add --no-cache \
        tzdata

COPY ./apcupsd-influxdb-exporter.py /apcupsd-influxdb-exporter.py
RUN pip install apcaccess influxdb

CMD ["python", "/apcupsd-influxdb-exporter.py"]
