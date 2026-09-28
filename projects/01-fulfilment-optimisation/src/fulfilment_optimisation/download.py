"""Fetch the external benchmark instances into ``data/raw/`` with pinned checksums.

Neither source states a licence, so the files are downloaded rather than committed.
Run from the project folder::

    PYTHONPATH=src python -m fulfilment_optimisation.download [henn_waescher|foodmart|all]
"""

from __future__ import annotations

import argparse
import hashlib
import ssl
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from portfolio import ProjectPaths, get_logger, load_config

log = get_logger(__name__)

_CHUNK = 1 << 20
_HW = "https://grafo.etsii.urjc.es/optsicom/obsp/obsp-files"
_FOODMART = "https://homepages.dcc.ufmg.br/~arbex/orderpicking"


@dataclass(frozen=True)
class Source:
    url: str
    sha256: str
    filename: str
    extract: bool = False
    extract_subdir: str = ""


# Three Foodmart links on the source page 404; the same files are served with a
# ``.txt`` suffix. They are saved under the documented (suffix-free) names.
DATASETS: dict[str, list[Source]] = {
    "henn_waescher": [
        Source(
            f"{_HW}/obsp_instances.zip",
            "d162d43dd01f16b198419f839a280fe61abee4380280ccd2f5c58c8b013cea5f",
            "obsp_instances.zip",
            extract=True,
        ),
        Source(
            f"{_HW}/comparative_vs_ils_sshape.xlsx",
            "8c3258ea6c5286259daef52acf1d0e87de37f1300abe47cd649432055601f914",
            "results/comparative_vs_ils_sshape.xlsx",
        ),
        Source(
            f"{_HW}/comparative_vs_ils_largest_gap.xlsx",
            "4844aa2d8531a8f14d33b09fdae5d7d05987fecd5664a8942eb52dabc099dca9",
            "results/comparative_vs_ils_largest_gap.xlsx",
        ),
    ],
    "foodmart": [
        Source(
            f"{_FOODMART}/warehouse_8_0_3_1560",
            "5083ec9839af413ca7008aeb376f43bdb51f3161f4b59427c6953431c4f591dd",
            "warehouse_8_0_3_1560",
        ),
        Source(
            f"{_FOODMART}/warehouse_8_1_3_1560.txt",
            "25f869bb0f5c24897304f66ede55e94b5d306bf825a6b5bc216738487facf73b",
            "warehouse_8_1_3_1560",
        ),
        Source(
            f"{_FOODMART}/warehouse_16_0_3_1560",
            "f5045516fd433dd2cc37d312b87578993fec47258e09cd749a1431d1378a6d8c",
            "warehouse_16_0_3_1560",
        ),
        Source(
            f"{_FOODMART}/warehouse_16_1_3_1560",
            "0e4525531cb04ad11482ee7a1f9503ae9a18e0dad4f6b33a1aabc908c446ae53",
            "warehouse_16_1_3_1560",
        ),
        Source(
            f"{_FOODMART}/productsDB_1560_list.txt",
            "0503a7aec4300b37c79ccfd36cdcaf0d729cac8ede3402e8cceca4cfb8bdb529",
            "productsDB_1560_list",
        ),
        Source(
            f"{_FOODMART}/productsDB_1560_locations.txt",
            "f4abc1bf366ed25232aa3e0142cb95f31ef2489a5aa3582f2f3d937278d28168",
            "productsDB_1560_locations",
        ),
        Source(
            f"{_FOODMART}/orders.tar.gz",
            "5f7b973e521a5da953473f4547fd0280a05d8fbbb7c0fee601ac48c34d6a28fb",
            "orders.tar.gz",
            extract=True,
        ),
        Source(
            f"{_FOODMART}/largeInstances.tar.gz",
            "6bf4b85a5f34714190496e8073a73510396eafc58874377f6ea5d853f23f0de7",
            "largeInstances.tar.gz",
            extract=True,
            extract_subdir="large_instances",
        ),
        Source(
            f"{_FOODMART}/instanceFilesDescription.txt",
            "afe46250addae32f9d05a897dacaf3b0cce739b84394f0044dc6c77bb31b113c",
            "instanceFilesDescription.txt",
        ),
    ],
}


class ChecksumError(RuntimeError):
    pass


def _ssl_context() -> ssl.SSLContext:
    # python.org macOS builds ship without a CA bundle; use certifi's when it's installed.
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(source: Source, dest_dir: Path) -> Path:
    """Download ``source`` into ``dest_dir``; a no-op if a verified copy already exists."""
    target = dest_dir / source.filename
    if target.exists():
        if sha256(target) == source.sha256:
            log.info("skip %s (checksum ok)", source.filename)
            return target
        raise ChecksumError(f"{target} exists but its checksum doesn't match; delete it to refetch")

    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    digest = hashlib.sha256()
    try:
        with (
            urllib.request.urlopen(source.url, context=_ssl_context()) as response,
            part.open("wb") as f,
        ):
            while chunk := response.read(_CHUNK):
                digest.update(chunk)
                f.write(chunk)
        if digest.hexdigest() != source.sha256:
            raise ChecksumError(
                f"{source.url}: expected sha256 {source.sha256}, got {digest.hexdigest()}"
            )
        part.replace(target)
    finally:
        part.unlink(missing_ok=True)
    log.info("fetched %s", source.filename)
    return target


def extract(archive: Path, dest_dir: Path) -> None:
    """Unpack a zip or tar archive into ``dest_dir`` once, refusing paths that escape it."""
    marker = dest_dir / f".{archive.name}.extracted"
    if marker.exists():
        log.info("skip extracting %s", archive.name)
        return
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            root = dest_dir.resolve()
            for name in zf.namelist():
                if not (root / name).resolve().is_relative_to(root):
                    raise ValueError(f"{archive.name}: member {name!r} escapes {dest_dir}")
            zf.extractall(dest_dir)
    else:
        with tarfile.open(archive) as tf:
            tf.extractall(dest_dir, filter="data")
    marker.touch()
    log.info("extracted %s", archive.name)


def download(sources: list[Source], dest_dir: Path) -> None:
    for source in sources:
        path = fetch(source, dest_dir)
        if source.extract:
            extract(path, dest_dir / source.extract_subdir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dataset", nargs="?", default="all", choices=[*DATASETS, "all"])
    args = parser.parse_args()

    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    names = list(DATASETS) if args.dataset == "all" else [args.dataset]
    for name in names:
        download(DATASETS[name], paths.data / cfg.data[name])


if __name__ == "__main__":
    main()
