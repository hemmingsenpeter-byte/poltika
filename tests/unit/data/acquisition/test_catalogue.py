"""Source catalogue (ADR-0022): validation and the shipped Stats NZ YAML."""

from __future__ import annotations

from pathlib import Path

import pytest

from poltika.data.acquisition.catalogue import (
    CatalogueError,
    default_catalogue_path,
    load_catalogue,
    parse_catalogue,
)

REPO = Path(__file__).resolve().parents[4]

ENTRY = """
  - id: {id}
    verification: synthetic
    dataset: {{identifier: "SYN:ONE"}}
    distribution: {{identifier: dist_one, access_kind: api}}
    request: {{agency_id: SYN, dataflow_id: ONE, version: "1.0"{extra}}}
"""


def doc(*entries: str) -> str:
    return "source_system: stats_nz\nsources:\n" + "".join(entries)


def test_shipped_catalogue_loads_and_is_verified() -> None:
    cat = load_catalogue(default_catalogue_path(REPO))
    assert cat.source_system == "stats_nz"
    assert len(cat.enabled()) >= 3
    for entry in cat.sources:
        assert entry.verification.strip()
        assert entry.check_frequency is None
        assert entry.dataset.identifier.startswith("STATSNZ:")
        # accrual_periodicity (source's) is a different field from check_frequency (ours)
        assert entry.dataset.accrual_periodicity is None
        assert entry.dataset.licence == "Creative Commons Attribution 4.0 International"


def test_get_and_enabled() -> None:
    cat = parse_catalogue(doc(ENTRY.format(id="one", extra="")))
    assert cat.get("one").dataset.identifier == "SYN:ONE"
    with pytest.raises(CatalogueError, match="unknown source id"):
        cat.get("missing")


def test_duplicate_ids_rejected() -> None:
    text = doc(ENTRY.format(id="one", extra=""), ENTRY.format(id="one", extra=""))
    with pytest.raises(CatalogueError, match="duplicate source id"):
        parse_catalogue(text)


@pytest.mark.parametrize("bad", ["One", "one-two", "1one", "one__two"])
def test_ids_must_be_lower_snake(bad: str) -> None:
    with pytest.raises(CatalogueError):
        parse_catalogue(doc(ENTRY.format(id=bad, extra="")))


@pytest.mark.parametrize(
    "extra",
    [
        ", api_key: abc",
        ", subscription_key: abc",
        ", token: abc",
        ", Secret: abc",
        ", password: abc",
        ", Ocp-Apim-Subscription-Key: abc",
        ", key: abc",
    ],
)
def test_credential_like_keys_rejected(extra: str) -> None:
    with pytest.raises(CatalogueError, match="credential-like key"):
        parse_catalogue(doc(ENTRY.format(id="one", extra=extra)))


@pytest.mark.parametrize(
    "value",
    ["0123456789abcdef0123456789abcdef", "Bearer abc.def", "Ocp-Apim-Subscription-Key"],
)
def test_credential_like_values_rejected(value: str) -> None:
    with pytest.raises(CatalogueError, match="credential-like value"):
        parse_catalogue(doc(ENTRY.format(id="one", extra=f", note: {value!r}")))


def test_unknown_fields_rejected_and_bad_yaml() -> None:
    with pytest.raises(CatalogueError):
        parse_catalogue(doc(ENTRY.format(id="one", extra="").replace("verification", "bogus")))
    with pytest.raises(CatalogueError):
        parse_catalogue("[not a mapping")
    with pytest.raises(CatalogueError):
        parse_catalogue("- a list")
