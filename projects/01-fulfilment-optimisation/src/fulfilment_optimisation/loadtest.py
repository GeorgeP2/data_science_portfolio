"""Load test of the live ``POST /batch`` endpoint on Lambda (T26).

    aws login
    PYTHONPATH=src python -m fulfilment_optimisation.loadtest
    PYTHONPATH=src python -m fulfilment_optimisation.loadtest --report  # redo doc + chart only

Settings come from the ``loadtest`` section of ``config.yaml``. Requests are generator windows
(development seeds only), sent at each concurrency level in turn: every worker holds one
keep-alive HTTPS connection and sends its requests back to back. The first ``warmup_per_worker``
requests of each worker at each level are not counted, so the reported latencies are warm; cold
starts are read from the function's ``REPORT`` log lines (``Init Duration``) instead.

The function URL accepts only IAM-signed requests. Requests are signed with SigV4 using the
credentials of the current ``aws login`` session (``aws configure export-credentials``), so no
AWS SDK is needed.

Two latencies are recorded per request: the client round trip, and the server-side time from the
``Server-Timing`` header (request arrival in the app to response ready, as in T23). Lambda runs one
request per instance, so concurrency above the account's unreserved limit is throttled (429);
throttles are counted, not timed.

Writes ``outputs/loadtest.parquet`` (one row per request), ``outputs/loadtest.json`` (the
function's settings at run time), ``reports/figures/load_test*.png`` and
``docs/projects/p1-fulfilment-optimisation/results/load_test.md``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import http.client
import json
import re
import subprocess
import threading
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.final import windows
from fulfilment_optimisation.generator import generate_instance, is_held_out
from fulfilment_optimisation.report import DARK, LIGHT, RESULTS_DOC, Theme
from portfolio import ProjectPaths, get_logger, load_config
from portfolio.io import read_table, write_table
from portfolio.plotting import save_fig

log = get_logger(__name__)


# --- SigV4 -------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Credentials:
    access_key: str
    secret_key: str
    token: str | None = None


def session_credentials() -> Credentials:
    """The current ``aws login`` session's credentials, via the AWS CLI."""
    out = subprocess.run(
        ["aws", "configure", "export-credentials", "--format", "process"],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"no AWS credentials ({out.stderr.strip()}); run `aws login` first")
    data = json.loads(out.stdout)
    return Credentials(data["AccessKeyId"], data["SecretAccessKey"], data.get("SessionToken"))


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def sign(
    method: str,
    url: str,
    body: bytes,
    creds: Credentials,
    region: str,
    service: str = "lambda",
    now: dt.datetime | None = None,
    headers: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Headers for an AWS Signature Version 4 request (URL without a query string)."""
    now = now or dt.datetime.now(dt.UTC)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    day = amz_date[:8]
    parts = urlsplit(url)
    payload_hash = hashlib.sha256(body).hexdigest()

    signed = {k.lower(): v.strip() for k, v in (headers or {}).items()}
    signed.update({"host": parts.netloc, "x-amz-date": amz_date})
    if creds.token:
        signed["x-amz-security-token"] = creds.token
    names = sorted(signed)
    canonical = "\n".join(
        [
            method,
            parts.path or "/",
            "",
            "".join(f"{k}:{signed[k]}\n" for k in names),
            ";".join(names),
            payload_hash,
        ]
    )
    scope = f"{day}/{region}/{service}/aws4_request"
    to_sign = "\n".join(
        ["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()]
    )
    key = _hmac(
        _hmac(_hmac(_hmac(f"AWS4{creds.secret_key}".encode(), day), region), service),
        "aws4_request",
    )
    signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
    signed["authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={creds.access_key}/{scope}, "
        f"SignedHeaders={';'.join(names)}, Signature={signature}"
    )
    return signed


# --- Request mix ---------------------------------------------------------------------------------


def request_body(instance: Instance, solver: str, router: str, budget_ms: int) -> dict[str, Any]:
    layout = instance.layout
    return {
        "layout": {
            "n_aisles": layout.n_aisles,
            "n_positions": layout.n_positions,
            "location_length": layout.location_length,
            "aisle_spacing": layout.aisle_spacing,
            "end_offset": layout.end_offset,
            "depot_offset": layout.depot_offset,
        },
        "capacity": instance.capacity,
        "solver": solver,
        "router": router,
        "budget_ms": budget_ms,
        "orders": [
            {
                "id": o.id,
                "locations": [
                    {"aisle": loc.aisle, "position": loc.position, "side": loc.side}
                    for loc in o.locations
                ],
            }
            for o in instance.orders
        ],
    }


def request_mix(lt: Mapping[str, Any], generator: Mapping[str, Any]) -> list[dict[str, Any]]:
    """One request per arrival window of each scenario and development seed."""
    low, high = lt["seeds"]
    bodies = []
    for scenario in lt["scenarios"]:
        for seed in range(low, high + 1):
            if is_held_out(generator, seed):
                raise ValueError(f"seed {seed} is held out; the load test uses development seeds")
            instance = generate_instance(generator, scenario, seed)
            for window in windows(instance, lt["window_seconds"]):
                bodies.append(request_body(window, lt["solver"], lt["router"], lt["budget_ms"]))
    return bodies


# --- Running -------------------------------------------------------------------------------------


def _server_ms(header: str | None) -> float:
    match = re.search(r"dur=([\d.]+)", header or "")
    return float(match.group(1)) if match else float("nan")


def _worker(
    url: str,
    creds: Credentials,
    region: str,
    bodies: Sequence[dict[str, Any]],
    start: int,
    count: int,
    warmup: int,
    concurrency: int,
    worker: int,
    rows: list[dict[str, Any]],
    lock: threading.Lock,
) -> None:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") + "/batch"
    conn = http.client.HTTPSConnection(parts.netloc, timeout=60)
    for i in range(warmup + count):
        body = bodies[(start + i) % len(bodies)]
        payload = json.dumps(body).encode()
        headers = sign(
            "POST",
            f"https://{parts.netloc}{path}",
            payload,
            creds,
            region,
            headers={"content-type": "application/json"},
        )
        sent = time.time()
        t0 = time.perf_counter()
        try:
            conn.request("POST", path, body=payload, headers=headers)
            response = conn.getresponse()
            data = response.read()
            client_ms = 1000 * (time.perf_counter() - t0)
            status, timing = response.status, response.getheader("Server-Timing")
        except (OSError, http.client.HTTPException) as exc:
            conn.close()
            conn = http.client.HTTPSConnection(parts.netloc, timeout=60)
            client_ms, status, timing, data = float("nan"), -1, None, str(exc).encode()
        result = json.loads(data) if status == 200 else {}
        row = {
            "concurrency": concurrency,
            "worker": worker,
            "seq": i,
            "warmup": i < warmup,
            "sent_at": sent,
            "orders": len(body["orders"]),
            "status_code": status,
            "client_ms": client_ms,
            "server_ms": _server_ms(timing),
            "solver_status": result.get("status"),
            "fallback_used": result.get("fallback_used"),
            "error": None if status == 200 else data[:200].decode(errors="replace"),
        }
        with lock:
            rows.append(row)
    conn.close()


def run_level(
    url: str,
    creds: Credentials,
    region: str,
    bodies: Sequence[dict[str, Any]],
    concurrency: int,
    requests: int,
    warmup: int,
) -> list[dict[str, Any]]:
    """``requests`` measured requests split across ``concurrency`` workers, plus warm-up."""
    rows: list[dict[str, Any]] = []
    lock = threading.Lock()
    per_worker = -(-requests // concurrency)
    threads = [
        threading.Thread(
            target=_worker,
            args=(
                url,
                creds,
                region,
                bodies,
                w * per_worker,
                per_worker,
                warmup,
                concurrency,
                w,
                rows,
                lock,
            ),
        )
        for w in range(concurrency)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return rows


# --- AWS lookups ---------------------------------------------------------------------------------


def _aws(*args: str) -> Any:
    out = subprocess.run(["aws", *args, "--output", "json"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"aws {' '.join(args[:2])} failed: {out.stderr.strip()}")
    return json.loads(out.stdout) if out.stdout.strip() else {}  # some calls print nothing


def function_info(name: str, region: str) -> dict[str, Any]:
    cfg = _aws("lambda", "get-function-configuration", "--function-name", name, "--region", region)
    url = _aws("lambda", "get-function-url-config", "--function-name", name, "--region", region)
    account = _aws("lambda", "get-account-settings", "--region", region)
    reserved = _aws(
        "lambda", "get-function-concurrency", "--function-name", name, "--region", region
    ).get("ReservedConcurrentExecutions")
    return {
        "url": url["FunctionUrl"],
        "memory_mb": cfg["MemorySize"],
        "architecture": cfg["Architectures"][0],
        "image": cfg.get("CodeSha256", "")[:12],
        "account_concurrency": account["AccountLimit"]["ConcurrentExecutions"],
        "unreserved_concurrency": account["AccountLimit"]["UnreservedConcurrentExecutions"],
        "reserved_concurrency": reserved,
    }


_REPORT = re.compile(
    r"Duration: ([\d.]+) ms.*?Max Memory Used: (\d+) MB(?:.*?Init Duration: ([\d.]+) ms)?"
)


def report_lines(name: str, region: str, start: float, end: float) -> pd.DataFrame:
    """Lambda's ``REPORT`` lines between two epoch times: duration, memory, init (cold) time."""
    group = f"/aws/lambda/{name}"
    events, token = [], None
    while True:
        args = [
            "logs",
            "filter-log-events",
            "--log-group-name",
            group,
            "--region",
            region,
            "--start-time",
            str(int(start * 1000)),
            "--end-time",
            str(int(end * 1000)),
            "--filter-pattern",
            "REPORT",
        ]
        if token:
            args += ["--next-token", token]
        page = _aws(*args)
        events += page.get("events", [])
        token = page.get("nextToken")
        if not token:
            break
    rows = []
    for e in events:
        m = _REPORT.search(e["message"])
        if m:
            rows.append(
                {
                    "at": e["timestamp"] / 1000,
                    "duration_ms": float(m.group(1)),
                    "max_memory_mb": int(m.group(2)),
                    "init_ms": float(m.group(3)) if m.group(3) else float("nan"),
                }
            )
    return pd.DataFrame(rows, columns=["at", "duration_ms", "max_memory_mb", "init_ms"])


# --- Summary -------------------------------------------------------------------------------------


def summarise(runs: pd.DataFrame) -> pd.DataFrame:
    """Per concurrency level: counts and warm percentiles (client and server-side)."""
    out = []
    for level, part in runs.groupby("concurrency"):
        measured = part[~part.warmup]
        ok = measured[measured.status_code == 200]
        duration = measured.sent_at.max() - measured.sent_at.min()
        row: dict[str, Any] = {
            "concurrency": level,
            "requests": len(measured),
            "ok": len(ok),
            "throttled": int((measured.status_code == 429).sum()),
            "errors": int(((measured.status_code != 200) & (measured.status_code != 429)).sum()),
            "fallback_share": float(ok.fallback_used.astype(bool).mean()) if len(ok) else np.nan,
            "throughput_rps": len(ok) / duration if duration > 0 else np.nan,
        }
        for kind in ("client", "server"):
            values = ok[f"{kind}_ms"].dropna()
            for q in (50, 95, 99):
                row[f"{kind}_p{q}"] = float(np.percentile(values, q)) if len(values) else np.nan
            row[f"{kind}_max"] = float(values.max()) if len(values) else np.nan
        out.append(row)
    return pd.DataFrame(out)


def plot(runs: pd.DataFrame, budget_ms: int, theme: Theme) -> plt.Figure:
    """Warm client round-trip time, one ECDF per concurrency level, against the budget."""
    colours = list(theme.series.values())
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=theme.surface)
    ax.set_facecolor(theme.surface)
    ok = runs[~runs.warmup & (runs.status_code == 200)]
    levels = sorted(ok.concurrency.unique())
    for colour, level in zip(colours, levels, strict=False):
        values = np.sort(ok.loc[ok.concurrency == level, "client_ms"].dropna().to_numpy())
        share = np.arange(1, len(values) + 1) / len(values)
        ax.step(values, share, where="post", color=colour, linewidth=2, label=f"{level} at a time")
        p95 = np.percentile(values, 95)
        ax.plot(
            [p95],
            [0.95],
            marker="o",
            markersize=8,
            color=colour,
            markeredgecolor=theme.surface,
            markeredgewidth=2,
            linestyle="none",
        )
    ax.axvline(budget_ms, color=theme.secondary, linewidth=1, linestyle=(0, (4, 3)))
    right = max(budget_ms, ok.client_ms.max())
    ax.set_xlim(min(budget_ms, ok.client_ms.min()) - 0.1 * (right - budget_ms), None)
    ax.annotate(
        f"budget {budget_ms:,} ms",
        (budget_ms, 0.5),
        xytext=(-6, 0),
        textcoords="offset points",
        color=theme.secondary,
        fontsize=9,
        ha="right",
        va="center",
        rotation=90,
    )
    ax.axhline(0.95, color=theme.baseline, linewidth=1)
    ax.text(
        1.0,
        0.955,
        "p95",
        color=theme.muted,
        fontsize=9,
        ha="right",
        va="bottom",
        transform=ax.get_yaxis_transform(),
    )
    ax.set_xlabel("Round trip from the client (ms)", color=theme.secondary)
    ax.set_ylabel("Share of requests", color=theme.secondary)
    ax.set_ylim(0, 1.02)
    ax.set_title(
        "Warm latency of the live endpoint by concurrency",
        color=theme.text,
        loc="left",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(color=theme.grid, linewidth=0.8)
    ax.tick_params(colors=theme.muted)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(theme.baseline)
    legend = ax.legend(frameon=False, loc="center right", labelcolor=theme.text)
    legend.set_title("Concurrent requests", prop={"size": 9})
    legend.get_title().set_color(theme.secondary)
    return fig


def to_markdown(
    summary: pd.DataFrame,
    runs: pd.DataFrame,
    reports: pd.DataFrame,
    info: Mapping[str, Any],
    lt: Mapping[str, Any],
    commit: str,
    when: str,
) -> str:
    sizes = runs[~runs.warmup].orders
    cold = reports.init_ms.dropna()
    reserved = info["reserved_concurrency"]
    cap = f"reserved {reserved}" if reserved else "no reserved concurrency"
    lines = [
        "# Load test",
        "",
        f"Generated by `python -m fulfilment_optimisation.loadtest` on {when}, commit `{commit}`, "
        f"against the live function URL (image `{info['image']}`).",
        "",
        "## Setup",
        "",
        f"- **Function:** {info['memory_mb']:,} MB ({info['architecture']}), `eu-west-2`, called "
        "from the UK over HTTPS with SigV4-signed requests and one keep-alive connection per "
        "client worker.",
        f"- **Concurrency cap:** {cap}; "
        f"account limit {info['account_concurrency']} "
        f"({info['unreserved_concurrency']} unreserved). Lambda serves one request per instance, "
        "so each level stays at or under the cap.",
        f"- **Requests:** `{lt['solver']}` with `{lt['router']}` routing and a "
        f"{lt['budget_ms']:,} ms budget. Bodies are {lt['window_seconds'] // 60}-minute arrival "
        f"windows of the generator's {', '.join(f'`{s}`' for s in lt['scenarios'])} scenarios on "
        f"development seeds {lt['seeds'][0]}-{lt['seeds'][1]}: {sizes.min()}-{sizes.max()} orders "
        f"per request (median {sizes.median():.0f}), sent in a fixed cycle.",
        f"- **Warm-up:** the first {lt['warmup_per_worker']} requests of each worker at each level "
        "are excluded.",
        "",
        "## Warm latency",
        "",
        "Client = round trip measured by the load generator. Server = the app's `Server-Timing` "
        "(request arrival in the app to response ready), which excludes the network and Lambda's "
        "own routing.",
        "",
        "| Concurrent | Requests | Throttled | Errors | Fallback | Req/s "
        "| Client p50 | Client p95 | Client p99 | Server p50 | Server p95 | Server p99 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary.itertuples():
        lines.append(
            f"| {r.concurrency} | {r.requests} | {r.throttled} | {r.errors} "
            f"| {r.fallback_share:.0%} | {r.throughput_rps:.1f} "
            f"| {r.client_p50:,.0f} | **{r.client_p95:,.0f}** | {r.client_p99:,.0f} "
            f"| {r.server_p50:,.0f} | {r.server_p95:,.0f} | {r.server_p99:,.0f} |"
        )
    lines += [
        "",
        "Times in ms. ![Warm latency ECDF](../../../../projects/01-fulfilment-optimisation/"
        "reports/figures/load_test.png)",
        "",
        "## By request size",
        "",
        "All concurrency levels together. Server-side times in ms.",
        "",
        "| Orders | Requests | Fallback | Server p50 | Server p95 | Server max | Over budget |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in by_size(runs, lt["budget_ms"]).itertuples():
        lines.append(
            f"| {r.orders} | {r.requests} | {r.fallback:.0%} | {r.server_p50:,.0f} "
            f"| {r.server_p95:,.0f} | {r.server_max:,.0f} | {r.over_budget:.0%} |"
        )
    lines += ["", "## Cold starts", ""]
    if len(cold):
        measured = runs[~runs.warmup].groupby("concurrency").sent_at.agg(["min", "max"])
        during = sum(
            # REPORT is logged when an invocation ends: allow for the last request's own duration.
            ((reports["at"] >= lo) & (reports["at"] <= hi + 5) & reports.init_ms.notna()).sum()
            for lo, hi in measured.itertuples(index=False)
        )
        lines.append(
            f"{len(cold)} cold starts during the run, init {cold.min():,.0f}-{cold.max():,.0f} ms "
            f"(median {cold.median():,.0f} ms), from the `Init Duration` in Lambda's `REPORT` "
            "logs; that time is on top of the request's own. "
            + (
                f"{during} of them fell inside the measured (post-warm-up) part of a level, so "
                "those requests' times include a cold start."
                if during
                else "All fell in the warm-up requests, so the tables above are warm only."
            )
        )
    else:
        lines.append(
            "No cold starts in the run's `REPORT` logs: every instance used was already warm "
            "(Lambda keeps idle instances for some minutes). See the README for single cold calls."
        )
    if len(reports):
        lines += [
            "",
            f"Peak memory used: {reports.max_memory_mb.max()} MB of {info['memory_mb']:,} MB.",
        ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--report", action="store_true", help="rebuild the doc and chart from the saved run"
    )
    args = parser.parse_args(argv)
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    lt = cfg.loadtest
    saved_runs, saved_meta = paths.outputs / "loadtest.parquet", paths.outputs / "loadtest.json"
    if args.report:
        runs = read_table(saved_runs)
        meta = json.loads(saved_meta.read_text())
        report(runs, meta, lt, paths)
        return

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    creds = session_credentials()
    info = function_info(lt["function"], lt["region"])
    bodies = request_mix(lt, cfg.generator)
    log.info(
        "%d request bodies; function %s MB, account concurrency %s",
        len(bodies),
        info["memory_mb"],
        info["account_concurrency"],
    )
    if max(lt["concurrency"]) > info["unreserved_concurrency"]:
        raise SystemExit("a concurrency level exceeds the account's unreserved concurrency")

    started = time.time()
    rows = []
    for level in lt["concurrency"]:
        log.info("concurrency %d", level)
        rows += run_level(
            info["url"],
            creds,
            lt["region"],
            bodies,
            level,
            lt["requests_per_level"],
            lt["warmup_per_worker"],
        )
    finished = time.time()
    runs = pd.DataFrame(rows)
    write_table(runs, saved_runs)
    meta = {**info, "commit": commit, "started": started, "finished": finished}
    saved_meta.write_text(json.dumps(meta, indent=2))
    time.sleep(lt["log_delay_s"])  # REPORT lines reach CloudWatch a few seconds late
    report(runs, meta, lt, paths)


def by_size(runs: pd.DataFrame, budget_ms: float) -> pd.DataFrame:
    """Warm successful requests grouped by order count: fallback share and server-side time."""
    ok = runs[~runs.warmup & (runs.status_code == 200)].copy()
    ok["bucket"] = pd.cut(ok.orders, [0, 50, 100, 150, 200, 300, 500])
    rows = []
    for bucket, part in ok.groupby("bucket", observed=True):
        rows.append(
            {
                "orders": f"{bucket.left + 1}-{bucket.right}",
                "requests": len(part),
                "fallback": float(part.fallback_used.astype(bool).mean()),
                "server_p50": float(part.server_ms.median()),
                "server_p95": float(np.percentile(part.server_ms, 95)),
                "server_max": float(part.server_ms.max()),
                "over_budget": float((part.server_ms > budget_ms).mean()),
            }
        )
    return pd.DataFrame(rows)


def report(
    runs: pd.DataFrame, meta: Mapping[str, Any], lt: Mapping[str, Any], paths: ProjectPaths
) -> None:
    """Chart and results doc for a run; the cold-start logs are fetched for the run's window."""
    reports = report_lines(lt["function"], lt["region"], meta["started"] - 1, meta["finished"] + 60)
    summary = summarise(runs)
    log.info("\n%s", summary.to_string(index=False))
    for theme, name in ((LIGHT, "load_test.png"), (DARK, "load_test_dark.png")):
        fig = plot(runs, lt["budget_ms"], theme)
        log.info("wrote %s", save_fig(fig, paths.figures / name))
        plt.close(fig)
    when = dt.datetime.fromtimestamp(meta["started"], dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    doc = RESULTS_DOC / "load_test.md"
    doc.write_text(to_markdown(summary, runs, reports, meta, lt, meta["commit"], when))
    log.info("wrote %s", doc)


if __name__ == "__main__":
    main()
