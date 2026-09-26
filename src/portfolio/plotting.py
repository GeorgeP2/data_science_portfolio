"""One house style for every figure in the portfolio."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

PALETTE = ["#2E5EAA", "#E07A5F", "#3D9970", "#F2CC8F", "#81B29A", "#6D597A"]


def set_style(context: str = "notebook") -> None:
    sns.set_theme(context=context, style="whitegrid", palette=PALETTE)
    plt.rcParams.update(
        {
            "figure.figsize": (8, 5),
            "figure.dpi": 110,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_fig(fig: Figure, path: str | Path, dpi: int = 150) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
