FROM cgr.dev/chainguard/python:latest-dev@sha256:c360a8cba8854251f987da9ef85ced963bde715fa08b10c39a477dd130dff5a3 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --require-hashes --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:2de43fd2e89b0b9bb708a5b4a9c7e8b0d23d77005c384b8b6d15a81e2673d37b
USER nonroot
ENV DB_HOST localhost
ENV DB_NAME postgres
ENV DB_USER postgres
ENV DB_PASS postgres
ENV DB_PORT 5432

COPY --from=builder /app /app
COPY --from=builder /home/nonroot/.local /home/nonroot/.local

WORKDIR /app

EXPOSE 8080
ENV PATH=$PATH:/home/nonroot/.local/bin

HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
