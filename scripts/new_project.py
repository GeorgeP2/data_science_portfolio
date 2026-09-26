"""Scaffold a new portfolio project from ``projects/_template``.

Usage:
    python scripts/new_project.py "Customer Churn Prediction" --category ml
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
TEMPLATE = PROJECTS / "_template"
README = ROOT / "README.md"
INDEX_END = "<!-- projects:end -->"

CATEGORIES = {
    "analytics": "Analytics & Visualisation",
    "stats": "Statistics & Experimentation",
    "ml": "Classical Machine Learning",
    "ts": "Time Series & Forecasting",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "nlp": "Natural Language Processing",
    "llm": "LLMs & Generative AI",
    "recsys": "Recommender Systems",
    "mlops": "MLOps & Deployment",
    "de": "Data Engineering",
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def next_number() -> int:
    nums = [int(m.group(1)) for p in PROJECTS.iterdir() if (m := re.match(r"(\d+)-", p.name))]
    return max(nums, default=0) + 1


def render(path: Path, subs: dict[str, str]) -> None:
    text = path.read_text()
    for key, value in subs.items():
        text = text.replace("{{" + key + "}}", value)
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("title", help="Human-readable project title")
    parser.add_argument("--category", choices=sorted(CATEGORIES), default="ml")
    args = parser.parse_args()

    base = slugify(args.title)
    if not base:
        parser.error("title must contain letters or digits")
    slug = f"{next_number():02d}-{base}"
    package = base.replace("-", "_")
    if package[0].isdigit():
        package = f"p_{package}"
    if any(p.name.endswith(f"-{base}") for p in PROJECTS.iterdir()):
        parser.error(f"a project called {base!r} already exists")

    dest = PROJECTS / slug
    shutil.copytree(TEMPLATE, dest)
    (dest / "src" / "{{package}}").rename(dest / "src" / package)

    subs = {
        "title": args.title,
        "slug": slug,
        "package": package,
        "category": CATEGORIES[args.category],
    }
    for f in dest.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".py", ".yaml", ".ipynb"}:
            render(f, subs)

    readme = README.read_text()
    row = f"| [{args.title}](projects/{slug}) | {CATEGORIES[args.category]} | 🚧 | _TBC_ |\n"
    README.write_text(readme.replace(INDEX_END, row + INDEX_END))

    print(f"Created projects/{slug}  (package: {package})")
    print(f"  cd projects/{slug} && PYTHONPATH=src python -m {package}.train")


if __name__ == "__main__":
    main()
