FROM quay.io/ortelius/ms-python-base:fastapi-1.0 as base

ENV DB_HOST localhost
ENV DB_NAME postgres
ENV DB_USER postgres
ENV DB_PASS postgres
ENV DB_PORT 5432

WORKDIR /app

COPY main.py /app
COPY requirements.txt /app
RUN pip install -r requirements.txt; \
python -m pip uninstall -y pip;
