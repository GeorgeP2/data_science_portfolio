# syntax=docker/dockerfile:1
# Build from the repo root, since the image needs the shared src/portfolio package:
#   docker build -f projects/01-fulfilment-optimisation/Dockerfile -t fulfilment-optimisation .

FROM python:3.13-slim AS builder
COPY pyproject.toml /build/
# Install only the `service` extra from the root pyproject, not the portfolio's full core deps.
RUN python -c "import tomllib; deps = tomllib.load(open('/build/pyproject.toml', 'rb'))['project']['optional-dependencies']['service']; print('\n'.join(deps))" > /build/requirements.txt \
    && python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r /build/requirements.txt

FROM python:3.13-slim
RUN useradd --create-home --uid 10001 app
COPY --from=builder /venv /venv
WORKDIR /app
# Same layout as the repo, so portfolio.ProjectPaths finds config.yaml.
COPY src/portfolio src/portfolio
COPY projects/01-fulfilment-optimisation/config.yaml projects/01-fulfilment-optimisation/
COPY projects/01-fulfilment-optimisation/src projects/01-fulfilment-optimisation/src

ENV PATH=/venv/bin:$PATH \
    PYTHONPATH=/app/src:/app/projects/01-fulfilment-optimisation/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080
USER app
EXPOSE 8080
# Cloud Run sets PORT. sh expands it at start-up, then exec hands PID 1 to uvicorn for signals.
CMD ["sh", "-c", "exec uvicorn fulfilment_optimisation.api.app:app --host 0.0.0.0 --port \"$PORT\""]
