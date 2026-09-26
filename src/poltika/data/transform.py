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


TRANSFORMATIONS: dict[str, Transformation] = {}


def transformation(transformation_id: str, version: int) -> Callable[[TransformFn], TransformFn]:
    def register(fn: TransformFn) -> TransformFn:
        if transformation_id in TRANSFORMATIONS:
            raise ValueError(f"transformation '{transformation_id}' is already registered")
        TRANSFORMATIONS[transformation_id] = Transformation(transformation_id, version, fn)
        return fn

    return register
