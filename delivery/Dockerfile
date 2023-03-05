FROM python:3.11.2-slim-buster as base

FROM base as builder

RUN apt update && \
    apt install gcc -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

WORKDIR /code

COPY requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt

FROM base

WORKDIR /code
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY app/ /code/app/
COPY delivery/ /code/delivery/
COPY pyproject.toml /code/

ENV PYTHONPATH=/code

ENTRYPOINT [ "/code/delivery/entrypoint.sh" ]
