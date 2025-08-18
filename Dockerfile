FROM cgr.dev/chainguard/python:latest-dev@sha256:2222671bd3478631089367ccce05f73a7a0cb50c221bfefb35e8467df0b9b4ef AS builder

COPY . /app

WORKDIR /app
ENV PATH=/home/nonroot/.local/bin:$PATH

# hadolint ignore=DL4006
RUN wget -q -O - https://install.python-poetry.org | python -
RUN poetry install --no-root;


FROM cgr.dev/chainguard/python:latest@sha256:03ea3f112ff878ace8f7aac31f4c71a66e77efef50d5bd7e62b39547b26cc1ae
USER nonroot
ENV DB_HOST=localhost
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASS=postgres
ENV DB_PORT=5432

COPY --from=builder /app /app
COPY --from=builder /home/nonroot /home/nonroot

WORKDIR /app

EXPOSE 8080
ENV PATH=$PATH:/home/nonroot/.local/bin

HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
