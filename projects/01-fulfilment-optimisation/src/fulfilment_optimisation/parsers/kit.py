"""Flatten the KIT order picking benchmark suite into two parquet tables.

    PYTHONPATH=src python -m fulfilment_optimisation.parsers.kit

The suite (Barlang, Lehmann & Furmans, 2026; see ``data/README.md``) has 132 parameter settings,
each with 100 replications of one 8-hour shift: 32 one-factor-at-a-time (OFAT) settings under
``Orders/OFAT/<factor>/<setting>/`` (the baseline is ``Orders/OFAT/Standard_case/``) and 100 Latin
hypercube (LHS) settings under ``Orders/LHS/<setting>/``. Each replication is a JSON file with the
generating configuration in ``meta`` and the orders in ``orders``.

Outputs, in ``data/processed/``:

- ``kit_instances.parquet``: one row per replication, with its configuration and layout size.
- ``kit_orders.parquet``: one row per order: lines, units, arrival time, due date, slack (due date
  minus arrival) and the number of distinct aisles its articles are stored in.

Files are read one at a time in a process pool and written in batches, so memory stays bounded
regardless of the suite's ~2 GB.

**Layout size.** The layout file names (``16x8``) and ``meta["layout_dimensions"]`` disagree on
which number is the aisle count. The storage assignment maps each article to ``(x, y)`` with ``x``
the aisle and ``y`` the location within it, so the dimensions are read from there instead. The
naming isn't even consistent between designs: OFAT ``128_pick_nodes_16x8`` has 8 aisles of 16
locations, while LHS ``001_220_pick_nodes_20x11`` has 20 aisles of 11.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from portfolio import ProjectPaths, get_logger, load_config

log = get_logger(__name__)

ORDER_SCHEMA = pa.schema(
    [
        ("instance", pa.string()),
        ("order_id", pa.int32()),
        ("lines", pa.int16()),
        ("units", pa.int32()),
        ("arrival_time", pa.float64()),
        ("due_date", pa.float64()),
        ("slack", pa.float64()),
        ("aisles_visited", pa.int16()),
    ]
)


def instance_paths(root: Path) -> list[Path]:
    """Every replication file, OFAT then LHS, in a stable order."""
    return sorted((root / "Orders").glob("*/**/instance_*.json"))


def describe_path(path: Path, root: Path) -> dict[str, Any]:
    """Design, factor, setting and replication from where the file sits."""
    parts = path.relative_to(root / "Orders").parts
    design = parts[0]
    if design == "OFAT" and parts[1] == "Standard_case":
        factor, setting = "Standard_case", "Standard_case"
    elif design == "OFAT":
        factor, setting = parts[1], parts[2]
    else:
        factor, setting = "LHS", parts[1]
    replication = int(path.stem.removeprefix("instance_"))
    return {
        "instance": f"{design}/{setting}/{replication}",
        "design": design,
        "factor": factor,
        "setting": setting,
        "replication": replication,
    }


def _from_root(root: Path, relative: str) -> Path:
    """Resolve a ``meta`` path. They start with ``../`` a different number of times depending on
    how deep the setting folder is, so drop those and join the rest (``Data_input/...``) to the
    suite root."""
    return root.joinpath(*(part for part in Path(relative).parts if part != ".."))


@cache
def storage_map(path: str) -> dict[str, tuple[int, int]]:
    """Article id -> (aisle, location) for one storage assignment file."""
    with open(path) as f:
        return {article: (int(x), int(y)) for article, (x, y) in json.load(f).items()}


def _arrival(config: Any) -> tuple[str, dict[str, Any]]:
    """``[type, params]``, except the OFAT stochasticity settings, which store a string like
    ``"wave_5_0.5"`` (5 waves, stochasticity 0.5)."""
    if isinstance(config, str):
        kind, waves, stochasticity = config.split("_")
        return kind, {"num_waves": int(waves), "stochasticity": float(stochasticity)}
    kind, params = config
    return kind, params


def _config_fields(meta: dict[str, Any]) -> dict[str, Any]:
    arrival_type, arrival = _arrival(meta["arrival_config"])
    lines_type, lines = meta["num_articles_in_order_config"]
    due_type, due = meta["due_date_config"]
    article_type, article = meta["article_config"]
    storage_type, _ = meta["storage_policy"]
    return {
        "exp_num_orders": int(meta["exp_num_orders"]),
        "shift_seconds": float(meta["max_simulation_time"]),
        "arrival_type": arrival_type,
        "num_waves": arrival.get("num_waves"),
        "stochasticity": arrival.get("stochasticity"),
        "lines_type": lines_type,
        "lines_config": json.dumps(lines, sort_keys=True),
        "due_type": due_type,
        "due_config": json.dumps(due, sort_keys=True),
        "article_type": article_type,
        "article_config": json.dumps(
            {k: v for k, v in article.items() if k != "seed"}, sort_keys=True
        ),
        "storage_policy": storage_type,
    }


def read_instance(path: Path, root: Path) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    """One replication: its instance row and its order columns."""
    with open(path) as f:
        data = json.load(f)
    meta = data["meta"]
    storage_file = _from_root(root, meta["storage_assignment"])
    locations = storage_map(str(storage_file))
    row = describe_path(path, root)
    row |= _config_fields(meta)
    row |= {
        "layout_file": _from_root(root, meta["layout"]).name,
        "storage_file": storage_file.name,
        "n_aisles": max(x for x, _ in locations.values()),
        "n_locations": max(y for _, y in locations.values()),
        "n_articles": len(locations),
        "n_orders": len(data["orders"]),
    }

    columns: dict[str, list[Any]] = {name: [] for name in ORDER_SCHEMA.names}
    for order in data["orders"]:
        items = order["items"]
        columns["instance"].append(row["instance"])
        columns["order_id"].append(order["order_id"])
        columns["lines"].append(len(items))
        columns["units"].append(sum(items.values()))
        columns["arrival_time"].append(order["arrival_time"])
        columns["due_date"].append(order["due_date"])
        columns["slack"].append(order["due_date"] - order["arrival_time"])
        columns["aisles_visited"].append(len({locations[a][0] for a in items}))
    row |= _order_stats(columns, row["shift_seconds"])
    return row, columns


def _order_stats(columns: dict[str, list[Any]], shift: float) -> dict[str, float]:
    """Per-replication summaries, computed while the file is in memory."""
    arrivals = np.sort(np.asarray(columns["arrival_time"]))
    gaps = np.diff(arrivals)
    per_bin = np.histogram(arrivals, bins=int(shift // 1800), range=(0, shift))[0]
    lines = np.asarray(columns["lines"])
    slack = np.asarray(columns["slack"])
    due = np.asarray(columns["due_date"])
    return {
        "interarrival_mean": float(gaps.mean()) if gaps.size else np.nan,
        "interarrival_cv": float(gaps.std() / gaps.mean()) if gaps.size else np.nan,
        "arrivals_per_30min_cv": float(per_bin.std() / per_bin.mean())
        if per_bin.mean()
        else np.nan,
        "mean_lines": float(lines.mean()),
        "share_lines_1": float((lines == 1).mean()),
        "share_lines_2": float((lines == 2).mean()),
        "share_lines_3": float((lines == 3).mean()),
        "share_lines_4plus": float((lines >= 4).mean()),
        "mean_units": float(np.mean(columns["units"])),
        "mean_aisles_visited": float(np.mean(columns["aisles_visited"])),
        "slack_p10": float(np.percentile(slack, 10)),
        "slack_median": float(np.median(slack)),
        "slack_p90": float(np.percentile(slack, 90)),
        "share_due_at_shift_end": float(np.isclose(due, shift).mean()),
    }


def _read(args: tuple[Path, Path]) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    return read_instance(*args)


def flatten(root: Path, out: Path, workers: int = 6) -> tuple[int, int]:
    """Write ``kit_instances.parquet`` and ``kit_orders.parquet`` under ``out``."""
    paths = instance_paths(root)
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    n_orders = 0
    chunk = 500  # files in flight at once, so finished results don't pile up in memory
    with (
        pq.ParquetWriter(out / "kit_orders.parquet", ORDER_SCHEMA) as writer,
        ProcessPoolExecutor(max_workers=workers) as pool,
    ):
        for start in range(0, len(paths), chunk):
            batch = ((p, root) for p in paths[start : start + chunk])
            for row, columns in pool.map(_read, batch, chunksize=16):
                rows.append(row)
                writer.write_table(pa.table(columns, schema=ORDER_SCHEMA))
                n_orders += row["n_orders"]
            log.info("%d / %d files", min(start + chunk, len(paths)), len(paths))
    pq.write_table(pa.Table.from_pylist(rows), out / "kit_instances.parquet")
    return len(rows), n_orders


def iter_orders(path: Path, batch_size: int = 1_000_000) -> Iterator[pa.RecordBatch]:
    """Stream ``kit_orders.parquet`` in batches, for summaries that don't need it all at once."""
    yield from pq.ParquetFile(path).iter_batches(batch_size=batch_size)


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    root = paths.data / cfg.data.kit / "Instances"
    n_instances, n_orders = flatten(root, paths.processed)
    log.info("wrote %d instances and %d orders to %s", n_instances, n_orders, paths.processed)


if __name__ == "__main__":
    main()
