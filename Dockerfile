FROM cgr.dev/chainguard/python:latest-dev@sha256:0b19b019efef129472c45582ca33a564105f80daa5a66ea89134b2a50e1688e8 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --require-hashes --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:47d0a74e92d3bd87438a4ad18a76f9a5e59dc2d040ffcfa544b780e1caa72561
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
