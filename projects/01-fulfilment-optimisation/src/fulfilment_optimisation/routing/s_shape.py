"""S-shape (traversal) routing for a single-block warehouse with the depot in front of aisle 0.

The picker enters every aisle that holds a pick and walks it end to end, alternating direction,
working left to right. Aisles without picks are skipped. If the number of pick aisles is odd, the
last (rightmost) one is entered from the front, walked to its deepest pick and left the way it came
in. The picker then returns along the front cross aisle to the depot.

For ``k`` pick aisles with the rightmost at ``R``::

    length = 2 * depot_offset + 2 * x(R)
             + (k if k is even else k - 1) * aisle_length
             + (0 if k is even else 2 * y(deepest pick in R))

This is the usual textbook variant (e.g. Roodbergen & de Koster, 2001). Henn & Wäscher (2012) only
describe S-shape informally, so reproducing their published results (T15) is what confirms it.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from fulfilment_optimisation.domain import Batch, Layout, Location, Route


def _by_aisle(locations: Iterable[Location]) -> dict[int, list[Location]]:
    aisles: dict[int, list[Location]] = defaultdict(list)
    for loc in locations:
        aisles[loc.aisle].append(loc)
    return dict(sorted(aisles.items()))


class SShape:
    name = "s_shape"

    def length(self, locations: Iterable[Location], layout: Layout) -> float:
        aisles = _by_aisle(locations)
        if not aisles:
            return 0.0
        last = max(aisles)
        k = len(aisles)
        total = 2 * layout.depot_offset + 2 * layout.x(last)
        if k % 2 == 0:
            return total + k * layout.aisle_length
        deepest = max(loc.position for loc in aisles[last])
        return total + (k - 1) * layout.aisle_length + 2 * layout.y(deepest)

    def route(self, batch: Batch, layout: Layout) -> Route:
        stops: list[Location] = []
        for i, picks in enumerate(_by_aisle(batch.locations).values()):
            # Even-numbered passes (0, 2, ...) go front to back, odd ones back to front. An odd
            # final aisle is in-and-back, so it is also front to back.
            stops.extend(sorted(picks, reverse=i % 2 == 1))
        return Route(batch, tuple(stops), self.length(stops, layout))
