# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
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

# BASE: a base image with updated packages
FROM python:3.13-alpine AS base
RUN apk upgrade --no-cache --available

# BUILDER: a container to build the service wheel
FROM base AS builder
# build backend, intentionally unpinned
# hadolint ignore=DL3013
RUN pip install --no-cache-dir build
COPY . /service
WORKDIR /service
RUN python -m build

# DEP-BUILDER: a container to (build and) install dependencies
FROM base AS dep-builder
# build tools are build-only, intentionally unpinned
# hadolint ignore=DL3018
RUN apk add --no-cache build-base gcc g++ libffi-dev zlib-dev && \
    apk upgrade --no-cache --available
WORKDIR /service
COPY --from=builder /service/lock/requirements.txt /service
RUN pip install --no-cache-dir --no-deps -r requirements.txt
# Binaries that are needed at runtime (opentelemetry-instrument is optional)
RUN mkdir -p /opt/runtime-bin \
 && { cp /usr/local/bin/opentelemetry-instrument /opt/runtime-bin/ 2>/dev/null || true; }

# RUNNER: a container to run the service
FROM base AS runner
ARG UID=1000
WORKDIR /service
RUN rm -rf /usr/local/lib/python3.13
COPY --from=dep-builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=dep-builder /opt/runtime-bin/ /usr/local/bin/
COPY --from=builder /service/dist/ /service
RUN pip install --no-cache-dir --no-deps ./*.whl && rm ./*.whl
# switch to non-root user (numeric UID for OpenShift arbitrary-UID compatibility)
USER ${UID}
ENV PYTHONUNBUFFERED=1

# Please adapt to package name:
ENTRYPOINT ["my-microservice"]
