import hashlib
import zipfile
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
