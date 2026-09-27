"""v0.2 Task 2.2: the transformation registry.

A transformation turns one raw snapshot's bytes into canonical observations.
It is a named, versioned, pure function: the same bytes give the same rows,
with no clock, network or file access. Changing what a transformation
produces means a new version, and the manifests that use it must name that
version, so a changed value can always be attributed to a data change or a
transformation change (provenance skill, "Change attribution").

Registered transformations live in modules under `poltika.data.transforms`
and register themselves with `@transformation(...)` when imported.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from poltika.data.manifest import DatasetManifest


@dataclass(frozen=True)
class Row:
    variable_id: str
    period_start: date
    period_end: date
    value: Decimal
    unit: str


TransformFn = Callable[[bytes, DatasetManifest], list[Row]]


@dataclass(frozen=True)
class Transformation:
    id: str
    version: int
    fn: TransformFn


# Every registered version, so a manifest naming an older version still reads
# the way it was committed after a newer version is added.
TRANSFORMATION_VERSIONS: dict[tuple[str, int], Transformation] = {}
# The latest version of each transformation.
TRANSFORMATIONS: dict[str, Transformation] = {}


def transformation(transformation_id: str, version: int) -> Callable[[TransformFn], TransformFn]:
    def register(fn: TransformFn) -> TransformFn:
        key = (transformation_id, version)
        if key in TRANSFORMATION_VERSIONS:
            raise ValueError(
                f"transformation '{transformation_id}' version {version} is already registered"
            )
        t = Transformation(transformation_id, version, fn)
        TRANSFORMATION_VERSIONS[key] = t
        latest = TRANSFORMATIONS.get(transformation_id)
        if latest is None or version > latest.version:
            TRANSFORMATIONS[transformation_id] = t
        return fn

    return register
