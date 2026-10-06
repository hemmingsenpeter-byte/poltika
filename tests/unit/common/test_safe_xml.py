"""The shared DTD guard (`poltika.common.safe_xml`). No network, no files."""

from __future__ import annotations

import ast
from pathlib import Path
from xml.etree import ElementTree

import pytest

from poltika.common import safe_xml
from poltika.common.errors import PoltikaError

SRC = Path(__file__).resolve().parents[3] / "src" / "poltika"

DOCTYPES = [
    '<!DOCTYPE x SYSTEM "https://example.invalid/external.dtd">',
    '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///never-read">]>',
    '<!DOCTYPE x [<!ENTITY % a SYSTEM "https://example.invalid/entity">%a;]>',
    '<!DOCTYPE x [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;"><!ENTITY c "&b;&b;&b;&b;">]>',
    "<!DOCTYPE x>",
]


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
@pytest.mark.parametrize("doctype", DOCTYPES)
def test_any_dtd_is_refused_before_element_tree(
    encoding: str, doctype: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_parse(*args: object, **kwargs: object) -> None:
        pytest.fail("ElementTree parsed a DTD-bearing document")

    monkeypatch.setattr(ElementTree, "fromstring", unexpected_parse)
    xml = f'<?xml version="1.0" encoding="{encoding}"?>{doctype}<x>&#65;</x>'
    with pytest.raises(safe_xml.UnsafeXmlError, match="DTD"):
        safe_xml.fromstring(xml.encode(encoding))


def test_a_malformed_document_with_a_dtd_is_still_refused_as_unsafe() -> None:
    with pytest.raises(safe_xml.UnsafeXmlError):
        safe_xml.fromstring(b'<!DOCTYPE x [<!ENTITY a "b">]><x><unclosed></x>')


def test_malformed_xml_without_a_dtd_still_raises_parse_error() -> None:
    with pytest.raises(ElementTree.ParseError):
        safe_xml.fromstring(b"<not xml")


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "iso-8859-1"])
def test_a_document_without_a_dtd_parses_exactly_as_element_tree(encoding: str) -> None:
    xml = f'<?xml version="1.0" encoding="{encoding}"?><a k="v"><b>café &amp; &#65;</b></a>'
    data = xml.encode(encoding)
    ours, theirs = safe_xml.fromstring(data), ElementTree.fromstring(data)
    assert ElementTree.tostring(ours) == ElementTree.tostring(theirs)


def test_the_error_is_a_poltika_error_and_a_value_error() -> None:
    assert issubclass(safe_xml.UnsafeXmlError, PoltikaError)
    assert issubclass(safe_xml.UnsafeXmlError, ValueError)


def test_only_safe_xml_parses_xml_from_bytes_or_text() -> None:
    """Every other module reaches ElementTree's parsers through the guard."""
    parsers = {"fromstring", "XML", "parse", "iterparse", "XMLParser", "XMLPullParser"}
    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        if path == SRC / "common" / "safe_xml.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        aliases = {"ElementTree", "ET"}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr in parsers
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                offenders.append(f"{path.relative_to(SRC)}:{node.lineno}")
            if isinstance(node, ast.ImportFrom) and node.module and "xml" in node.module:
                names = {a.name for a in node.names}
                if names & parsers or "expat" in names or node.module.startswith("xml.dom"):
                    offenders.append(f"{path.relative_to(SRC)}:{node.lineno}")
    assert offenders == []


# Codex recheck of #174, R1: malformed input that stops Expat before a
# declaration callback must fail closed, never reaching ElementTree.
MALFORMED = [
    b'<!ENTITY a "test"><x/>',
    b'!<!DOCTYPE x [<!ENTITY a "test">]><x>&a;</x>',
    b"<!DOCTYPE x SYSTEM><x/>",
    b"<not xml",
    b"",
]


@pytest.mark.parametrize("data", MALFORMED)
def test_malformed_input_never_reaches_element_tree(
    data: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_parse(*args: object, **kwargs: object) -> None:
        pytest.fail("ElementTree parsed bytes the guard could not validate")

    monkeypatch.setattr(ElementTree, "fromstring", unexpected_parse)
    with pytest.raises(ElementTree.ParseError):
        safe_xml.fromstring(data)


@pytest.mark.parametrize(
    "data",
    [
        b"<not xml",
        b"<a><b></a>",
        b'<!ENTITY a "test"><x/>',
        b"",
        b"<a:x>",
        b"<:a >",
        b'<a xmlns:xmlns="u">',
    ],
)
def test_parse_error_matches_element_tree(data: bytes) -> None:
    with pytest.raises(ElementTree.ParseError) as ours:
        safe_xml.fromstring(data)
    with pytest.raises(ElementTree.ParseError) as theirs:
        ElementTree.fromstring(data)
    assert str(ours.value) == str(theirs.value)
    assert ours.value.code == theirs.value.code
    assert ours.value.position == theirs.value.position
