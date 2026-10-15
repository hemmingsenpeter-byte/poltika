"""Independent Phase B method examples and optional official-source retrieval.

No Poltika simulator imports. Inputs below are hypothetical accounting amounts
or the explicitly identified Treasury method illustrations, never statutory
parameters or approved protected expectations. Run without network by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SOURCES = {
    "hils-concepts": "https://www.stats.govt.nz/methods/"
    "measuring-child-poverty-in-the-household-income-and-living-survey-concepts-and-definitions/",
    "hils-appendix": "https://www.stats.govt.nz/methods/"
    "child-poverty-statistics-year-ended-june-2025-technical-appendix/",
    "hils-correction": "https://www.stats.govt.nz/reports/"
    "error-notification-for-household-income-and-living-survey-hils-data-for-year-ended-june-2025/",
    "emtr-an25-01": "https://www.treasury.govt.nz/sites/default/files/2025-01/an25-01.pdf",
    "msd-household-incomes-2019": "https://www.msd.govt.nz/documents/about-msd-and-our-work/"
    "publications-resources/monitoring/household-income-report/2019/household-incomes-report-2019.doc",
}


class PageData(HTMLParser):
    """Read Stats NZ's published page payload rather than its empty HTML shell."""

    payload: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id") == "pageViewData":
            self.payload = json.loads(attributes["data-value"] or "{}")


def examples() -> dict[str, str]:
    d = Decimal
    # Annual same-period, hypothetical inputs, not amounts calculated under NZ law.
    person_a = sum(map(d, ("40000", "5000", "2000", "3000"))) - d("8000") - d("600")
    person_b = d("25000") - d("3500") - d("400")
    return {
        "hypothetical_person_a_disposable": str(person_a),
        "hypothetical_two_person_disposable": str(person_a + person_b),
        "treasury_emtr_illustration_percent": str((1 - (d(1) - d(".30") - d(".40"))) * 100),
        "hypothetical_tax_only_change_percent": str((1 - (d(1) - d(".30"))) * 100),
        "hypothetical_cliff_change_percent": str((1 - d("-9.20") / d(1)) * 100),
        "treasury_ptr_illustration_percent": str((1 - (d(800) - d(600)) / d(1000)) * 100),
        "treasury_rr_illustration_percent": str(d(600) / d(1000) * 100),
    }


def retrieve(destination: Path) -> list[dict[str, object]]:
    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for name, url in SOURCES.items():
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=45) as response:
            raw = response.read()
        extension = (
            ".html" if name.startswith("hils-") else ".pdf" if name.startswith("emtr-") else ".doc"
        )
        (destination / (name + extension)).write_bytes(raw)
        record: dict[str, object] = {
            "id": name,
            "url": url,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        if extension == ".html":
            reader = PageData()
            reader.feed(raw.decode("utf-8"))
            if not reader.payload:
                raise ValueError(f"{name}: published page payload missing; do not infer content")
            (destination / (name + ".json")).write_text(
                json.dumps(reader.payload, indent=2), encoding="utf-8"
            )
            record["page_date"] = reader.payload.get("PageDate")
        records.append(record)
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources-dir", type=Path, help="Optional explicit network retrieval directory"
    )
    options = parser.parse_args()
    output: dict[str, object] = {"method_examples": examples()}
    if options.sources_dir is not None:
        output["retrieved_sources"] = retrieve(options.sources_dir)
    print(json.dumps(output, indent=2))
