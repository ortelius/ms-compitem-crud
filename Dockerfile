# Copyright (c) 2021 Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM python:3.10-slim AS python-base

### Install pipenv and compilation dependencies
RUN apt-get update; \
    apt-get install -y --no-install-recommends gcc libbz2-dev;

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip; \
    pip install --no-cache-dir --upgrade -r requirements.txt; \
    pip uninstall -y pip wheel setuptools; \
    cp $(which uvicorn) /app

## ------------------------------- distroless base image ------------------------------ ##

# build from distroless C or cc:debug, because lots of Python depends on C
FROM gcr.io/distroless/cc

ARG CHIPSET_ARCH=x86_64-linux-gnu

## ------------------------- copy python itself from builder -------------------------- ##

# this carries more risk than installing it fully, but makes the image a lot smaller
COPY --from=python-base /usr/local/lib/ /usr/local/lib/
COPY --from=python-base /usr/local/bin/python /usr/local/bin/python
COPY --from=python-base /etc/ld.so.cache /etc/ld.so.cache

## -------------------------- add common compiled libraries --------------------------- ##

# If seeing ImportErrors, check if in the python-base already and copy as below

# required by lots of packages - e.g. six, numpy, wsgi
COPY --from=python-base /lib/${CHIPSET_ARCH}/libz.so.1 /lib/${CHIPSET_ARCH}/
# required by google-cloud/grpcio
COPY --from=python-base /usr/lib/${CHIPSET_ARCH}/libffi* /usr/lib/${CHIPSET_ARCH}/
COPY --from=python-base /lib/${CHIPSET_ARCH}/libexpat* /lib/${CHIPSET_ARCH}/

## -------------------------------- non-root user setup ------------------------------- ##

COPY --from=python-base /bin/echo /bin/echo
COPY --from=python-base /bin/rm /bin/rm
COPY --from=python-base /bin/sh /bin/sh

RUN echo "monty:x:1000:monty" >> /etc/group
RUN echo "monty:x:1001:" >> /etc/group
RUN echo "monty:x:1000:1001::/home/monty:" >> /etc/passwd

# quick validation that python still works whilst we have a shell
RUN python --version
RUN rm /bin/sh /bin/echo /bin/rm

## --------------------------- standardise execution env ----------------------------- ##

# default to running as non-root, uid=1000
USER monty

# standardise on locale, don't generate .pyc, enable tracebacks on seg faults
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
# end base
ENV DB_HOST localhost
ENV DB_NAME postgres
ENV DB_USER postgres
ENV DB_PASS postgres
ENV DB_PORT 5432

COPY --from=python-base /app /app
COPY --from=python-base /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=python-base /usr/lib/x86_64-linux-gnu/libsqlite3* /usr/lib/x86_64-linux-gnu
COPY --from=python-base /lib/x86_64-linux-gnu/libbz2* /lib/x86_64-linux-gnu
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages

WORKDIR /app

EXPOSE 80
ENTRYPOINT ["./uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
