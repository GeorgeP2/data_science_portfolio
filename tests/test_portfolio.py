import numpy as np
import pandas as pd
import pytest

from portfolio import ProjectPaths, load_config, seed_everything
from portfolio.evaluation import classification_report, regression_report
from portfolio.io import load_json, read_table, save_json, write_table
from portfolio.paths import PROJECTS_DIR


def test_load_config_dot_access(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("seed: 1\nmodel:\n  params:\n    depth: 3\n")
    cfg = load_config(path, overrides={"seed": 7})
    assert cfg.seed == 7
    assert cfg.model.params.depth == 3
    with pytest.raises(AttributeError):
        _ = cfg.missing


def test_seed_everything_is_deterministic():
    seed_everything(0)
    a = np.random.rand(3)  # noqa: NPY002
    seed_everything(0)
    b = np.random.rand(3)  # noqa: NPY002
    np.testing.assert_array_equal(a, b)


def test_project_paths(tmp_path):
    paths = ProjectPaths(tmp_path).ensure()
    assert paths.models.is_dir()
    assert paths.figures.is_dir()
    assert ProjectPaths.from_file(PROJECTS_DIR / "x" / "src" / "m.py").root == PROJECTS_DIR / "x"
    with pytest.raises(ValueError):
        ProjectPaths.from_file(tmp_path / "file.py")


@pytest.mark.parametrize("suffix", [".csv", ".parquet"])
def test_table_roundtrip(tmp_path, suffix):
    if suffix == ".parquet":
        pytest.importorskip("pyarrow")
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    path = write_table(df, tmp_path / f"t{suffix}")
    pd.testing.assert_frame_equal(read_table(path), df)


def test_json_roundtrip(tmp_path):
    save_json({"x": 1}, tmp_path / "m.json")
    assert load_json(tmp_path / "m.json") == {"x": 1}


def test_metric_reports():
    clf = classification_report([0, 1, 1, 0], [0, 1, 0, 0], y_proba=[0.1, 0.9, 0.4, 0.2])
    assert clf["accuracy"] == 0.75
    assert clf["roc_auc"] == 1.0
    reg = regression_report([1.0, 2.0, 3.0], [1.0, 2.0, 4.0])
    assert reg["mae"] == pytest.approx(0.3333, abs=1e-4)
