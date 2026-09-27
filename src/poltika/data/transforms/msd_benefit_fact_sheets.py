"""Ministry of Social Development, Benefit Fact Sheets: national benefit tables.

Reads the "Supplementary - last 5 years" sheet exactly as published (v0.2
Task 9.4): recipients of Accommodation Supplement, all ages, by quarter.
The table labels each quarter by its last month ("Jun-26"); the count is
recorded for that quarter. The fact sheets note that people may receive
more than one supplementary assistance, and that supplementary data covers
all ages and non-beneficiaries.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation
from poltika.data.xlsx import read_sheet

UNIT = "recipients"
VARIABLES: dict[str, str] = {"accommodation_supplement.recipients": UNIT}
_MONTHS = {m: i for i, m in enumerate(("Mar", "Jun", "Sep", "Dec"), start=1)}


class MsdWorkbookError(ValueError):
    pass


def _quarter(label: str) -> tuple[date, date]:
    month, _, yy = label.partition("-")
    if month not in _MONTHS or not yy.isdigit():
        raise MsdWorkbookError(f"unexpected quarter label '{label}'")
    year, q = 2000 + int(yy), _MONTHS[month]
    start = date(year, 3 * q - 2, 1)
    end = date(year + 1, 1, 1) if q == 4 else date(year, 3 * q + 1, 1)
    return start, end


@transformation("msd_benefit_fact_sheets_national", version=1)
def benefit_fact_sheets(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    sheet = read_sheet(raw, "Supplementary - last 5 years")
    header = next(r for r in sorted(sheet) if sheet[r].get(1) == "Assistance")
    row = next(
        (
            r
            for r in sorted(sheet)
            if r > header and sheet[r].get(1) == "Accommodation Supplement (AS)"
        ),
        None,
    )
    if row is None:
        raise MsdWorkbookError("no Accommodation Supplement (AS) row")
    out = []
    for col, label in sorted(sheet[header].items()):
        if col <= 1:
            continue
        text = sheet[row].get(col, "").strip()
        if text:
            out.append(
                Row("accommodation_supplement.recipients", *_quarter(label), Decimal(text), UNIT)
            )
    return out
