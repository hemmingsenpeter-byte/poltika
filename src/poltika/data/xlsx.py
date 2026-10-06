"""A minimal reader for published `.xlsx` workbooks (v0.2 Task 9.4).

Agencies publish some tables only as Excel workbooks. An `.xlsx` file is a
zip of XML parts, so the standard library is enough to read cell values
without a new dependency (D6). This returns each cell's stored text exactly:
shared and inline strings as text, numbers as their stored digits. Styles,
formulas and formatting are ignored, and dates stay as Excel serial numbers
(`excel_date()` converts them). Transformations use it on raw snapshot bytes.
"""

from __future__ import annotations

import io
import posixpath
import re
import zipfile
from datetime import date, timedelta
from xml.etree import ElementTree  # nosec B405
from xml.parsers import expat  # nosec B407

_NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
_CELL = re.compile(r"^([A-Z]+)(\d+)$")
_EXCEL_EPOCH = date(1899, 12, 30)

Sheet = dict[int, dict[int, str]]  # 1-based row -> 0-based column -> text


class XlsxError(ValueError):
    pass


def _fromstring(data: bytes) -> ElementTree.Element:
    """Parse one XML part, refusing any DTD or entity declaration first.

    A workbook part never needs a DTD, and a DTD is the only way for XML to
    ask a parser for entity expansion or an external resource. Expat reports
    one before the element tree parser sees the part, whatever its encoding.
    The input is a retained, hash-checked snapshot, so this is defence in
    depth: it adds no dependency and changes no parsed value. A part with a
    DTD is refused whether or not it is also well-formed."""
    guard = expat.ParserCreate()

    def refuse(*_: object) -> None:
        raise XlsxError("workbook part declares a DTD or entity")

    guard.StartDoctypeDeclHandler = refuse
    guard.EntityDeclHandler = refuse
    try:
        guard.Parse(data, True)
    except expat.ExpatError:
        pass  # not well-formed: the element tree parser below reports it
    # Safe: the guard above rejected every DTD and entity declaration.
    return ElementTree.fromstring(data)  # nosec B314


def _column(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def _text(element: ElementTree.Element) -> str:
    return "".join(t.text or "" for t in element.iter(f"{{{_NS['m']}}}t"))


def read_sheet(raw: bytes, sheet_name: str) -> Sheet:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        workbook = _fromstring(archive.read("xl/workbook.xml"))
        rels = _fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", _NS)}
        rel_id = next(
            (
                s.get(f"{{{_NS['r']}}}id")
                for s in workbook.iterfind("m:sheets/m:sheet", _NS)
                if s.get("name") == sheet_name
            ),
            None,
        )
        if rel_id is None or rel_id not in targets:
            raise XlsxError(f"no sheet named '{sheet_name}'")
        target = targets[rel_id] or ""
        path = target.lstrip("/") if target.startswith("/") else posixpath.join("xl", target)
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = _fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [_text(si) for si in strings.findall("m:si", _NS)]
        sheet = _fromstring(archive.read(path))

    cells: Sheet = {}
    for c in sheet.iterfind("m:sheetData/m:row/m:c", _NS):
        match = _CELL.match(c.get("r") or "")
        if match is None:
            raise XlsxError(f"unexpected cell reference {c.get('r')!r}")
        kind = c.get("t")
        value = c.find("m:v", _NS)
        if kind == "inlineStr":
            inline = c.find("m:is", _NS)
            text = _text(inline) if inline is not None else ""
        elif value is None or value.text is None:
            continue
        elif kind == "s":
            text = shared[int(value.text)]
        else:
            text = value.text
        cells.setdefault(int(match.group(2)), {})[_column(match.group(1))] = text
    return cells


def excel_date(serial: str) -> date:
    """An Excel (1900 date system) serial number as a date."""
    return _EXCEL_EPOCH + timedelta(days=int(float(serial)))
