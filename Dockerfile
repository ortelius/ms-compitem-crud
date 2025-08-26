FROM cgr.dev/chainguard/python:latest-dev@sha256:53a696211852eb96dfa7024efa7bf49154865da50c33a2fe6cd5f02effe4373f AS builder

COPY . /app

WORKDIR /app
ENV PATH=/home/nonroot/.local/bin:$PATH

# hadolint ignore=DL4006
RUN wget -q -O - https://install.python-poetry.org | python -
RUN poetry install --no-root;


FROM cgr.dev/chainguard/python:latest@sha256:40a29d69c56a8908f5367a66275cbc84c9a0532234fdbe945156fdd49ef26fc5
USER nonroot
ENV DB_HOST=localhost
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASS=postgres
ENV DB_PORT=5432

COPY --from=builder /app /app
COPY --from=builder /home/nonroot /home/nonroot

WORKDIR /app

EXPOSE 8080
ENV PATH=$PATH:/home/nonroot/.local/bin

HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
