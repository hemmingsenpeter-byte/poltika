"""Parse untrusted XML with the standard library, refusing any DTD first.

Poltika reads XML from published workbooks (`data/xlsx.py`) and from source
API responses (`data/acquisition/stats_nz.py`). Neither ever needs a DTD, and
a DTD is the only way for XML to ask a parser for entity expansion or an
external resource (billion laughs, XXE, parameter entities). So `fromstring`
refuses a document that declares one, whatever its encoding, before the
element tree parser sees it. It adds no dependency and changes no parsed
value: a document without a DTD parses exactly as `ElementTree.fromstring`
would parse it.

It lives in `common/` because `data/acquisition/` may depend only on `common/`
and the standard library (ADR-0022).
"""

from __future__ import annotations

from xml.etree import ElementTree  # nosec B405
from xml.parsers import expat  # nosec B407

from poltika.common.errors import PoltikaError


class UnsafeXmlError(PoltikaError, ValueError):
    """The document declares a DTD or an entity, so it was not parsed."""


def fromstring(data: bytes) -> ElementTree.Element:
    """Parse one XML document, refusing any DTD or entity declaration first.

    Expat reports the declaration before the element tree parser sees the
    document. A document with a DTD is refused whether or not it is also
    well-formed. Malformed XML without a DTD still raises
    `ElementTree.ParseError`, as before."""
    guard = expat.ParserCreate()

    def refuse(*_: object) -> None:
        raise UnsafeXmlError("XML document declares a DTD or entity")

    guard.StartDoctypeDeclHandler = refuse
    # Redundant defence in depth: an entity declaration can only appear inside
    # a DTD, which the handler above already refuses.
    guard.EntityDeclHandler = refuse
    try:
        guard.Parse(data, True)
    except expat.ExpatError:
        pass  # not well-formed: the element tree parser below reports it
    # Safe: the guard above rejected every DTD and entity declaration.
    return ElementTree.fromstring(data)  # nosec B314
