"""The `.xlsx` reader's output on every retained workbook is pinned.

Bandit B314 flagged the reader's XML parsing (v0.2 closeout). Hardening the
parser must not change one stored cell, so this pins, for every sheet of
every retained workbook, the SHA-256 of the sheet as canonical JSON (keys
sorted) and its cell count. The digests were taken from the reader before
it was hardened. A change here means the reader's output changed.
"""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest

from poltika.data.xlsx import XlsxError, _fromstring, read_sheet

ROOT = Path(__file__).resolve().parents[3]

# Retained workbook -> SHA-256 of its raw bytes (the hash-checked snapshot).
WORKBOOKS = {
    "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx": "d94bb1b27c86f2206208cf54edfdc7dc285aa25398030457dbb04a1bcb8bce2d",
    "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx": "d94bb1b27c86f2206208cf54edfdc7dc285aa25398030457dbb04a1bcb8bce2d",
    "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx": "90cd8e7c8ff210ca9334eb035dfef3a39abdefe10365e5f7a6ccbd4291248f74",
}

# (workbook, sheet, SHA-256 of json.dumps(sheet, sort_keys=True), cell count)
SHEETS = [
    (
        "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx",
        "Explanatory notes",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        0,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx",
        "Working for familes parameters",
        "272c07731dfd36f00211debf70e58809e3448e121a437423a84d3d83d3e4a6e0",
        415,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx",
        "Working for families charts",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        0,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx",
        "Working for families data",
        "00419cc4f93b6b50bac56576a69a0f7192db2dacba9e3a8df97d594d26633adf",
        797,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v1/working-for-families-statistics.xlsx",
        "Working for families income",
        "becfe8c492e473990938e7d9dcfa8c2469726e3c121f298dd874571c0c1be91f",
        2236,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx",
        "Explanatory notes",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        0,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx",
        "Working for familes parameters",
        "272c07731dfd36f00211debf70e58809e3448e121a437423a84d3d83d3e4a6e0",
        415,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx",
        "Working for families charts",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        0,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx",
        "Working for families data",
        "00419cc4f93b6b50bac56576a69a0f7192db2dacba9e3a8df97d594d26633adf",
        797,
    ),
    (
        "data/raw/ird/ird_working_for_families_statistics/v2/working-for-families-statistics.xlsx",
        "Working for families income",
        "becfe8c492e473990938e7d9dcfa8c2469726e3c121f298dd874571c0c1be91f",
        2236,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Contents and notes",
        "974cc159388bb2e7bedc2b2c6fc9e93d04f853d2dc2dc9324a3817341206a462",
        46,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Summary table-current",
        "cd812ef3000302ca2cbb89368b3e1ae7dbc20834180a85717cf3e6afb824f8ea",
        264,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Summary table - last 5 years",
        "3cce90a85240d3ccd107f350a744a2ceec019b87332cf63c727f772ead2f330b",
        134,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Main benefits - last 5 years",
        "2da53d7b580f448153e76efa90f2a053193e73397ee7007ba1fdc13a758a1b6d",
        424,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "JS - last 5 years",
        "662e1c223e81d453c7aed88b88229dcc435cf27096dbedb45575a5e5635afd27",
        602,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "SPS - last 5 years",
        "5e413db82b280da28706f23dc8f95750ebe1db1b991d9bc7b5e0ea3f4bdc93fa",
        469,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "SLP - last 5 years",
        "1b0f19136370c95303250b746aa41142cfdcda413b105af320014a3d6f7233f8",
        646,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Other - last 5 years",
        "b375a0afc138cdea1c295e5f51e4a8d1c13992231d2e6adcf26b6a54c6dd39ea",
        648,
    ),
    (
        "data/raw/msd/msd_benefit_fact_sheets_national/v1/quarterly-benefit-fact-sheets-national-benefit-tables-june-2026.xlsx",
        "Supplementary - last 5 years",
        "4c46e531f31c84e83eb481875d5d53996ef7bf035654d6de24fdcdda391038fc",
        980,
    ),
]


@pytest.mark.parametrize("path", sorted(WORKBOOKS))
def test_retained_workbook_bytes_are_the_pinned_snapshot(path: str) -> None:
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == WORKBOOKS[path]


@pytest.mark.parametrize(
    ("path", "sheet", "digest", "cells"),
    SHEETS,
    ids=[f"{s[0].rsplit('/', 3)[-3]}:{s[1]}" for s in SHEETS],
)
def test_sheet_output_is_byte_identical(path: str, sheet: str, digest: str, cells: int) -> None:
    parsed = read_sheet((ROOT / path).read_bytes(), sheet)
    assert sum(len(row) for row in parsed.values()) == cells
    canonical = json.dumps(parsed, sort_keys=True, ensure_ascii=True).encode()
    assert hashlib.sha256(canonical).hexdigest() == digest


def test_every_sheet_of_every_retained_workbook_is_pinned() -> None:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    found = set()
    for path in WORKBOOKS:
        with zipfile.ZipFile(io.BytesIO((ROOT / path).read_bytes())) as archive:
            workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        found |= {(path, s.get("name")) for s in workbook.iterfind("m:sheets/m:sheet", ns)}
    assert found == {(p, s) for p, s, _, _ in SHEETS}


MAIN = b"http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = b"http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = b"http://schemas.openxmlformats.org/package/2006/relationships"
SHEET = (
    b'<worksheet xmlns="' + MAIN + b'"><sheetData>'
    b'<row r="1"><c r="A1"><v>1.50</v></c><c r="C1" t="inlineStr"><is><t>x</t></is></c></row>'
    b"</sheetData></worksheet>"
)


def _workbook(sheet_xml: bytes, workbook_prefix: bytes = b"") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr(
            "xl/workbook.xml",
            workbook_prefix
            + b'<workbook xmlns="'
            + MAIN
            + b'" xmlns:r="'
            + REL
            + b'"><sheets><sheet name="S" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        z.writestr(
            "xl/_rels/workbook.xml.rels",
            b'<Relationships xmlns="'
            + PKG
            + b'"><Relationship Id="rId1" Target="worksheets/s1.xml"/></Relationships>',
        )
        z.writestr("xl/worksheets/s1.xml", sheet_xml)
    return buffer.getvalue()


def test_a_plain_workbook_reads_as_before() -> None:
    assert read_sheet(_workbook(SHEET), "S") == {1: {0: "1.50", 2: "x"}}


@pytest.mark.parametrize("part", ["workbook", "sheet"])
def test_a_workbook_with_a_dtd_or_entity_is_refused(part: str) -> None:
    bomb = b'<!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]>'
    raw = _workbook(bomb + SHEET) if part == "sheet" else _workbook(SHEET, workbook_prefix=bomb)
    with pytest.raises(XlsxError, match="DTD"):
        read_sheet(raw, "S")


@pytest.mark.parametrize("part", ["xl/_rels/workbook.xml.rels", "xl/sharedStrings.xml"])
def test_every_part_read_refuses_a_dtd(part: str) -> None:
    source = zipfile.ZipFile(io.BytesIO(_workbook(SHEET)))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for name in source.namelist():
            z.writestr(name, source.read(name))
        if part in source.namelist():
            z.writestr(part, b'<!DOCTYPE x [<!ENTITY a "b">]>' + source.read(part))
        else:
            z.writestr(part, b'<!DOCTYPE x [<!ENTITY a "b">]><sst xmlns="' + MAIN + b'"/>')
    with pytest.raises(XlsxError, match="DTD"):
        read_sheet(buffer.getvalue(), "S")


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "iso-8859-1"])
@pytest.mark.parametrize(
    "doctype",
    [
        '<!DOCTYPE x SYSTEM "https://example.invalid/external.dtd">',
        '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///never-read">]>',
        '<!DOCTYPE x [<!ENTITY % a SYSTEM "https://example.invalid/entity">%a;]>',
        '<!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]>',
    ],
)
def test_dtd_is_refused_before_element_tree_parsing(
    encoding: str, doctype: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_parse(*args: object, **kwargs: object) -> None:
        pytest.fail("ElementTree parsed a DTD-bearing part before it was refused")

    monkeypatch.setattr(ElementTree, "fromstring", unexpected_parse)
    xml = f'<?xml version="1.0" encoding="{encoding}"?>{doctype}<x/>'
    with pytest.raises(XlsxError, match="DTD"):
        _fromstring(xml.encode(encoding))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "iso-8859-1"])
def test_supported_xml_encodings_keep_cell_text(encoding: str) -> None:
    declaration = f'<?xml version="1.0" encoding="{encoding}"?>'
    xml = (declaration + SHEET.decode()).encode(encoding)
    assert read_sheet(_workbook(xml), "S") == {1: {0: "1.50", 2: "x"}}


def test_malformed_xml_keeps_the_original_parse_error() -> None:
    with pytest.raises(ElementTree.ParseError):
        read_sheet(_workbook(b"<worksheet>"), "S")
