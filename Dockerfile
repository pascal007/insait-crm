FROM python:3.11-bookworm
LABEL authors="Pascal Ezeama"

WORKDIR .

RUN  apt-get update

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY . .

