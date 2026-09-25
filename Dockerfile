# v0.1.5 Task 8.1: the pilot image -- the API, its locked dependencies, and a
# default copy of policy_specs/. Deployments mount their reviewed copy over
# /policy_specs (ADR-0011: policy files are deploy-time configuration).
FROM python:3.12-slim

RUN pip install --no-cache-dir "uv>=0.8,<1"

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --extra serve --no-editable \
    && rm -rf /root/.cache

COPY policy_specs /policy_specs
COPY deploy/entrypoint.sh /entrypoint.sh

ENV PATH=/app/.venv/bin:$PATH \
    POLTIKA_POLICY_SPECS_DIR=/policy_specs \
    PYTHONUNBUFFERED=1

RUN useradd --system --no-create-home poltika
USER poltika

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
