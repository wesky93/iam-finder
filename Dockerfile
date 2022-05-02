FROM python:3.9-slim-buster

RUN pip install -U pip setuptools wheel

WORKDIR /app
COPY requirements.txt  /app/requirements.txt

RUN pip install -r requirements.txt
ARG CACHEBUST=1

COPY ./src /app
CMD ["uvicorn", "main:app", "--host","0.0.0.0","--port","80"]
