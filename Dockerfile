FROM cgr.dev/chainguard/python:latest-dev@sha256:78c327ed9c3bb20fcef2226452b67c5071b03e51de35048acce21e4ae319e614 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:9c774781fbaf008bbf43eeae6fd3aef61aed210b11033415a0fd635d4c684633
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
