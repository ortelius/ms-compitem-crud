FROM cgr.dev/chainguard/python:latest-dev@sha256:b24cd7bac41c19e0ddf5e3ebd794fe4efa04bb6f03d2053b188796193682e1e0 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --require-hashes --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:36d9faf5198aec34124b2d8434b23dbe518f72ecc62d51b2b8e29fbd62f44110
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
