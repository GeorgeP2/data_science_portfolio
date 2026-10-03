# Data Science Portfolio

[![CI](https://github.com/GeorgeP2/data_science_portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/GeorgeP2/data_science_portfolio/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A collection of end-to-end projects showing my data science, machine learning and AI skills,
from exploratory analysis and classical ML to deep learning, NLP and LLM applications.
Every project is reproducible, tested and follows the same structure.

## Projects

| Project | Area | Status | Highlights |
|---------|------|--------|------------|
| [Fulfilment Optimisation](projects/01-fulfilment-optimisation) | MLOps & Deployment | 🚧 | _TBC_ |
<!-- projects:end -->

## Skills

| Area | Tools & techniques |
|------|--------------------|
| **Data wrangling & analysis** | pandas, NumPy, SQL, data cleaning, feature engineering |
| **Visualisation** | matplotlib, seaborn, Plotly, Streamlit |
| **Statistics** | hypothesis testing, A/B testing, regression, Bayesian methods |
| **Machine learning** | scikit-learn, XGBoost, LightGBM, Optuna, SHAP |
| **Deep learning** | PyTorch, CNNs, transformers |
| **NLP & LLMs** | Hugging Face, sentence embeddings, RAG, Claude API |
| **MLOps** | MLflow, FastAPI, Docker, GitHub Actions, pytest |

## Repository layout

```
.
├── projects/                 # one self-contained folder per project
│   ├── _template/            # copied by `make new-project`
│   └── NN-project-name/
│       ├── README.md         # problem, data, approach, results
│       ├── config.yaml       # every tunable value
│       ├── notebooks/        # exploration & storytelling
│       ├── src/<package>/    # reusable pipeline code
│       ├── tests/
│       ├── reports/figures/  # committed figures used in the README
│       ├── data/             # git-ignored
│       └── outputs/          # git-ignored (models, metrics)
├── src/portfolio/            # shared utilities (paths, config, I/O, plotting, metrics)
├── tests/                    # tests for the shared package
├── scripts/                  # repo tooling
└── docs/                     # conventions & guides
```

## Getting started

```bash
git clone git@github.com:GeorgeP2/data_science_portfolio.git
cd data_science_portfolio
make setup            # venv + core, dev and notebook deps + pre-commit hooks
source .venv/bin/activate
make check            # lint, type-check and test everything
```

Heavier dependencies are grouped as optional extras (`ml`, `dl`, `nlp`, `llm`, `tracking`, `app`, `opt`),
e.g. `pip install -e ".[dl,nlp]"`, or `make setup-all` for everything.

### Adding a project

```bash
make new-project name="Customer Churn Prediction" category=ml
```

This copies the template to `projects/NN-customer-churn-prediction/`, fills in names, and adds a row
to the table above. Categories: `analytics`, `stats`, `ml`, `ts`, `dl`, `cv`, `nlp`, `llm`, `recsys`,
`mlops`, `de`. See [docs/conventions.md](docs/conventions.md) for the house rules.

## How this was built

I build these projects with an AI coding assistant ([Claude Code](https://claude.com/claude-code));
some commits list it as a co-author. I choose the problems, write the briefs in
[docs/projects/](docs/projects), set the scope and make the design calls. The assistant speeds up
implementation, and I review, test and can explain every change. Each project's README records the
decisions and trade-offs in my own words.

## Contact

George Priestley · [CV](https://georgep2.github.io/data_science_portfolio/cv.html) · [LinkedIn](https://www.linkedin.com/in/george-priestley-93704530) · [GitHub](https://github.com/GeorgeP2)
