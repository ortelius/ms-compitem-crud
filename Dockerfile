FROM cgr.dev/chainguard/python:latest-dev@sha256:da16a852e53e8f2ad0f7b96812e1598d36635c086e7d3883fbde1f9f249b75b8 AS builder

COPY . /app

WORKDIR /app
ENV PATH=/home/nonroot/.local/bin:$PATH

# hadolint ignore=DL4006
RUN wget -q -O - https://install.python-poetry.org | python -
RUN poetry install --no-root;


FROM cgr.dev/chainguard/python:latest@sha256:8f69b7d33a65d7b3833797301e0f94f95b0dc16662c3e22d7d1db9c8ebbf9c8d
USER nonroot
ENV DB_HOST localhost
ENV DB_NAME postgres
ENV DB_USER postgres
ENV DB_PASS postgres
ENV DB_PORT 5432

COPY --from=builder /app /app
COPY --from=builder /home/nonroot /home/nonroot

WORKDIR /app

EXPOSE 8080
ENV PATH=$PATH:/home/nonroot/.local/bin

HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
