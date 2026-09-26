"""YAML config loading with light dot-access."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Config(dict[str, Any]):
    """A dict that also allows ``cfg.model.params`` style access."""

    def __getattr__(self, key: str) -> Any:
        try:
            value = self[key]
        except KeyError as e:
            raise AttributeError(key) from e
        return Config(value) if isinstance(value, dict) else value


def load_config(path: str | Path, overrides: dict[str, Any] | None = None) -> Config:
    """Load a YAML file, optionally shallow-merging ``overrides`` on top."""
    with Path(path).open() as f:
        data = yaml.safe_load(f) or {}
    if overrides:
        data.update(overrides)
    return Config(data)
