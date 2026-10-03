"""Largest-gap routing for a single-block warehouse with the depot in front of aisle 0.

The picker walks along the front cross aisle to the leftmost pick aisle and walks it end to end.
They then move right along the back cross aisle and walk the rightmost pick aisle end to end, back
to the front. Each pick aisle in between is split at its largest gap: the gap between adjacent
picks, or between a cross aisle and its nearest pick. Picks above the gap are collected from the
back cross aisle on the way right, and picks below it from the front cross aisle on the way back
to the depot. Neither part crosses the gap.

With one pick aisle the picker goes in from the front to the deepest pick and back out, as in
S-shape. With two, both aisles are walked in full, which also matches S-shape.

For ``k >= 2`` pick aisles, ``L`` the leftmost and ``R`` the rightmost, and ``g_i`` the largest gap
in each aisle in between::

    length = 2 * depot_offset + 2 * x(R) + 2 * aisle_length + sum(2 * (aisle_length - g_i))

Hall (1993), Distance approximations for routing manual pickers in a warehouse. *IIE Transactions*
25(4), 76-87; Roodbergen & de Koster (2001), Routing order pickers in a warehouse with a middle
aisle. *EJOR* 133(1), 32-43.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable

from fulfilment_optimisation.domain import Batch, Layout, Location, Route
from fulfilment_optimisation.routing.base import picks_by_aisle


def split_at_largest_gap(
    picks: list[Location], layout: Layout
) -> tuple[list[Location], list[Location], float]:
    """Split one aisle's picks into those below and above its largest gap, and return the gap.

    Ties go to the gap nearest the front, so the result is deterministic.
    """
    depths = sorted({layout.y(loc.position) for loc in picks})
    bounds = [0.0, *depths, layout.aisle_length]
    gaps = [b - a for a, b in itertools.pairwise(bounds)]
    i = max(range(len(gaps)), key=lambda j: (gaps[j], -j))
    cut = bounds[i]  # deepest point reached from the front
    below = [loc for loc in picks if layout.y(loc.position) <= cut]
    above = [loc for loc in picks if layout.y(loc.position) > cut]
    return below, above, gaps[i]


class LargestGap:
    name = "largest_gap"

    def length(self, locations: Iterable[Location], layout: Layout) -> float:
        # The solvers' hot path, so it works on integer positions per aisle and only measures
        # each middle aisle's largest gap, without building the split (``route`` does that).
        positions: dict[int, list[int]] = {}
        for loc in locations:
            in_aisle = positions.get(loc.aisle)
            if in_aisle is None:
                positions[loc.aisle] = [loc.position]
            else:
                in_aisle.append(loc.position)
        if not positions:
            return 0.0
        first, last = min(positions), max(positions)
        total = 2 * layout.depot_offset + 2 * layout.x(last)
        if len(positions) == 1:
            return total + 2 * layout.y(max(positions[last]))

        step, end, top = layout.location_length, layout.end_offset, layout.n_positions - 1
        total += 2 * layout.aisle_length
        for aisle, in_aisle in positions.items():
            if aisle in (first, last):
                continue
            in_aisle.sort()
            # Gaps to the front and back cross aisles, then between neighbouring picks.
            widest = max(in_aisle[0], top - in_aisle[-1]) * step + end
            for a, b in itertools.pairwise(in_aisle):
                widest = max(widest, (b - a) * step)
            total += 2 * (layout.aisle_length - widest)
        return total

    def route(self, batch: Batch, layout: Layout) -> Route:
        aisles = list(picks_by_aisle(batch.locations).values())
        if len(aisles) <= 1:
            stops = sorted(aisles[0]) if aisles else []
            return Route(batch, tuple(stops), self.length(stops, layout))

        first, *middle, last = aisles
        splits = [split_at_largest_gap(picks, layout) for picks in middle]
        stops = sorted(first)  # front to back
        for _, above, _ in splits:  # left to right along the back cross aisle
            stops.extend(sorted(above, reverse=True))
        stops.extend(sorted(last, reverse=True))  # back to front
        for below, _, _ in reversed(splits):  # right to left along the front cross aisle
            stops.extend(sorted(below))
        return Route(batch, tuple(stops), self.length(stops, layout))
