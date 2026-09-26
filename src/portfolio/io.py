"""Small, format-agnostic read/write helpers."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

_READERS: dict[str, Callable[..., pd.DataFrame]] = {
    ".csv": pd.read_csv,
    ".parquet": pd.read_parquet,
    ".json": pd.read_json,
    ".xlsx": pd.read_excel,
}


def read_table(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    path = Path(path)
    try:
        reader = _READERS[path.suffix.lower()]
    except KeyError as e:
        raise ValueError(f"Unsupported table format: {path.suffix}") from e
    return reader(path, **kwargs)


def write_table(df: pd.DataFrame, path: str | Path, **kwargs: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False, **kwargs)
    elif suffix == ".parquet":
        df.to_parquet(path, index=False, **kwargs)
    else:
        raise ValueError(f"Unsupported table format: {suffix}")
    return path


def save_json(obj: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")
    return path


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def save_model(model: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(path: str | Path) -> Any:
    return joblib.load(path)
