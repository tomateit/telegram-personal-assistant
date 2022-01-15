FROM python:3.8-slim-buster

ENV ENVIRONMENT=production
WORKDIR /app

RUN apt update && apt upgrade -y

RUN pip install 'poetry==1.1.7'

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-dev

COPY ./ /app/

COPY ./.env.docker ./.env

CMD ["python", "/app/main/main.py"]