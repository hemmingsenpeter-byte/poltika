"""Source preservation archive: optional data.govt.nz secondary reference
(ADR-0022, spec section 13).

catalogue.data.govt.nz is a CKAN catalogue. A matching record is a pointer, not
a substitute: it is never the source of content or metadata, and its
`Reference` is marked `authoritative=False`. This module never searches and
guesses. It looks up one package name that a human configured in the
reviewed catalogue, and only when the record exists under exactly that name.

A failed lookup (network, HTTP error, bad JSON, wrong name) returns `None`. It
never raises and never fails acquisition. No CKAN client dependency: one
`package_show` GET through the shared retrying `fetch`.
"""

from __future__ import annotations

import json
import urllib.parse
from collections.abc import Callable

from poltika.data.acquisition.models import Reference, ReferenceKind
from poltika.data.acquisition.source import (
    AcquisitionError,
    FetchRequest,
    RetryPolicy,
    Transport,
    UrllibTransport,
    fetch,
)

CKAN_API = "https://catalogue.data.govt.nz/api/3/action/package_show"
CKAN_DATASET_PAGE = "https://catalogue.data.govt.nz/dataset/"
LOOKUP_POLICY = RetryPolicy(max_attempts=2, base_delay=1.0, max_delay=5.0, timeout=15.0)

SecondaryLookup = Callable[[str], Reference | None]


def lookup_package(
    package_name: str | None,
    transport: Transport | None = None,
    policy: RetryPolicy = LOOKUP_POLICY,
) -> Reference | None:
    """A secondary catalogue reference for a configured package name, or None."""
    if not package_name:
        return None
    try:
        request = FetchRequest(
            url=CKAN_API,
            query=(("id", package_name),),
            headers=(("Accept", "application/json"),),
        )
        response = fetch(request, transport if transport is not None else UrllibTransport(), policy)
        payload = json.loads(response.body)
        result = payload["result"]
        if payload.get("success") is not True or result.get("name") != package_name:
            return None
        return Reference(
            kind=ReferenceKind.SECONDARY_CATALOGUE_RECORD,
            url=CKAN_DATASET_PAGE + urllib.parse.quote(package_name, safe=""),
            authoritative=False,
        )
    except (AcquisitionError, ValueError, KeyError, TypeError, AttributeError):
        return None
