#!/bin/sh
# Apply the scenario-store migrations when a database is configured (the API
# never migrates on its own; see README), then serve the API on $PORT (set by
# most hosting platforms; 8000 otherwise).
set -eu
if [ -n "${POLTIKA_DATABASE_URL:-}" ]; then
  python -c "import os; from poltika.scenarios.store import migrate; migrate(os.environ['POLTIKA_DATABASE_URL'])"
fi
exec uvicorn poltika.api.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'
