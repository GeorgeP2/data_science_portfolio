"""Train and evaluate. Run: ``PYTHONPATH=src python -m {{package}}.train``."""

from __future__ import annotations

from portfolio import ProjectPaths, get_logger, load_config, seed_everything
from portfolio.io import save_json

PATHS = ProjectPaths.from_file(__file__)
log = get_logger(__name__)


def main() -> dict[str, float]:
    cfg = load_config(PATHS.config)
    seed_everything(cfg.seed)
    PATHS.ensure()

    # TODO: load data, fit model, evaluate
    metrics: dict[str, float] = {}

    save_json(metrics, PATHS.outputs / "metrics.json")
    log.info("Metrics: %s", metrics)
    return metrics


if __name__ == "__main__":
    main()
