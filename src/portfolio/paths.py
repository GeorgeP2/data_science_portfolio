"""Canonical filesystem layout for the repo and for each project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_DIR = REPO_ROOT / "projects"


@dataclass(frozen=True)
class ProjectPaths:
    """Standard directories for a single project under ``projects/<slug>``.

    ``data`` and ``outputs`` are git-ignored; ``reports`` is committed so that
    figures and write-ups render on GitHub.
    """

    root: Path

    @classmethod
    def for_project(cls, slug: str) -> ProjectPaths:
        root = PROJECTS_DIR / slug
        if not root.is_dir():
            raise FileNotFoundError(f"No project named {slug!r} in {PROJECTS_DIR}")
        return cls(root)

    @classmethod
    def from_file(cls, file: str | Path) -> ProjectPaths:
        """Locate the enclosing project from any file inside it (e.g. ``__file__``)."""
        path = Path(file).resolve()
        for parent in path.parents:
            if parent.parent == PROJECTS_DIR:
                return cls(parent)
        raise ValueError(f"{path} is not inside {PROJECTS_DIR}")

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def raw(self) -> Path:
        return self.data / "raw"

    @property
    def processed(self) -> Path:
        return self.data / "processed"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"

    @property
    def models(self) -> Path:
        return self.outputs / "models"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def figures(self) -> Path:
        return self.reports / "figures"

    @property
    def config(self) -> Path:
        return self.root / "config.yaml"

    def ensure(self) -> ProjectPaths:
        """Create every writable directory; returns self for chaining."""
        for d in (self.raw, self.processed, self.models, self.figures):
            d.mkdir(parents=True, exist_ok=True)
        return self
