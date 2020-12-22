FROM python:3.9-buster

COPY . /app
WORKDIR /app

RUN pip install requirements.txt