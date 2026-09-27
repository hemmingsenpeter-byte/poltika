"""Inland Revenue, Working for Families statistics (the dataset workbook).

Reads the "Working for families data" sheet exactly as published (v0.2
Task 9.4): the number of families with non-zero entitlement (thousands),
aggregate entitlements ($ million) and children supported (thousands), by
tax year. The workbook labels each tax year with a date in its March; the
tax year runs from 1 April of the year before. Some cells store binary
floating-point noise (for example 2.2999999999999998 for 2.3), so counts
are rounded to the published one decimal place and dollar totals to whole
millions.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from poltika.data.manifest import DatasetManifest
from poltika.data.transform import Row, transformation
from poltika.data.xlsx import Sheet, excel_date, read_sheet

FAMILIES = "thousands of families"
DOLLARS = "NZD million per tax year"
CHILDREN = "thousands of children"

# (block heading prefix, column header, variable, unit, precision)
_BLOCKS = (
    (
        "Working for Families tax credits - number of WFF claims",
        "FTC",
        "wff.families_entitled.family_tax_credit",
        FAMILIES,
        "0.1",
    ),
    (
        "Working for Families tax credits - number of WFF claims",
        "BSTC",
        "wff.families_entitled.best_start",
        FAMILIES,
        "0.1",
    ),
    (
        "Working for Families Tax Credits - aggregate entitlements",
        "FTC",
        "wff.entitlement.family_tax_credit",
        DOLLARS,
        "1",
    ),
    (
        "Working for Families Tax Credits - aggregate entitlements",
        "BSTC",
        "wff.entitlement.best_start",
        DOLLARS,
        "1",
    ),
    (
        "Working for Families Tax Credits - number of children supported",
        "Total number of children (000s)",
        "wff.children_supported",
        CHILDREN,
        "0.1",
    ),
)
VARIABLES: dict[str, str] = {variable: unit for _, _, variable, unit, _ in _BLOCKS}


class IrdWorkbookError(ValueError):
    pass


def _block(sheet: Sheet, heading: str, column: str) -> list[tuple[date, str]]:
    start = next((r for r in sorted(sheet) if sheet[r].get(0, "").startswith(heading)), None)
    if start is None:
        raise IrdWorkbookError(f"no block headed '{heading}'")
    header_row = next(r for r in sorted(sheet) if r > start and sheet[r].get(0) == "Tax Year")
    col = next((c for c, text in sheet[header_row].items() if text.strip() == column), None)
    if col is None:
        raise IrdWorkbookError(f"block '{heading}' has no column '{column}'")
    values: list[tuple[date, str]] = []
    for r in sorted(sheet):
        if r <= header_row:
            continue
        first = sheet[r].get(0, "")
        if not first.replace(".", "").isdigit():
            if values:
                break  # the block's data has ended
            continue  # a sub-header row before the data
        text = sheet[r].get(col, "").strip()
        if text and text != "-":
            values.append((excel_date(first), text))
    return values


@transformation("ird_wff_statistics", version=1)
def wff_statistics(raw: bytes, manifest: DatasetManifest) -> list[Row]:
    sheet = read_sheet(raw, "Working for families data")
    rows: list[Row] = []
    for heading, column, variable, unit, precision in _BLOCKS:
        for labelled, text in _block(sheet, heading, column):
            value = Decimal(text).quantize(Decimal(precision), rounding=ROUND_HALF_UP)
            year = labelled.year  # tax year ending 31 March of this year
            rows.append(Row(variable, date(year - 1, 4, 1), date(year, 4, 1), value, unit))
    return rows
