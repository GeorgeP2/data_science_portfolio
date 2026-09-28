import hashlib
import io
import tarfile
import urllib.error
import urllib.request
import zipfile
from email.message import Message
from pathlib import Path

import pytest
from fulfilment_optimisation.download import (
    DATASETS,
    ChecksumError,
    Source,
    download,
    extract,
    fetch,
)


def _zip_source(tmp_path: Path) -> Source:
    archive = tmp_path / "remote" / "instances.zip"
    archive.parent.mkdir()
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("instances/a.txt", "Order 0\n")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return Source(archive.as_uri(), digest, "instances.zip", extract=True)


def test_download_fetches_and_extracts(tmp_path):
    source = _zip_source(tmp_path)
    dest = tmp_path / "raw"
    download([source], dest)
    assert (dest / "instances.zip").exists()
    assert (dest / "instances" / "a.txt").read_text() == "Order 0\n"


def test_rerun_is_a_no_op(tmp_path):
    source = _zip_source(tmp_path)
    dest = tmp_path / "raw"
    download([source], dest)
    mtime = (dest / "instances.zip").stat().st_mtime_ns
    download([source], dest)
    assert (dest / "instances.zip").stat().st_mtime_ns == mtime


def test_wrong_checksum_fails_and_leaves_nothing(tmp_path):
    source = _zip_source(tmp_path)
    bad = Source(source.url, "0" * 64, source.filename)
    dest = tmp_path / "raw"
    with pytest.raises(ChecksumError, match="expected sha256"):
        fetch(bad, dest)
    assert list(dest.iterdir()) == []


def test_corrupted_local_copy_is_reported(tmp_path):
    source = _zip_source(tmp_path)
    dest = tmp_path / "raw"
    fetch(source, dest)
    (dest / "instances.zip").write_bytes(b"corrupt")
    with pytest.raises(ChecksumError, match="delete it to refetch"):
        fetch(source, dest)


class _FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int) -> None:
        super().__init__(body)
        self.status = status


def _pinned(body: bytes) -> Source:
    return Source("https://example.org/f.bin", hashlib.sha256(body).hexdigest(), "f.bin")


def test_partial_download_is_resumed_with_a_range_request(tmp_path, monkeypatch):
    body = b"0123456789"
    source = _pinned(body)
    (tmp_path / "f.bin.part").write_bytes(body[:4])
    requests = []

    def urlopen(request, context=None):
        requests.append(request)
        return _FakeResponse(body[4:], status=206)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert fetch(source, tmp_path).read_bytes() == body
    assert requests[0].get_header("Range") == "bytes=4-"
    assert not (tmp_path / "f.bin.part").exists()


def test_stale_partial_is_overwritten_when_range_is_ignored(tmp_path, monkeypatch):
    body = b"0123456789"
    source = _pinned(body)
    (tmp_path / "f.bin.part").write_bytes(b"junk")
    monkeypatch.setattr(urllib.request, "urlopen", lambda r, context=None: _FakeResponse(body, 200))
    assert fetch(source, tmp_path).read_bytes() == body


def test_complete_partial_is_verified_when_server_returns_416(tmp_path, monkeypatch):
    body = b"0123456789"
    source = _pinned(body)
    (tmp_path / "f.bin.part").write_bytes(body)

    def urlopen(request, context=None):
        raise urllib.error.HTTPError(source.url, 416, "Range Not Satisfiable", Message(), None)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert fetch(source, tmp_path).read_bytes() == body


def test_nested_tar_member_is_extracted(tmp_path):
    inner = tmp_path / "Instances.tar"
    with tarfile.open(inner, "w") as tf:
        info = tarfile.TarInfo("Instances/Orders/a.json")
        info.size = 2
        tf.addfile(info, io.BytesIO(b"{}"))
    outer = tmp_path / "bag.tar"
    with tarfile.open(outer, "w") as tf:
        tf.add(inner, arcname="bag/data/dataset/Instances.tar")
        tf.addfile(tarfile.TarInfo("bag/bagit.txt"), io.BytesIO())
    dest = tmp_path / "raw"
    extract(outer, dest, member="bag/data/dataset/Instances.tar")
    assert (dest / "Instances" / "Orders" / "a.json").read_text() == "{}"
    assert not (dest / "bag").exists()


def test_zip_path_traversal_is_rejected(tmp_path):
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escaped.txt", "x")
    dest = tmp_path / "raw"
    dest.mkdir()
    with pytest.raises(ValueError, match="escapes"):
        extract(archive, dest)
    assert not (tmp_path / "escaped.txt").exists()


@pytest.mark.parametrize("source", [s for sources in DATASETS.values() for s in sources])
def test_sources_are_pinned(source):
    assert source.url.startswith("https://")
    assert len(source.sha256) == 64
    int(source.sha256, 16)
