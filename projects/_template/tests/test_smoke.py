from portfolio import load_config
from portfolio.paths import ProjectPaths

PATHS = ProjectPaths.from_file(__file__)


def test_config_loads():
    cfg = load_config(PATHS.config)
    assert "seed" in cfg


def test_package_imports():
    import {{package}}  # noqa: F401
