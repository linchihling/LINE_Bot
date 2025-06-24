FROM python:3.12-alpine

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /bot
COPY . /bot

EXPOSE 6000
