FROM python:3.9-buster as dev

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt