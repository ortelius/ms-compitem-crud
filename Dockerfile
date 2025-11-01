FROM cgr.dev/chainguard/python:latest-dev@sha256:3001eae1634ecc6292fa278b1f5042f939275224ece61240b3afde97721ff613 AS builder

COPY . /app

WORKDIR /app
ENV PATH=/home/nonroot/.local/bin:$PATH

# hadolint ignore=DL4006
RUN wget -q -O - https://install.python-poetry.org | python -
RUN poetry install --no-root;


FROM cgr.dev/chainguard/python:latest@sha256:383c8b591d31dd66d36fc0a565a24c7ce7ed04df63114f0074489bc13a8dc925
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
