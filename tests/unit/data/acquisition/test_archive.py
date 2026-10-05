"""Archive: content-addressed storage, records, change detection, safety."""

from __future__ import annotations

import os
import threading
from pathlib import Path

import pytest

from poltika.data.acquisition import archive as archive_mod
from poltika.data.acquisition.archive import (
    ENV_ARCHIVE_DIR,
    ArchiveError,
    CorruptBlobError,
    LocalBlobStore,
    SourceArchive,
    UnsafePathError,
    default_archive_root,
)
from poltika.data.acquisition.models import BlobStatus, sha256_hex

from .conftest import SYNTHETIC_BYTES, ObservationFactory, make_metadata

SECRET = "archive-secret-VALUE-987"


def all_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def test_exact_bytes_in_and_out(tmp_path: Path) -> None:
    store = LocalBlobStore(tmp_path)
    data = b"\x00\xffexact\r\n bytes\n"
    blob, status = store.put(data)
    assert status is BlobStatus.CREATED
    assert blob.sha256 == sha256_hex(data) and blob.size == len(data)
    assert blob.identifier == f"sha256:{blob.sha256}"
    assert store.get(blob.sha256) == data
    assert (tmp_path / "blobs" / "sha256" / blob.sha256[:2] / blob.sha256).read_bytes() == data
    assert store.exists(blob.sha256)
    assert (
        os.stat(tmp_path / "blobs" / "sha256" / blob.sha256[:2] / blob.sha256).st_mode & 0o222 == 0
    )


def test_five_identical_retrievals_five_records_one_blob(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    results = [archive.preserve(make_observation(), collector_version="t") for _ in range(5)]
    assert len(archive.records("synthetic_series")) == 5
    blobs = [p for p in all_files(archive.root / "blobs")]
    assert len(blobs) == 1
    assert [r.content_blob_status for r in results] == [BlobStatus.CREATED] + [
        BlobStatus.EXISTING
    ] * 4
    assert len({r.record.retrieval_id for r in results}) == 5


def test_changed_bytes_new_blob(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    archive.preserve(make_observation(), collector_version="t")
    archive.preserve(make_observation(body=SYNTHETIC_BYTES + b"2022,3\n"), collector_version="t")
    assert len(all_files(archive.root / "blobs")) == 2


def test_corrupt_blob_detected_on_put_and_get(tmp_path: Path) -> None:
    store = LocalBlobStore(tmp_path)
    blob, _ = store.put(b"good")
    path = tmp_path / "blobs" / "sha256" / blob.sha256[:2] / blob.sha256
    path.chmod(0o644)
    path.write_bytes(b"tampered")
    with pytest.raises(CorruptBlobError):
        store.get(blob.sha256)
    with pytest.raises(CorruptBlobError):
        store.put(b"good")
    assert path.read_bytes() == b"tampered"  # never silently replaced


def test_missing_blob_is_archive_error(tmp_path: Path) -> None:
    with pytest.raises(ArchiveError):
        LocalBlobStore(tmp_path).get("a" * 64)


def test_atomic_write_leaves_no_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalBlobStore(tmp_path)

    def boom(fd: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(archive_mod.os, "fsync", boom)
    with pytest.raises(OSError):
        store.put(b"payload")
    monkeypatch.undo()
    assert all_files(tmp_path) == []  # no final file, no leftover temp file
    assert not store.exists(sha256_hex(b"payload"))
    store.put(b"payload")  # still usable afterwards


def test_concurrent_put_same_bytes_is_safe(tmp_path: Path) -> None:
    store = LocalBlobStore(tmp_path)
    data = os.urandom(200_000)
    statuses: list[BlobStatus] = []
    errors: list[BaseException] = []

    def work() -> None:
        try:
            statuses.append(store.put(data)[1])
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=work) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors
    assert statuses.count(BlobStatus.CREATED) == 1
    assert store.get(sha256_hex(data)) == data
    assert len(all_files(tmp_path)) == 1


def test_race_on_link_verifies_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = LocalBlobStore(tmp_path)
    data = b"race"
    real_link = os.link

    def racing_link(src: str | Path, dst: str | Path) -> None:
        real_link(src, dst)  # another writer wins first
        raise FileExistsError

    monkeypatch.setattr(archive_mod.os, "link", racing_link)
    blob, status = store.put(data)
    assert status is BlobStatus.EXISTING and store.get(blob.sha256) == data


def test_record_never_overwritten(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    obs = make_observation()
    archive.preserve(obs, collector_version="t")
    # same started_at + same request fingerprint -> same retrieval_id
    with pytest.raises(ArchiveError):
        archive.preserve(obs, collector_version="t")
    assert len(archive.records("synthetic_series")) == 1


def test_first_observation_and_four_change_states(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    base = make_metadata()
    first = archive.preserve(make_observation(metadata=base), collector_version="t").record
    assert first.content_changed is None and first.metadata_changed is None
    assert first.previous_retrieval_id is None

    same = archive.preserve(make_observation(metadata=base), collector_version="t").record
    assert (same.content_changed, same.metadata_changed) == (False, False)
    assert same.previous_retrieval_id == first.retrieval_id

    new_meta = make_metadata(title="Retitled", licence="L")
    meta_only = archive.preserve(make_observation(metadata=new_meta), collector_version="t").record
    assert (meta_only.content_changed, meta_only.metadata_changed) == (False, True)
    assert meta_only.previous_metadata_sha256 == base.sha256()

    content_only = archive.preserve(
        make_observation(body=b"new", metadata=new_meta), collector_version="t"
    ).record
    assert (content_only.content_changed, content_only.metadata_changed) == (True, False)
    assert content_only.previous_content_sha256 == first.content_sha256

    both = archive.preserve(
        make_observation(body=b"newer", metadata=base), collector_version="t"
    ).record
    assert (both.content_changed, both.metadata_changed) == (True, True)
    assert len(archive.records("synthetic_series")) == 5
    assert archive.latest_record("synthetic_series") == both


def test_latest_record_none_when_empty(archive: SourceArchive) -> None:
    assert archive.latest_record("nothing_yet") is None
    assert archive.records("nothing_yet") == []


def test_records_round_trip_and_utc(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    result = archive.preserve(make_observation(native=b"<meta/>"), collector_version="t")
    text = result.record_path.read_text()
    assert '"request_started_at":"2026-01-01T12:00:01Z"' in text
    assert archive.latest_record("synthetic_series") == result.record
    assert result.record.metadata_raw_sha256 == sha256_hex(b"<meta/>")
    assert result.metadata_blob_status is BlobStatus.CREATED
    assert result.record.content_length == len(SYNTHETIC_BYTES)
    assert result.record.query_parameters == (("a", "1"), ("b", "2"))
    assert result.record.endpoint == "https://example.invalid/data"
    assert result.record.blob_identifier == f"sha256:{sha256_hex(SYNTHETIC_BYTES)}"


def test_metadata_snapshot_read_back_and_dedup(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    meta = make_metadata(licence="CC-BY synthetic")
    r1 = archive.preserve(make_observation(metadata=meta), collector_version="t")
    r2 = archive.preserve(make_observation(metadata=meta), collector_version="t")
    assert r1.metadata_snapshot_status is BlobStatus.CREATED
    assert r2.metadata_snapshot_status is BlobStatus.EXISTING
    loaded = archive.read_metadata(meta.sha256(), "synthetic_src", "synthetic_series")
    assert loaded == meta
    snapshots = all_files(archive.root / "metadata")
    assert len(snapshots) == 1


def test_corrupt_metadata_snapshot_detected(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    meta = make_metadata()
    archive.preserve(make_observation(metadata=meta), collector_version="t")
    path = next(all_files(archive.root / "metadata").__iter__())
    path.chmod(0o644)
    path.write_bytes(b"{}")
    with pytest.raises(CorruptBlobError):
        archive.read_metadata(meta.sha256(), "synthetic_src", "synthetic_series")
    with pytest.raises(CorruptBlobError):
        archive.preserve(make_observation(metadata=meta), collector_version="t")


def test_unknown_metadata_stays_none_in_snapshot(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    meta = make_metadata()
    archive.preserve(make_observation(metadata=meta), collector_version="t")
    loaded = archive.read_metadata(meta.sha256(), "synthetic_src", "synthetic_series")
    assert loaded.dataset.issued is None and loaded.dataset.modified is None
    assert loaded.dataset.licence is None
    assert b'"issued":null' in (all_files(archive.root / "metadata")[0]).read_bytes()


def test_publisher_name_at_capture_preserved_after_rename(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    old = make_metadata(publisher_name_at_capture="Old Agency")
    new = make_metadata(publisher_name_at_capture="Renamed Agency", publisher_name="Renamed Agency")
    first = archive.preserve(make_observation(metadata=old), collector_version="t").record
    archive.preserve(make_observation(metadata=new), collector_version="t")
    reread = archive.read_metadata(first.metadata_sha256 or "", "synthetic_src", "synthetic_series")
    assert reread.dataset.publisher_name_at_capture == "Old Agency"
    latest = archive.latest_record("synthetic_series")
    assert latest is not None and latest.metadata_changed is True


def test_several_distributions_under_one_dataset(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    a = make_metadata()
    b = a.model_copy(
        update={
            "distribution": a.distribution.model_copy(
                update={"distribution_identifier": "synthetic_json"}
            )
        }
    )
    ra = archive.preserve(make_observation(metadata=a, source_id="syn_csv"), collector_version="t")
    rb = archive.preserve(make_observation(metadata=b, source_id="syn_json"), collector_version="t")
    assert ra.record.dataset_identifier == rb.record.dataset_identifier
    assert ra.record.distribution_identifier != rb.record.distribution_identifier
    assert archive.latest_record("syn_csv") == ra.record
    assert archive.latest_record("syn_json") == rb.record


def test_secret_never_written_anywhere(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    obs = make_observation(secret_headers=(("Ocp-Apim-Subscription-Key", SECRET),), native=b"m")
    result = archive.preserve(obs, collector_version="t")
    for path in all_files(archive.root):
        assert SECRET.encode() not in path.read_bytes(), path
    assert SECRET not in repr(result) and SECRET not in repr(obs.content.request)
    assert SECRET not in obs.content.request.fingerprint()
    assert SECRET not in obs.model_dump_json()
    assert SECRET not in result.record.model_dump_json()


def test_non_2xx_not_preserved(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    with pytest.raises(ArchiveError):
        archive.preserve(make_observation(status=404), collector_version="t")
    assert all_files(archive.root) == [] if archive.root.exists() else True


@pytest.mark.parametrize("bad", ["..", "../x", "a/b", "/abs", "", "A", ".hidden", "a\x00b", "a..b"])
def test_unsafe_ids_rejected(
    archive: SourceArchive, make_observation: ObservationFactory, bad: str
) -> None:
    with pytest.raises(UnsafePathError):
        archive.preserve(make_observation(source_id=bad), collector_version="t")
    with pytest.raises(UnsafePathError):
        archive.records(bad)
    with pytest.raises(UnsafePathError):
        archive.read_metadata("a" * 64, bad, "ok_id")
    with pytest.raises(UnsafePathError):
        archive.read_metadata("a" * 64, "ok_id", bad)


def test_unsafe_source_system_rejected(
    archive: SourceArchive, make_observation: ObservationFactory
) -> None:
    with pytest.raises(UnsafePathError):
        archive.preserve(
            make_observation(metadata=make_metadata(source_system="../evil")), collector_version="t"
        )
    assert not (archive.root.parent / "evil").exists()


@pytest.mark.parametrize("bad", ["../etc/passwd", "ab", "A" * 64, "a" * 63, "a" * 63 + "/", ""])
def test_unsafe_hashes_rejected(tmp_path: Path, bad: str) -> None:
    store = LocalBlobStore(tmp_path)
    with pytest.raises(UnsafePathError):
        store.get(bad)
    with pytest.raises(UnsafePathError):
        store.exists(bad)
    with pytest.raises(UnsafePathError):
        SourceArchive(tmp_path).read_metadata(bad, "x", "y")


def test_default_archive_root_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv(ENV_ARCHIVE_DIR, raising=False)
    assert default_archive_root(tmp_path) == tmp_path / "data" / "source_archive" / "runtime"
    monkeypatch.setenv(ENV_ARCHIVE_DIR, str(tmp_path / "elsewhere"))
    assert default_archive_root(tmp_path) == tmp_path / "elsewhere"
    monkeypatch.setenv(ENV_ARCHIVE_DIR, "")
    assert default_archive_root(tmp_path) == tmp_path / "data" / "source_archive" / "runtime"
