"""When orders arrive during a shift, how many lines they have, and when they are due.

All times are seconds from the start of the shift, as in the KIT suite.

- **Count:** Poisson around ``orders_per_shift`` (T17: KIT's replication counts have variance/mean
  1.03).
- **Arrivals:** ``poisson`` spreads them uniformly over the shift (a homogeneous Poisson process,
  inter-arrival CV 1). ``waves`` mixes that with ``num_waves`` equally spaced bursts: each arrival
  is in a burst with probability ``stochasticity``, at a normally distributed offset of
  ``wave_width`` seconds from the burst's centre. With the default 900 s the inter-arrival CV is
  1.0 / 1.20 / 2.83 at stochasticity 0 / 0.5 / 1, against KIT's OFAT wave settings' 0.99 / 1.13 /
  2.78 (one width can't hit all three; 900 s minimises the squared error at 1,000 orders). KIT's
  LHS stochasticity values aren't used: they don't affect burstiness (T17).
- **Lines:** drawn from a categorical distribution over line counts (``lines`` / ``weights``), e.g.
  KIT's 1-3 lines at 0.8 / 0.15 / 0.05, or Henn & Wäscher's 5-25 uniformly.
- **Due dates:** ``shift_end``, ``relative`` (arrival + ``offset_seconds``) or ``mixed`` (a rule
  per order with the given weights), the KIT rules.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

SHIFT_SECONDS = 8 * 3600.0


def arrival_times(
    n: int,
    rng: np.random.Generator,
    process: str = "poisson",
    shift: float = SHIFT_SECONDS,
    num_waves: int = 5,
    stochasticity: float = 0.0,
    wave_width: float = 900.0,
) -> np.ndarray:
    """``n`` sorted arrival times within ``[0, shift)``."""
    if process == "poisson":
        return np.sort(rng.uniform(0, shift, n))
    if process != "waves":
        raise ValueError(f"unknown arrival process {process!r}; choose 'poisson' or 'waves'")
    centres = (np.arange(num_waves) + 0.5) * shift / num_waves
    in_wave = rng.random(n) < stochasticity
    times = rng.uniform(0, shift, n)
    burst = centres[rng.integers(num_waves, size=n)] + rng.normal(0, wave_width, n)
    times[in_wave] = np.clip(burst[in_wave], 0, np.nextafter(shift, 0))
    return np.sort(times)


def line_counts(
    n: int, rng: np.random.Generator, lines: Sequence[int], weights: Sequence[float] | None = None
) -> np.ndarray:
    """Lines per order: ``lines`` with probabilities ``weights`` (uniform if omitted)."""
    p = None if weights is None else np.asarray(weights, dtype=float) / np.sum(weights)
    return rng.choice(np.asarray(lines), size=n, p=p)


def due_dates(
    arrivals: np.ndarray,
    rng: np.random.Generator,
    rule: Mapping[str, Any],
    shift: float = SHIFT_SECONDS,
) -> np.ndarray:
    """Due date per order under a KIT rule (see the module docstring)."""
    kind = rule["rule"]
    if kind == "shift_end":
        return np.full(arrivals.shape, shift)
    if kind == "relative":
        return arrivals + float(rule["offset_seconds"])
    if kind == "mixed":
        options: list[Mapping[str, Any]] = rule["options"]
        picks = rng.choice(len(options), size=arrivals.size, p=rule["weights"])
        out = np.empty_like(arrivals)
        for i, option in enumerate(options):
            mask = picks == i
            out[mask] = due_dates(arrivals[mask], rng, option, shift)
        return out
    raise ValueError(f"unknown due-date rule {kind!r}; choose shift_end, relative or mixed")
