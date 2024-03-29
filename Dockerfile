FROM cgr.dev/chainguard/python:latest-dev@sha256:d56eb91964f17391ab9933079f89d6d2cd7b5bf5c2d10e1a33b2208c130da77f AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --require-hashes --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:3559f62cb6e38925fb97b9479612522abb4522c95b80e65e7f50e9e4a67cc0d9
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
