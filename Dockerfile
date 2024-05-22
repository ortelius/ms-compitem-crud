FROM cgr.dev/chainguard/python:latest-dev@sha256:fe6862ec302fd71288cba4bc636454fe160859f615d0d207d73dd76128ad6744 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:fcabd6b5ea4a1f20a2451791d4c5db3aacb9f5a097275ba2a90722aa9f0cd9bf
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
