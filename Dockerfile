FROM cgr.dev/chainguard/python:latest-dev@sha256:288ffec27bf57c778b71c637369f9014c1b19e555de16a0c10615f44de4f0ae8 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:2d89e581391c8f5b4d6da7f3e9212f6882fb3f007fd5e245cad787b625b41791
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
