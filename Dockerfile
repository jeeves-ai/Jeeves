FROM python:3.10-slim


RUN apt update && apt install -y gcc wait-for-it


WORKDIR /usr/src/app

COPY reqs.txt ./reqs.txt

RUN pip3 install --upgrade pip --default-timeout=100 && pip3 install -r reqs.txt --default-timeout=100


COPY . .