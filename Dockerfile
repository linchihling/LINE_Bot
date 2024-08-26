FROM python:3.12-alpine

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /bot
COPY . /bot

# ENV PYTHONPATH=.
# RUN pytest

EXPOSE 6000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000", "--reload"]

