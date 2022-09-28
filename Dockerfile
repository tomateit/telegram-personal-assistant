FROM python:3.10-slim-buster

ENV ENVIRONMENT=production
WORKDIR /app

RUN apt update && apt upgrade -y && apt install curl -y

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN /root/.local/bin/poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

RUN /root/.local/bin/poetry install --no-dev

COPY ./ /app/

COPY ./.env.docker ./.env

CMD ["python", "/app/main/main.py"]