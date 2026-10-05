"""Synthetic fixtures for the archive tests. Every value is made up and
labelled synthetic; none describes a real publication."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from poltika.data.acquisition.archive import SourceArchive
from poltika.data.acquisition.models import (
    AccessKind,
    DatasetDescriptor,
    DistributionDescriptor,
    SourceMetadata,
)
from poltika.data.acquisition.source import FetchRequest, FetchResponse, SourceObservation

T0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
SYNTHETIC_BYTES = b"period,value\n2020,1\n2021,2\n"


def make_metadata(**dataset_overrides: object) -> SourceMetadata:
    dataset: dict[str, object] = {
        "source_system": "synthetic_src",
        "source_dataset_identifier": "SYN:DATAFLOW",
        "title": "Synthetic dataset",
        "publisher_identifier": "synthetic-publisher",
        "publisher_name": "Synthetic Publisher",
        "publisher_name_at_capture": "Synthetic Publisher",
    }
    dataset.update(dataset_overrides)
    return SourceMetadata(
        dataset=DatasetDescriptor(**dataset),  # type: ignore[arg-type]
        distribution=DistributionDescriptor(
            distribution_identifier="synthetic_csv",
            dataset_identifier="SYN:DATAFLOW",
            access_kind=AccessKind.API,
        ),
    )


@pytest.fixture
def archive(tmp_path: Path) -> SourceArchive:
    return SourceArchive(tmp_path / "archive")


ObservationFactory = Callable[..., SourceObservation]


@pytest.fixture
def make_observation() -> ObservationFactory:
    counter = {"n": 0}

    def _make(
        body: bytes = SYNTHETIC_BYTES,
        metadata: SourceMetadata | None = None,
        source_id: str = "synthetic_series",
        started_at: datetime | None = None,
        secret_headers: tuple[tuple[str, str], ...] = (),
        native: bytes | None = b"<native/>",  # None: a run without native metadata
        status: int = 200,
    ) -> SourceObservation:
        counter["n"] += 1
        start = started_at or T0 + timedelta(seconds=counter["n"])
        request = FetchRequest(
            url="https://example.invalid/data",
            query=(("b", "2"), ("a", "1")),
            headers=(("Accept", "text/csv"),),
            secret_headers=secret_headers,
        )

        def response(data: bytes) -> FetchResponse:
            return FetchResponse(
                request=request,
                status=status,
                headers=(("content-type", "text/csv"), ("etag", '"x"')),
                body=data,
                started_at=start,
                received_at=start + timedelta(milliseconds=5),
            )

        return SourceObservation(
            poltika_source_id=source_id,
            metadata=metadata or make_metadata(),
            content=response(body),
            native_metadata=response(native) if native is not None else None,
        )

    return _make
