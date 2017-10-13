FROM ubuntu:14.04

MAINTAINER Craig Northway

RUN apt-get update && apt-get install -y python python3 python-pip git && pip install -U setuptools==25.2.0 tox

COPY . /src

RUN tox -c /src/tox.ini
