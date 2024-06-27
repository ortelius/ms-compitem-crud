FROM cgr.dev/chainguard/python:latest-dev@sha256:2ad42bda7fe146e3f717aaa1d8ecd0f178aa5450898d52b33c52ea1714df5aa6 AS builder

COPY . /app

WORKDIR /app
RUN python -m pip install --no-cache-dir -r requirements.txt --no-warn-script-location;

FROM cgr.dev/chainguard/python:latest@sha256:9e1f35b5aac96317bb15c2102d80964b9e6151fcae2662094d4871c87d1c3cfd
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
