"""v0.2 Task 2.3: `DataContext`, the data layer's `CanonicalContext`.

It joins the registry, the transformation registry and the data dictionary.
A snapshot is transformed only when first asked for, and every row is
checked before anything downstream can see it:

- the manifest names the transformation's current version;
- the row's variable is in both the manifest's mapping and the dictionary;
- the row's unit is the dictionary's unit;
- its period is non-empty and inside the variable's valid period;
- no two rows of one variable overlap.

Each variable comes from exactly one dataset. Two datasets mapping the same
variable is an error until a source-precedence rule is decided.
"""

from __future__ import annotations

import hashlib
from datetime import date
from itertools import pairwise
from pathlib import Path

import yaml

import poltika.data.transforms  # noqa: F401  (registers the transformations)
from poltika.common.errors import PoltikaError
from poltika.data.registry import DatasetRegistry, Snapshot
from poltika.data.transform import TRANSFORMATIONS, Transformation
from poltika.semantics.variables import DataDictionary, Lineage, Observation


class DataContextError(PoltikaError):
    """A snapshot's transformation, mapping or rows break the data contract."""


class NoObservationError(PoltikaError):
    """No observation of the variable covers the requested date. An expected
    outcome, like a date outside every parameter interval, not a data fault."""


class DataContext:
    def __init__(
        self,
        data_root: Path,
        transformations: dict[str, Transformation] | None = None,
    ) -> None:
        self.registry = DatasetRegistry(data_root)
        self.dictionary = DataDictionary.model_validate(
            yaml.safe_load((data_root / "metadata" / "variables" / "dictionary.yaml").read_text())
            or {}
        )
        self._transformations = TRANSFORMATIONS if transformations is None else transformations
        self._source_of = self._variable_sources()
        self._cache: dict[tuple[str, int], list[Observation]] = {}

    def get(self, variable_id: str, on: date, vintage: str | None = None) -> Observation:
        if variable_id not in self._source_of:
            raise NoObservationError(f"no dataset provides '{variable_id}'")
        snapshot = self.registry.resolve(self._source_of[variable_id], vintage)
        for obs in self._observations(snapshot):
            if obs.variable_id == variable_id and obs.period_start <= on < obs.period_end:
                return obs
        raise NoObservationError(
            f"'{variable_id}' has no observation covering {on} in "
            f"{snapshot.manifest.dataset_id} vintage '{snapshot.manifest.vintage}'"
        )

    def _variable_sources(self) -> dict[str, str]:
        known = self.dictionary.by_id()
        sources: dict[str, str] = {}
        for snapshot in self.registry.snapshots():
            m = snapshot.manifest
            for variable_id in m.canonical_variable_mapping:
                if variable_id not in known:
                    raise DataContextError(
                        f"{m.manifest_name} maps '{variable_id}', which is not in the data dictionary"
                    )
                if sources.setdefault(variable_id, m.dataset_id) != m.dataset_id:
                    raise DataContextError(
                        f"'{variable_id}' is mapped by both {sources[variable_id]} and {m.dataset_id}"
                    )
        return sources

    def _observations(self, snapshot: Snapshot) -> list[Observation]:
        m = snapshot.manifest
        key = (m.dataset_id, m.raw_snapshot_version)
        if key not in self._cache:
            self._cache[key] = self._transform(snapshot)
        return self._cache[key]

    def _transform(self, snapshot: Snapshot) -> list[Observation]:
        m = snapshot.manifest
        t = self._transformations.get(m.transformation_id)
        if t is None:
            raise DataContextError(f"{m.manifest_name}: no transformation '{m.transformation_id}'")
        if t.version != m.transformation_version:
            raise DataContextError(
                f"{m.manifest_name}: names {t.id} version {m.transformation_version}; "
                f"the registered version is {t.version}"
            )
        lineage = Lineage(
            transformation_id=t.id,
            transformation_version=t.version,
            dataset_id=m.dataset_id,
            raw_snapshot_version=m.raw_snapshot_version,
            raw_sha256=m.sha256,
            source_organisation=m.source_organisation,
            publication=m.dataset_series,
            source_url_or_identifier=m.source_url_or_identifier,
            vintage=m.vintage,
            retrieval_date=m.retrieval_date,
        )
        variables = self.dictionary.by_id()
        observations: list[Observation] = []
        raw = snapshot.path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != m.sha256:
            raise DataContextError(f"{m.manifest_name}: raw snapshot sha256 changed before transformation")
        for row in t.fn(raw, m):
            where = f"{m.manifest_name}: {row.variable_id} [{row.period_start}, {row.period_end})"
            if row.variable_id not in m.canonical_variable_mapping:
                raise DataContextError(f"{where}: variable is not in the manifest's mapping")
            variable = variables[row.variable_id]
            if row.unit != variable.unit:
                raise DataContextError(
                    f"{where}: unit '{row.unit}', the dictionary says '{variable.unit}'"
                )
            if row.period_end <= row.period_start:
                raise DataContextError(f"{where}: empty period")
            if row.period_start < variable.valid_from or (
                variable.valid_to is not None and row.period_end > variable.valid_to
            ):
                raise DataContextError(f"{where}: outside the variable's valid period")
            observations.append(
                Observation(
                    variable_id=row.variable_id,
                    period_start=row.period_start,
                    period_end=row.period_end,
                    value=row.value,
                    unit=row.unit,
                    lineage=lineage,
                )
            )
        _check_no_overlap(m.manifest_name, observations)
        return observations


def _check_no_overlap(manifest_name: str, observations: list[Observation]) -> None:
    ordered = sorted(observations, key=lambda o: (o.variable_id, o.period_start))
    for a, b in pairwise(ordered):
        if a.variable_id == b.variable_id and b.period_start < a.period_end:
            raise DataContextError(
                f"{manifest_name}: {a.variable_id} has overlapping periods "
                f"starting {a.period_start} and {b.period_start}"
            )
