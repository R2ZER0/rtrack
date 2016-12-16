FROM debian:jessie
MAINTAINER Rikki Guy <git@rikkiguy.me.uk>

RUN apt-get update && apt-get install -y python python-setuptools sqlite3 python-pip
RUN pip install gunicorn

RUN mkdir /opt/rtrack
WORKDIR /opt/rtrack

COPY requirements.txt /opt/rtrack/requirements.txt
RUN pip install -r /opt/rtrack/requirements.txt

COPY rtrack.py /opt/rtrack/rtrack.py
COPY schema.sql /opt/rtrack/schema.sql

COPY entrypoint.sh /entrypoint.sh

VOLUME ["/var/rtrack"]
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
