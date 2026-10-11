"""Write the API's OpenAPI document to `web/openapi.json` (Task B0.1.3).

`web/src/api/schema.gen.ts` is generated from that file, and CI fails when
either drifts from the Pydantic models (ADR-0023, decision 8). Run from the
repository root: `uv run --extra dev python scripts/development/dump_openapi.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

from poltika.api.main import app

OUTPUT = Path(__file__).resolve().parents[2] / "web" / "openapi.json"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
