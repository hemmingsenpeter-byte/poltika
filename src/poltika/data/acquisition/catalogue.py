"""Source preservation archive: the reviewed source catalogue (ADR-0022).

`data/source_archive/sources/<system>.yaml` lists which public source
distributions Poltika preserves. A human reviews every entry. Nothing here
fetches anything, and nothing here is governed modelling data.

Two rules the loader enforces:

- ids are unique lower_snake and the dataset identifier is the publisher's
  own, never a title;
- no credential ever lives in the YAML. Keys named like a secret, and values
  that look like one, are rejected before the models are built. Secrets come
  from the environment at run time and go only into `FetchRequest.secret_headers`.

`check_frequency` is Poltika's own retrieval cadence. It is deliberately a
different field from `dataset.accrual_periodicity`, which is how often the
SOURCE says it publishes.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from poltika.common.errors import PoltikaError
from poltika.data.acquisition.models import AccessKind, Reference

_LOWER_SNAKE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
# Key names that look like credentials. Matched on whole snake/kebab words.
_SECRET_KEY_WORDS = frozenset(
    {
        "key",
        "apikey",
        "token",
        "secret",
        "password",
        "passwd",
        "subscription",
        "credential",
        "credentials",
        "authorization",
        "bearer",
        "ocp",
    }
)
_SECRET_VALUE = re.compile(
    r"(?i)(ocp-apim|subscription[-_ ]key|^bearer\s|api[-_]?key\s*[=:]|\b[0-9a-f]{32}\b)"
)


# Hosts a connector may send its credential to, per source system. Stats NZ: the https
# base URL in https://www.stats.govt.nz/tools/aotearoa-data-explorer/ade-api-user-guide/
# (the guide's http://apis.stats.govt.nz alternative is plain http, so it is not allowed).
ALLOWED_BASE_HOSTS: dict[str, frozenset[str]] = {
    "stats_nz": frozenset({"api.data.stats.govt.nz"}),
}


class CatalogueError(PoltikaError):
    """The source catalogue is invalid."""


def check_base_url(source_system: str, value: str) -> str:
    """`value` unchanged if it is https on an allow-listed host for the system."""
    allowed = ALLOWED_BASE_HOSTS.get(source_system)
    if allowed is None:
        return value
    parts = urllib.parse.urlsplit(value)
    if parts.scheme != "https" or (parts.hostname or "") not in allowed:
        raise CatalogueError(
            f"base_url must be https on one of {sorted(allowed)} for {source_system} "
            "(the credential is sent to it)"
        )
    if parts.username or parts.password or parts.port not in (None, 443):
        raise CatalogueError("base_url must not carry userinfo or a non-default port")
    if parts.query or parts.fragment or "?" in value or "#" in value:
        raise CatalogueError("base_url must not carry a query or fragment")
    return value


def _key_is_secret_like(key: str) -> bool:
    words = re.split(r"[^a-z0-9]+", key.lower())
    return any(w in _SECRET_KEY_WORDS for w in words) or "apikey" in key.lower().replace("_", "")


def _scan_for_credentials(node: Any, path: str = "") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if _key_is_secret_like(str(key)):
                raise CatalogueError(f"credential-like key {here!r} is not allowed in a catalogue")
            _scan_for_credentials(value, here)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _scan_for_credentials(value, f"{path}[{i}]")
    elif isinstance(node, str) and _SECRET_VALUE.search(node):
        raise CatalogueError(f"credential-like value at {path!r} is not allowed in a catalogue")


class DatasetSpec(BaseModel):
    """Reviewer-verified dataset values (DCAT dataset). Unknown stays null."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    identifier: str
    publisher_identifier: str | None = None
    publisher_name: str | None = None
    licence: str | None = None
    rights: str | None = None
    attribution: str | None = None
    accrual_periodicity: str | None = None
    landing_page: str | None = None
    references: tuple[Reference, ...] = ()


class DistributionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    identifier: str
    access_kind: AccessKind
    title: str | None = None
    format: str | None = None
    media_type: str | None = None
    access_url: str | None = None

    @field_validator("identifier")
    @classmethod
    def _snake(cls, v: str) -> str:
        if not _LOWER_SNAKE.match(v):
            raise ValueError(f"distribution identifier {v!r} must be lower_snake")
        return v


class SecondaryCatalogue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    data_govt_nz_package: str | None = None


class SourceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    enabled: bool = True
    note: str | None = None  # reviewer's free text; never archived
    verification: str  # where the identifier was verified, or what is missing
    dataset: DatasetSpec
    distribution: DistributionSpec
    request: dict[str, str]  # connector-specific; no credentials
    secondary_catalogue: SecondaryCatalogue = SecondaryCatalogue()
    check_frequency: str | None = None  # Poltika's retrieval cadence, not the source's

    @field_validator("id")
    @classmethod
    def _snake(cls, v: str) -> str:
        if not _LOWER_SNAKE.match(v):
            raise ValueError(f"source id {v!r} must be lower_snake")
        return v


class SourceCatalogue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_system: str
    sources: tuple[SourceEntry, ...]

    @field_validator("source_system")
    @classmethod
    def _snake(cls, v: str) -> str:
        if not _LOWER_SNAKE.match(v):
            raise ValueError(f"source_system {v!r} must be lower_snake")
        return v

    @model_validator(mode="after")
    def _unique_ids(self) -> SourceCatalogue:
        seen: set[str] = set()
        for entry in self.sources:
            if entry.id in seen:
                raise ValueError(f"duplicate source id {entry.id!r}")
            seen.add(entry.id)
        return self

    @model_validator(mode="after")
    def _allowed_base_urls(self) -> SourceCatalogue:
        for entry in self.sources:
            base = entry.request.get("base_url")
            if base is not None:
                try:
                    check_base_url(self.source_system, base)
                except CatalogueError as exc:
                    raise ValueError(f"{entry.id}: {exc}") from None
        return self

    def get(self, source_id: str) -> SourceEntry:
        for entry in self.sources:
            if entry.id == source_id:
                return entry
        raise CatalogueError(f"unknown source id {source_id!r}")

    def enabled(self) -> tuple[SourceEntry, ...]:
        return tuple(e for e in self.sources if e.enabled)


def parse_catalogue(text: str) -> SourceCatalogue:
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise CatalogueError(f"catalogue is not valid YAML: {exc}") from None
    if not isinstance(raw, dict):
        raise CatalogueError("catalogue must be a YAML mapping")
    _scan_for_credentials(raw)
    try:
        return SourceCatalogue.model_validate(raw)
    except ValueError as exc:
        raise CatalogueError(f"invalid catalogue: {exc}") from None


def load_catalogue(path: Path) -> SourceCatalogue:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CatalogueError(f"cannot read catalogue {path}: {exc}") from None
    return parse_catalogue(text)


def default_catalogue_path(repo_root: Path, source_system: str = "stats_nz") -> Path:
    return repo_root / "data" / "source_archive" / "sources" / f"{source_system}.yaml"
