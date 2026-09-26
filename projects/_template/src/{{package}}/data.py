"""Load and split data for {{title}}."""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from portfolio.config import Config
from portfolio.io import read_table
from portfolio.paths import ProjectPaths

PATHS = ProjectPaths.from_file(__file__)


def load_raw(cfg: Config) -> pd.DataFrame:
    return read_table(PATHS.data / cfg.data.raw_file)


def split(df: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    X = df.drop(columns=[cfg.data.target])
    y = df[cfg.data.target]
    return train_test_split(X, y, test_size=cfg.data.test_size, random_state=cfg.seed)
