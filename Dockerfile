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

# The synthetic development population for /analyst/microsim, generated from
# its committed spec (v0.2 Task 3.3). Seeded, so every build gives the same
# file. A deployment can point POLTIKA_POPULATION_PATH elsewhere.
COPY data/metadata/populations/nz_synthetic_development.v1.yaml /app/population-spec.yaml
RUN /app/.venv/bin/python -m poltika.scenarios.microsim.synthetic \
    /app/population-spec.yaml /app/population.json

# A hosted pilot is password protected (api/access.py): the image refuses to
# start unless POLTIKA_ACCESS_PASSWORD is set (docs/pilot/HOSTING.md).
ENV PATH=/app/.venv/bin:$PATH \
    POLTIKA_POLICY_SPECS_DIR=/policy_specs \
    POLTIKA_POPULATION_PATH=/app/population.json \
    POLTIKA_REQUIRE_ACCESS_PASSWORD=1 \
    PYTHONUNBUFFERED=1

RUN useradd --system --no-create-home poltika
USER poltika

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
