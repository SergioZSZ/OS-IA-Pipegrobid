FROM python:3.13

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml README.md ./
COPY ./src/ ./src/

RUN poetry install

CMD ["pipegrobid"]



