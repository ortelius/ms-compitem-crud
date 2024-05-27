FROM cgr.dev/chainguard/python:latest-dev@sha256:70f97dd84e4f7f3962ee3dc46b0c206f583981ea3317bfb7faca3d6082d4d41e AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:99ee1559c4632e06f293a2f03a2677e6bff371d37b4de6e21322715cb0697055
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
