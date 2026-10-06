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

    Expat reads the whole document before the element tree parser sees it.
    A document with a DTD is refused whether or not it is also well-formed.
    A document Expat cannot read raises `ElementTree.ParseError`, as before,
    but ElementTree is never called on it."""
    guard = expat.ParserCreate()

    def refuse(*_: object) -> None:
        raise UnsafeXmlError("XML document declares a DTD or entity")

    guard.StartDoctypeDeclHandler = refuse
    # Redundant defence in depth: an entity declaration can only appear inside
    # a DTD, which the handler above already refuses.
    guard.EntityDeclHandler = refuse
    try:
        guard.Parse(data, True)
    except expat.ExpatError as exc:
        # Fail closed: Expat can stop on malformed input before it reaches a
        # declaration, so bytes it could not validate never go to ElementTree.
        # Raise ElementTree's own error, with Expat's message, code and position.
        error = ElementTree.ParseError(str(exc))
        error.code = exc.code
        error.position = (exc.lineno, exc.offset)
        raise error from None
    # Safe: the guard above parsed the whole document and rejected every DTD
    # and entity declaration.
    return ElementTree.fromstring(data)  # nosec B314
