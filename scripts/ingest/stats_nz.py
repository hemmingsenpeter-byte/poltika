"""Entry point: preserve Stats NZ source evidence (ADR-0022).

    uv run python scripts/ingest/stats_nz.py --list
    uv run python scripts/ingest/stats_nz.py --all --dry-run
    POLTIKA_STATS_NZ_API_KEY=... uv run python scripts/ingest/stats_nz.py --all

All logic lives in `poltika.data.acquisition.ingest`.
"""

from __future__ import annotations

import sys

from poltika.data.acquisition.ingest import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
