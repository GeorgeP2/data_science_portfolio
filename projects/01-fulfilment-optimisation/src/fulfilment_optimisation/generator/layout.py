"""Generate a single-block layout with its size drawn from the KIT ranges.

The aisle count and locations per aisle are drawn independently and uniformly from integer ranges,
as the KIT suite's Latin hypercube design does (T17 found no correlation between the two). The
geometry (cell length, aisle spacing, cross-aisle and depot offsets) is fixed at Henn & Wäscher's,
because KIT's distances are abstract units; that also keeps generated layouts comparable with the
benchmark instances. The defaults live in the ``generator.layout`` section of ``config.yaml``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from fulfilment_optimisation.domain import Layout


@dataclass(frozen=True, slots=True)
class LayoutRanges:
    aisles: tuple[int, int]  # inclusive
    locations_per_aisle: tuple[int, int]  # inclusive
    location_length: float
    aisle_spacing: float
    end_offset: float
    depot_offset: float

    def __post_init__(self) -> None:
        for name in ("aisles", "locations_per_aisle"):
            low, high = getattr(self, name)
            if not 1 <= low <= high:
                raise ValueError(f"{name} range {low}-{high} must satisfy 1 <= low <= high")

    @classmethod
    def from_config(cls, section: Mapping[str, Any]) -> LayoutRanges:
        return cls(
            aisles=tuple(section["aisles"]),  # type: ignore[arg-type]
            locations_per_aisle=tuple(section["locations_per_aisle"]),  # type: ignore[arg-type]
            location_length=float(section["location_length"]),
            aisle_spacing=float(section["aisle_spacing"]),
            end_offset=float(section["end_offset"]),
            depot_offset=float(section["depot_offset"]),
        )


def sample_layout(ranges: LayoutRanges, rng: np.random.Generator) -> Layout:
    """A layout with a uniformly drawn size; use ``np.random.default_rng(seed)`` for a fixed one."""
    return Layout(
        n_aisles=int(rng.integers(ranges.aisles[0], ranges.aisles[1], endpoint=True)),
        n_positions=int(
            rng.integers(
                ranges.locations_per_aisle[0], ranges.locations_per_aisle[1], endpoint=True
            )
        ),
        location_length=ranges.location_length,
        aisle_spacing=ranges.aisle_spacing,
        end_offset=ranges.end_offset,
        depot_offset=ranges.depot_offset,
    )
