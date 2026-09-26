"""Standard metric bundles so projects report results the same way."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from sklearn import metrics


def classification_report(
    y_true: ArrayLike, y_pred: ArrayLike, y_proba: ArrayLike | None = None
) -> dict[str, float]:
    """Core classification metrics. ``y_proba`` = positive-class scores (binary only)."""
    out = {
        "accuracy": metrics.accuracy_score(y_true, y_pred),
        "balanced_accuracy": metrics.balanced_accuracy_score(y_true, y_pred),
        "f1_macro": metrics.f1_score(y_true, y_pred, average="macro"),
        "precision_macro": metrics.precision_score(
            y_true, y_pred, average="macro", zero_division=0
        ),
        "recall_macro": metrics.recall_score(y_true, y_pred, average="macro"),
    }
    if y_proba is not None:
        out["roc_auc"] = metrics.roc_auc_score(y_true, y_proba)
        out["average_precision"] = metrics.average_precision_score(y_true, y_proba)
    return {k: round(float(v), 4) for k, v in out.items()}


def regression_report(y_true: ArrayLike, y_pred: ArrayLike) -> dict[str, float]:
    out = {
        "mae": metrics.mean_absolute_error(y_true, y_pred),
        "rmse": float(np.sqrt(metrics.mean_squared_error(y_true, y_pred))),
        "r2": metrics.r2_score(y_true, y_pred),
        "mape": metrics.mean_absolute_percentage_error(y_true, y_pred),
    }
    return {k: round(float(v), 4) for k, v in out.items()}
